/* ============================================================
   notifications.js — client for the navbar notification badge
   Drop this in /static/js/notifications.js and include it on EVERY
   page that needs the bell badge — mirrors wishlist.js's structure
   and conventions.

   Talks to the JSON endpoint in notifications/views.py
   (UnreadCountView, at notifications:unread_count).

   URL path is read from window.NOTIFICATIONS_ENDPOINTS so this file
   never has to hardcode where the "notifications" app is mounted.
   A sensible default is used if that global isn't set.
   ============================================================ */

const NOTIFICATIONS_ENDPOINT_DEFAULTS = {
  unreadCount: "/notifications/unread-count/",
};

function notificationsEndpoint(name) {
  const overrides = window.NOTIFICATIONS_ENDPOINTS || {};
  return overrides[name] || NOTIFICATIONS_ENDPOINT_DEFAULTS[name];
}

// getCookie() and apiRequest() are already defined globally by cart.js,
// which loads before this file on every page (see layout.html). Reusing
// them here keeps CSRF handling and the 401/403 redirect in one place.

const Notifications = {
  // cache of the last payload from the server: { unread_count }
  _cache: { unread_count: 0 },

  async refresh() {
    try {
      this._cache = await apiRequest(notificationsEndpoint("unreadCount"));
    } catch (e) {
      console.error("Notifications: failed to load unread count", e);
    }
    this.renderBadge();
    return this._cache;
  },

  getCached() {
    return this._cache;
  },

  renderBadge() {
    const badge = document.querySelector("#notification-badge");
    if (!badge) return;
    const count = this._cache.unread_count || 0;
    badge.textContent = count;
    badge.style.display = count > 0 ? "inline-flex" : "none";
  },
};

document.addEventListener("DOMContentLoaded", async () => {
  await Notifications.refresh();
});
