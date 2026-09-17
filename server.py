"""
Servidor local da loja de smartphones.

Usa apenas a biblioteca padrão do Python — nenhuma dependência para instalar.

- GET  /*                 -> serve os arquivos estáticos de public/
- GET  /api/config        -> entrega ao navegador a chave publicável do Clerk
- POST /api/recomendacao  -> consulta a IA e devolve o smartphone recomendado
- POST /api/checkout      -> cria uma sessão do Stripe Checkout e devolve a URL

A chave da OpenAI é lida EXCLUSIVAMENTE da variável de ambiente OPENAI_API_KEY.
Ela nunca é gravada em disco nem enviada ao navegador.

A chave publicável do Clerk (login) vem da variável CLERK_PUBLISHABLE_KEY.
Ela é pública por natureza (roda no navegador), mas também não fica no código.

A chave secreta de teste do Stripe vem da variável STRIPE_SECRET_KEY e
nunca sai do servidor.

Uso:  python3 server.py
"""

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
CATALOG_FILE = os.path.join(PUBLIC_DIR, "products.js")

PORT = int(os.environ.get("PORT", 3000))

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
# Modelo definido pela atividade. Pode ser sobrescrito por variável de ambiente
# caso a API recuse este nome.
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.6-luna")
OPENAI_TIMEOUT = 45

PRIORITY_LABELS = {
    "camera": "Câmera",
    "bateria": "Bateria",
    "jogos": "Jogos",
    "trabalho": "Trabalho",
}


# --- Clerk (login) ----------------------------------------------------------

CLERK_PUBLISHABLE_KEY = ""  # preenchida em main() a partir da variável de ambiente
CLERK_KEY_RE = re.compile(r"pk_(test|live)_([A-Za-z0-9+/=]+)")


def parse_clerk_key(raw):
    """Extrai a chave publicável de um texto possivelmente "sujo".

    A chave carrega, em base64, o domínio da instância terminado em "$".
    Se o texto colado trouxe algo a mais (rótulo, secret key...), encurta
    até que o base64 decodifique num domínio válido.
    Retorna (chave_limpa, dominio) ou (None, motivo).
    """
    raw = (raw or "").strip().strip('"').strip("'")
    match = CLERK_KEY_RE.search(raw)
    if not match:
        return None, "não encontrei um valor começando com pk_test_ ou pk_live_"

    prefix, body = match.group(1), match.group(2).rstrip("=")
    for end in range(len(body), 15, -1):
        candidate = body[:end]
        try:
            padded = candidate + "=" * (-len(candidate) % 4)
            host = base64.b64decode(padded).decode("ascii")
        except Exception:
            continue
        if re.fullmatch(r"[a-z0-9.-]+\$", host):
            return f"pk_{prefix}_{candidate}", host[:-1]

    return None, "a chave está incompleta ou corrompida (não decodifica num domínio do Clerk)"


def check_clerk():
    """Valida a chave na inicialização e imprime um diagnóstico legível."""
    raw = os.environ.get("CLERK_PUBLISHABLE_KEY", "")
    if not raw.strip():
        print("AVISO: CLERK_PUBLISHABLE_KEY não definida — o login não vai funcionar.")
        return ""

    key, info = parse_clerk_key(raw)
    if not key:
        print(f"ERRO Clerk: {info}. Copie a Publishable key de novo pelo ícone de copiar.")
        return ""

    print(f"Clerk: chave reconhecida ({key[:8]}...) -> instância {info}")
    if key != raw.strip():
        print("Clerk: a variável tinha texto a mais além da chave; usei só a chave.")

    try:
        with urllib.request.urlopen(f"https://{info}/v1/environment", timeout=10):
            print("Clerk: instância encontrada, login pronto para uso.")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")
        try:
            detail = json.loads(detail)["errors"][0]["long_message"]
        except Exception:
            detail = detail[:200]
        print(f"ERRO Clerk: a instância respondeu HTTP {error.code}: {detail}")
    except Exception as error:
        print(f"AVISO Clerk: não consegui contatar {info} ({error}). Verifique a internet.")
    return key


# --- Catálogo ---------------------------------------------------------------


def load_catalog():
    """Lê o catálogo de public/products.js para não duplicar os dados.

    O arquivo é um literal JavaScript; a conversão abaixo cobre exatamente o
    formato usado nele (chaves sem aspas, strings com aspas simples).
    """
    with open(CATALOG_FILE, encoding="utf-8") as handle:
        source = handle.read()

    literal = source[source.index("[") : source.rindex("]") + 1]
    literal = re.sub(r"([{,]\s*)([A-Za-z_]\w*)\s*:", r'\1"\2":', literal)
    literal = literal.replace("'", '"')
    return json.loads(literal)


CATALOG = load_catalog()


# --- Chamada à IA -----------------------------------------------------------


