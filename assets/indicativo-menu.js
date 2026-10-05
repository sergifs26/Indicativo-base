/*
 * Desplegables del menú de escritorio: se abren al pasar el cursor, como en The North Face.
 *
 * El tema los monta como <details> dentro de <header-menu> y los abre con clic. Aquí, solo en
 * pantallas grandes con ratón:
 *   - al entrar el cursor en un apartado se abre su desplegable (y se cierra el que hubiera);
 *   - al salir del apartado y de su panel se cierra, con un margen para cruzar el hueco
 *     entre la cabecera y el panel;
 *   - un clic de ratón ya no lo cierra (el teclado sigue igual: Enter/espacio abren y cierran).
 * En móvil y tablet no cambia nada (menú lateral).
 */
(function () {
  var escritorio = window.matchMedia('(hover: hover) and (pointer: fine) and (min-width: 990px)');
  var ESPERA_CIERRE = 200;

  function cerrar(details) {
    var menu = details.closest('header-menu');
    if (menu && typeof menu.close === 'function') {
      menu.close();
    } else {
      details.removeAttribute('open');
    }
  }

  function iniciar() {
    var menus = Array.prototype.slice.call(document.querySelectorAll('.header__inline-menu details'));

    menus.forEach(function (details) {
      var summary = details.querySelector('summary');
      var temporizador = null;
      if (!summary) return;

      function abrir() {
        if (!escritorio.matches) return;
        clearTimeout(temporizador);
        menus.forEach(function (otro) {
          if (otro !== details && otro.hasAttribute('open')) cerrar(otro);
        });
        if (!details.hasAttribute('open')) {
          details.setAttribute('open', '');
          summary.setAttribute('aria-expanded', 'true');
        }
      }

      details.addEventListener('mouseenter', abrir);

      details.addEventListener('mouseleave', function () {
        if (!escritorio.matches) return;
        clearTimeout(temporizador);
        temporizador = setTimeout(function () { cerrar(details); }, ESPERA_CIERRE);
      });

      // Clic de ratón (detail > 0): deja el desplegable abierto en vez de alternarlo.
      // Los clics de teclado llegan con detail 0 y siguen el comportamiento del tema.
      summary.addEventListener('click', function (evento) {
        if (!escritorio.matches || evento.detail === 0) return;
        evento.preventDefault();
        abrir();
        // global.js del tema ya ha alternado aria-expanded en este clic: se corrige.
        summary.setAttribute('aria-expanded', 'true');
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
