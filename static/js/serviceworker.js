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

// Cache on install
self.addEventListener("install", event => {
    self.skipWaiting(); // Activate immediately
    event.waitUntil(
        caches.open(staticCacheName)
            .then(cache => cache.addAll(filesToCache))
    );
});

// Clear old caches on activate
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(name => name.startsWith("django-pwa-"))
                    .filter(name => name !== staticCacheName)
                    .map(name => caches.delete(name))
            );
        })
    );
    self.clients.claim(); // Take control immediately
});

// Serve from cache, update in background
self.addEventListener("fetch", event => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') return;

    // Handle network requests
    event.respondWith(
        caches.match(event.request)
            .then(cachedResponse => {
                // Always fetch from network in background
                const networkFetch = fetch(event.request)
                    .then(freshResponse => {
                        // Check if response is valid
                        if (freshResponse.ok) {
                            // Clone and update cache
                            caches.open(staticCacheName)
                                .then(cache => cache.put(event.request, freshResponse.clone()));
                        }
                        return freshResponse;
                    })
                    .catch(() => cachedResponse); // Fallback to cache if network fails

                // Return cached response if available, otherwise wait for network
                return cachedResponse || networkFetch;
            })
            .catch(() => {
                // Fallback to offline page
                return caches.match('/offline/');
            })
    );
});
