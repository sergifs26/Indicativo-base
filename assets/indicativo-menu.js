/*
 * Desplegables del menú de escritorio.
 *
 * 05/10/2026: se abren al pasar el cursor, como en The North Face.
 * 23/10/2026: comportamiento del «Directional Menu» de 21st.dev (hyperiux), adaptado sin React ni
 * GSAP: un solo panel blanco flotante para todos los apartados; al pasar de un apartado a otro, el
 * contenido nuevo entra deslizándose desde el lado hacia el que va el cursor, el anterior sale por
 * el contrario y el panel cambia de alto. Animaciones con la Web Animations API.
 *
 * El tema monta cada desplegable como <details> dentro de <header-menu> y lo abre con clic. Aquí,
 * solo en pantallas grandes con ratón (clase html.ib-dm, que activa los estilos «Panel
 * direccional» de assets/indicativo-base.css):
 *   - al entrar el cursor en un apartado se abre su desplegable;
 *   - al salir del apartado y de su panel se cierra, con un margen para cruzar el hueco;
 *   - un clic de ratón no lo cierra (el teclado sigue como en el tema: Enter/espacio, Esc).
 * El panel blanco (.ib-dm__fondo) es un elemento aparte: el contenido de cada <details> va encima,
 * transparente. Para la salida del contenido anterior se anima una copia inerte (.ib-dm__fantasma).
 * En móvil y tablet no cambia nada (menú lateral).
 */