class RecommendationError(Exception):
    """Erro já tratado, com mensagem amigável para a interface."""


def build_messages(budget, priority, affordable):
    lines = [
        "{id} | {brand} {model} | R$ {price} | {storage} | {description}".format(**p)
        for p in affordable
    ]
    system = (
        "Você é um consultor de smartphones de uma loja brasileira. "
        "Escolha UM aparelho da lista fornecida, sem inventar modelos. "
        'Responda somente com JSON válido no formato {"id": "<id da lista>", '
        '"justificativa": "<no máximo 2 frases>"}.'
    )
    user = (
        f"Orçamento máximo: R$ {budget}\n"
        f"Prioridade de uso: {PRIORITY_LABELS[priority]}\n"
        "Catálogo disponível (id | aparelho | preço | armazenamento | descrição):\n"
        + "\n".join(lines)
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def call_openai(messages):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[IA] ERRO: variável de ambiente OPENAI_API_KEY não definida.")
        raise RecommendationError(
            "O serviço de recomendação não está configurado no momento."
        )

    payload = json.dumps({"model": OPENAI_MODEL, "messages": messages}).encode("utf-8")
    request = urllib.request.Request(
        OPENAI_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=OPENAI_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:500]
        print(f"[IA] ERRO HTTP {error.code} da OpenAI: {detail}")
        raise RecommendationError(
            "Não foi possível gerar a recomendação agora. Tente novamente em instantes."
        )
    except Exception as error:  # timeout, DNS, conexão
        print(f"[IA] ERRO de conexão com a OpenAI: {error}")
        raise RecommendationError(
            "Não conseguimos falar com o serviço de recomendação. Tente novamente."
        )


def log_usage(data):
    """Registra no terminal os números pedidos pela atividade."""
    usage = data.get("usage") or {}
    model = data.get("model", OPENAI_MODEL)
    prompt = usage.get("prompt_tokens", usage.get("input_tokens", "?"))
    completion = usage.get("completion_tokens", usage.get("output_tokens", "?"))
    total = usage.get("total_tokens", "?")

    print("[IA] ----- uso de tokens -----")
    print(f"[IA] modelo ............ {model}")
    print(f"[IA] tokens de entrada . {prompt}")
    print(f"[IA] tokens de saída ... {completion}")
    print(f"[IA] total de tokens ... {total}")
    print("[IA] --------------------------")


def parse_choice(data):
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        print(f"[IA] ERRO: resposta em formato inesperado: {str(data)[:300]}")
        raise RecommendationError("Recebemos uma resposta inválida da IA.")

    cleaned = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.MULTILINE)
    try:
        choice = json.loads(cleaned.strip())
        return choice["id"], choice["justificativa"]
    except (ValueError, KeyError):
        print(f"[IA] ERRO: JSON inválido na resposta da IA: {content[:300]}")
        raise RecommendationError("Recebemos uma resposta inválida da IA.")


def format_brl(value):
    return f"R$ {value:,.0f}".replace(",", ".")


def recommend(budget, priority):
    # A filtragem por orçamento é feita aqui: a IA só vê o que cabe no bolso.
    affordable = [p for p in CATALOG if p["price"] <= budget]
    if not affordable:
        cheapest = min(p["price"] for p in CATALOG)
        return {
            "status": "sem_opcoes",
            "message": (
                "Nenhum aparelho do catálogo cabe nesse orçamento. "
                f"O modelo mais acessível custa {format_brl(cheapest)}."
            ),
        }

    data = call_openai(build_messages(budget, priority, affordable))
    log_usage(data)

    chosen_id, reason = parse_choice(data)

    # A IA só pode recomendar itens do catálogo dentro do orçamento.
    product = next((p for p in affordable if p["id"] == chosen_id), None)
    if product is None:
        print(f"[IA] ERRO: a IA devolveu um id fora do catálogo: {chosen_id!r}")
        raise RecommendationError("Recebemos uma resposta inválida da IA.")

    return {
        "status": "ok",
        "product": {
            "brand": product["brand"],
            "model": product["model"],
            "price": product["price"],
            "storage": product["storage"],
        },
        "reason": reason,
    }


# --- Stripe (checkout) ------------------------------------------------------

STRIPE_URL = "https://api.stripe.com/v1/checkout/sessions"


class CheckoutError(Exception):
    """Erro já tratado, com mensagem amigável para a interface."""


