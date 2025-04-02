const VERSION = '1.0.1'; // Update this whenever cached files change
const staticCacheName = `django-pwa-v${VERSION}`;
const filesToCache = [
  '/offline/',
  '/static/css/django-pwa-app.css',
  '/static/images/icons/icon-72x72.png',
  '/static/images/icons/icon-96x96.png',
  '/static/images/icons/icon-128x128.png',
  '/static/images/icons/icon-144x144.png',
  '/static/images/icons/icon-152x152.png',
  '/static/images/icons/icon-192x192.png',
  '/static/images/icons/icon-384x384.png',
  '/static/images/icons/icon-512x512.png',
  '/static/images/icons/splash-640x1136.png',
  '/static/images/icons/splash-750x1334.png',
  '/static/images/icons/splash-1242x2208.png',
  '/static/images/icons/splash-1125x2436.png',
  '/static/images/icons/splash-828x1792.png',
  '/static/images/icons/splash-1242x2688.png',
  '/static/images/icons/splash-1536x2048.png',
  '/static/images/icons/splash-1668x2224.png',
  '/static/images/icons/splash-1668x2388.png',
  '/static/images/icons/splash-2048x2732.png'
];

// Cache static assets during installation
self.addEventListener("install", event => {
  // Force the waiting service worker to become the active service worker
  self.skipWaiting();
  event.waitUntil(
    caches.open(staticCacheName)
      .then(cache => cache.addAll(filesToCache))
      .catch(err => console.error('Error during service worker installation:', err))
  );
});

// Clean up old caches during activation
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name => name.startsWith("django-pwa-") && name !== staticCacheName)
          .map(name => caches.delete(name))
      );
    })
  );
  // Claim clients immediately so that the updated service worker takes control
  self.clients.claim();
});

// Intercept fetch events with a stale-while-revalidate strategy
self.addEventListener("fetch", event => {
  // Skip non-GET requests (POST, PUT, etc.)
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      const networkFetch = fetch(event.request)
        .then(freshResponse => {
          // Only update the cache if the response is valid
          if (freshResponse && freshResponse.ok) {
            caches.open(staticCacheName)
              .then(cache => cache.put(event.request, freshResponse.clone()))
              .catch(err => console.error('Error updating cache:', err));
          }
          return freshResponse;
        })
        .catch(() => {
          // If network fetch fails, fall back to cache (or offline page)
          return cachedResponse || caches.match('/offline/');
        });
      // Return cached response immediately if available, then update in background
      return cachedResponse || networkFetch;
    })
  );
});
