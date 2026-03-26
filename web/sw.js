const CACHE_NAME = 'dragon-norteno-v3';
const ASSETS = [
  './',
  './index.html',
  './style.css',
  './app.js',
  './manifest.json'
];

// Instalar: cachear solo assets estáticos
self.addEventListener('install', event => {
  self.skipWaiting(); // Forzar activación inmediata
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
});

// Activar: limpiar caches viejos
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim()) // Tomar control inmediato
  );
});

// Fetch: NUNCA cachear llamadas a la API
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Cualquier request que NO sea al mismo origin (es decir, API) → network only
  if (url.origin !== self.location.origin) {
    event.respondWith(
      fetch(event.request).catch(() => new Response(
        JSON.stringify({ error: 'Sin conexión' }),
        { headers: { 'Content-Type': 'application/json' }, status: 503 }
      ))
    );
    return;
  }

  // Requests a rutas de API en el mismo origen → network only
  const apiPaths = ['/sucursales', '/login', '/categorias', '/productos', '/mesas', '/pedido', '/pedidos', '/reporte'];
  if (apiPaths.some(p => url.pathname.startsWith(p))) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Assets estáticos: cache first, luego network
  event.respondWith(
    caches.match(event.request).then(cached => {
      return cached || fetch(event.request).then(response => {
        // Cachear nuevas respuestas estáticas
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        return response;
      });
    })
  );
});
