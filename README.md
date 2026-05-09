# pyMC Repeater WM1302

LoRa MeshCore repeater daemon with web setup support and WM1302/SX1302 concentrator support.

This branch is intended for installing from GitHub onto a Raspberry Pi/SenseCAP-style device with a WM1302/SX1302 concentrator.

## Supported Flow

- Install from GitHub `dev` branch.
- Run the SX1302 preinstall helper.
- Run the CLI installer.
- Complete radio/admin setup in the web wizard.

## Fresh WM1302/SX1302 Install

Enable SPI first if it is not already enabled:

```bash
sudo raspi-config
```

Then reboot if SPI was changed.

Install from GitHub:

```bash
sudo apt update
sudo apt install -y git
git clone -b dev https://github.com/l34rn3d/pyMC_Repeater_WM1302.git pyMC_Repeater
cd pyMC_Repeater
./preinstall-sx1302.sh
sudo ./manage.sh install
```

Open the setup wizard:

```text
http://<device-ip>:8000/setup
```

In the web setup wizard:

- Set the repeater name.
- Select `WM1302 / SX1302 Concentrator`.
- Select the radio preset/frequency.
- Set the admin password.
- Save/apply setup.

The service will restart after setup.

## Verify

Watch logs:

```bash
sudo journalctl -u pymc-repeater -f
```

Expected startup lines:

```text
SX1302 concentrator started successfully
HTTP stats server started on http://0.0.0.0:8000
```

Check service status:

```bash
sudo systemctl status pymc-repeater --no-pager
```

Dashboard:

```text
http://<device-ip>:8000
```

## Clean Reinstall

Use this before a fresh test install:

```bash
sudo systemctl stop pymc-repeater 2>/dev/null || true
sudo systemctl disable pymc-repeater 2>/dev/null || true
sudo rm -f /etc/systemd/system/pymc-repeater.service
sudo systemctl daemon-reload
sudo systemctl reset-failed pymc-repeater 2>/dev/null || true
sudo rm -rf /opt/pymc_repeater /etc/pymc_repeater /var/log/pymc_repeater /var/lib/pymc_repeater ~/pyMC_Repeater
sudo userdel -r repeater 2>/dev/null || true
```

## What The Installer Creates

- `/opt/pymc_repeater` application and virtualenv
- `/opt/pymc_repeater/sx1302_hal` built SX1302 HAL
- `/etc/pymc_repeater/config.yaml` runtime config
- `/var/lib/pymc_repeater` data and database
- `/var/log/pymc_repeater` logs
- `pymc-repeater.service` systemd service
- `repeater` service user

## Updating

From the cloned repo:

```bash
cd ~/pyMC_Repeater
git pull origin dev
./preinstall-sx1302.sh
sudo ./manage.sh upgrade
```

Or use the web update page after the initial install is complete.

## Web UI Asset Build Notes

If the web UI/icon is rebuilt in the separate web builder:

1. Put the icon into the web builder project.
2. Run the web build.
3. Copy the built output into `repeater/web/html/` in this repo.
4. Commit and push to `dev`.
5. Reinstall or update from GitHub.

## Troubleshooting

If the setup page does not load:

```bash
sudo systemctl status pymc-repeater --no-pager
sudo journalctl -u pymc-repeater -n 100 --no-pager
```

If SX1302 fails to start, confirm SPI exists:

```bash
ls /dev/spidev*
```

Expected for WM1302/SX1302:

```text
/dev/spidev0.0
```

If the HAL library is missing, rebuild manually:

```bash
cd /opt/pymc_repeater/sx1302_hal
sudo make clean
sudo make all
cd libloragw
sudo gcc -shared -fPIC -o libloragw.so \
  -Wl,--whole-archive \
  libloragw.a \
  ../libtools/libtinymt32.a \
  ../libtools/libparson.a \
  ../libtools/libbase64.a \
  -Wl,--no-whole-archive
sudo systemctl restart pymc-repeater
```
