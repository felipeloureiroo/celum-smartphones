// ---------------------------------------------------------------------------
// Autenticação com Clerk (login com Google)
//
// A chave publicável NÃO fica neste arquivo: ela é lida pelo servidor da
// variável de ambiente CLERK_PUBLISHABLE_KEY e entregue via GET /api/config.
// ---------------------------------------------------------------------------

(function () {
  const authEl = document.getElementById('auth');
  let clerk = null;

  // A chave publicável carrega, em base64, o domínio do Frontend API do Clerk
  // (ex.: pk_test_<base64("xxx.clerk.accounts.dev$")>). É daí que vem o script.
  function frontendApiFromKey(key) {
    const encoded = key.replace(/^pk_(test|live)_/, '');
    return atob(encoded).replace(/\$$/, '');
  }

  function loadScript(src, attrs) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = src;
      script.async = true;
      script.crossOrigin = 'anonymous';
      Object.entries(attrs || {}).forEach(([k, v]) => script.setAttribute(k, v));
      script.onload = resolve;
      script.onerror = () => reject(new Error('Falha ao carregar ' + src));
      document.head.appendChild(script);
    });
  }

  function button(label, className, onClick) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn btn-sm ' + className;
    btn.textContent = label;
    btn.addEventListener('click', onClick);
    return btn;
  }

  // Estado deslogado: botão "Entrar". Estado logado: nome/e-mail + "Sair".
  function render(user) {
    authEl.innerHTML = '';

    if (!user) {
      authEl.appendChild(button('Entrar', 'btn-primary', () => clerk.openSignIn()));
      return;
    }

    const email = user.primaryEmailAddress ? user.primaryEmailAddress.emailAddress : '';
    const name = document.createElement('span');
    name.className = 'auth-user';
    name.textContent = user.fullName || email || 'Usuário';
    name.title = email;

    authEl.appendChild(name);
    authEl.appendChild(button('Sair', 'btn-ghost', () => clerk.signOut()));
  }

  function renderUnavailable(message) {
    authEl.innerHTML = '';
    authEl.appendChild(button('Entrar', 'btn-primary', () => alert(message)));
  }

  async function init() {
    const config = await fetch('/api/config')
      .then((r) => r.json())
      .catch(() => ({}));

    const key = config.clerkPublishableKey;
    if (!key) {
      console.warn('[auth] CLERK_PUBLISHABLE_KEY não definida no servidor.');
      renderUnavailable('Login não configurado: defina CLERK_PUBLISHABLE_KEY e reinicie o servidor.');
      return;
    }

    try {
      const fapi = frontendApiFromKey(key);
      await loadScript(`https://${fapi}/npm/@clerk/ui@1/dist/ui.browser.js`);
      await loadScript(`https://${fapi}/npm/@clerk/clerk-js@6/dist/clerk.browser.js`, {
        'data-clerk-publishable-key': key
      });

      clerk = window.Clerk;
      const ui = window.__internal_ClerkUICtor;
      await clerk.load(ui ? { ui: { ClerkUI: ui } } : {});

      render(clerk.user);
      clerk.addListener(({ user }) => render(user));
    } catch (error) {
      console.error('[auth]', error);
      const detail = error && error.message ? error.message : String(error);
      renderUnavailable('Não foi possível carregar o login.\n\nDetalhe técnico: ' + detail);
    }
  }

  init();
})();
