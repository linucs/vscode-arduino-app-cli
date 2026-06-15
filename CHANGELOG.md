# Change Log

All notable changes to the "Arduino App CLI" extension will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/).

## [0.1.0] - 2026-06-14

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
- **Serial monitor & plotter** — a monitor terminal over the daemon WebSocket
  with configurable line ending and auto-reconnect, and a data plotter.
- **Python environment** — optional managed virtual-environment setup.
- **System utilities** — show version, configuration and properties; reconnect to
  the daemon; update and cleanup; network mode, keyboard layout and board naming.
- **AI assistant integration** — install a Claude/Copilot skill describing the
  CLI.
- **Localization** — UI translated into 14 locales.
- **Get Started walkthrough** — a guided tour shown on first install.
