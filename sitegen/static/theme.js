/* Runs in <head> before first paint, so a saved theme never flashes the wrong colours.
   A separate file, not inline, because the content security policy forbids inline scripts. */
(function () {
  try {
    var t = localStorage.getItem('abc-theme');
    if (t === 'dark' || t === 'light') document.documentElement.setAttribute('data-theme', t);
  } catch (e) { /* storage blocked: follow the system setting */ }
})();
