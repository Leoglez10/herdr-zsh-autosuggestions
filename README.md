# Herdr zsh autosuggestions

[![Made with gentle-ai](https://img.shields.io/badge/made%20with-gentle--ai-8A2BE2)](https://github.com/Gentleman-Programming/gentle-ai)

## La historia: quería autocompletado en Herdr sin tocar Herdr

Uso Herdr todos los días y me cansé de escribir los mismos comandos. Quería lo que
tenía en otras terminales: escribir tres letras, ver el resto del comando en gris, y
aceptarlo con la flecha derecha.

La opción fácil era modificar la app. La opción que elegí fue no tocar la app.

Así que hice este repositorio: una integración de zsh que se instala **encima** de tu
configuración de shell y se activa solo cuando Herdr arranca una terminal. Herdr
sigue siendo Herdr, sin parches, sin forks y sin actualizaciones rotas. Si algún día
lo quieres fuera, se quita con un comando y tu `.zshrc` queda como estaba.

## Qué hace

Mientras escribes, te muestra una sugerencia tenue al final de la línea:

- **Primero tu historial.** Si ya escribiste ese comando alguna vez, aparece el
  resto de la línea.
- **Si no hay historial, una ruta local.** Escribes `cd app-ex` y te sugiere
  `cd app-example/` si ese directorio existe en tu carpeta actual.
- **Aceptar rellena, no ejecuta.** La flecha derecha completa la línea; Enter es
  el que ejecuta. Tú siempre decides.

Todo es local: tu historial de shell y tu sistema de archivos. Nada de IA, nada de
red, nada se sube a ninguna parte.

## Qué no hace (esto también importa)

Prefiero decirlo antes de que lo descubras:

- **No modifica la aplicación Herdr.** Es una integración de zsh, no un parche.
- **No ejecuta nada por ti.** Aceptar una sugerencia solo escribe la línea.
- **No entiende todo el shell.** El respaldo de rutas acepta un comando simple y una
  ruta literal. Opciones, varios argumentos, `~`, variables, `$(...)`, operadores
  (`|`, `>`, `&&`) y backslashes dentro de comillas dobles no producen sugerencia de
  ruta: mejor no adivinar.
- **No reemplaza tus plugins.** Si ya tienes `zsh-autosuggestions` cargado, lo deja
  intacto.
- **No trae IA.** Ni ahora ni como plan futuro escondido.

## Instalación rápida

Probado en macOS con zsh 5.9, Python 3 y Git. Pega esto en una terminal zsh: instala
en `~/.local/share/herdr-zsh-autosuggestions` y agrega un bloque marcado a tu
`.zshrc` (respetando `ZDOTDIR`):

```sh
git clone https://github.com/Leoglez10/herdr-zsh-autosuggestions.git ~/.local/share/herdr-zsh-autosuggestions \
  && cd ~/.local/share/herdr-zsh-autosuggestions \
  && python3 bin/fetch-plugin \
  && python3 bin/manage install --rc "${ZDOTDIR:-$HOME}/.zshrc"
```

Después abre una terminal nueva de Herdr. Para quitarlo:

```sh
python3 ~/.local/share/herdr-zsh-autosuggestions/bin/manage uninstall --rc "${ZDOTDIR:-$HOME}/.zshrc"
```

## Instalación paso a paso (si prefieres entender lo que pasa)

Los mismos pasos, con calma, desde una carpeta donde quieras conservar el proyecto:

```sh
git clone https://github.com/Leoglez10/herdr-zsh-autosuggestions.git
cd herdr-zsh-autosuggestions
python3 bin/fetch-plugin
# Opcional: probar la demo aislada antes de instalar
/bin/bash bin/trial
python3 bin/manage install --rc "$HOME/.zshrc"
```

Qué hace cada uno:

1. **`git clone`** baja el repositorio. Vive donde tú decidas.
2. **`python3 bin/fetch-plugin`** descarga el plugin público que hace el trabajo de
   sugerencias y verifica sus hashes SHA-256 contra `dependency.json`. **No** toca
   ningún archivo de arranque.
3. **`bin/trial`** (opcional) abre una zsh aislada con HOME y historial temporales,
   para que veas cómo se siente sin tocar tu configuración real.
4. **`python3 bin/manage install`** agrega un bloque marcado al archivo de arranque
   que tú elijas explícitamente. Respeta el resto del archivo byte por byte.

Dos advertencias honestas:

- **El archivo de arranque se modifica de verdad.** Elige el correcto. Si tu zsh usa
  `ZDOTDIR`, es el `.zshrc` de esa carpeta, no `$HOME/.zshrc`. El instalador nunca
  elige por ti.
- **El bloque usa una ruta absoluta.** No muevas ni borres la carpeta mientras esté
  instalado. Desinstala primero, mueve, y vuelve a instalar.

Abre una terminal nueva de Herdr después de instalar o actualizar. Detalles
completos en [instalación](docs/install.md).

### O pídeselo a tu agente

Copia esto en Claude Code, Codex, Cursor o un agente similar con acceso a shell:

```text
Install https://github.com/Leoglez10/herdr-zsh-autosuggestions for me.
1. Clone it into ~/.local/share/herdr-zsh-autosuggestions (if it already exists, run `git pull` there instead).
2. Run `python3 bin/fetch-plugin` from that folder; stop and report if checksum verification fails.
3. Find my real zsh startup file: "${ZDOTDIR:-$HOME}/.zshrc". Show me the path before changing it.
4. Run `python3 bin/manage install --rc <that path>`, then `python3 bin/manage status --rc <that path>`.
5. Do not edit the startup file by hand, do not move the folder afterwards, and tell me to open a new Herdr terminal.
```

## Cómo se usa

Escribe el principio de un comando y mira la continuación tenue.

```text
❯ cd app-ex                    ← tú escribes
❯ cd app-example/              ← en gris, la sugerencia
```

Lo que sí y lo que no:

| Caso | Resultado |
| --- | --- |
| Comando que ya está en tu historial | Se sugiere el resto de la línea |
| `cd app-ex` con el directorio `app-example/` | Se sugiere `cd app-example/` |
| `ls "my fi` con el archivo `my file` | Se sugiere cerrando la comilla |
| Rutas sin comillas o con espacios escapados | Soportado |
| `~`, variables, `$(...)`, operadores, varios argumentos | Sin sugerencia de ruta |
| Varias coincidencias posibles | Se ofrece la primera en orden alfabético |
| Sin sufijo que agregar | No se muestra nada |

Los ejemplos son ilustrativos: los archivos tienen que existir de verdad.

Teclas (dependen de tus bindings de zsh, estos son los habituales):

- **Flecha derecha** al final de la línea: acepta la sugerencia.
- **Enter**: ejecuta la línea completa. Nada se ejecuta solo.
- **Tab**: mantiene su comportamiento normal.

Si quieres probar sin compromiso, la [demo aislada](docs/trial.md) explica cómo.

## Estado y desinstalación

Usa siempre el mismo archivo de arranque que elegiste al instalar:

```sh
python3 bin/manage status --rc "$HOME/.zshrc"
python3 bin/manage uninstall --rc "$HOME/.zshrc"
```

- `status` te dice si el bloque está ahí. No imprime el contenido de tu configuración.
- `uninstall` quita **solo** el bloque que este proyecto agregó, y conserva lo que
  hayas editado después.
- Instalar y desinstalar son idempotentes: correrlos dos veces no rompe nada.
- Desinstalar no descarga nada de un shell ya abierto: abre uno nuevo.
- La integración solo se activa en shells interactivos donde existan **ambas**
  variables, `HC_TERMINAL_ID` y `HC_TERMINAL_SOCKET`. No depende de `TERM_PROGRAM`.

## Si algo no funciona

- **No aparece ninguna sugerencia.** Revisa que exista coincidencia en tu historial o
  una ruta que el analizador acepte (comando simple + ruta literal).
- **No se activa.** Corre `status` sobre el archivo correcto, verifica las dos marcas
  de Herdr y abre una terminal nueva.
- **Se ve demasiado tenue.** El estilo es `fg=8`; depende de la paleta y el contraste
  de tu terminal.
- **Moví la carpeta y dejó de funcionar.** Vuelve a dejarla en su ruta original,
  desinstala desde ahí, mueve e instala de nuevo.
- **Falla la descarga.** Revisa la conexión y repite `python3 bin/fetch-plugin`;
  verifica los dos hashes SHA-256 antes de escribir nada.

## Datos y privacidad

- El bootstrap descarga, por HTTPS, solo el plugin público fijado y su licencia,
  dentro de `.cache/`.
- **No sube** tu entrada de terminal ni tu historial de shell.
- Las sugerencias normales usan tu historial local y rutas de tu sistema de archivos.
- Los datos de la demo son temporales, en `.state/`.
- Los cambios de arranque se limitan al archivo que elegiste explícitamente.

Antes de editar ese archivo a mano, lee [instalación](docs/install.md).

## Desarrollo

Después del bootstrap, corre las pruebas:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
```

Mapa rápido del repositorio:

| Ruta | Qué hay |
| --- | --- |
| `integration.zsh` | Cargador de Herdr y respaldo de rutas locales |
| `bin/fetch-plugin` | Descarga y verifica la dependencia fijada |
| `bin/manage` | Instala, consulta y quita el bloque del archivo de arranque |
| `bin/trial` | Demo aislada, sin tocar tu configuración |
| `sandbox.zsh` | Configuración de esa demo |
| `tests/` | Pruebas de instalación, verificación y comportamiento |
| `docs/` | Instalación y demo en detalle |

Contribuciones bienvenidas: abre un issue o un pull request en el
[repositorio del proyecto](https://github.com/Leoglez10/herdr-zsh-autosuggestions)
con un ejemplo reproducible y su prueba. Para soporte, usa el issue tracker, sin
publicar tu historial ni tu configuración privada.

## Créditos y licencia

Este proyecto no inventó el autocompletado: se apoya en
[zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions) de
zsh-users, distribuido bajo su propia licencia MIT (ver
`licenses/zsh-autosuggestions.LICENSE` y [NOTICE](NOTICE)). La versión fijada y sus
hashes están en `dependency.json`.

Lo que agrega este repositorio es la integración con Herdr, el respaldo de rutas
locales y el gestor del bloque de arranque.

El código del proyecto está bajo la [licencia MIT](LICENSE).
