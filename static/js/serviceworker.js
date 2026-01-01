/**
 * Advanced PWA Service Worker for Kumasi Central Church of Christ
 * Version: 2.0.0
 * 
 * Features:
 * - Intelligent caching strategies (Cache-First, Network-First, Stale-While-Revalidate)
 * - Push notifications support
 * - Background sync for offline form submissions
 * - Periodic background sync for content updates
 * - App update management
 * - Analytics integration
 * - Offline fallback with cached pages
 * - Image optimization and lazy caching
 */

// ============================================
// Configuration
// ============================================

const VERSION = '2.0.0';
const APP_PREFIX = 'kccc-pwa-';
const CACHE_NAMES = {
    core: `${APP_PREFIX}core-v${VERSION}`,
    dynamic: `${APP_PREFIX}dynamic-v${VERSION}`,
    images: `${APP_PREFIX}images-v${VERSION}`,
    api: `${APP_PREFIX}api-v${VERSION}`,
    pages: `${APP_PREFIX}pages-v${VERSION}`,
    fonts: `${APP_PREFIX}fonts-v${VERSION}`,
};

const OFFLINE_URL = '/offline/';
const MAX_CACHE_SIZE = {
    dynamic: 75,
    images: 100,
    api: 50,
    pages: 30,
};

// Core assets to precache - essential for offline functionality
const CORE_ASSETS = [
    '/',
    OFFLINE_URL,
    '/static/css/output.css',
    '/static/css/custom_admin.css',
    '/static/js/main.js',
    '/static/js/settings.js',
    '/static/images/icons/churchPwaIcon.png',
    '/static/images/icons/services-icon1.png',
    '/static/images/icons/about-icon.png',
    '/static/images/icons/contact-icon.png',
    '/static/images/icons/events-icon.png',
    '/static/images/icons/gallery-icon.png',
    '/static/images/icons/faq-icon.png',
];

// Pages to pre-cache for offline access
const IMPORTANT_PAGES = [
    '/',
    '/about/',
    '/services/',
    '/contact/',
    '/events/',
];

// CDN hosts for external resources
const CDN_HOSTS = [
    'cdnjs.cloudflare.com',
    'cdn.jsdelivr.net',
    'unpkg.com',
    'fonts.googleapis.com',
    'fonts.gstatic.com',
    'ajax.googleapis.com',
    'stackpath.bootstrapcdn.com',
];

// ============================================
// Helper Functions
// ============================================

/**
 * Trim cache to maximum size
 */
async function trimCache(cacheName, maxItems) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    if (keys.length > maxItems) {
        await cache.delete(keys[0]);
        return trimCache(cacheName, maxItems);
    }
}

/**
 * Check if a request is valid for caching
 */
function isValidResponse(response) {
    return response && response.status === 200 && response.type === 'basic';
}

/**
 * Check if URL is from a CDN
 */
function isCDNRequest(url) {
    return CDN_HOSTS.some(host => url.hostname.includes(host));
}

/**
 * Generate cache key with versioning
 */
function getCacheKey(request) {
    const url = new URL(request.url);
    // Remove query params for static assets
    if (url.pathname.includes('/static/')) {
        return url.origin + url.pathname;
    }
    return request.url;
}

/**
 * Log message with SW prefix
 */
function log(message, type = 'info') {
    const prefix = `[SW ${VERSION}]`;
    switch(type) {
        case 'error':
            console.error(`${prefix} ${message}`);
            break;
        case 'warn':
            console.warn(`${prefix} ${message}`);
            break;
        default:
            console.log(`${prefix} ${message}`);
    }
}

// ============================================
// Install Event - Precache Core Assets
// ============================================

self.addEventListener('install', event => {
    log('Installing service worker...');
    self.skipWaiting();

    event.waitUntil(
        (async () => {
            const cache = await caches.open(CACHE_NAMES.core);
            
            // Cache core assets one by one to prevent single failure from breaking install
            const cachePromises = CORE_ASSETS.map(async (asset) => {
                try {
                    const response = await fetch(asset, { 
                        credentials: 'same-origin',
                        redirect: 'follow'
                    });
                    if (!response.ok) {
                        throw new Error(`Failed to fetch ${asset}: ${response.status}`);
                    }
                    await cache.put(asset, response);
                    log(`Cached: ${asset}`);
                } catch (error) {
                    log(`Failed to cache ${asset}: ${error.message}`, 'warn');
                }
            });

            await Promise.all(cachePromises);

            // Pre-cache important pages in background
            const pagesCache = await caches.open(CACHE_NAMES.pages);
            IMPORTANT_PAGES.forEach(async (page) => {
                try {
                    const response = await fetch(page);
                    if (response.ok) {
                        await pagesCache.put(page, response);
                    }
                } catch (error) {
                    log(`Background pre-cache failed for ${page}`, 'warn');
                }
            });

            log('Installation complete!');
        })()
    );
});

