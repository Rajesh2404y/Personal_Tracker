// FinPilot — Main JS

// HTMX CSRF setup
document.addEventListener('htmx:configRequest', (e) => {
  e.detail.headers['X-CSRFToken'] = getCookie('csrftoken');
}, { passive: true });

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[1]) : null;
}

function initializeFinPilotPage() {
  document.querySelectorAll('.alert:not(.alert-permanent)').forEach(el => {
    setTimeout(() => bootstrap.Alert.getOrCreateInstance(el)?.close(), 4000);
  });
  document.querySelectorAll('input[type="date"]:not([value])').forEach(el => {
    if (!el.value) el.value = new Date().toISOString().split('T')[0];
  });
}

function applyChartDefaults() {
  if (typeof Chart === 'undefined') return;
  Chart.defaults.font.family = 'Inter, sans-serif';
  Chart.defaults.font.size = 12;
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.animation.duration = 600;
}

document.addEventListener('DOMContentLoaded', () => {
  applyChartDefaults();
  initializeFinPilotPage();
  initializeInstantNavigation();
}, { once: true });

function initializeInstantNavigation() {
  const pageContent = document.getElementById('page-content');
  const pageTitle = document.querySelector('.page-title');
  if (!pageContent || !pageTitle) return;

  let controller = null;

  document.addEventListener('click', (event) => {
    const link = event.target.closest('a');
    if (isInstantNavigationLink(link, event)) {
      event.preventDefault();
      navigateTo(link.href);
    }
  }, { passive: false });

  window.addEventListener('popstate', () => {
    navigateTo(window.location.href, { push: false });
  }, { passive: true });

  async function navigateTo(url, options = {}) {
    // Strict same-origin check — prevents SSRF (CWE-918)
    const parsed = new URL(url, window.location.origin);
    if (parsed.origin !== window.location.origin) {
      window.location.href = url;
      return;
    }

    const push = options.push !== false;
    if (controller) controller.abort();
    controller = new AbortController();
    document.body.classList.add('page-is-loading');

    try {
      const response = await fetch(parsed.href, {
        signal: controller.signal,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-FinPilot-Navigation': 'instant',
        },
      });

      if (!response.ok) { window.location.href = url; return; }

      const html = await response.text();
      const next = new DOMParser().parseFromString(html, 'text/html');
      const nextContent = next.getElementById('page-content');
      const nextTitle = next.querySelector('.page-title');

      if (!nextContent || !nextTitle) { window.location.href = url; return; }

      destroyCharts();
      pageContent.replaceChildren(...Array.from(nextContent.childNodes));
      pageTitle.textContent = nextTitle.textContent;
      document.title = next.title || document.title;
      updateActiveNavigation(new URL(response.url || url, window.location.origin));
      // Safe script re-execution — only runs scripts already in the server response
      runPageScripts(pageContent);
      applyChartDefaults();
      initializeFinPilotPage();
      window.scrollTo({ top: 0, behavior: 'instant' });
      if (push) history.pushState({}, '', response.url || url);
    } catch (err) {
      if (err.name !== 'AbortError') window.location.href = url;
    } finally {
      document.body.classList.remove('page-is-loading');
    }
  }
}

function isInstantNavigationLink(link, event) {
  if (!link) return false;
  if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return false;
  if (link.target || link.hasAttribute('download')) return false;
  if (link.hasAttribute('hx-get') || link.hasAttribute('hx-post') || link.hasAttribute('data-no-instant')) return false;
  try {
    const url = new URL(link.href, window.location.href);
    if (url.origin !== window.location.origin) return false;
    if (url.pathname === window.location.pathname && url.hash) return false;
    if (url.pathname.includes('/logout/') || url.pathname.startsWith('/admin/')) return false;
  } catch (_) {
    return false;
  }
  return true;
}

function updateActiveNavigation(url) {
  document.querySelectorAll('.sidebar .nav-item[href]').forEach(item => {
    try {
      item.classList.toggle('active', new URL(item.href, window.location.origin).pathname === url.pathname);
    } catch (_) {}
  });
}

/**
 * Re-execute inline <script> tags injected via innerHTML/replaceChildren.
 * Uses createElement('script') — safer than Function() or eval (fixes CWE-94).
 * Only scripts already present in the trusted server HTML are executed.
 */
function runPageScripts(container) {
  container.querySelectorAll('script:not([src])').forEach(oldScript => {
    const newScript = document.createElement('script');
    newScript.textContent = oldScript.textContent;
    oldScript.replaceWith(newScript);
  });
}

function destroyCharts() {
  if (typeof Chart === 'undefined') return;
  Object.values(Chart.instances || {}).forEach(chart => chart?.destroy?.());
}
