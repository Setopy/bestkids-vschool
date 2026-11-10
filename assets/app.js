// Progress tracking (per device). Storage can be unavailable, so every call is guarded.
(function () {
  var KEY = 'bestkids-done';
  function load() {
    try { return JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { return {}; }
  }
  function save(d) {
    try { localStorage.setItem(KEY, JSON.stringify(d)); } catch (e) { /* ignore */ }
  }
  var done = load();

  document.querySelectorAll('[data-lesson]').forEach(function (el) {
    if (done[el.getAttribute('data-lesson')]) el.classList.add('is-done');
  });

  var count = document.getElementById('donecount');
  if (count) count.textContent = Object.keys(done).length;

  var main = document.querySelector('main[data-lesson]');
  var btn = document.querySelector('[data-complete]');
  if (main && btn) {
    var id = main.getAttribute('data-lesson');
    var paint = function () {
      btn.textContent = done[id] ? '✓ Completed (tap to undo)' : 'Mark lesson complete';
      btn.classList.toggle('complete', !!done[id]);
    };
    paint();
    btn.addEventListener('click', function () {
      if (done[id]) delete done[id]; else done[id] = new Date().toISOString().slice(0, 10);
      save(done);
      paint();
    });
  }

  var tog = document.querySelector('[data-toggle-answers]');
  if (tog) {
    tog.addEventListener('click', function () {
      var all = document.querySelectorAll('.practice details, .challenge details');
      var open = tog.getAttribute('data-open') !== '1';
      all.forEach(function (d) { d.open = open; });
      tog.setAttribute('data-open', open ? '1' : '0');
      tog.textContent = open ? 'Hide all answers' : 'Show all answers';
    });
  }

  // Installable app: offline cache + install button.
  if ('serviceWorker' in navigator && window.SW_PATH) {
    navigator.serviceWorker.register(window.SW_PATH).catch(function () { /* offline mode unavailable */ });
  }
  var installBtn = document.querySelector('[data-install]');
  var deferred = null;
  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferred = e;
    if (installBtn) installBtn.hidden = false;
  });
  if (installBtn) {
    installBtn.addEventListener('click', function () {
      if (!deferred) return;
      deferred.prompt();
      deferred = null;
      installBtn.hidden = true;
    });
  }
  window.addEventListener('appinstalled', function () { if (installBtn) installBtn.hidden = true; });
})();
