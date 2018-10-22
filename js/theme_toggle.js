(function() {
  'use strict';

  var storageKey = 'theme';
  var root = document.documentElement;

  function getStoredTheme() {
    try { return localStorage.getItem(storageKey); } catch (e) { return null; }
  }

  function setStoredTheme(theme) {
    try { localStorage.setItem(storageKey, theme); } catch (e) {}
  }

  function getPreferredTheme() {
    var stored = getStoredTheme();
    if (stored) return stored;
    return 'auto';
  }

  function applyTheme(theme) {
    if (theme === 'auto') {
      var isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.setAttribute('data-bs-theme', isDark ? 'dark' : 'light');
    } else {
      root.setAttribute('data-bs-theme', theme);
    }
    updateActiveMenuItem(theme);
  }

  function updateActiveMenuItem(theme) {
    var items = document.querySelectorAll('[data-bs-theme-value]');
    items.forEach(function(item) {
      var isActive = item.getAttribute('data-bs-theme-value') === theme;
      if (isActive) {
        item.classList.add('active');
        item.setAttribute('aria-current', 'true');
        item.setAttribute('aria-pressed', 'true');
      } else {
        item.classList.remove('active');
        item.removeAttribute('aria-current');
        item.setAttribute('aria-pressed', 'false');
      }
    });
  }

  function initDropdown() {
    var items = document.querySelectorAll('[data-bs-theme-value]');
    if (!items.length) return;

    items.forEach(function(item) {
      item.addEventListener('click', function() {
        var value = item.getAttribute('data-bs-theme-value');
        setStoredTheme(value);
        applyTheme(value);
      });
    });

    // React to system theme changes when in auto
    var media = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)');
    if (media && typeof media.addEventListener === 'function') {
      media.addEventListener('change', function() {
        if (getPreferredTheme() === 'auto') {
          applyTheme('auto');
        }
      });
    } else if (media && typeof media.addListener === 'function') {
      media.addListener(function() {
        if (getPreferredTheme() === 'auto') {
          applyTheme('auto');
        }
      });
    }

    // Sync UI on load
    applyTheme(getPreferredTheme());
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDropdown);
  } else {
    initDropdown();
  }
})();


