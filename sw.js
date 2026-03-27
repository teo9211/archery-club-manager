const CACHE_NAME = 'archery-club-v1';
const STATIC_ASSETS = [
    '/',
    '/index.html',
    'https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Exo+2:wght@300;400;600;800&display=swap'
];

// Installazione: metti in cache gli asset statici
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// Attivazione: rimuovi cache vecchie
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// Fetch: serve dalla cache se offline, altrimenti dalla rete
self.addEventListener('fetch', event => {
    // Non intercettare le richieste Firebase
    if (event.request.url.includes('firestore.googleapis.com') ||
        event.request.url.includes('firebase') ||
        event.request.url.includes('gstatic.com/firebasejs')) {
        return;
    }
    event.respondWith(
        caches.match(event.request).then(cached => {
            return cached || fetch(event.request).then(response => {
                // Metti in cache le risorse statiche nuove
                if (response.status === 200 && event.request.method === 'GET') {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                }
                return response;
            }).catch(() => cached); // Se offline e non in cache, usa quello che hai
        })
    );
});

// Notifiche push
self.addEventListener('push', event => {
    if (!event.data) return;
    const data = event.data.json();
    event.waitUntil(
        self.registration.showNotification(data.title || 'Archery Club', {
            body: data.body || '',
            icon: 'icon-192.png',
            badge: 'icon-192.png',
            tag: data.tag || 'archery-notification',
            data: { url: data.url || '/' }
        })
    );
});

// Click su notifica: apri l'app
self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(windowClients => {
            if (windowClients.length > 0) {
                windowClients[0].focus();
            } else {
                clients.openWindow(event.notification.data?.url || '/');
            }
        })
    );
});
