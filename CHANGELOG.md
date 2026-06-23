# Change Log

All notable changes to the "Arduino App CLI" extension will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/).

## [0.1.0] - 2026-06-23

### Added

- **My Apps view** — a new **Installed Apps** tree listing the apps installed on
  the board (the non-example apps), each row showing its emoji icon and name with
  its running and default state. Clicking a row reveals the app's folder; the
  context menu offers Run/Stop, Show Console, Set as Default and Delete.
- **"What's New" on update** — after the extension updates to a new version, a
  notification offers to open the changelog, now rendered in VS Code's native
  **Changelog** tab for the extension.

### Changed

- **Renamed to "Arduino App CLI"** — the extension display name, commands, views
  and localized strings now consistently use **Arduino App CLI** (previously
  "Arduino App").

## [0.0.1] - 2026-06-16

Initial release — a lightweight VS Code wrapper over the `arduino-app-cli` daemon
for building, running and monitoring **Arduino UNO Q** apps without leaving the
editor.

### Added

- **App Lab views** — an Activity Bar container with **Examples**, **Brick
  Catalog** and **Models** trees, plus per-app **Project Bricks** and **Project
  Libraries** views in the Explorer.
- **App lifecycle** — create, import, run, stop, restart and delete apps; stream
  build and run progress to a live **Console**; export apps and copy examples to
  edit; set a default app and open an app's exposed port.
- **Bricks** — browse the catalog, add bricks to an app, configure their
  variables, rename and remove them.
- **Models** — list models, import an Edge Impulse project, view details and
  delete.
- **Sketch (MCU) C++ libraries** — search the Arduino catalog and add or remove
  per-app libraries.
- **IntelliSense** — one **Configure IntelliSense** command sets up both halves:
  `.vscode/c_cpp_properties.json` from the sketch's last build (the compilation
  database under `<app>/.cache/sketch/`), resolving the Arduino core, board defines
  and libraries; and `.vscode/typings/arduino/**` Python stubs (with
  `python.analysis.stubPath` pointed at them) so Pylance resolves
  `arduino.app_utils` / `arduino.app_bricks.*` (which live only in the app image).
  Both refresh automatically after each successful run.
- **Serial monitor & plotter** — a monitor terminal over the daemon WebSocket
  with configurable line ending and auto-reconnect, and a data plotter.
- **System utilities** — show version, configuration and properties; reconnect to
  the daemon; update and cleanup; network mode, keyboard layout and board naming.
- **AI assistant integration** — install a Claude/Copilot skill describing the
  CLI.
- **Localization** — UI translated into 14 locales.
- **Get Started walkthrough** — a guided tour shown on first install.
