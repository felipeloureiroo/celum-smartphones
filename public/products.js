// Catálogo estático da loja (sem banco de dados).
// Cada produto tem: marca, modelo, preço, armazenamento, descrição e um tema visual
// usado para gerar o placeholder de imagem via CSS.
const PRODUCTS = [
  {
    id: 'iphone-15',
    brand: 'Apple',
    model: 'iPhone 15',
    price: 5299,
    storage: '256 GB',
    description:
      'Câmera de 48 MP com modo retrato automático, chip A16 Bionic e construção em alumínio com USB-C.',
    tags: ['camera', 'trabalho'],
    theme: { from: '#1f2937', to: '#4b5563' }
  },
  {
    id: 'galaxy-s24',
    brand: 'Samsung',
    model: 'Galaxy S24',
    price: 4499,
    storage: '256 GB',
    description:
      'Tela AMOLED de 120 Hz, processador de alto desempenho e recursos de produtividade com S Pen compatível.',
    tags: ['trabalho', 'jogos'],
    theme: { from: '#1e3a8a', to: '#3b82f6' }
  },
  {
    id: 'pixel-8a',
    brand: 'Google',
    model: 'Pixel 8a',
    price: 3499,
    storage: '128 GB',
    description:
      'Fotografia computacional de referência, Android puro e sete anos de atualizações garantidas.',
    tags: ['camera'],
    theme: { from: '#065f46', to: '#10b981' }
  },
  {
    id: 'edge-50-pro',
    brand: 'Motorola',
    model: 'Edge 50 Pro',
    price: 3199,
    storage: '512 GB',
    description:
      'Carregamento turbo de 125 W, tela curva pOLED e o maior armazenamento da seleção.',
    tags: ['bateria', 'trabalho'],
    theme: { from: '#4c1d95', to: '#8b5cf6' }
  },
  {
    id: 'redmi-note-13-pro',
    brand: 'Xiaomi',
    model: 'Redmi Note 13 Pro',
    price: 1899,
    storage: '256 GB',
    description:
      'Bateria de 5.100 mAh com autonomia de dois dias e câmera principal de 200 MP por um preço acessível.',
    tags: ['bateria', 'camera'],
    theme: { from: '#9a3412', to: '#f97316' }
  },
  {
    id: 'realme-12-pro-plus',
    brand: 'Realme',
    model: '12 Pro+',
    price: 2299,
    storage: '256 GB',
    description:
      'Desempenho estável em jogos, refrigeração dedicada e taxa de atualização de 120 Hz.',
    tags: ['jogos', 'bateria'],
    theme: { from: '#831843', to: '#ec4899' }
  }
];