// ============================================
// Activate Event - Clean Up Old Caches
// ============================================

self.addEventListener('activate', event => {
    log('Activating service worker...');

    event.waitUntil(
        (async () => {
            // Get all cache names
            const cacheNames = await caches.keys();
            
            // Delete old caches
            const deletePromises = cacheNames
                .filter(name => name.startsWith(APP_PREFIX))
                .filter(name => !Object.values(CACHE_NAMES).includes(name))
                .map(name => {
                    log(`Deleting old cache: ${name}`);
                    return caches.delete(name);
                });

            await Promise.all(deletePromises);

            // Take control of all clients immediately
            await self.clients.claim();

            // Notify clients about the update
            const clients = await self.clients.matchAll({ type: 'window' });
            clients.forEach(client => {
                client.postMessage({
                    type: 'SW_ACTIVATED',
                    version: VERSION,
                    message: 'New version activated!'
                });
            });

            log('Activation complete!');
        })()
    );
});

// ============================================
// Fetch Event - Intelligent Caching Strategies
// ============================================

self.addEventListener('fetch', event => {
    const request = event.request;
    
    // Only handle GET requests
    if (request.method !== 'GET') {
        return;
    }

    const url = new URL(request.url);

    // Skip chrome-extension and other non-http protocols
    if (!url.protocol.startsWith('http')) {
        return;
    }

    // Skip problematic requests (kit.fontawesome.com has CORS issues)
    if (url.hostname.includes('kit.fontawesome.com')) {
        event.respondWith(fetch(request, { mode: 'no-cors' }));
        return;
    }

    // Determine caching strategy based on request type
    event.respondWith(handleFetch(request, url));
});

async function handleFetch(request, url) {
    // 1. API Requests - Network First with Cache Fallback
    if (url.pathname.startsWith('/api/') || url.pathname.includes('/keep-alive/')) {
        return networkFirstStrategy(request, CACHE_NAMES.api, MAX_CACHE_SIZE.api);
    }

    // 2. Core Assets - Cache First
    if (CORE_ASSETS.includes(url.pathname)) {
        return cacheFirstStrategy(request, CACHE_NAMES.core);
    }

    // 3. HTML Pages - Network First with Offline Fallback
    if (request.headers.get('Accept')?.includes('text/html')) {
        return networkFirstWithOfflineFallback(request);
    }

    // 4. Images - Cache First with Network Fallback
    if (isImageRequest(url)) {
        return cacheFirstWithNetworkFallback(request, CACHE_NAMES.images, MAX_CACHE_SIZE.images);
    }

    // 5. Fonts - Cache First (fonts rarely change)
    if (url.pathname.includes('.woff') || url.pathname.includes('.ttf') || 
        url.hostname.includes('fonts.gstatic.com')) {
        return cacheFirstStrategy(request, CACHE_NAMES.fonts);
    }

    // 6. CDN Resources - Stale While Revalidate
    if (isCDNRequest(url)) {
        return staleWhileRevalidate(request, CACHE_NAMES.dynamic, MAX_CACHE_SIZE.dynamic);
    }

    // 7. External Images (Cloudinary, Supabase) - Cache First with Background Update
    if (isExternalMedia(url)) {
        return cacheFirstWithBackgroundUpdate(request, CACHE_NAMES.images, MAX_CACHE_SIZE.images);
    }

    // 8. Default - Stale While Revalidate
    return staleWhileRevalidate(request, CACHE_NAMES.dynamic, MAX_CACHE_SIZE.dynamic);
}

/**
 * Check if request is for an image
 */
function isImageRequest(url) {
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico'];
    return imageExtensions.some(ext => url.pathname.toLowerCase().endsWith(ext)) ||
           url.pathname.includes('/image') ||
           (url.searchParams.get('format') || '').includes('image');
}

/**
 * Check if URL is external media (Cloudinary, Supabase storage)
 */
function isExternalMedia(url) {
    return url.hostname.includes('res.cloudinary.com') ||
           (url.hostname.includes('supabase.co') && url.pathname.includes('/storage/'));
}

// ============================================
// Caching Strategies
// ============================================

/**
 * Cache First Strategy - Use cached response, fallback to network
 */
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
        log(`Cache first fetch failed: ${error.message}`, 'warn');
        return new Response('Network error', { status: 503 });
    }
}

/**
 * Network First Strategy - Try network, fallback to cache
 */
