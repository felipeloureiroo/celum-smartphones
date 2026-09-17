# Loja de Smartphones — MVP de demonstração

Loja online simples, com catálogo estático e a seção **"Encontre o smartphone ideal"**.
Sem banco de dados, sem login, sem checkout. Zero dependências.

## Rodar localmente

```bash
python3 server.py
```

Abra http://localhost:3000

## Arquivos

- `server.py` — servidor estático (biblioteca padrão do Python). Aqui entrará o endpoint da IA.
- `public/index.html` — estrutura da página (hero, catálogo, seção de IA).
- `public/styles.css` — estilo do e-commerce (claro, responsivo).
- `public/products.js` — catálogo estático com 6 smartphones.
- `public/app.js` — renderiza os cards e controla o formulário da seção de IA.
- `public/auth.js` — login com Google via Clerk (botão "Entrar" / "Sair" no header).
- `public/checkout.js` — botão "Comprar" → Stripe Checkout (modo de teste).

## Feature de IA

A seção "Encontre o smartphone ideal" chama `POST /api/recomendacao`. O servidor
filtra o catálogo pelo orçamento, consulta a OpenAI e devolve o aparelho escolhido.

### Configurar a chave

A chave é lida **somente** da variável de ambiente `OPENAI_API_KEY` — nunca fica no
código nem chega ao navegador.

```bash
export OPENAI_API_KEY="sua-chave-aqui"
python3 server.py
```

O modelo padrão é `gpt-5.6-luna` e pode ser trocado sem editar o código:

```bash
export OPENAI_MODEL="outro-modelo"
```

No Replit, cadastre `OPENAI_API_KEY` em **Secrets** (não em arquivo).

### Log de tokens

A cada chamada o terminal registra modelo, tokens de entrada, tokens de saída e total:

```
[IA] ----- uso de tokens -----
[IA] modelo ............ gpt-5.6-luna
[IA] tokens de entrada . 412
[IA] tokens de saída ... 38
[IA] total de tokens ... 450
[IA] --------------------------
```

## Login com Google (Clerk)

O header tem o botão **Entrar**, que abre o modal do Clerk com "Continue with Google".
A chave publicável vem da variável de ambiente `CLERK_PUBLISHABLE_KEY` (o servidor
entrega ao navegador em `GET /api/config`); nada fica no código.

```bash
export CLERK_PUBLISHABLE_KEY="pk_test_..."
python3 server.py
```

Para rodar tudo (IA + login) num só comando:

```bash
export OPENAI_API_KEY="..." CLERK_PUBLISHABLE_KEY="pk_test_..." && python3 server.py
```

## Compra com Stripe Checkout (modo de teste)

Cada card tem o botão **Comprar**. O servidor cria uma sessão de checkout pela API
do Stripe e o navegador é redirecionado para a página de pagamento. A chave secreta
de teste vem da variável `STRIPE_SECRET_KEY` e nunca sai do servidor.

```bash
export STRIPE_SECRET_KEY="sk_test_..."
python3 server.py
```

Cartão de teste: `4242 4242 4242 4242`, qualquer validade futura, qualquer CVC.
