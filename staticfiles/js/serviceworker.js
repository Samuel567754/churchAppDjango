// ===== Enhanced Service Worker for Church PWA =====
// Version & cache names
const VERSION = '2.0.0';
const CORE_CACHE = `church-pwa-core-v${VERSION}`;
const DYNAMIC_CACHE = `church-pwa-dynamic-v${VERSION}`;
const IMAGE_CACHE = `church-pwa-images-v${VERSION}`;
const API_CACHE = `church-pwa-api-v${VERSION}`;
const OFFLINE_URL = '/offline/';

// ===== Cache Configuration =====
const CACHE_LIMITS = {
  dynamic: 100,
  images: 50,
  api: 30
};

// Core assets to precache immediately
const CORE_ASSETS = [
  '/',
  OFFLINE_URL,
  '/static/css/output.css',
  '/static/js/main.js',
  '/static/js/settings.js',
  '/static/images/icons/churchPwaIcon.png',
  '/static/images/icons/androidPwd.png',
];

// ===== Utility Functions =====

// Limit cache size
async function limitCacheSize(cacheName, maxItems) {
  const cache = await caches.open(cacheName);
  const keys = await cache.keys();
  if (keys.length > maxItems) {
    await cache.delete(keys[0]);
    return limitCacheSize(cacheName, maxItems);
  }
}

// Check if request is an image
function isImage(request) {
  const acceptHeader = request.headers.get('Accept');
  return acceptHeader && acceptHeader.includes('image');
}

// Check if request is an API call
function isApiRequest(url) {
  return url.pathname.startsWith('/api/') || 
         url.pathname.startsWith('/keep-alive/') ||
         url.pathname.startsWith('/health/');
}

// Check if request is for static assets
function isStaticAsset(url) {
  return url.pathname.startsWith('/static/') || 
         url.pathname.startsWith('/media/');
}

// Check if request is for HTML page
function isHtmlRequest(request) {
  const acceptHeader = request.headers.get('Accept');
  return acceptHeader && acceptHeader.includes('text/html');
}

// Check if request is from external CDN
function isExternalCDN(url) {
  const cdnHosts = [
    'cdn.jsdelivr.net',
    'cdnjs.cloudflare.com',
    'unpkg.com',
    'fonts.googleapis.com',
    'fonts.gstatic.com',
    'ajax.googleapis.com',
    'stackpath.bootstrapcdn.com'
  ];
  return cdnHosts.some(host => url.hostname.includes(host));
}

// Check if request is for cloud storage
function isCloudStorage(url) {
  return url.hostname.includes('cloudinary.com') ||
         url.hostname.includes('supabase.co') ||
         url.hostname.includes('amazonaws.com');
}

// ===== Install Event =====
self.addEventListener('install', event => {
  console.log('[SW] Installing Service Worker v' + VERSION);
  self.skipWaiting();
  
  event.waitUntil(
    caches.open(CORE_CACHE).then(cache => {
      console.log('[SW] Precaching core assets');
      return Promise.all(
        CORE_ASSETS.map(asset => {
          return fetch(asset, { mode: 'no-cors' })
            .then(response => {
              if (!response.ok && response.type !== 'opaque') {
                throw new Error(`Failed to fetch ${asset}`);
              }
              return cache.put(asset, response);
            })
            .catch(err => {
              console.warn(`[SW] Failed to cache ${asset}:`, err.message);
            });
        })
      );
    })
  );
});

// ===== Activate Event =====
self.addEventListener('activate', event => {
  console.log('[SW] Activating Service Worker v' + VERSION);
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name => {
            return name.startsWith('church-pwa-') && 
                   ![CORE_CACHE, DYNAMIC_CACHE, IMAGE_CACHE, API_CACHE].includes(name);
          })
          .map(name => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => self.clients.claim())
  );
});

