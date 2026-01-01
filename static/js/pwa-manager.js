/**
 * Advanced PWA Manager for Kumasi Central Church of Christ
 * Version: 2.0.0
 * 
 * Features:
 * - Smart app install prompt management
 * - Service worker lifecycle management
 * - Push notification management
 * - Background sync integration
 * - Network status monitoring
 * - App update handling with user notification
 * - Performance monitoring
 * - Analytics integration
 */

class PWAManager {
    constructor(options = {}) {
        this.options = {
            serviceWorkerPath: '/serviceworker.js',
            promptDelay: 30000, // 30 seconds before showing install prompt
            updateCheckInterval: 3600000, // Check for updates every hour
            enablePushNotifications: true,
            enableBackgroundSync: true,
            enableAnalytics: true,
            vapidPublicKey: null, // Set this for push notifications
            onInstallPromptShown: null,
            onInstalled: null,
            onUpdateAvailable: null,
            onOnline: null,
            onOffline: null,
            ...options
        };

        this.deferredPrompt = null;
        this.registration = null;
        this.isInstalled = false;
        this.isOnline = navigator.onLine;
        this.installPromptShown = false;
        this.updateAvailable = false;

        this.init();
    }

    /**
     * Initialize the PWA Manager
     */
    async init() {
        console.log('[PWA Manager] Initializing...');

        // Check if already installed
        this.checkInstallState();

        // Register service worker
        await this.registerServiceWorker();

        // Setup event listeners
        this.setupEventListeners();

        // Setup network monitoring
        this.setupNetworkMonitoring();

        // Schedule update checks
        this.scheduleUpdateChecks();

        console.log('[PWA Manager] Initialization complete!');
    }

    /**
     * Check if app is already installed
     */
    checkInstallState() {
        // Check display-mode
        if (window.matchMedia('(display-mode: standalone)').matches) {
            this.isInstalled = true;
            console.log('[PWA Manager] App is running in standalone mode');
        }

        // Check iOS standalone
        if (window.navigator.standalone === true) {
            this.isInstalled = true;
            console.log('[PWA Manager] App is running as iOS standalone');
        }

        // Check if installed via getInstalledRelatedApps
        if ('getInstalledRelatedApps' in navigator) {
            navigator.getInstalledRelatedApps().then(apps => {
                if (apps.length > 0) {
                    this.isInstalled = true;
                    console.log('[PWA Manager] App is installed (Related Apps API)');
                }
            });
        }
    }

    /**
     * Register the service worker
     */
    async registerServiceWorker() {
        if (!('serviceWorker' in navigator)) {
            console.warn('[PWA Manager] Service workers not supported');
            return;
        }

        try {
            this.registration = await navigator.serviceWorker.register(
                this.options.serviceWorkerPath,
                { scope: '/' }
            );

            console.log('[PWA Manager] Service worker registered:', this.registration.scope);

            // Handle updates
            this.handleServiceWorkerUpdates();

            // Setup message handler
            this.setupMessageHandler();

        } catch (error) {
            console.error('[PWA Manager] Service worker registration failed:', error);
        }
    }