async function networkFirstStrategy(request, cacheName, maxSize) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
            trimCache(cacheName, maxSize);
        }
        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        log(`Network first failed, no cache: ${error.message}`, 'warn');
        return new Response(JSON.stringify({ error: 'Offline', cached: false }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

/**
 * Network First with Offline Page Fallback
 */
async function networkFirstWithOfflineFallback(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAMES.pages);
            cache.put(request, networkResponse.clone());
            trimCache(CACHE_NAMES.pages, MAX_CACHE_SIZE.pages);
        }
        return networkResponse;
    } catch (error) {
        // Try to return cached page
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        // Return offline page
        const offlinePage = await caches.match(OFFLINE_URL);
        if (offlinePage) {
            return offlinePage;
        }
        return new Response('Offline', { status: 503 });
    }
}

/**
 * Stale While Revalidate - Return cached, update in background
 */
async function staleWhileRevalidate(request, cacheName, maxSize) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);

    const networkPromise = fetch(request).then(networkResponse => {
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
            trimCache(cacheName, maxSize);
        }
        return networkResponse;
    }).catch(() => null);

    return cachedResponse || await networkPromise || new Response('Resource unavailable', { status: 503 });
}

/**
 * Cache First with Network Fallback - Good for images
 */
async function cacheFirstWithNetworkFallback(request, cacheName, maxSize) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }

    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
            trimCache(cacheName, maxSize);
        }
        return networkResponse;
    } catch (error) {
        // Return a default placeholder image or empty response
        return new Response('', { status: 404 });
    }
}

/**
 * Cache First with Background Update - Good for external media
 */
async function cacheFirstWithBackgroundUpdate(request, cacheName, maxSize) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);

    // Start background update regardless of cache hit
    const networkUpdate = fetch(request).then(async (networkResponse) => {
        if (networkResponse.ok) {
            await cache.put(request, networkResponse.clone());
            trimCache(cacheName, maxSize);
        }
        return networkResponse;
    }).catch(() => null);

    if (cachedResponse) {
        // Return cached response immediately, update in background
        return cachedResponse;
    }

    // Wait for network if no cache
    const networkResponse = await networkUpdate;
    if (networkResponse) {
        return networkResponse;
    }

    return new Response('Media unavailable', { status: 404 });
}

// ============================================
// Push Notifications
// ============================================

