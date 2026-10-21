/* Starts the shared shell (wtc-shell.js from the front-end standard) for this site.
   Media come from this server's /static folder; there is no Drive adapter here. */
(function () {
  var home = document.body.getAttribute('data-home') === '1';
  WTC.init({
    themeKey: 'abc-theme',
    home: home,
    still: home ? '/static/abc-home-still.jpg' : null,
    media: function (name) { return Promise.resolve('/static/' + name); }
  });
  WTC.reveal('page');
})();

/* Live prices. The pages are rebuilt every 15 minutes, too slow for a price, so
   while a page with prices is open it reads /status/prices.json (written every
   minute by scripts/refresh_prices.py) and updates the figures in place. It
   pauses while the tab is hidden and catches up when the tab is shown again.
   Any failure leaves the built prices on the page. */
(function () {
  var prices = document.querySelectorAll('[data-live-price]');
  if (!prices.length) return;
  var notes = document.querySelectorAll('[data-live-note]');
  var EVERY_MS = 60000;
  var timer = null;

  function money(value, symbol) {
    return symbol + Number(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function apply(data) {
    var all = data && data.prices;
    if (!all) return;
    prices.forEach(function (el) {
      var p = all[el.getAttribute('data-live-price')];
      if (p && p.usd) el.textContent = money(p.usd, '$');
    });
    document.querySelectorAll('[data-live-change]').forEach(function (el) {
      var p = all[el.getAttribute('data-live-change')];
      if (!p || p.zar == null) return;
      var change = Number(p.usd_24h_change || 0);
      el.textContent = money(p.zar, 'R') + ' · ' + (change >= 0 ? '+' : '') + change.toFixed(2) + '% in 24 hours';
    });
    var when = new Date(data.fetched_at);
    if (!isNaN(when)) {
      var time = when.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
      notes.forEach(function (el) {
        el.textContent = 'Live prices from CoinGecko, last updated at ' + time + '. They update every minute while this page is open.';
      });
    }
  }

  function load() {
    fetch('/status/prices.json', { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(apply)
      .catch(function () { /* keep the prices already on the page */ });
  }

  function start() { if (!timer) { load(); timer = setInterval(load, EVERY_MS); } }
  function stop() { clearInterval(timer); timer = null; }

  document.addEventListener('visibilitychange', function () {
    if (document.hidden) stop(); else start();
  });
  if (!document.hidden) start();
})();
