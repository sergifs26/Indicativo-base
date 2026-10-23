# Fotos de ambiente por entorno

Unsplash, «Free to use under the Unsplash License» (uso comercial, sin atribución obligatoria;
la dejamos anotada). Licencia comprobada en la página de cada foto el 04/10/2026. Los `.jpg` no
van a git: se regeneran con `https://images.unsplash.com/<id>?w=<ancho>&q=80&fm=jpg&fit=max`.
En Shopify Files se suben como `entorno-<fichero>` con `scripts/subir_fichero.mjs`.

| Fichero | Uso | Foto (id) | Autor |
|---|---|---|---|
| slide-nautica.jpg (2400) | Pase del carrusel: náutica | [photo-1572817686968-d3b2f1fd643f](https://unsplash.com/photos/1O1uAd9wcLQ) | Nick Fewings (@jannerboy62) |
| slide-nieve.jpg (2400) | Pase: nieve. Banner principal el 23/10/2026 (unas horas, provisional) | [photo-1518784095177-ef1da6313126](https://unsplash.com/photos/EnTU_hr9wPA) | Joris Berthelot (@eexit) |
| slide-camping.jpg (2400) | Pase: camping y familia | [photo-1515444744559-7be63e1600de](https://unsplash.com/photos/yBgC-qVCxMg) | Rahul Bhosale (@rahul_design) |
| slide-caza-pesca.jpg (2400) | Pase: caza y pesca | [photo-1597957729111-848ad99de4b5](https://unsplash.com/photos/CvSrx0TtxZY) | Samantha Deleo (@sammycakesss) |
| tile-nautica.jpg (1200) | Tarjeta «¿A dónde vas?» | [photo-1773834194438-f8325273c655](https://unsplash.com/photos/ZAj3VTvgFVQ) | Fabrizio Saudino (@fabba) |
| tile-nieve.jpg (1200) | Tarjeta | [photo-1643358598688-2e829316d96f](https://unsplash.com/photos/nxc15snaKHw) | Hendrik Morkel (@hendrikmorkel) |
| tile-camping.jpg (1200) | Tarjeta | [photo-1444124818704-4d89a495bbae](https://unsplash.com/photos/i9FLJwYhVQs) | Andreas Rønningen (@andozo) |
| tile-caza-pesca.jpg (1200) | Tarjeta | [photo-1755870344289-00ac1db1b144](https://unsplash.com/photos/SqqIdrvkXS8) | Chris Riggs (@bigrig) |
| tile-para-empezar.jpg (1200) | Tarjeta y bloque «Empiezo» | [photo-1464207687429-7505649dae38](https://unsplash.com/photos/NhU0nUR7920) | Arthur Poulin (@barchpou) |
| bloque-experiencia.jpg (1200) | Bloque «Tengo experiencia» | [photo-1789288046242-5a2a4ae14889](https://unsplash.com/photos/FU-xytmckg0) | Egor Myznik (@vonshnauzer) |
| bloque-nieve.jpg (1400, vertical) | Bloque «Tres entornos»: nieve | [photo-1576866946478-8d0d015bf3e5](https://unsplash.com/photos/UkIinksPvT0) | Greg Rosenke (@greg_rosenke) |
| hero-midland-g15.jpg (1500×1500) | Banner principal de la portada desde el 13/10/2026 (elegida por el usuario) | Galería del producto Midland G15 Pro en nuestra tienda (`Midland-G15-PRO-Walkie-PMR-446_7.jpg`) | Midland / Pihernz — mismo permiso pendiente que el resto de fotos de producto |
| hero-dynascan-p19.jpg (2560×1920) | **Reserva** del banner principal (estuvo puesta el 13/10/2026; el usuario pidió guardarla) | Galería del producto Dynascan P19 en nuestra tienda (foto del fabricante/proveedor: `P19_Dynascan-P19_pareja-walkies-IP54_recort-scaled.jpg`) | Dynascan / Pihernz — mismo permiso pendiente que el resto de fotos de producto |
| hero-walkie-mochila.jpg (2400) | Banner principal del 07/10/2026. **No usar**: el walkie es un Baofeng con el logo visible (el cliente no quiere otras marcas que Icom/Yaesu) | [photo-1789288046242-5a2a4ae14889](https://unsplash.com/photos/FU-xytmckg0) | Egor Myznik (@vonshnauzer) |
| tile-montana.jpg (1200) | Tarjeta montaña (la del banner actual) | photo-1563442162585-fa1426255ea9 | ver PROYECTO_INDICATIVO_BASE.md (29/09) |

Alternativas descartadas por si se quiere cambiar: náutica `photo-1773834194438` como pase (más
acción, sin cielo), nieve `photo-1643358598688`, camping `photo-1444124818704`, pesca
`photo-1755870344289`, grupo `photo-1520880867055-1e30d1cb001c` (Helena Lopes; sale una botella).

## Reserva para el banner principal

La foto de los Dynascan P19 sobre la roca sigue en Ficheros de Shopify como
`entorno-hero-dynascan-p19.jpg`. Para volver a ponerla, en el banner (`templates/index.json`,
sección `hero`, o en el editor de temas): foto `shopify://shop_images/entorno-hero-dynascan-p19.jpg`,
disposición «Foto a la izquierda», encuadre en ordenador «Centro» y en móvil «Centro-izquierda»
(`35% 50%`).

Otras candidatas probadas el 13/10/2026 (capturas en `../pruebas-portada/`), guardadas en
`reserva-portada/` (fuera de git; todas de galerías de producto de nuestra tienda):

| Fichero | Producto | Fichero original en la galería |
|---|---|---|
| dynascan-capucha.jpg | Dynascan P19 (persona con capucha) | `P19_Dynascan-P19_hablando-capucha-scaled.jpg` |
| dynascan-noche.jpg | Dynascan F-15 flotando de noche | `F015_Dynascan-F-15_floating-walkie.jpg` |
| dynascan-roca-agua.jpg | Dynascan F-15 en roca y agua | `f015_Dynascan_F-15_water-scaled.jpg` |
| jopix-flotando.jpg | Jopix Marine 616P naranja flotando | `616PN_JOPIX_MARINE_616P_sea.jpg` |
| jopix-velero.jpg | Jopix Marine 616P en un velero | `Jopix-Marine-616P_boat-barco.jpg` |
| midland-gorra.jpg | Midland XT50 Pro (chica con gorra) | `Midland-XT50-PRO_5.jpg` |
| midland-bosque.jpg | Midland XT30 Pro (excursionista) | `Midland-XT30-PRO_6.jpg` |

## Probada y descartada el 23/10/2026: Yaesu FT-817 en el Monte Rossola (al usuario no le gustó)

`hero-yaesu-ft817-rossola.jpg` (2048×1362; en Ficheros `entorno-hero-yaesu-ft817-rossola.jpg`).
Original: [I/LG-043 M.te Rossola](https://www.flickr.com/photos/46474281@N08/4335103338/) de
**iz1ksw** en Flickr, **CC BY-SA 2.0**, original de 1024×681: un FT-817 sobre una roca en la cumbre,
con el logo YAESU visible. La eligió el usuario porque en la silueta del Monte Cucco «no se ve mucho
el walkie». Escalada ×2 (Lanczos + enfoque suave); por ShareAlike, también CC BY-SA 2.0.
Banner con disposición «Foto a la izquierda» y crédito «Foto: iz1ksw · CC BY-SA 2.0» enlazado a la
foto (**obligatorio**). En móvil y tablet esa disposición pone la foto arriba y el texto debajo.

## Banner principal desde el 23/10/2026: Yaesu FT-817 en el Monte Cucco (silueta)

`hero-yaesu-ft817-cucco.jpg` (2539×1092; en Ficheros de Shopify `entorno-hero-yaesu-ft817.jpg`).
Original: [IMG_0835](https://www.flickr.com/photos/46474281@N08/4263542844/) de **iz1ksw** en Flickr,
«Operating FT-817 from Monte Cucco, beautiful sunset» (08/12/2009), **CC BY-SA 2.0**, original de
1024×683. Es lo que pidió el cliente: un Yaesu en exterior transmitiendo aventura (en silueta, la
marca no se lee). Encontrada con Openverse el 23/10/2026; en Unsplash, Pexels y Commons no había
ninguna libre de Icom/Yaesu al aire libre.

- **Modificada**: cielo ampliado por la izquierda (prolongando el degradado del borde) para que el
  texto del banner no tape la radio, y escalada ×1,6. Por la cláusula ShareAlike, esta versión
  también es CC BY-SA 2.0.
- **Atribución obligatoria**: el banner muestra «Foto: iz1ksw · CC BY-SA 2.0» con enlace a la foto
  (ajustes `credito` y `credito_url` de la sección `hero`). No quitarla mientras se use la foto.
- Regenerar: descargar el original de Flickr, ampliar el lienzo un 55 % por la izquierda con el
  color medio de las 10 primeras columnas de cada fila (+ grano leve y fundido de 40 px) y escalar ×1,6.
- Otra del mismo autor, con el logo YAESU visible: [I/LG-043 M.te Rossola](https://www.flickr.com/photos/46474281@N08/4335103338/)
  (FT-817 sobre una roca de cumbre, CC BY-SA 2.0, 1024×681; se ve blanda a tamaño de banner).

## Galería de aficiones de «Nuestra comunidad» (23/10/2026)

Una foto por afición en `templates/page.comunidad.json` (sección `galeria-aficiones`). Son fotos de
ambiente, no de clientes: la página lo dice («Fotos de ambiente. Pronto, las vuestras»).

| Afición | Fichero en Shopify | Origen |
|---|---|---|
| Radioafición | `entorno-hero-yaesu-ft817-rossola.jpg` | iz1ksw, CC BY-SA 2.0 (ver arriba): **crédito en la tarjeta** |
| Montaña | `entorno-tile-nieve.jpg` | Unsplash, Hendrik Morkel (ver tabla de arriba) |
| Náutica | `entorno-tile-nautica.jpg` | Unsplash, Fabrizio Saudino |
| Outdoor | `entorno-tile-para-empezar.jpg` | Unsplash, Arthur Poulin |
| Aviación | `entorno-comunidad-aviacion.jpg` (`comunidad-aviacion.jpg`, 2400×1600) | [Unsplash photo-1681157403973-ca5dc73d8a5c](https://unsplash.com/photos/3_zFKZGxWzs), Pasqualino Capobianco (@photoloni), licencia Unsplash. **Retocada**: borrado el logo «BOSE» de los cascos (máscara suave), para no mostrar otras marcas |
| Caza y pesca | `entorno-slide-caza-pesca.jpg` | Unsplash, Samantha Deleo |
