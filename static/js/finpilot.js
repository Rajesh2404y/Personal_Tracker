// FinPilot — Main JS

// HTMX CSRF setup
document.addEventListener('htmx:configRequest', (e) => {
  e.detail.headers['X-CSRFToken'] = getCookie('csrftoken');
});

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function initializeFinPilotPage() {
  document.querySelectorAll('.alert:not(.alert-permanent)').forEach(el => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert?.close();
    }, 4000);
  });

  // Animate health score ring
  document.querySelectorAll('.health-score-ring').forEach(el => {
    const score = parseInt(el.dataset.score || 0);
    const circle = el.querySelector('circle:last-child');
    if (circle) {
      const circumference = 2 * Math.PI * 50;
      const dashArray = (score / 100) * circumference;
      setTimeout(() => {
        circle.style.strokeDasharray = `${dashArray} ${circumference}`;
      }, 300);
    }
  });

  // Set today's date as default for date inputs without values
  document.querySelectorAll('input[type="date"]:not([value])').forEach(el => {
    if (!el.value) el.value = new Date().toISOString().split('T')[0];
  });
}

// Auto-dismiss alerts and page-level enhancements
document.addEventListener('DOMContentLoaded', () => {
  initializeFinPilotPage();
  initializeInstantNavigation();
});

// Chart.js global defaults
if (typeof Chart !== 'undefined') {
  Chart.defaults.font.family = 'Inter, sans-serif';
  Chart.defaults.font.size = 12;
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
}

function initializeInstantNavigation() {
  const pageContent = document.getElementById('page-content');
  const pageTitle = document.querySelector('.page-title');

  if (!pageContent || !pageTitle) return;

  let controller = null;

  document.addEventListener('click', (event) => {
    const link = event.target.closest('a');
    if (!isInstantNavigationLink(link, event)) return;

    event.preventDefault();
    navigateTo(link.href);
  });

  window.addEventListener('popstate', () => {
    navigateTo(window.location.href, { push: false });
  });

  async function navigateTo(url, options = {}) {
    const push = options.push !== false;

    if (controller) controller.abort();
    controller = new AbortController();

    document.body.classList.add('page-is-loading');

    try {
      const response = await fetch(url, {
        signal: controller.signal,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-FinPilot-Navigation': 'instant',
        },
      });

      if (!response.ok) {
        window.location.href = url;
        return;
      }

      const html = await response.text();
      const nextDocument = new DOMParser().parseFromString(html, 'text/html');
      const nextContent = nextDocument.getElementById('page-content') || nextDocument.querySelector('.page-content');
      const nextTitle = nextDocument.querySelector('.page-title');

      if (!nextContent || !nextTitle) {
        window.location.href = url;
        return;
      }

      destroyCharts();
      pageContent.replaceChildren(...Array.from(nextContent.childNodes));
      pageTitle.textContent = nextTitle.textContent;
      document.title = nextDocument.title || document.title;
      updateActiveNavigation(new URL(response.url || url, window.location.origin));
      runInlinePageScripts(nextDocument);
      initializeFinPilotPage();
      window.scrollTo({ top: 0, behavior: 'instant' in window ? 'instant' : 'auto' });

      if (push) history.pushState({}, '', response.url || url);
    } catch (error) {
      if (error.name !== 'AbortError') window.location.href = url;
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

  const url = new URL(link.href, window.location.href);
  if (url.origin !== window.location.origin) return false;
  if (url.pathname === window.location.pathname && url.hash) return false;
  if (url.pathname.includes('/logout/')) return false;
  if (url.pathname.startsWith('/admin/')) return false;

  return true;
}

function updateActiveNavigation(url) {
  document.querySelectorAll('.sidebar .nav-item[href]').forEach(item => {
    const itemUrl = new URL(item.href, window.location.origin);
    item.classList.toggle('active', itemUrl.pathname === url.pathname);
  });
}

function runInlinePageScripts(nextDocument) {
  nextDocument.querySelectorAll('script:not([src])').forEach(script => {
    try {
      Function(script.textContent)();
    } catch (error) {
      console.error('FinPilot page script failed:', error);
    }
  });
}

function destroyCharts() {
  if (typeof Chart === 'undefined' || !Chart.instances) return;
  Object.values(Chart.instances).forEach(chart => chart?.destroy?.());
}
