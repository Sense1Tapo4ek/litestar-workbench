(function () {
  function apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('s1t_theme', theme);
  }
  function toggle() {
    var cur = document.documentElement.getAttribute('data-theme') || 'light';
    apply(cur === 'dark' ? 'light' : 'dark');
  }
  window.s1tTheme = { toggle: toggle, apply: apply };
})();
