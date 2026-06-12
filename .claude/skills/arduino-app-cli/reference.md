# Arduino App Lab CLI — reference

`arduino-app-cli` manages **Arduino Apps** on the Arduino UNO Q, a dual-brain
board: a Linux-capable CPU (runs Python apps in Docker + this CLI) and an Arduino
MCU (runs C++ sketches). It runs **on the board** (as UID 1000, needs Docker);
developers typically reach it through VS Code Remote-SSH or the on-board daemon.

## Global flags

- `--format text|json|jsonmini` (default `text`) — use `json` for scripting.
- `--log-level debug|info|warn|error` (default `error`).

## CLI command tree

```
arduino-app-cli
├── app
│   ├── new <name>            --icon/-i, --description/-d, --from-app, --bricks/-b, --no-sketch
│   ├── start <app>           --verbose/-v   (compiles+flashes the sketch AND runs Python)
│   ├── stop <app>
│   ├── restart <app>         --verbose/-v
│   ├── destroy <app>
│   ├── list                  --show-broken-apps
│   ├── logs <app>            --tail <n>, --follow, --all
│   ├── clean-cache <app-id>  --force
│   ├── export <app> [out]    --include-data, --overwrite
│   └── import <zip>          (supports stdin '-')
├── brick
│   ├── list
│   └── details <brick-id>
├── model
│   ├── list                  --exclude-builtin
│   └── delete <model-id>     --force
├── system
│   ├── init                  --only-docker-images, --only-arduino-platform
│   ├── update                --only-arduino, --yes
│   ├── cleanup
│   ├── network-mode <enable|disable|status>
│   ├── keyboard [layout]
│   └── set-name <name>
├── config get
├── properties
│   ├── get default
│   └── set default <app|none>
├── monitor                   (serial monitor to the MCU)
├── daemon                    --port <n>   (default 8080; on-board systemd uses 8800)
├── version                   --port <n>
└── completion <bash|zsh|fish|powershell>
```

## Daemon REST API (base `http://127.0.0.1:8800/v1`)

SSE endpoints emit `event: <type>\ndata: <json>\n\n` frames (types: `progress
{name,progress}`, `message {message}`, `app {AppInfo}`, `error {code,message}`).

- System: `GET /version`, `GET /config`, `GET /system/resources`,
  `GET /system/update/check`, `GET /system/update/events` (SSE),
  `PUT /system/update/apply`, properties `GET /properties`,
  `GET|PUT|DELETE /properties/{key}`.
- Apps: `GET /apps?filter=apps|examples`, `POST /apps`, `GET /apps/events` (SSE),
  `GET|PATCH|DELETE /apps/{id}`, `POST /apps/{id}/start` (SSE),
  `POST /apps/{id}/stop` (SSE), `GET /apps/{id}/logs` (SSE,
  `?filter=app,services&tail=N&nofollow`), `GET /apps/{id}/export`,
  `POST /apps/import`, `GET /apps/{id}/exposed-ports`, `POST /apps/{id}/clone`.
- Bricks: `GET /bricks`, `GET /bricks/{id}`, `GET /apps/{id}/bricks`,
  `POST /apps/{id}/bricks`, `GET|PUT|PATCH|DELETE /apps/{id}/bricks/{brickId}`,
  `POST /apps/{id}/bricks/{brickId}/rename`.
- Models: `GET /models?bricks=`, `GET /models/{id}`,
  `PUT /models/ei/projects/{projectId}` (Edge Impulse), `DELETE /models/{id}`.
- Sketch C++ libraries: `GET /apps/{id}/sketch/libraries`,
  `PUT /apps/{id}/sketch/libraries/{ref}?add_deps=`,
  `DELETE /apps/{id}/sketch/libraries/{ref}?remove_deps=`,
  `GET /libraries?search=&page=&limit=` (catalog).
- Serial monitor: `GET /apps/{id}/serial-monitor` (WebSocket), or global
  `GET /monitor/ws`.

No auth (loopback only; `X-API-Key` is passed through but not enforced).

## App on-disk layout

```
~/ArduinoApps/<app>/
├── app.yaml              # name, icon, default flag, bricks
├── python/
│   ├── main.py           # from arduino.app_utils import App ; App.run(...)
│   └── requirements.txt  # pip deps (installed in the container)
├── sketch/
│   ├── sketch.ino        # MCU C++
│   └── sketch.yaml       # profile: platform arduino:zephyr, libraries
└── bricks/               # local brick code (optional)
```

- FQBN is hardware-fixed (`arduino:zephyr:unoq`, detected from the device tree).
- Compiling/flashing happens inside `app start`; build artifacts (incl.
  `compile_commands.json`) land in `<app>/.cache/sketch/`.
- The Python framework (`arduino.app_utils`, `arduino.app_bricks.*`) and the
  `requirements.txt` deps live inside the `python-apps-base` Docker image, not on
  the host filesystem.

## Common workflows

```bash
arduino-app-cli app new "My App" -d "Reads a sensor"
arduino-app-cli app start "My App"           # compile+flash sketch, run Python
arduino-app-cli app logs "My App" --follow
arduino-app-cli app stop "My App"
arduino-app-cli brick list
arduino-app-cli app new "From example" --from-app air-quality-monitoring
```