def check_stripe():
    """Valida a chave do Stripe na inicialização e imprime um diagnóstico."""
    key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not key:
        print("AVISO: STRIPE_SECRET_KEY não definida — o botão Comprar não vai funcionar.")
        return
    if key.startswith("sk_live_"):
        print("ATENÇÃO Stripe: essa é uma chave de PRODUÇÃO (sk_live_). Use a de teste (sk_test_).")
        return
    if not key.startswith("sk_test_"):
        print("ERRO Stripe: a chave deve começar com sk_test_. Copie a Secret key do modo de teste.")
        return

    request = urllib.request.Request(
        "https://api.stripe.com/v1/balance",
        headers={"Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10):
            print("Stripe: chave de teste válida, checkout pronto para uso.")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")
        try:
            detail = json.loads(detail)["error"]["message"]
        except Exception:
            detail = detail[:200]
        print(f"ERRO Stripe: a chave foi recusada (HTTP {error.code}): {detail}")
    except Exception as error:
        print(f"AVISO Stripe: não consegui contatar a API ({error}). Verifique a internet.")


def create_checkout_session(product, origin):
    key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not key:
        print("[Stripe] ERRO: variável de ambiente STRIPE_SECRET_KEY não definida.")
        raise CheckoutError("O pagamento não está configurado no momento.")

    fields = {
        "mode": "payment",
        "locale": "pt-BR",
        "success_url": f"{origin}/?compra=sucesso",
        "cancel_url": f"{origin}/?compra=cancelada",
        "line_items[0][quantity]": "1",
        "line_items[0][price_data][currency]": "brl",
        "line_items[0][price_data][unit_amount]": str(product["price"] * 100),
        "line_items[0][price_data][product_data][name]": (
            f"{product['brand']} {product['model']} ({product['storage']})"
        ),
        "line_items[0][price_data][product_data][description]": product["description"],
    }
    request = urllib.request.Request(
        STRIPE_URL,
        data=urllib.parse.urlencode(fields).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            session = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:500]
        print(f"[Stripe] ERRO HTTP {error.code}: {detail}")
        raise CheckoutError("Não foi possível iniciar o pagamento. Tente novamente.")
    except Exception as error:
        print(f"[Stripe] ERRO de conexão: {error}")
        raise CheckoutError("Não conseguimos falar com o Stripe. Tente novamente.")

    print(f"[Stripe] sessão {session.get('id')} criada para {product['id']} "
          f"({fields['line_items[0][price_data][unit_amount]']} centavos)")
    return session["url"]


# --- HTTP -------------------------------------------------------------------


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Evita cache durante o desenvolvimento.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

    def send_json(self, status, body):
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.path.split("?")[0].rstrip("/") == "/api/config":
            self.send_json(
                200,
                {"clerkPublishableKey": CLERK_PUBLISHABLE_KEY},
            )
            return
        super().do_GET()

    def handle_checkout(self):
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except ValueError:
            self.send_json(400, {"message": "Requisição inválida."})
            return

        product = next((p for p in CATALOG if p["id"] == body.get("id")), None)
        if product is None:
            self.send_json(400, {"message": "Produto não encontrado."})
            return

        origin = f"http://{self.headers.get('Host', f'localhost:{PORT}')}"
        try:
            self.send_json(200, {"url": create_checkout_session(product, origin)})
        except CheckoutError as error:
            self.send_json(502, {"message": str(error)})
        except Exception as error:
            print(f"[Stripe] ERRO inesperado: {error}")
            self.send_json(500, {"message": "Erro inesperado. Tente novamente."})

    def do_POST(self):
        path = self.path.rstrip("/")
        if path == "/api/checkout":
            self.handle_checkout()
            return
        if path != "/api/recomendacao":
            self.send_error(404, "Not Found")
            return

        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except ValueError:
            self.send_json(400, {"message": "Requisição inválida."})
            return

        budget = body.get("budget")
        priority = body.get("priority")
        if not isinstance(budget, (int, float)) or budget <= 0:
            self.send_json(400, {"message": "Informe um orçamento válido."})
            return
        if priority not in PRIORITY_LABELS:
            self.send_json(400, {"message": "Escolha uma prioridade válida."})
            return

        try:
            self.send_json(200, recommend(int(budget), priority))
        except RecommendationError as error:
            self.send_json(502, {"message": str(error)})
        except Exception as error:  # rede de segurança: nunca vazar stacktrace
            print(f"[IA] ERRO inesperado: {error}")
            self.send_json(500, {"message": "Erro inesperado. Tente novamente."})


def main():
    # Sem buffer: os logs de tokens precisam aparecer assim que a chamada termina.
    sys.stdout.reconfigure(line_buffering=True)

    handler = partial(Handler, directory=PUBLIC_DIR)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), handler)
    print(f"Catálogo carregado: {len(CATALOG)} smartphones")
    print(f"Modelo de IA: {OPENAI_MODEL}")
    if not os.environ.get("OPENAI_API_KEY"):
        print("AVISO: OPENAI_API_KEY não definida — a recomendação vai falhar.")
    global CLERK_PUBLISHABLE_KEY
    CLERK_PUBLISHABLE_KEY = check_clerk()
    check_stripe()
    print(f"Loja rodando em http://localhost:{PORT}  (Ctrl+C para parar)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        server.server_close()


if __name__ == "__main__":
    main()