// ===== Fetch Event =====
self.addEventListener('fetch', event => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;
  
  const url = new URL(event.request.url);
  
  // Skip chrome-extension and other non-http(s) requests
  if (!url.protocol.startsWith('http')) return;
  
  // Skip problematic requests
  if (url.hostname.includes('kit.fontawesome.com') ||
      url.pathname.includes('serviceworker') ||
      url.pathname.includes('manifest')) {
    return;
  }

  // Strategy 1: API requests - Network first, cache fallback
  if (isApiRequest(url)) {
    event.respondWith(networkFirstStrategy(event.request, API_CACHE, CACHE_LIMITS.api));
    return;
  }

  // Strategy 2: Static assets - Cache first, network fallback
  if (isStaticAsset(url)) {
    event.respondWith(cacheFirstStrategy(event.request, CORE_CACHE));
    return;
  }

  // Strategy 3: External CDN - Stale while revalidate
  if (isExternalCDN(url)) {
    event.respondWith(staleWhileRevalidate(event.request, DYNAMIC_CACHE, CACHE_LIMITS.dynamic));
    return;
  }

  // Strategy 4: Cloud storage images - Cache first with network update
  if (isCloudStorage(url)) {
    event.respondWith(cacheFirstWithNetworkUpdate(event.request, IMAGE_CACHE, CACHE_LIMITS.images));
    return;
  }

  // Strategy 5: Images - Cache first
  if (isImage(event.request)) {
    event.respondWith(cacheFirstStrategy(event.request, IMAGE_CACHE));
    return;
  }

  // Strategy 6: HTML pages - Network first with offline fallback
  if (isHtmlRequest(event.request)) {
    event.respondWith(networkFirstWithOffline(event.request));
    return;
  }

  // Default: Stale while revalidate
  event.respondWith(staleWhileRevalidate(event.request, DYNAMIC_CACHE, CACHE_LIMITS.dynamic));
});

// ===== Caching Strategies =====

// Network First Strategy
async function networkFirstStrategy(request, cacheName, cacheLimit) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
      limitCacheSize(cacheName, cacheLimit);
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    return cachedResponse || new Response(JSON.stringify({ error: 'Offline' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Cache First Strategy
async function cacheFirstStrategy(request, cacheName) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    return new Response('Resource not available offline', { status: 503 });
  }
}

// Stale While Revalidate Strategy
async function staleWhileRevalidate(request, cacheName, cacheLimit) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  const networkFetch = fetch(request).then(networkResponse => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
      limitCacheSize(cacheName, cacheLimit);
    }
    return networkResponse;
  }).catch(() => cachedResponse);
  
  return cachedResponse || networkFetch;
}

// Cache First with Background Network Update
async function cacheFirstWithNetworkUpdate(request, cacheName, cacheLimit) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  // Background fetch to update cache
  fetch(request).then(networkResponse => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
      limitCacheSize(cacheName, cacheLimit);
    }
  }).catch(() => {});
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    return new Response('Image not available offline', { status: 503 });
  }
}

// Network First with Offline Fallback
async function networkFirstWithOffline(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    return caches.match(OFFLINE_URL);
  }
}

// ===== Background Sync =====
self.addEventListener('sync', event => {
  console.log('[SW] Background sync triggered:', event.tag);
  
  if (event.tag === 'sync-forms') {
    event.waitUntil(syncFormData());
  }
});

async function syncFormData() {
  // Implement form data sync when back online
  console.log('[SW] Syncing form data...');
}

// ===== Push Notifications =====
self.addEventListener('push', event => {
  console.log('[SW] Push notification received');
  
  let data = { title: 'Church Update', body: 'You have a new notification!' };
  
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data.body = event.data.text();
    }
  }
  
  const options = {
    body: data.body,
    icon: '/static/images/icons/churchPwaIcon.png',
    badge: '/static/images/icons/churchPwaIcon.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/',
      dateOfArrival: Date.now()
    },
    actions: [
      { action: 'open', title: 'Open' },
      { action: 'close', title: 'Dismiss' }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
  console.log('[SW] Notification clicked:', event.action);
  event.notification.close();
  
  if (event.action === 'close') return;
  
  const urlToOpen = event.notification.data?.url || '/';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(windowClients => {
        // Check if there's already a window open
        for (const client of windowClients) {
          if (client.url === urlToOpen && 'focus' in client) {
            return client.focus();
          }
        }
        // Open new window if not found
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});

// ===== Message Handler =====
self.addEventListener('message', event => {
  console.log('[SW] Message received:', event.data);
  
  if (event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }
  
  if (event.data.action === 'clearCache') {
    event.waitUntil(
      caches.keys().then(names => {
        return Promise.all(names.map(name => caches.delete(name)));
      })
    );
  }
});

console.log('[SW] Service Worker v' + VERSION + ' loaded');
