// ===== Service Worker: static/js/service-worker.js =====

// Version & cache names
const VERSION = '1.0.1';
const CORE_CACHE_NAME = `django-pwa-core-v${VERSION}`;
const DYNAMIC_CACHE_NAME = `django-pwa-dynamic-v${VERSION}`;
const API_CACHE_NAME = `django-pwa-api-v${VERSION}`;
const OFFLINE_URL = '/offline/';

// Core assets to precache (list well-known Django static assets)
const CORE_ASSETS = [
  '/',                            // Homepage / App Shell
  OFFLINE_URL,                    // Offline fallback page
  '/static/css/output.css',
  '/static/css/custom_admin.css',
  '/static/js/main.js',
  '/static/js/settings.js',
  // Common icons (adjust these paths as needed)
  '/static/images/icons/churchPwaIcon.png',
  '/static/images/icons/services-icon1.png',
  '/static/images/icons/services-icon.png',
  '/static/images/icons/offline.png',
  '/static/images/icons/gallery-icon.png',
  '/static/images/icons/about-icon.png',
  '/static/images/icons/contact-icon.png',
  '/static/images/icons/events-icon.png',
  '/static/images/icons/events-icon1.png',
  '/static/images/icons/faq-icon.png',
  '/static/images/icons/androidPwd.png',
];

// Utility: Trim cache to a maximum number of items
async function trimCache(cacheName, maxItems) {
  const cache = await caches.open(cacheName);
  const keys = await cache.keys();
  if (keys.length > maxItems) {
    await cache.delete(keys[0]);
    return trimCache(cacheName, maxItems);
  }
}

// Install event: Precache core assets
self.addEventListener('install', event => {
  self.skipWaiting(); // Activate worker immediately
  event.waitUntil(
    caches.open(CORE_CACHE_NAME)
      .then(cache => {
        // Cache each file individually so that one missing file won't break installation
        return Promise.all(
          CORE_ASSETS.map(asset => {
            return fetch(asset)
              .then(response => {
                if (!response.ok) {
                  throw new Error(`Failed to fetch ${asset}: ${response.statusText}`);
                }
                return cache.put(asset, response);
              })
              .catch(error => {
                console.error(`Error caching ${asset}:`, error);
              });
          })
        );
      })
      .catch(err => console.error('Error during service worker install:', err))
  );
});

// Activate event: Clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(name =>
          name !== CORE_CACHE_NAME &&
          name !== DYNAMIC_CACHE_NAME &&
          name !== API_CACHE_NAME
        ).map(name => caches.delete(name))
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event: Different caching strategies based on request type
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);

  // Bypass problematic CDNs (e.g., kit.fontawesome.com)
  if (url.hostname.includes('kit.fontawesome.com')) {
    event.respondWith(fetch(event.request, { mode: 'no-cors' }));
    return;
  }

  // 1. API requests: Network-first strategy.
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then(networkResponse => {
          if (networkResponse && networkResponse.ok) {
            const responseClone = networkResponse.clone();
            caches.open(API_CACHE_NAME).then(cache => cache.put(event.request, responseClone));
          }
          return networkResponse;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // 2. Core static assets (pre-cached): Cache-first strategy.
  if (CORE_ASSETS.includes(url.pathname)) {
    event.respondWith(
      caches.match(event.request)
        .then(cachedResponse => cachedResponse || fetch(event.request))
    );
    return;
  }

  // 3. HTML pages: Network-first with offline fallback.
  if (event.request.headers.get('Accept')?.includes('text/html')) {
    event.respondWith(
      fetch(event.request)
        .then(response => response)
        .catch(() => caches.match(OFFLINE_URL))
    );
    return;
  }

  // 4. Cloudinary images: Cache-first with background revalidation.
  if (url.hostname.includes('res.cloudinary.com')) {
    event.respondWith(
      caches.open(DYNAMIC_CACHE_NAME).then(cache => {
        return cache.match(event.request).then(cachedResponse => {
          const networkFetch = fetch(event.request).then(networkResponse => {
            if (networkResponse && networkResponse.ok) {
              const responseClone = networkResponse.clone();
              cache.put(event.request, responseClone);
              trimCache(DYNAMIC_CACHE_NAME, 100);
            }
            return networkResponse;
          }).catch(() => cachedResponse);
          return cachedResponse || networkFetch;
        });
      })
    );
    return;
  }

  // 5. Supabase storage files: Cache-first with background revalidation.
  if (url.hostname.includes('supabase.co') && url.pathname.includes('/storage/')) {
    event.respondWith(
      caches.open(DYNAMIC_CACHE_NAME).then(cache => {
        return cache.match(event.request).then(cachedResponse => {
          const networkFetch = fetch(event.request).then(networkResponse => {
            if (networkResponse && networkResponse.ok) {
              const responseClone = networkResponse.clone();
              cache.put(event.request, responseClone);
              trimCache(DYNAMIC_CACHE_NAME, 50);
            }
            return networkResponse;
          }).catch(() => cachedResponse);
          return cachedResponse || networkFetch;
        });
      })
    );
    return;
  }

  // 6. Popular CDNs: Use stale-while-revalidate strategy.
  if (
    url.hostname.includes('cdnjs.cloudflare.com') ||
    url.hostname.includes('cdn.jsdelivr.net') ||
    url.hostname.includes('unpkg.com') ||
    url.hostname.includes('esm.sh') ||
    url.hostname.includes('ajax.googleapis.com') ||
    url.hostname.includes('stackpath.bootstrapcdn.com') ||
    url.hostname.includes('fonts.googleapis.com') ||
    url.hostname.includes('fonts.gstatic.com') ||
    url.hostname.includes('polyfill.io')
  ) {
    event.respondWith(
      caches.open(DYNAMIC_CACHE_NAME).then(cache => {
        return cache.match(event.request).then(cachedResponse => {
          const networkFetch = fetch(event.request).then(networkResponse => {
            if (networkResponse && networkResponse.ok) {
              const responseClone = networkResponse.clone();
              cache.put(event.request, responseClone);
              trimCache(DYNAMIC_CACHE_NAME, 100);
            }
            return networkResponse;
          });
          return cachedResponse || networkFetch;
        });
      })
    );
    return;
  }

  // 7. Default: Use stale-while-revalidate for other requests.
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      const networkFetch = fetch(event.request).then(networkResponse => {
        if (networkResponse && networkResponse.ok) {
          const responseClone = networkResponse.clone();
          caches.open(DYNAMIC_CACHE_NAME).then(cache => {
            cache.put(event.request, responseClone);
            trimCache(DYNAMIC_CACHE_NAME, 50);
          });
        }
        return networkResponse;
      });
      return cachedResponse || networkFetch;
    })
  );
});
