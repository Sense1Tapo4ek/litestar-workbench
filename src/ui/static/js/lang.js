(function () {
  var STRINGS = {
    ru: {
      theory:          'Теория',
      scenario:        'Сценарий',
      server_logs:     'Логи сервера',
      save:            'Сохранить',
      reset:           'Сбросить',
      clear:           'Очистить',
      btn_start:       'Запустить',
      btn_stop:        'Стоп',
      btn_starting:    'Запуск...',
      no_theory:       'Нет теории для этого урока.',
      no_scenario:     'Нет сценария для этого урока.',
      no_code:         'Файлы кода не найдены.',
      logs_empty:      'Запустите сервер для просмотра логов',
      logs_starting:   'Запуск сервера...',
      lesson_complete: 'Урок пройден',
      overlay_continue:'Продолжить',
      overlay_close:   'Закрыть',
      reset_progress:  'Сбросить прогресс',
      admin_on:        'Admin: Вкл',
      admin_off:       'Admin: Выкл',
      back_home:       '← На главную',
      chapters_label:  'Главы',
      continue_btn:    'Продолжить →',
      all_done:        'Всё пройдено',
      n_completed:     'пройдено',
      lesson_done:     'Пройден',
      lesson_open:     'Открыть →',
      lesson_continue: 'Продолжить →',
      done_btn:        'Готово',
      server_is_running: 'запущен',
      another_server:  'Другой сервер запущен',
      ws_connect:      'Подключить',
      ws_not_connected:'Не подключено',
      ws_send:         'Отправить',
    },
    en: {
      theory:          'Theory',
      scenario:        'Scenario',
      server_logs:     'Server Logs',
      save:            'Save',
      reset:           'Reset',
      clear:           'Clear',
      btn_start:       'Start',
      btn_stop:        'Stop',
      btn_starting:    'Starting...',
      no_theory:       'No theory for this lesson.',
      no_scenario:     'No scenario for this lesson.',
      no_code:         'No code files found.',
      logs_empty:      'Start the server to see logs',
      logs_starting:   'Starting server...',
      lesson_complete: 'Lesson Complete',
      overlay_continue:'Continue',
      overlay_close:   'Close',
      reset_progress:  'Reset Progress',
      admin_on:        'Admin: On',
      admin_off:       'Admin: Off',
      back_home:       '← Home',
      chapters_label:  'Chapters',
      continue_btn:    'Continue →',
      all_done:        'All done',
      n_completed:     'completed',
      lesson_done:     'Done',
      lesson_open:     'Open →',
      lesson_continue: 'Continue →',
      done_btn:        'Done',
      server_is_running: 'is running',
      another_server:  'Another server is running',
      ws_connect:      'Connect',
      ws_not_connected:'Not connected',
      ws_send:         'Send',
    },
  };

  function applyTo(root) {
    var lang = document.documentElement.getAttribute('data-lang') || 'ru';
    var dict = STRINGS[lang] || STRINGS.ru;
    var els = (root || document).querySelectorAll('[data-i18n]');
    for (var i = 0; i < els.length; i++) {
      var key = els[i].getAttribute('data-i18n');
      if (dict[key] !== undefined) els[i].textContent = dict[key];
    }
  }

  function apply(lang) {
    document.documentElement.setAttribute('data-lang', lang);
    localStorage.setItem('s1t_lang', lang);
    applyTo(document);
    document.dispatchEvent(new CustomEvent('s1t:langchange', { detail: { lang: lang } }));
  }

  function toggle() {
    var cur = document.documentElement.getAttribute('data-lang') || 'ru';
    apply(cur === 'en' ? 'ru' : 'en');
  }

  function t(key) {
    var lang = document.documentElement.getAttribute('data-lang') || 'ru';
    var dict = STRINGS[lang] || STRINGS.ru;
    return dict[key] !== undefined ? dict[key] : key;
  }

  // Re-apply after HTMX swaps (server_controls reload etc.)
  document.addEventListener('htmx:afterSettle', function (e) {
    if (e.detail && e.detail.target) applyTo(e.detail.target);
  });

  document.addEventListener('DOMContentLoaded', function () {
    var lang = localStorage.getItem('s1t_lang') || 'ru';
    apply(lang);
  });

  window.s1tLang = { toggle: toggle, apply: apply, t: t };
})();
