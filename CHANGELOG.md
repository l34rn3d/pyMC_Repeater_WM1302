# Changelog

All notable changes to pyMC_Repeater will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] - dev branch

### Breaking Changes
- **WM1302→SX1302 rename**: All code, config keys, and docs renamed to `sx1302`/`SX1302`.
  Config change required for existing SX1302 installs:
  - `radio_type: "wm1302"` → `radio_type: "sx1302"`
  - `wm1302:` config section → `sx1302:`
  No backward-compat shim — update `config.yaml` manually or re-run setup.

### Added
- **SX1261 spectral scan noise floor**: Noise floor is now measured using the SX1261
  companion chip's spectral scan at the operating frequency, updated every 30 seconds.
  Replaces the previous approach of reading `pkt.rssic` from received packets (which
  only updated on packet arrival and measured signal+noise, not ambient noise floor).
  The SX1261 runs independently — scans do not interrupt packet reception.
- **`sx1261_spi_path` config option** in the `sx1302:` section (e.g. `/dev/spidev0.1`).
  Optional — if omitted, noise floor is not measured and a warning is logged at startup.

### Fixed
- **Spectral scan status enum**: `SPECTRAL_SCAN_STATUS_COMPLETED` and `SPECTRAL_SCAN_STATUS_ABORTED`
  were swapped in `sx1302_bindings.py`. The actual `lgw_spectral_scan_status_t` enum is
  `ABORTED=2, COMPLETED=3` — we had them reversed, so every completed scan was treated as aborted
  and every abort treated as completed. Noise floor was never updated as a result.

- **Spectral scan noise floor calculation**: The bin-search loop broke on the first zero-count bin
  (always bin 0, threshold=0 dBm) before reaching the ~-95 dBm noise floor region. Fixed to break
  on the first full-count bin instead, giving the highest threshold where all samples exceeded it.

- **SX1302 CRC filtering**: Bad-CRC packets were being passed to the repeater engine
  instead of being discarded. The SX1302 C library sets `pkt.status` to `STAT_CRC_BAD`
  (0x11) for invalid packets but still includes them in the receive buffer. The Python
  `_rx_loop` was only checking `pkt.size > 0`, so corrupt packets made it through.
  Now checks `pkt.status == STAT_CRC_OK` (0x10) before dispatching to the callback,
  matching the behaviour of the SX1262 path in pymc_core.

- **CRC status constants** in `sx1302_bindings.py` matching `loragw_hal.h`:
  - `STAT_NO_CRC = 0x01` — CRC not present in packet
  - `STAT_CRC_BAD = 0x11` — CRC present but failed
  - `STAT_CRC_OK = 0x10` — CRC present and valid

---

### Running the dev branch

```bash
# Clone and switch to dev
git clone -b dev https://github.com/l34rn3d/pyMC_Repeater_WM1302.git
cd pyMC_Repeater_WM1302

# Install
sudo ./manage.sh install
```

Or if already installed, upgrade in-place:

```bash
cd /path/to/pyMC_Repeater_WM1302
git pull origin dev
sudo ./manage.sh upgrade
sudo systemctl restart pymc-repeater
```

Verify the running version:
```bash
sudo journalctl -u pymc-repeater -n 20
```

---

## [1.1.0] - 2026-02-13

### Added - WM1302 LoRa Concentrator Support

This release adds full support for the **WM1302/SX1302 LoRa concentrator** hardware, enabling gateway-class repeaters with enhanced performance.

#### New Hardware Support
- **WM1302 concentrator** (SX1302-based) driver integration
- **ctypes bindings** for sx1302_hal C library (`repeater/hardware/sx1302_bindings.py`)
- **High-level wrapper** compatible with existing repeater architecture (`repeater/hardware/wm1302_wrapper.py`)
- **Automatic GPIO reset** sequence for WM1302 hardware initialization
- **Noise floor tracking** using channel RSSI from received packets

#### Configuration Enhancements
- New `radio_type` field in config.yaml to select hardware (`"sx1262"` or `"wm1302"`)
- New `wm1302` configuration section for concentrator-specific settings
- Hardware detection in `setup-radio-config.sh` to auto-configure appropriate section
- Updated `radio-settings.json` with WM1302 hardware profile

#### Installation Improvements
- `manage.sh` now copies `sx1302_hal/` directory during install/upgrade
- `setup-radio-config.sh` detects hardware type and configures appropriately
- Automatic selection of correct config section based on hardware type

#### Documentation
- **INSTALL_WM1302.md** - Complete step-by-step installation guide
- **docs/WM1302_README.md** - Technical details and architecture
- **docs/WM1302_QUICKSTART.md** - Quick reference guide
- Regional configuration examples (EU868, US915, AU915, AS923)

#### Features
- **Single-channel mode** operation of WM1302 concentrator
- **Higher TX power** support (up to 26 dBm EU / 25 dBm US)
- **Better sensitivity** (-139 dBm @ SF12)
- **Async send/receive** implementation for concentrator hardware
- **Multi-bandwidth support** (125kHz, 250kHz, 500kHz) with automatic IF chain selection

