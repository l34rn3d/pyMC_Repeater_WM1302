# WM1302 Installation Guide

Complete step-by-step guide for setting up pyMC_Repeater with WM1302 LoRa concentrator hardware.

---

## Table of Contents

1. [Hardware Requirements](#hardware-requirements)
2. [Pre-Installation Steps](#pre-installation-steps)
3. [Quick Installation](#quick-installation)
4. [Manual Installation](#manual-installation)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Regional Configuration Examples](#regional-configuration-examples)

---

## Hardware Requirements

### WM1302 Module
- **WM1302 LoRa concentrator** (SX1302-based gateway module)
- Compatible form factors:
  - WM1302 Pi HAT (Raspberry Pi)
  - WM1302 SPI module
  - WM1302 USB module (not yet supported)

### Raspberry Pi
- **Raspberry Pi 3B+, 4, or 5** (recommended)
- **Raspberry Pi OS** (Debian 11 or 12)
- **SPI interface** enabled
- **4GB+ SD card** (8GB+ recommended)

### Power Supply
- **5V/3A power supply** recommended
- WM1302 peak current: ~415mA during TX

---

## Pre-Installation Steps

### 1. Enable SPI Interface

```bash
sudo raspi-config
```

Navigate to: **Interface Options → SPI → Enable**

Reboot when prompted:
```bash
sudo reboot
```

### 2. Verify SPI is Enabled

After reboot, check SPI devices exist:
```bash
ls /dev/spi*
```

Expected output:
```
/dev/spidev0.0  /dev/spidev0.1
```

### 3. Add User to Hardware Groups

```bash
sudo usermod -a -G spi,gpio,i2c $USER
```

**Important:** Log out and log back in for group changes to take effect.

### 4. Install System Dependencies

```bash
sudo apt update
sudo apt install -y git python3-pip libffi-dev jq wget \
    swig build-essential python3-dev
```

---

## Quick Installation

The fastest way to install pyMC_Repeater with WM1302 support:

```bash
# Clone repository
git clone https://github.com/rightup/pyMC_Repeater.git
cd pyMC_Repeater

# Run interactive installer
sudo ./manage.sh
```

The interactive installer will:
1. ✅ Install system dependencies
2. ✅ Create service user and directories
3. ✅ Install Python packages
4. ✅ Launch hardware configuration wizard
5. ✅ Set up systemd service
6. ✅ Start the repeater

### During Installation

When the **hardware selection menu** appears:
- Select **"WM1302 LoRa Concentrator"** from the list
- Choose your region's radio settings (EU868, US915, AU915, etc.)
- Confirm your repeater name

The installer will automatically:
- Set `radio_type: "wm1302"` in config
- Configure WM1302-specific settings
- Copy the sx1302_hal library

---

## Manual Installation

If you prefer step-by-step control:

### 1. Clone Repository

```bash
git clone https://github.com/rightup/pyMC_Repeater.git
cd pyMC_Repeater
```

### 2. Install Python Package

```bash
pip install -e .
```

Or install to system (Bookworm):
```bash
pip install --break-system-packages -e .
```

### 3. Create Configuration Directory

```bash
sudo mkdir -p /etc/pymc_repeater
sudo cp config.yaml.example /etc/pymc_repeater/config.yaml
```

### 4. Configure for WM1302

Edit the config file:
```bash
sudo nano /etc/pymc_repeater/config.yaml
```

**Critical settings to change:**

```yaml
# Change radio_type from sx1262 to wm1302
radio_type: "wm1302"

repeater:
  node_name: "my-wm1302-repeater"  # Choose unique name

radio:
  frequency: 869618000      # Your region's frequency (Hz)
  tx_power: 26              # Max for WM1302 EU (26 dBm)
  bandwidth: 125000         # 125 kHz
  spreading_factor: 8
  coding_rate: 8
  preamble_length: 17
  sync_word: 13380

wm1302:
  com_path: "/dev/spidev0.0"  # SPI device
```

### 5. Create Systemd Service

```bash
sudo cp pymc-repeater.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pymc-repeater
sudo systemctl start pymc-repeater
```

### 6. Verify Service Started

```bash
sudo systemctl status pymc-repeater
```

---

## Configuration

### Minimal WM1302 Configuration

```yaml
radio_type: "wm1302"

repeater:
  node_name: "wm1302-rpt-01"

radio:
  frequency: 869618000
  tx_power: 26
  bandwidth: 125000
  spreading_factor: 8
  coding_rate: 8
  preamble_length: 17
  sync_word: 13380

wm1302:
  com_path: "/dev/spidev0.0"
```

### Understanding WM1302 Settings

**`com_path`** - SPI device path
- Default: `/dev/spidev0.0` (SPI0)
- Alternative: `/dev/spidev1.0` (if using SPI1)

**`tx_power`** - Transmit power in dBm
- EU868: Max 26 dBm
- US915: Max 25 dBm
- AU915: Max 25 dBm

**Important Notes:**
- WM1302 does **not** use GPIO pin configuration like SX1262
- Reset/control pins are handled internally by the driver
- Multi-channel configuration is not used (single channel mode)

---

## Verification

### 1. Check Service Status

```bash
sudo systemctl status pymc-repeater
```

Look for:
```
✓ Active: active (running)
✓ "WM1302 concentrator started successfully"
```

### 2. View Live Logs

```bash
sudo journalctl -u pymc-repeater -f
```

Expected logs:
```
INFO - Initializing WM1302: freq=869618000Hz, SF=8, BW=125000Hz, CR=4/8
INFO - Performing WM1302 GPIO reset sequence
INFO - Board configuration successful
INFO - WM1302 concentrator started successfully
```

### 3. Access Web Dashboard

Open browser to:
```
http://<raspberry-pi-ip>:8000
```

Default port: **8000**

You should see:
- ✅ Green status indicator
- ✅ Current RSSI/noise floor
- ✅ Packet statistics (after packets received)

### 4. Test Packet Reception

If you have a MeshCore device nearby:
- Send a packet from your device
- Check repeater logs for `Received packet` messages
- Check web dashboard for updated statistics

---

## Troubleshooting

### Error: "No such file or directory: /dev/spidev0.0"

**Cause:** SPI not enabled

**Fix:**
```bash
sudo raspi-config
# Interface Options → SPI → Enable
sudo reboot
```

### Error: "Permission denied: /dev/spidev0.0"

**Cause:** User not in spi group

**Fix:**
```bash
sudo usermod -a -G spi,gpio $USER
# Log out and log back in
```

### Error: "Failed to load library"

**Cause:** libloragw.so not compiled for ARM architecture

**Fix:**
```bash
cd sx1302_hal
make clean
make
cd libloragw
gcc -shared -o libloragw.so obj/*.o ../libtools/obj/*.o -lrt -lm -lpthread
```

### Error: "Board config failed: -1"

**Possible causes:**
1. SPI device doesn't exist
2. Permission issue
3. Hardware not connected properly

**Debug steps:**
```bash
# Check SPI device exists
ls -l /dev/spidev0.0

# Check user groups
groups

# Check hardware connections (if using HAT)
# Ensure HAT is firmly seated on GPIO header

# Check kernel logs
sudo dmesg | grep spi
```

### Warning: "I2C for temperature sensor failed"

**Cause:** WM1302 has optional I2C temperature sensor

**Fix (optional):**
```bash
# Enable I2C
sudo raspi-config
# Interface Options → I2C → Enable

# Load I2C modules
sudo modprobe i2c-dev i2c-bcm2835

# Add to /boot/firmware/config.txt
echo "dtparam=i2c_arm=on" | sudo tee -a /boot/firmware/config.txt
```

**Note:** This warning is non-critical. Repeater will work without temperature sensor.

### Service Fails to Start

**Check logs for specific error:**
```bash
sudo journalctl -u pymc-repeater -n 50 --no-pager
```

**Common issues:**
- Config file syntax error → Check YAML syntax
- Import errors → Reinstall: `pip install --break-system-packages -e .`
- SPI permission → Check groups: `groups`

### No Packets Being Received

**Checklist:**
1. ✅ Service running: `systemctl status pymc-repeater`
2. ✅ Logs show "concentrator started successfully"
3. ✅ Frequency matches your device
4. ✅ Bandwidth matches your device
5. ✅ Spreading factor matches your device
6. ✅ Sync word matches (critical!)
7. ✅ Device is in range and transmitting

**Test transmission:**
```bash
# Check logs for TX confirmation
sudo journalctl -u pymc-repeater -f
# Look for "TX 129 bytes" messages (advert packets)
```

---

## Regional Configuration Examples

### EU868 (Europe)

```yaml
radio:
  frequency: 869618000      # 869.618 MHz
  tx_power: 26              # Max 26 dBm
  bandwidth: 125000         # 125 kHz
  spreading_factor: 8
  coding_rate: 8
  preamble_length: 17
  sync_word: 13380
```

### US915 (USA)

```yaml
radio:
  frequency: 915000000      # 915.0 MHz
  tx_power: 25              # Max 25 dBm
  bandwidth: 125000         # 125 kHz
  spreading_factor: 8
  coding_rate: 8
  preamble_length: 17
  sync_word: 13380
```

### AU915 (Australia)

```yaml
radio:
  frequency: 915800000      # 915.8 MHz
  tx_power: 25              # Max 25 dBm
  bandwidth: 250000         # 250 kHz
  spreading_factor: 11
  coding_rate: 5
  preamble_length: 16
  sync_word: 18             # 0x12
```

### AS923 (Asia-Pacific)

```yaml
radio:
  frequency: 923200000      # 923.2 MHz
  tx_power: 14              # Max 14 dBm
  bandwidth: 125000         # 125 kHz
  spreading_factor: 8
  coding_rate: 8
  preamble_length: 17
  sync_word: 13380
```

---

## Performance Notes

### WM1302 vs SX1262

**Advantages:**
- ✅ Better sensitivity: -139 dBm @ SF12 (vs -148 dBm SX1262)
- ✅ Higher TX power: 26 dBm (vs 22 dBm typical)
- ✅ Multi-channel capable (not used in this mode)

**Trade-offs:**
- ⚠️ Higher power consumption: 415mA TX peak (vs ~120mA SX1262)
- ⚠️ Larger form factor: Mini-PCIe module vs small HAT
- ⚠️ Higher cost: ~$30-40 (vs ~$15-20 SX1262)

### Expected Range

With optimal conditions:
- **Line of sight:** 15-20+ km
- **Urban:** 2-5 km
- **Indoor:** 500m - 1km

Actual range depends on:
- Antenna quality
- Terrain/obstacles
- TX power setting
- Spreading factor

---

## Next Steps

After successful installation:

1. **Monitor logs** - Watch for packet activity
   ```bash
   sudo journalctl -u pymc-repeater -f
   ```

2. **Test with devices** - Send packets from MeshCore devices

3. **Optimize settings** - Adjust TX power/SF for your deployment

4. **Configure automatic start** - Already enabled via systemd

5. **Set up remote access** - Configure firewall for web dashboard

---

## Support Resources

- **Documentation:** See `docs/` folder
  - `WM1302_README.md` - Technical details
  - `WM1302_QUICKSTART.md` - Quick reference
- **MeshCore Discord:** https://discord.gg/meshcore
- **pyMC_core Docs:** https://rightup.github.io/pyMC_core/
- **Issue Tracker:** https://github.com/rightup/pyMC_Repeater/issues

---

## License

MIT License - Same as pyMC_Repeater

See LICENSE file for details.

---

**Installation Complete! 🚀**

Your WM1302 repeater is now ready to extend your mesh network.
