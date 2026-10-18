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