(function () {
  var escritorio = window.matchMedia('(hover: hover) and (pointer: fine) and (min-width: 990px)');
  var sinMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)');
  var ESPERA_CIERRE = 200;
  var DURACION = 350; // ms, deslizamiento y cambio de alto (0,35 s en el original)
  var DISTANCIA = 100; // px que se desliza el contenido al cambiar de apartado
  var CURVA = 'cubic-bezier(0.45, 0, 0.55, 1)'; // power2.inOut de GSAP
  var RETRASO_FUNDIDO = 60;
  var DURACION_FUNDIDO = 180;
  var FUNDIDO_REDUCIDO = 160;

  var menus = [];
  var fondo = null;
  var abierto = null;
  var cerrando = false;
  var temporizador = null;
  var enCurso = [];
  var fantasmas = [];

  function contenido(details) {
    return details.querySelector('.mega-menu__content');
  }

  function abrirDetails(details) {
    if (!details.hasAttribute('open')) details.setAttribute('open', '');
    var summary = details.querySelector('summary');
    if (summary) summary.setAttribute('aria-expanded', 'true');
  }

  function cerrarDetails(details) {
    var menu = details.closest('header-menu');
    if (menu && typeof menu.close === 'function') {
      menu.close();
    } else {
      details.removeAttribute('open');
      var summary = details.querySelector('summary');
      if (summary) summary.setAttribute('aria-expanded', 'false');
    }
  }

  function detener() {
    enCurso.forEach(function (animacion) { animacion.cancel(); });
    enCurso = [];
    fantasmas.forEach(function (fantasma) { fantasma.remove(); });
    fantasmas = [];
  }

  function animar(elemento, fotogramas, opciones) {
    var animacion = elemento.animate(fotogramas, Object.assign({ duration: DURACION, easing: CURVA }, opciones));
    enCurso.push(animacion);
    return animacion;
  }

  // Recorta por abajo: lo que sobresale del panel mientras este cambia de alto no se ve
  function recorte(px) {
    return 'inset(0px 0px ' + Math.max(0, Math.round(px)) + 'px 0px)';
  }

  function altoFondo() {
    return fondo && fondo.isConnected ? fondo.getBoundingClientRect().height : 0;
  }

  // El fondo comparte bloque contenedor con los contenidos, así el CSS les da la misma caja
  function prepararFondo(referencia) {
    if (!fondo) {
      fondo = document.createElement('div');
      fondo.className = 'ib-dm__fondo';
      fondo.setAttribute('aria-hidden', 'true');
      fondo.addEventListener('mouseenter', function () { clearTimeout(temporizador); });
      fondo.addEventListener('mouseleave', programarCierre);
    }
    var padre = referencia.offsetParent;
    if (padre && fondo.parentNode !== padre) padre.appendChild(fondo);
  }

  // Copia inerte del contenido que se va, para animar su salida mientras entra el nuevo
  function copiar(origen) {
    var copia = origen.cloneNode(true);
    copia.classList.add('ib-dm__fantasma');
    copia.setAttribute('aria-hidden', 'true');
    copia.setAttribute('inert', '');
    copia.removeAttribute('id');
    copia.querySelectorAll('[id]').forEach(function (nodo) { nodo.removeAttribute('id'); });
    return copia;
  }

  function mostrar(details) {
    clearTimeout(temporizador);
    if (abierto === details && !cerrando) return;

    var anterior = cerrando ? null : abierto;
    var altoInicial = altoFondo();
    var copia = null;
    var altoCopia = 0;
    if (anterior && anterior !== details && !sinMovimiento.matches) {
      copia = copiar(contenido(anterior));
      altoCopia = contenido(anterior).offsetHeight;
    }

    detener();
    cerrando = false;
    menus.forEach(function (otro) {
      if (otro !== details && otro.hasAttribute('open')) cerrarDetails(otro);
    });
    abierto = details;
    abrirDetails(details);

    var nuevo = contenido(details);
    prepararFondo(nuevo);
    var alto = nuevo.offsetHeight;
    fondo.style.height = alto + 'px';
    fondo.style.opacity = '1';

    if (sinMovimiento.matches) {
      if (!anterior) {
        animar(fondo, [{ opacity: 0 }, { opacity: 1 }], { duration: FUNDIDO_REDUCIDO, easing: 'ease-out' });
        animar(nuevo, [{ opacity: 0 }, { opacity: 1 }], { duration: FUNDIDO_REDUCIDO, easing: 'ease-out' });
      }
      return;
    }

    animar(fondo, [{ height: altoInicial + 'px', opacity: 1 }, { height: alto + 'px', opacity: 1 }]);

    if (!anterior) {
      // Primera apertura (o vuelta mientras se cerraba): el panel crece y el contenido aparece
      animar(nuevo, [{ clipPath: recorte(alto - altoInicial) }, { clipPath: recorte(0) }]);
      animar(nuevo, [{ opacity: 0 }, { opacity: 1 }], {
        delay: RETRASO_FUNDIDO, duration: DURACION_FUNDIDO, easing: 'ease-out', fill: 'backwards',
      });
      return;
    }

    // Cambio de apartado: hacia la derecha entra por la derecha; hacia la izquierda, por la izquierda
    var sentido = menus.indexOf(details) > menus.indexOf(anterior) ? 1 : -1;
    animar(nuevo, [
      { transform: 'translateX(' + sentido * DISTANCIA + 'px)', opacity: 0, clipPath: recorte(alto - altoInicial) },
      { transform: 'translateX(0)', opacity: 1, clipPath: recorte(0) },
    ]);

    if (copia) {
      fondo.parentNode.appendChild(copia);
      fantasmas.push(copia);
      animar(copia, [
        { transform: 'translateX(0)', opacity: 1, clipPath: recorte(Math.max(0, altoCopia - altoInicial)) },
        { transform: 'translateX(' + -sentido * DISTANCIA + 'px)', opacity: 0, clipPath: recorte(altoCopia - alto) },
      ], { fill: 'forwards' }).onfinish = function () {
        copia.remove();
        fantasmas = fantasmas.filter(function (f) { return f !== copia; });
      };
    }
  }

  function ocultar() {
    if (!abierto || cerrando) return;
    var details = abierto;
    var actual = contenido(details);
    var alto = altoFondo();

    detener();
    cerrando = true;
    fondo.style.height = '0px';
    fondo.style.opacity = '0';

    var final;
    if (sinMovimiento.matches) {
      final = animar(fondo, [{ height: alto + 'px', opacity: 1 }, { height: alto + 'px', opacity: 0 }], {
        duration: FUNDIDO_REDUCIDO, easing: 'ease-out',
      });
      animar(actual, [{ opacity: 1 }, { opacity: 0 }], { duration: FUNDIDO_REDUCIDO, easing: 'ease-out', fill: 'forwards' });
    } else {
      final = animar(fondo, [{ height: alto + 'px', opacity: 1 }, { height: '0px', opacity: 0 }]);
      animar(actual, [{ clipPath: recorte(0), opacity: 1 }, { clipPath: recorte(alto), opacity: 0 }], { fill: 'forwards' });
    }

    final.onfinish = function () {
      if (!cerrando || abierto !== details) return;
      cerrando = false;
      abierto = null;
      cerrarDetails(details);
      detener();
    };
  }

  function programarCierre() {
    if (!escritorio.matches) return;
    clearTimeout(temporizador);
    temporizador = setTimeout(ocultar, ESPERA_CIERRE);
  }

  // Al salir del escritorio (ventana estrecha, tableta) se vuelve al comportamiento del tema
  function alCambiarPantalla() {
    document.documentElement.classList.toggle('ib-dm', escritorio.matches);
    if (escritorio.matches) return;
    clearTimeout(temporizador);
    detener();
    cerrando = false;
    abierto = null;
    if (fondo) {
      fondo.style.height = '0px';
      fondo.style.opacity = '0';
    }
  }

  function iniciar() {
    menus = Array.prototype.slice.call(document.querySelectorAll('.header__inline-menu details'));
    if (!menus.length) return;
    alCambiarPantalla();
    if (escritorio.addEventListener) escritorio.addEventListener('change', alCambiarPantalla);

    menus.forEach(function (details) {
      var summary = details.querySelector('summary');
      if (!summary || !contenido(details)) return;

      details.addEventListener('mouseenter', function () {
        if (escritorio.matches) mostrar(details);
      });
      details.addEventListener('mouseleave', programarCierre);

      // Clic de ratón (detail > 0): deja el desplegable abierto en vez de alternarlo.
      // Los clics de teclado llegan con detail 0 y siguen el comportamiento del tema.
      summary.addEventListener('click', function (evento) {
        if (!escritorio.matches || evento.detail === 0) return;
        evento.preventDefault();
        mostrar(details);
        // global.js del tema ya ha alternado aria-expanded en este clic: se corrige.
        summary.setAttribute('aria-expanded', 'true');
      });

      // Aperturas y cierres del tema (teclado, Esc, foco fuera): el panel los acompaña
      details.addEventListener('toggle', function () {
        if (!escritorio.matches) return;
        if (details.open) {
          if (abierto !== details) mostrar(details);
        } else if (abierto === details && !cerrando) {
          detener();
          abierto = null;
          if (fondo) {
            fondo.style.height = '0px';
            fondo.style.opacity = '0';
          }
        }
      });
    });

    // Apartados sin desplegable: al pasar por ellos se cierra el panel, como en el original
    document.querySelectorAll('.header__inline-menu .list-menu--inline > li > a').forEach(function (enlace) {
      enlace.addEventListener('mouseenter', function () {
        if (escritorio.matches) ocultar();
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
