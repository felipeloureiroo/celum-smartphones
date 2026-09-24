// ---------------------------------------------------------------------------
// Loja de smartphones — MVP de demonstração
// ---------------------------------------------------------------------------

const brl = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  maximumFractionDigits: 0
});

const PRIORITY_LABELS = {
  camera: 'Câmera',
  bateria: 'Bateria',
  jogos: 'Jogos',
  trabalho: 'Trabalho'
};

// --- Catálogo ---------------------------------------------------------------

function productCard(p) {
  const card = document.createElement('article');
  card.className = 'card';
  card.innerHTML = `
    <div class="card-media" role="img" aria-label="Ilustração do ${p.brand} ${p.model}"
         style="background: linear-gradient(140deg, ${p.theme.from}, ${p.theme.to});">
      <div class="phone-shape" aria-hidden="true"></div>
    </div>
    <div class="card-body">
      <span class="card-brand">${p.brand}</span>
      <h3 class="card-model">${p.model}</h3>
      <p class="card-desc">${p.description}</p>
      <div class="card-foot">
        <span class="card-price">${brl.format(p.price)}</span>
        <span class="pill">${p.storage}</span>
      </div>
      <button class="btn btn-primary btn-sm btn-block buy-btn" type="button" data-id="${p.id}">
        Comprar
      </button>
    </div>
  `;
  return card;
}

function renderCatalog() {
  const grid = document.getElementById('product-grid');
  PRODUCTS.forEach((p) => grid.appendChild(productCard(p)));
}

// --- Formulário "Encontre o smartphone ideal" -------------------------------

const form = document.getElementById('ai-form');
const budgetInput = document.getElementById('budget');
const budgetError = document.getElementById('budget-error');
const priorityError = document.getElementById('priority-error');
const resultEl = document.getElementById('ai-result');
const submitBtn = document.getElementById('submit-btn');

function readForm() {
  const budget = Number(budgetInput.value);
  const checked = form.querySelector('input[name="priority"]:checked');

  const budgetOk = Number.isFinite(budget) && budget > 0;
  const priorityOk = Boolean(checked);

  budgetError.hidden = budgetOk;
  priorityError.hidden = priorityOk;

  if (!budgetOk || !priorityOk) return null;
  return { budget, priority: checked.value };
}

function showLoading() {
  resultEl.innerHTML = `
    <div class="ai-result-panel">
      <div class="skeleton-line"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line short"></div>
    </div>
  `;
}

function showResult(data) {
  if (data.status === 'sem_opcoes') {
    resultEl.innerHTML = `
      <div class="ai-result-panel">
        <h3>Sem opções nesse orçamento</h3>
        <p class="ai-note">${data.message}</p>
      </div>
    `;
    return;
  }

  const p = data.product;
  resultEl.innerHTML = `
    <div class="ai-result-panel">
      <h3>${p.brand} ${p.model}</h3>
      <p class="summary">${brl.format(p.price)} · ${p.storage}</p>
      <p class="ai-note">${data.reason}</p>
    </div>
  `;
}

function showError(message) {
  resultEl.innerHTML = `
    <div class="ai-result-panel">
      <h3>Não foi possível recomendar agora</h3>
      <p class="error">${message}</p>
    </div>
  `;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const data = readForm();
  if (!data) return;

  submitBtn.disabled = true;
  showLoading();

  try {
    const response = await fetch('/api/recomendacao', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
      showError(payload.message || 'Tente novamente em alguns instantes.');
      return;
    }

    showResult(payload);
  } catch (error) {
    showError('Verifique sua conexão e tente novamente.');
  } finally {
    submitBtn.disabled = false;
  }
});

// Limpa o erro assim que o usuário corrige o campo.
budgetInput.addEventListener('input', () => {
  if (budgetInput.value) budgetError.hidden = true;
});
form.querySelectorAll('input[name="priority"]').forEach((input) => {
  input.addEventListener('change', () => {
    priorityError.hidden = true;
  });
});

renderCatalog();