self.addEventListener('push', event => {
    log('Push notification received');

    let notificationData = {
        title: 'Kumasi Central Church of Christ',
        body: 'You have a new notification!',
        icon: '/static/images/icons/churchPwaIcon.png',
        badge: '/static/images/icons/churchPwaIcon.png',
        vibrate: [200, 100, 200],
        tag: 'kccc-notification',
        requireInteraction: false,
        data: {
            url: '/',
            timestamp: Date.now()
        }
    };

    // Parse push data if available
    if (event.data) {
        try {
            const pushData = event.data.json();
            notificationData = { ...notificationData, ...pushData };
        } catch (e) {
            notificationData.body = event.data.text();
        }
    }

    const options = {
        body: notificationData.body,
        icon: notificationData.icon,
        badge: notificationData.badge,
        vibrate: notificationData.vibrate,
        tag: notificationData.tag,
        requireInteraction: notificationData.requireInteraction,
        data: notificationData.data,
        actions: notificationData.actions || [
            { action: 'open', title: 'Open' },
            { action: 'dismiss', title: 'Dismiss' }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(notificationData.title, options)
    );
});

self.addEventListener('notificationclick', event => {
    log('Notification clicked');

    event.notification.close();

    const urlToOpen = event.notification.data?.url || '/';

    if (event.action === 'dismiss') {
        return;
    }

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(windowClients => {
                // Check if there's already a window open
                for (const client of windowClients) {
                    if (client.url.includes(self.location.origin) && 'focus' in client) {
                        client.navigate(urlToOpen);
                        return client.focus();
                    }
                }
                // Open new window
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

// ============================================
// Background Sync
// ============================================

self.addEventListener('sync', event => {
    log(`Background sync triggered: ${event.tag}`);

    if (event.tag === 'sync-forms') {
        event.waitUntil(syncPendingForms());
    }

    if (event.tag === 'sync-attendance') {
        event.waitUntil(syncAttendanceData());
    }

    if (event.tag === 'sync-donations') {
        event.waitUntil(syncDonationData());
    }
});

async function syncPendingForms() {
    log('Syncing pending forms...');
    
    try {
        // Get pending form data from IndexedDB
        const pendingData = await getPendingData('forms');
        
        for (const formData of pendingData) {
            try {
                const response = await fetch(formData.url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': formData.csrfToken
                    },
                    body: JSON.stringify(formData.data)
                });

                if (response.ok) {
                    await removePendingData('forms', formData.id);
                    log(`Form synced successfully: ${formData.id}`);
                }
            } catch (error) {
                log(`Failed to sync form ${formData.id}: ${error.message}`, 'error');
            }
        }
    } catch (error) {
        log(`Background sync error: ${error.message}`, 'error');
    }
}

async function syncAttendanceData() {
    // Placeholder for attendance sync
    log('Syncing attendance data...');
}

async function syncDonationData() {
    // Placeholder for donation sync
    log('Syncing donation data...');
}

// ============================================
// Periodic Background Sync
// ============================================

self.addEventListener('periodicsync', event => {
    log(`Periodic sync triggered: ${event.tag}`);

    if (event.tag === 'update-content') {
        event.waitUntil(updateCachedContent());
    }

    if (event.tag === 'check-updates') {
        event.waitUntil(checkForAppUpdates());
    }
});

async function updateCachedContent() {
    log('Updating cached content...');
    
    try {
        // Refresh important pages
        const cache = await caches.open(CACHE_NAMES.pages);
        for (const page of IMPORTANT_PAGES) {
            try {
                const response = await fetch(page);
                if (response.ok) {
                    await cache.put(page, response);
                    log(`Updated cache for: ${page}`);
                }
            } catch (error) {
                log(`Failed to update ${page}`, 'warn');
            }
        }
    } catch (error) {
        log(`Content update error: ${error.message}`, 'error');
    }
}

async function checkForAppUpdates() {
    log('Checking for app updates...');
    
    try {
        // Check if there's a new service worker
        const registration = await self.registration.update();
        if (registration.waiting) {
            // Notify clients about available update
            const clients = await self.clients.matchAll({ type: 'window' });
            clients.forEach(client => {
                client.postMessage({
                    type: 'SW_UPDATE_AVAILABLE',
                    version: VERSION
                });
            });
        }
    } catch (error) {
        log(`Update check error: ${error.message}`, 'error');
    }
}

// ============================================
// Message Handler
// ============================================

self.addEventListener('message', event => {
    log(`Message received: ${event.data.type}`);

    switch (event.data.type) {
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;

        case 'GET_VERSION':
            event.source.postMessage({
                type: 'SW_VERSION',
                version: VERSION
            });
            break;

        case 'CLEAR_CACHE':
            event.waitUntil(clearAllCaches());
            break;

        case 'CACHE_PAGE':
            event.waitUntil(cachePage(event.data.url));
            break;

        case 'PREFETCH':
            event.waitUntil(prefetchUrls(event.data.urls));
            break;
    }
});

async function clearAllCaches() {
    log('Clearing all caches...');
    const cacheNames = await caches.keys();
    await Promise.all(
        cacheNames
            .filter(name => name.startsWith(APP_PREFIX))
            .map(name => caches.delete(name))
    );
    log('All caches cleared!');
}

async function cachePage(url) {
    try {
        const cache = await caches.open(CACHE_NAMES.pages);
        const response = await fetch(url);
        if (response.ok) {
            await cache.put(url, response);
            log(`Page cached: ${url}`);
        }
    } catch (error) {
        log(`Failed to cache page: ${error.message}`, 'warn');
    }
}

async function prefetchUrls(urls) {
    log(`Prefetching ${urls.length} URLs...`);
    const cache = await caches.open(CACHE_NAMES.pages);
    
    await Promise.all(urls.map(async (url) => {
        try {
            const response = await fetch(url, { priority: 'low' });
            if (response.ok) {
                await cache.put(url, response);
            }
        } catch (error) {
            // Silently fail for prefetch
        }
    }));
}

// ============================================
// IndexedDB Helpers (for Background Sync)
// ============================================

const DB_NAME = 'kccc-pwa-sync';
const DB_VERSION = 1;

function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('pending-forms')) {
                db.createObjectStore('pending-forms', { keyPath: 'id', autoIncrement: true });
            }
            if (!db.objectStoreNames.contains('pending-attendance')) {
                db.createObjectStore('pending-attendance', { keyPath: 'id', autoIncrement: true });
            }
            if (!db.objectStoreNames.contains('pending-donations')) {
                db.createObjectStore('pending-donations', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

async function getPendingData(storeName) {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(`pending-${storeName}`, 'readonly');
        const store = transaction.objectStore(`pending-${storeName}`);
        const request = store.getAll();
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

async function removePendingData(storeName, id) {
    const db = await openDatabase();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(`pending-${storeName}`, 'readwrite');
        const store = transaction.objectStore(`pending-${storeName}`);
        const request = store.delete(id);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve();
    });
}

log('Service Worker loaded successfully!');
