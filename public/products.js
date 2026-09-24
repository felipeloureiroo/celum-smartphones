// Catálogo estático da loja (sem banco de dados).
// Cada produto tem: marca, modelo, preço, armazenamento, descrição e a imagem
// correspondente em public/img/. Os mesmos dados alimentam a recomendação por IA
// (o servidor lê este arquivo em server.py).
const PRODUCTS = [
  {
    id: 'iphone-16',
    brand: 'Apple',
    model: 'iPhone 16',
    price: 4299,
    storage: '128 GB',
    description:
      'Chip A18, câmera dupla de 48 MP com modo retrato automático e botão de controle da câmera.',
    tags: ['camera', 'trabalho'],
    image: 'iphone-16.png'
  },
  {
    id: 'iphone-16-pro',
    brand: 'Apple',
    model: 'iPhone 16 Pro',
    price: 5799,
    storage: '256 GB',
    description:
      'Chip A18 Pro, tela ProMotion de 120 Hz, teleobjetiva de 5x e gravação em 4K 120 fps.',
    tags: ['camera', 'jogos', 'trabalho'],
    image: 'iphone-16-pro.png'
  },
  {
    id: 'iphone-16-pro-max',
    brand: 'Apple',
    model: 'iPhone 16 Pro Max',
    price: 6799,
    storage: '256 GB',
    description:
      'A maior tela e a maior autonomia da linha, com chip A18 Pro e sistema de câmeras profissional.',
    tags: ['camera', 'bateria', 'jogos', 'trabalho'],
    image: 'iphone-16-pro-max.png'
  },
  {
    id: 'galaxy-s25',
    brand: 'Samsung',
    model: 'Galaxy S25',
    price: 3299,
    storage: '256 GB',
    description:
      'Compacto e potente, com tela AMOLED de 120 Hz e recursos de produtividade do Galaxy AI.',
    tags: ['trabalho', 'jogos'],
    image: 'galaxy-s25.png'
  },
  {
    id: 'galaxy-s25-plus',
    brand: 'Samsung',
    model: 'Galaxy S25+',
    price: 3999,
    storage: '256 GB',
    description:
      'Tela maior de 6,7 polegadas e bateria de 4.900 mAh para um dia inteiro de uso intenso.',
    tags: ['bateria', 'trabalho'],
    image: 'galaxy-s25-plus.png'
  },
  {
    id: 'galaxy-s25-ultra',
    brand: 'Samsung',
    model: 'Galaxy S25 Ultra',
    price: 5299,
    storage: '256 GB',
    description:
      'Câmera de 200 MP, zoom óptico de 5x e S Pen integrada para anotações e trabalho.',
    tags: ['camera', 'trabalho', 'jogos'],
    image: 'galaxy-s25-ultra.png'
  },
  {
    id: 'xiaomi-15',
    brand: 'Xiaomi',
    model: '15',
    price: 3399,
    storage: '256 GB',
    description:
      'Câmeras com lentes Leica, corpo compacto e carregamento rápido de 90 W.',
    tags: ['camera', 'bateria'],
    image: 'xiaomi-15.png'
  },
  {
    id: 'xiaomi-15-pro',
    brand: 'Xiaomi',
    model: '15 Pro',
    price: 3799,
    storage: '256 GB',
    description:
      'Bateria de 6.100 mAh, refrigeração dedicada e desempenho estável em jogos pesados.',
    tags: ['bateria', 'jogos'],
    image: 'xiaomi-15-pro.png'
  },
  {
    id: 'xiaomi-15-ultra',
    brand: 'Xiaomi',
    model: '15 Ultra',
    price: 5499,
    storage: '512 GB',
    description:
      'Conjunto Leica com teleobjetiva de 200 MP, o maior armazenamento da loja e bateria de longa duração.',
    tags: ['camera', 'bateria'],
    image: 'xiaomi-15-ultra.png'
  }
];