    /**
     * Handle service worker updates
     */
    handleServiceWorkerUpdates() {
        // New service worker installing
        this.registration.addEventListener('updatefound', () => {
            const newWorker = this.registration.installing;
            console.log('[PWA Manager] New service worker installing...');

            newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed') {
                    if (navigator.serviceWorker.controller) {
                        // New update available
                        this.updateAvailable = true;
                        console.log('[PWA Manager] Update available!');
                        this.showUpdateNotification();

                        if (this.options.onUpdateAvailable) {
                            this.options.onUpdateAvailable();
                        }
                    } else {
                        // Fresh install
                        console.log('[PWA Manager] Content cached for offline use');
                    }
                }
            });
        });

        // Check for updates on page focus
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                this.registration.update();
            }
        });
    }

    /**
     * Setup message handler for service worker communication
     */
    setupMessageHandler() {
        navigator.serviceWorker.addEventListener('message', event => {
            const { type, version, message } = event.data;

            switch (type) {
                case 'SW_ACTIVATED':
                    console.log(`[PWA Manager] Service worker activated: v${version}`);
                    this.showToast(message || 'App updated!', 'success');
                    break;

                case 'SW_UPDATE_AVAILABLE':
                    this.updateAvailable = true;
                    this.showUpdateNotification();
                    break;

                case 'SW_VERSION':
                    console.log(`[PWA Manager] Service worker version: ${version}`);
                    break;
            }
        });
    }

    /**
     * Setup event listeners for install prompt and app lifecycle
     */
    setupEventListeners() {
        // Before install prompt
        window.addEventListener('beforeinstallprompt', (event) => {
            console.log('[PWA Manager] Install prompt available');
            event.preventDefault();
            this.deferredPrompt = event;

            // Show install button after delay (if not already installed)
            if (!this.isInstalled && !this.installPromptShown) {
                setTimeout(() => {
                    this.showInstallPrompt();
                }, this.options.promptDelay);
            }
        });

        // App installed
        window.addEventListener('appinstalled', () => {
            console.log('[PWA Manager] App installed successfully!');
            this.isInstalled = true;
            this.deferredPrompt = null;
            this.hideInstallPrompt();

            if (this.options.onInstalled) {
                this.options.onInstalled();
            }

            // Track installation
            this.trackEvent('pwa_installed');
            this.showToast('App installed successfully! 🎉', 'success');
        });

        // Display mode change
        window.matchMedia('(display-mode: standalone)').addEventListener('change', (event) => {
            if (event.matches) {
                console.log('[PWA Manager] Switched to standalone mode');
                this.isInstalled = true;
            }
        });
    }

    /**
     * Setup network status monitoring
     */
    setupNetworkMonitoring() {
        const updateOnlineStatus = () => {
            const wasOnline = this.isOnline;
            this.isOnline = navigator.onLine;

            if (this.isOnline && !wasOnline) {
                console.log('[PWA Manager] Back online');
                this.showToast('Connection restored! 🌐', 'success');
                document.body.classList.remove('pwa-offline');
                document.body.classList.add('pwa-online');
                
                if (this.options.onOnline) {
                    this.options.onOnline();
                }

                // Trigger any pending syncs
                this.triggerBackgroundSync();
            } else if (!this.isOnline && wasOnline) {
                console.log('[PWA Manager] Gone offline');
                this.showToast('You are offline. Some features may be limited.', 'warning');
                document.body.classList.remove('pwa-online');
                document.body.classList.add('pwa-offline');
                
                if (this.options.onOffline) {
                    this.options.onOffline();
                }
            }
        };

        window.addEventListener('online', updateOnlineStatus);
        window.addEventListener('offline', updateOnlineStatus);

        // Initial state
        document.body.classList.add(this.isOnline ? 'pwa-online' : 'pwa-offline');
    }

    /**
     * Schedule periodic update checks
     */
    scheduleUpdateChecks() {
        setInterval(() => {
            if (this.registration) {
                console.log('[PWA Manager] Checking for updates...');
                this.registration.update();
            }
        }, this.options.updateCheckInterval);
    }

    /**
     * Show install prompt UI
     */
    showInstallPrompt() {
        if (!this.deferredPrompt || this.isInstalled || this.installPromptShown) {
            return;
        }

        this.installPromptShown = true;

        // Create and show install banner
        this.createInstallBanner();

        if (this.options.onInstallPromptShown) {
            this.options.onInstallPromptShown();
        }

        this.trackEvent('pwa_install_prompt_shown');
    }

    /**
     * Create install banner UI
     */
    createInstallBanner() {
        // Remove existing banner if any
        const existingBanner = document.getElementById('pwa-install-banner');
        if (existingBanner) {
            existingBanner.remove();
        }

        const banner = document.createElement('div');
        banner.id = 'pwa-install-banner';
        banner.innerHTML = `
            <div class="pwa-install-content">
                <div class="pwa-install-icon">
                    <img src="/static/images/icons/churchPwaIcon.png" alt="App Icon" width="48" height="48">
                </div>
                <div class="pwa-install-text">
                    <strong>Install Our App</strong>
                    <span>Get quick access and offline features</span>
                </div>
                <div class="pwa-install-actions">
                    <button class="pwa-install-btn" id="pwa-install-btn">Install</button>
                    <button class="pwa-dismiss-btn" id="pwa-dismiss-btn">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        // Add styles
        const styles = document.createElement('style');
        styles.textContent = `
            #pwa-install-banner {
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%) translateY(100px);
                z-index: 10000;
                animation: slideUp 0.5s ease forwards;
                max-width: 400px;
                width: calc(100% - 40px);
            }

            @keyframes slideUp {
                to { transform: translateX(-50%) translateY(0); }
            }

            .pwa-install-content {
                display: flex;
                align-items: center;
                gap: 1rem;
                padding: 1rem 1.25rem;
                background: linear-gradient(135deg, #AD4477 0%, #8B3660 100%);
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(173, 68, 119, 0.4);
                color: white;
            }

            .pwa-install-icon img {
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }

            .pwa-install-text {
                flex: 1;
                display: flex;
                flex-direction: column;
            }

            .pwa-install-text strong {
                font-size: 1rem;
                margin-bottom: 2px;
            }

            .pwa-install-text span {
                font-size: 0.85rem;
                opacity: 0.9;
            }

            .pwa-install-actions {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .pwa-install-btn {
                padding: 0.6rem 1.25rem;
                background: white;
                color: #AD4477;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 0.95rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .pwa-install-btn:hover {
                transform: scale(1.05);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }

            .pwa-dismiss-btn {
                padding: 0.5rem;
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 50%;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.3s ease;
                color: white;
            }

            .pwa-dismiss-btn:hover {
                background: rgba(255, 255, 255, 0.3);
            }

            @media (max-width: 480px) {
                .pwa-install-content {
                    flex-wrap: wrap;
                }
                
                .pwa-install-text {
                    flex-basis: calc(100% - 64px);
                }
                
                .pwa-install-actions {
                    flex-basis: 100%;
                    justify-content: flex-end;
                    margin-top: 0.5rem;
                }
            }
        `;

        document.head.appendChild(styles);
        document.body.appendChild(banner);

        // Add event listeners
        document.getElementById('pwa-install-btn').addEventListener('click', () => {
            this.installApp();
        });

        document.getElementById('pwa-dismiss-btn').addEventListener('click', () => {
            this.hideInstallPrompt();
            this.trackEvent('pwa_install_dismissed');
        });
    }

    /**
     * Hide install prompt UI
     */
    hideInstallPrompt() {
        const banner = document.getElementById('pwa-install-banner');
        if (banner) {
            banner.style.animation = 'slideDown 0.3s ease forwards';
            setTimeout(() => banner.remove(), 300);
        }
    }

    /**
     * Install the app
     */
    async installApp() {
        if (!this.deferredPrompt) {
            console.warn('[PWA Manager] No install prompt available');
            return false;
        }

        // Show the install prompt
        this.deferredPrompt.prompt();

        // Wait for the user's response
        const { outcome } = await this.deferredPrompt.userChoice;
        console.log(`[PWA Manager] User ${outcome} the install prompt`);

        this.trackEvent('pwa_install_' + outcome);

        // Clear the deferred prompt
        this.deferredPrompt = null;

        return outcome === 'accepted';
    }

    /**
     * Show update notification
     */
    showUpdateNotification() {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: 'Update Available! 🎉',
                text: 'A new version of the app is available. Would you like to update now?',
                icon: 'info',
                showCancelButton: true,
                confirmButtonColor: '#AD4477',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Update Now',
                cancelButtonText: 'Later'
            }).then((result) => {
                if (result.isConfirmed) {
                    this.applyUpdate();
                }
            });
        } else {
            // Fallback to native confirm
            if (confirm('A new version is available. Update now?')) {
                this.applyUpdate();
            }
        }
    }

    /**
     * Apply service worker update
     */
    applyUpdate() {
        console.log('[PWA Manager] Applying update...');

        if (this.registration && this.registration.waiting) {
            // Tell the waiting service worker to skip waiting
            this.registration.waiting.postMessage({ type: 'SKIP_WAITING' });
        }

        // Reload the page to activate new service worker
        window.location.reload();
    }

    /**
     * Request push notification permission
     */
    async requestNotificationPermission() {
        if (!('Notification' in window)) {
            console.warn('[PWA Manager] Notifications not supported');
            return 'denied';
        }

        if (Notification.permission === 'granted') {
            return 'granted';
        }

        const permission = await Notification.requestPermission();
        console.log(`[PWA Manager] Notification permission: ${permission}`);

        if (permission === 'granted') {
            await this.subscribeToPush();
        }

        return permission;
    }

    /**
     * Subscribe to push notifications
     */
    async subscribeToPush() {
        if (!this.registration || !this.options.vapidPublicKey) {
            console.warn('[PWA Manager] Cannot subscribe: missing registration or VAPID key');
            return null;
        }

        try {
            const subscription = await this.registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(this.options.vapidPublicKey)
            });

            console.log('[PWA Manager] Push subscription:', subscription);

            // Send subscription to server
            await this.sendSubscriptionToServer(subscription);

            return subscription;
        } catch (error) {
            console.error('[PWA Manager] Push subscription failed:', error);
            return null;
        }
    }

    /**
     * Send push subscription to backend
     */
    async sendSubscriptionToServer(subscription) {
        try {
            const response = await fetch('/api/push-subscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(subscription)
            });

            if (response.ok) {
                console.log('[PWA Manager] Subscription sent to server');
            }
        } catch (error) {
            console.error('[PWA Manager] Failed to send subscription:', error);
        }
    }

    /**
     * Trigger background sync
     */
    async triggerBackgroundSync(tag = 'sync-forms') {
        if (!this.registration || !('sync' in this.registration)) {
            console.warn('[PWA Manager] Background sync not supported');
            return;
        }

        try {
            await this.registration.sync.register(tag);
            console.log(`[PWA Manager] Background sync registered: ${tag}`);
        } catch (error) {
            console.error('[PWA Manager] Background sync registration failed:', error);
        }
    }

    /**
     * Cache a specific page for offline access
     */
    async cachePage(url) {
        if (navigator.serviceWorker.controller) {
            navigator.serviceWorker.controller.postMessage({
                type: 'CACHE_PAGE',
                url: url
            });
        }
    }

    /**
     * Prefetch multiple URLs
     */
    async prefetchUrls(urls) {
        if (navigator.serviceWorker.controller) {
            navigator.serviceWorker.controller.postMessage({
                type: 'PREFETCH',
                urls: urls
            });
        }
    }

    /**
     * Clear all PWA caches
     */
    async clearCaches() {
        if (navigator.serviceWorker.controller) {
            navigator.serviceWorker.controller.postMessage({
                type: 'CLEAR_CACHE'
            });
            console.log('[PWA Manager] Cache clear requested');
        }
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        // Use SweetAlert if available
        if (typeof Swal !== 'undefined') {
            const Toast = Swal.mixin({
                toast: true,
                position: 'bottom-end',
                showConfirmButton: false,
                timer: 3000,
                timerProgressBar: true,
                didOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer);
                    toast.addEventListener('mouseleave', Swal.resumeTimer);
                }
            });

            Toast.fire({
                icon: type,
                title: message
            });
        } else {
            // Fallback to console
            console.log(`[PWA Toast] ${type}: ${message}`);
        }
    }

    /**
     * Track analytics event
     */
    trackEvent(eventName, eventParams = {}) {
        if (!this.options.enableAnalytics) return;

        // Google Analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, eventParams);
        }

        // Console logging as fallback
        console.log(`[PWA Analytics] ${eventName}`, eventParams);
    }

    /**
     * Utility: Convert VAPID key to Uint8Array
     */
    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }

        return outputArray;
    }

    /**
     * Utility: Get CSRF token from cookies
     */
    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Get current install state
     */
    getState() {
        return {
            isInstalled: this.isInstalled,
            isOnline: this.isOnline,
            updateAvailable: this.updateAvailable,
            canInstall: !!this.deferredPrompt,
            serviceWorkerReady: !!this.registration
        };
    }
}

// ============================================
// Offline Form Handler
// ============================================

class OfflineFormHandler {
    constructor() {
        this.dbName = 'kccc-pwa-sync';
        this.dbVersion = 1;
        this.storeName = 'pending-forms';
    }

    async openDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(this.storeName)) {
                    db.createObjectStore(this.storeName, { keyPath: 'id', autoIncrement: true });
                }
            };
        });
    }

    async saveForm(formData) {
        const db = await this.openDB();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction(this.storeName, 'readwrite');
            const store = transaction.objectStore(this.storeName);
            
            const data = {
                url: formData.action || window.location.href,
                data: Object.fromEntries(new FormData(formData)),
                csrfToken: formData.querySelector('[name=csrfmiddlewaretoken]')?.value,
                timestamp: Date.now()
            };

            const request = store.add(data);
            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                console.log('[Offline Form] Saved for later sync');
                resolve(request.result);
            };
        });
    }

    async getPendingCount() {
        const db = await this.openDB();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction(this.storeName, 'readonly');
            const store = transaction.objectStore(this.storeName);
            const request = store.count();
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);
        });
    }
}

// ============================================
// Auto-initialize PWA Manager
// ============================================

let pwaManager = null;
let offlineFormHandler = null;

document.addEventListener('DOMContentLoaded', () => {
    // Initialize PWA Manager
    pwaManager = new PWAManager({
        enablePushNotifications: true,
        enableBackgroundSync: true,
        enableAnalytics: true,
        promptDelay: 60000, // Show install prompt after 1 minute
        onInstalled: () => {
            console.log('App was installed!');
        },
        onUpdateAvailable: () => {
            console.log('Update available!');
        },
        onOnline: () => {
            // Sync pending data when back online
            if (pwaManager) {
                pwaManager.triggerBackgroundSync('sync-forms');
            }
        }
    });

    // Initialize offline form handler
    offlineFormHandler = new OfflineFormHandler();

    // Add offline form submission support to forms
    document.querySelectorAll('form[data-offline-submit]').forEach(form => {
        form.addEventListener('submit', async (e) => {
            if (!navigator.onLine) {
                e.preventDefault();
                await offlineFormHandler.saveForm(form);
                
                if (pwaManager) {
                    pwaManager.showToast('Form saved! Will submit when online.', 'info');
                    pwaManager.triggerBackgroundSync('sync-forms');
                }
            }
        });
    });

    // Expose globally for debugging
    window.pwaManager = pwaManager;
    window.offlineFormHandler = offlineFormHandler;
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PWAManager, OfflineFormHandler };
}
