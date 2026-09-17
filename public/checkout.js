// ---------------------------------------------------------------------------
// Compra com Stripe Checkout (modo de teste)
//
// O navegador só pede ao servidor uma sessão de checkout e é redirecionado
// para a página do Stripe. A chave secreta fica exclusivamente no servidor.
// ---------------------------------------------------------------------------

(function () {
  const grid = document.getElementById('product-grid');
  const notice = document.getElementById('purchase-notice');

  async function startCheckout(button) {
    const original = button.textContent;
    button.disabled = true;
    button.textContent = 'Abrindo pagamento…';

    try {
      const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: button.dataset.id })
      });
      const payload = await response.json().catch(() => ({}));

      if (!response.ok || !payload.url) {
        alert(payload.message || 'Não foi possível iniciar o pagamento.');
        return;
      }

      window.location.href = payload.url;
    } catch (error) {
      alert('Verifique sua conexão e tente novamente.');
    } finally {
      button.disabled = false;
      button.textContent = original;
    }
  }

  grid.addEventListener('click', (event) => {
    const button = event.target.closest('.buy-btn');
    if (button) startCheckout(button);
  });

  // Mensagem ao voltar do Stripe (?compra=sucesso | ?compra=cancelada)
  const status = new URLSearchParams(window.location.search).get('compra');
  if (status === 'sucesso') {
    notice.textContent = 'Pagamento de teste aprovado! Obrigado pela compra.';
    notice.className = 'notice notice-success';
    notice.hidden = false;
  } else if (status === 'cancelada') {
    notice.textContent = 'Pagamento cancelado. Nenhuma cobrança foi feita.';
    notice.className = 'notice notice-cancel';
    notice.hidden = false;
  }
})();