### Changed
- **Version bump** from 1.0.5 → 1.1.0
- **config.py** updated with WM1302 radio initialization (`get_radio_for_board()`)
- **setup-radio-config.sh** refactored to handle both SX1262 and SX1302 hardware types
- **manage.sh** install/upgrade functions now copy additional directories

### Technical Details

#### Architecture
```
Config (YAML)
    ↓
config.py (detects radio_type)
    ↓
WM1302Radio (Python wrapper)
    ↓
sx1302_bindings (ctypes)
    ↓
libloragw.so (C library)
    ↓
WM1302 Hardware (SPI)
```

#### Key Files
- `repeater/hardware/sx1302_bindings.py` - ctypes structure definitions and C library interface
- `repeater/hardware/wm1302_wrapper.py` - WM1302Radio class with begin/send/receive methods
- `sx1302_hal/libloragw/libloragw.so` - Compiled shared library for sx1302_hal
- `sx1302_hal/libloragw/reset_lgw.sh` - GPIO reset script for concentrator

#### Compatibility
- ✅ **Backward compatible** - Existing SX1262 configurations work unchanged
- ✅ **Drop-in replacement** - WM1302 uses same repeater architecture
- ✅ **Automatic detection** - Setup wizard identifies hardware type

### Known Limitations

#### WM1302-Specific
- **Single-channel mode only** - Multi-channel gateway features not used
- **Higher power consumption** - 415mA TX peak vs ~120mA for SX1262
- **No USB support yet** - Only SPI interface supported
- **Requires recompilation** - libloragw.so must be compiled on target architecture (ARM)

#### General
- **No CAD support** - Concentrators don't support Channel Activity Detection
- **LoRaWAN features unused** - Operating in LoRa physical layer mode only
- **Temperature sensor optional** - I2C sensor on WM1302 not required for operation

### Fixed
- **Async send implementation** - WM1302 send() now properly async
- **Struct alignment** - Fixed com_type field size in sx1302_bindings (c_uint32)
- **IF chain selection** - Proper handling of bandwidth >125kHz (uses IF chain 8)
- **Noise floor measurement** - Tracking rssic from received packets

### Dependencies
- **sx1302_hal** - Semtech sx1302_hal library (included in repo)
- **libgpiod** - Modern GPIO interface (Debian 12 compatible)
- **ctypes** - Python C library bindings (standard library)
- Existing dependencies unchanged

### Migration Guide

#### Upgrading from 1.0.x to 1.1.0

**For existing SX1262 users:**
```bash
cd pyMC_Repeater
git pull
sudo ./manage.sh
# Select "upgrade"
```

No configuration changes needed. Your existing config.yaml will continue to work.

**For new WM1302 installations:**
```bash
git clone https://github.com/l34rn3d/pyMC_Repeater_WM1302.git
cd pyMC_Repeater
sudo ./manage.sh
# Select "install"
# Choose "WM1302 LoRa Concentrator" from hardware menu
```

**Manual WM1302 configuration:**
1. Set `radio_type: "wm1302"` in config.yaml
2. Configure `wm1302:` section with SPI device path
3. Ensure sx1302_hal directory is present
4. Restart service

### Testing

Tested on:
- ✅ Raspberry Pi 4 Model B (ARM aarch64, Debian 12)
- ✅ WM1302 Pi HAT (SPI interface)
- ✅ Frequencies: EU868, US915, AU915
- ✅ Bandwidths: 62.5kHz, 125kHz, 250kHz
- ✅ Spreading Factors: SF7-SF12
- ✅ TX power: 14-26 dBm
- ✅ Packet TX/RX in mesh network

### Credits

WM1302 integration based on:
- **sx1302_hal** by Semtech
- **WM1302 module** by Seeed Studio
- **pyMC_Repeater** by Lloyd (rightup)

---

## [1.0.5] - Previous Release

### Features
- Core repeater functionality
- SX1262 hardware support
- Web dashboard
- MQTT publishing
- LetsMesh integration
- Automatic advertisements
- Discovery response
- Score-based filtering

### Supported Hardware
- Waveshare LoRa HAT
- uConsole LoRa Module
- FrequencyLabs MeshAdv
- Heltec HT-RA62

---

## Release Notes Format

Each release includes:
- **Version number** following semantic versioning
- **Date** of release
- **Added** - New features
- **Changed** - Changes to existing functionality
- **Fixed** - Bug fixes
- **Deprecated** - Features to be removed
- **Removed** - Removed features
- **Security** - Security fixes

---

## Reporting Issues

Found a bug or have a feature request?

1. Check existing issues: https://github.com/rightup/pyMC_Repeater/issues
2. Open new issue with:
   - Hardware details (Pi model, radio type)
   - Software version (`cat /opt/pymc_repeater/pyproject.toml | grep version`)
   - Configuration (sanitized config.yaml)
   - Logs (`sudo journalctl -u pymc-repeater -n 100`)
   - Steps to reproduce

---

## Contributing

Pull requests welcome! Please:
1. Fork the repository
2. Create feature branch from `dev`
3. Test with real hardware
4. Submit PR to `dev` branch
5. Include clear description of changes

---

**[1.1.0]** | WM1302 Support Release | Stable ✓
