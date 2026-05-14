(function () {
  "use strict";

  var STORAGE_KEY = "__nav_state";
  var TOGGLE_SELECTOR = ".md-sidebar--primary input.md-nav__toggle[id^='__nav_']";

  function getNavToggles() {
    return Array.prototype.slice.call(document.querySelectorAll(TOGGLE_SELECTOR));
  }

  function loadState() {
    if (typeof __md_get === "function") {
      return __md_get(STORAGE_KEY) || {};
    }

    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    } catch (_error) {
      return {};
    }
  }

  function saveState(state) {
    if (typeof __md_set === "function") {
      __md_set(STORAGE_KEY, state);
      return;
    }

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (_error) {
      // Ignore storage failures and keep default Material behavior.
    }
  }

  function persistNavState() {
    var state = {};

    getNavToggles().forEach(function (toggle) {
      state[toggle.id] = toggle.checked;
    });

    saveState(state);
  }

  function restoreNavState() {
    var state = loadState();

    getNavToggles().forEach(function (toggle) {
      if (Object.prototype.hasOwnProperty.call(state, toggle.id)) {
        toggle.checked = !!state[toggle.id];
      }
    });
  }

  function bindNavStateHandlers() {
    getNavToggles().forEach(function (toggle) {
      if (toggle.dataset.navStateBound === "true") {
        return;
      }

      toggle.dataset.navStateBound = "true";
      toggle.addEventListener("change", persistNavState);
    });
  }

  function setupNavStatePersistence() {
    restoreNavState();
    bindNavStateHandlers();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupNavStatePersistence);
  } else {
    setupNavStatePersistence();
  }

  if (typeof document$ !== "undefined" && typeof document$.subscribe === "function") {
    document$.subscribe(setupNavStatePersistence);
  }
})();
