# WM1302 LoRa Concentrator Driver

This fork adds support for the **WM1302 LoRa concentrator** (SX1302-based) to pyMC_Repeater.

## ⚠️ Important Notes

### Architecture Differences

The WM1302 is fundamentally different from standard LoRa transceivers:

- **SX1262** = Simple LoRa transceiver (single channel, point-to-point)
- **WM1302/SX1302** = LoRaWAN concentrator (multi-channel gateway receiver)

### Hardware Capabilities

**WM1302 Module Components:**
- **SX1302** - Baseband concentrator processor
- **SX1250** - TX/RX RF front-end (main radio)
- **SX1261** - LBT/Spectral scan (regulatory compliance only)

**Performance:**
- TX Power: 26 dBm (EU868) / 25 dBm (US915)
- Sensitivity: -139 dBm @SF12
- Multi-channel capable (8+ simultaneous channels)

## Installation

### Prerequisites

1. **Enable SPI:**
```bash
sudo raspi-config
# Interface Options → SPI → Enable
sudo reboot
```

2. **Verify SPI:**
```bash
ls /dev/spi*
# Should show: /dev/spidev0.0  /dev/spidev0.1
```

### Setup

1. **Clone this repository:**
```bash
git clone <this-repo-url>
cd pyMC_Repeater_WM1302
```

2. **The sx1302_hal library is already included and compiled.**
   - Located in: `sx1302_hal/libloragw/libloragw.so`
   - Python bindings: `repeater/hardware/sx1302_bindings.py`
   - Wrapper: `repeater/hardware/wm1302_wrapper.py`

3. **Configure for WM1302:**

Create your config file:
```bash
sudo cp config.yaml.example /etc/pymc_repeater/config.yaml
sudo nano /etc/pymc_repeater/config.yaml
```

Change the `radio_type` to `wm1302`:
```yaml
# Radio hardware type
radio_type: "wm1302"
```

Verify WM1302 section:
```yaml
wm1302:
  com_path: "/dev/spidev0.0"
```

4. **Install and run:**
```bash
pip install -e .
pymc-repeater
```

## Configuration Example

```yaml
radio_type: "wm1302"

repeater:
  node_name: "wm1302-repeater-01"

radio:
  frequency: 869618000  # EU868
  tx_power: 26          # Max for WM1302
  bandwidth: 125000     # 125 kHz
  spreading_factor: 8
  coding_rate: 8
  preamble_length: 17
  sync_word: 13380

wm1302:
  com_path: "/dev/spidev0.0"
```

## GPIO Pins (WM1302 Pi HAT)

The WM1302 uses the following GPIO pins (handled internally by the driver):
- GPIO 17: SX1302 reset
- GPIO 5: SX1261 reset
- GPIO 8: SX1302 chip select
- SPI0: MOSI, MISO, SCK (GPIO 10, 9, 11)

## Limitations

1. **Mesh Networking:** The concentrator is designed for gateway operation, not mesh nodes. Performance in mesh networks may differ from standard transceivers.

2. **Single Channel Mode:** This driver operates the WM1302 in single-channel mode to maintain compatibility with pyMC_Repeater's architecture.

3. **Power Consumption:** Higher than standard transceivers (415mA peak TX vs ~120mA for SX1262).

## Troubleshooting

### SPI Permissions
```bash
sudo usermod -a -G spi,gpio $USER
# Logout and login again
```

### Library Not Found
```bash
# Verify shared library exists
ls -l sx1302_hal/libloragw/libloragw.so

# If missing, rebuild:
cd sx1302_hal
make clean
make
cd libloragw
gcc -shared -o libloragw.so obj/*.o ../libtools/obj/*.o -lrt -lm -lpthread
```

### Concentrator Start Fails
- Check SPI is enabled: `ls /dev/spi*`
- Verify correct SPI device: `/dev/spidev0.0` vs `/dev/spidev1.0`
- Check dmesg for errors: `sudo dmesg | grep spi`
- Ensure no other process is using the concentrator

## Technical Details

### Python Bindings

The driver uses **ctypes** to interface with the C sx1302_hal library:
- `repeater/hardware/sx1302_bindings.py` - Low-level ctypes bindings
- `repeater/hardware/wm1302_wrapper.py` - High-level wrapper compatible with pyMC_Repeater

### Architecture

```
pyMC_Repeater
    ↓
config.py (detects radio_type)
    ↓
wm1302_wrapper.py (Python wrapper)
    ↓
sx1302_bindings.py (ctypes)
    ↓
libloragw.so (C library)
    ↓
WM1302 Hardware (SPI)
```

## Resources

- [WM1302 Documentation](https://wiki.seeedstudio.com/WM1302_module/)
- [sx1302_hal GitHub](https://github.com/Lora-net/sx1302_hal)
- [Original pyMC_Repeater](https://github.com/rightup/pyMC_Repeater)

## License

MIT License (same as original pyMC_Repeater)
