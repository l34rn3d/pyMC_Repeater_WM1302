# Prerequisites for pyMC_Repeater

Complete guide for preparing your Raspberry Pi before installing pyMC_Repeater with WM1302 or SX1262 hardware.

---

## Hardware Requirements

### Raspberry Pi
- **Raspberry Pi 3B+, 4, or 5** (recommended)
- **Raspberry Pi OS** (Debian 11 Bullseye or 12 Bookworm)
- **4GB+ SD card** (8GB+ recommended)
- **Power supply:** 5V/2.5A minimum (5V/3A for WM1302)

### LoRa Hardware
- **WM1302** LoRa concentrator (SPI interface), OR
- **SX1262** LoRa transceiver (Waveshare, MeshAdv, uConsole, etc.)

### Network
- **Network connection** (Ethernet or WiFi)
- **SSH access** (optional but recommended)

---

## System Interfaces

The following interfaces must be enabled on your Raspberry Pi:

### 1. SPI Interface (Required)

**Why:** WM1302 and SX1262 communicate via SPI bus

**Enable via raspi-config:**
```bash
sudo raspi-config
```

Navigate to:
```
Interface Options → SPI → Enable
```

Reboot when prompted:
```bash
sudo reboot
```

**Verify SPI is enabled:**
```bash
ls /dev/spi*
```

Expected output:
```
/dev/spidev0.0  /dev/spidev0.1
```

**Alternative manual enable:**

Edit `/boot/firmware/config.txt` (or `/boot/config.txt` on older systems):
```bash
sudo nano /boot/firmware/config.txt
```

Add or uncomment:
```
dtparam=spi=on
```

Save, exit, and reboot.

---

### 2. I2C Interface (Optional - WM1302 Only)

**Why:** WM1302 has optional I2C temperature sensor

**Note:** Not required for operation, but eliminates warning messages in logs.

**Enable via raspi-config:**
```bash
sudo raspi-config
```

Navigate to:
```
Interface Options → I2C → Enable
```

**Manual enable:**

Edit `/boot/firmware/config.txt`:
```bash
sudo nano /boot/firmware/config.txt
```

Add or uncomment:
```
dtparam=i2c_arm=on
```

**Load I2C kernel modules:**
```bash
sudo modprobe i2c-dev i2c-bcm2835
```

**Make modules load at boot:**
```bash
echo "i2c-dev" | sudo tee -a /etc/modules
echo "i2c-bcm2835" | sudo tee -a /etc/modules
```

**Verify I2C is enabled:**
```bash
ls /dev/i2c-*
```

Expected output:
```
/dev/i2c-1
```

---

### 3. User Permissions (Required)

**Why:** Non-root users need permission to access hardware interfaces

**Add user to hardware groups:**
```bash
sudo usermod -a -G spi,gpio,i2c $USER
```

Or for specific user:
```bash
sudo usermod -a -G spi,gpio,i2c chris
```

**Important:** You must **log out and log back in** for group changes to take effect.

**Verify group membership:**
```bash
groups
```

Should show:
```
... spi gpio i2c ...
```

---

## System Dependencies

### Package Installation

**Update package list:**
```bash
sudo apt update
```

**Install required packages:**
```bash
sudo apt install -y \
    git \
    python3-pip \
    libffi-dev \
    jq \
    wget \
    swig \
    build-essential \
    python3-dev \
    python3-rrdtool
```

**Package descriptions:**
- `git` - Version control for cloning repository
- `python3-pip` - Python package installer
- `libffi-dev` - Foreign function interface library
- `jq` - JSON processor for config scripts
- `wget` - File downloader
- `swig` - Interface compiler for C libraries
- `build-essential` - GCC compiler and build tools
- `python3-dev` - Python development headers
- `python3-rrdtool` - Optional, for statistics graphs

---

## Quick Setup Script

Run all prerequisites at once:

```bash
#!/bin/bash
# Quick prerequisites setup for pyMC_Repeater

echo "=== pyMC_Repeater Prerequisites Setup ==="
echo ""

# Update package list
echo "[1/4] Updating package list..."
sudo apt update

# Install packages
echo "[2/4] Installing system packages..."
sudo apt install -y git python3-pip libffi-dev jq wget swig \
    build-essential python3-dev python3-rrdtool

# Add user to groups
echo "[3/4] Adding user to hardware groups..."
sudo usermod -a -G spi,gpio,i2c $USER

# Load I2C modules
echo "[4/4] Loading I2C kernel modules..."
sudo modprobe i2c-dev i2c-bcm2835 2>/dev/null || true
echo "i2c-dev" | sudo tee -a /etc/modules >/dev/null 2>&1 || true
echo "i2c-bcm2835" | sudo tee -a /etc/modules >/dev/null 2>&1 || true

echo ""
echo "✓ Package installation complete"
echo "✓ User added to hardware groups"
echo "✓ I2C modules loaded"
echo ""
echo "⚠ IMPORTANT: You must enable SPI manually:"
echo "  sudo raspi-config"
echo "  Navigate to: Interface Options → SPI → Enable"
echo "  Then reboot"
echo ""
echo "⚠ After reboot, log out and log back in for group changes"
echo ""
```

Save as `setup_prerequisites.sh`, make executable, and run:
```bash
chmod +x setup_prerequisites.sh
./setup_prerequisites.sh
```

---

## Verification Checklist

Before installing pyMC_Repeater, verify:

### ✓ SPI Enabled
```bash
ls /dev/spidev0.0
# Should exist
```

### ✓ User Groups
```bash
groups | grep -E "spi|gpio"
# Should show: spi gpio i2c
```

### ✓ I2C Enabled (Optional)
```bash
ls /dev/i2c-*
# Should show: /dev/i2c-1
```

### ✓ System Packages
```bash
which git python3 pip jq gcc
# All should return paths
```

### ✓ Python Version
```bash
python3 --version
# Should be Python 3.8+
```

---

## Hardware-Specific Requirements

### WM1302 Concentrator

**Additional requirements:**
- SPI0 interface enabled (default)
- Adequate power supply (5V/3A recommended)
- GPIO pins available for reset sequence:
  - GPIO 17: SX1302 reset
  - GPIO 18: Power enable
  - GPIO 5: SX1261 reset
  - GPIO 13: ADC reset

**No manual wiring needed** if using WM1302 Pi HAT.

### SX1262 Transceiver

**GPIO pins (configured in radio-settings.json):**
- Varies by hardware model
- Typical: CS, Reset, Busy, IRQ pins
- Optional: TX/RX enable pins, LED pins

**See hardware-specific documentation** for your board.

---

## Network Configuration

### Static IP (Recommended)

For reliable access to web dashboard:

**Edit dhcpcd.conf:**
```bash
sudo nano /etc/dhcpcd.conf
```

**Add at end (adjust for your network):**
```
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Or for WiFi:
```
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

**Restart networking:**
```bash
sudo systemctl restart dhcpcd
```

### Hostname (Optional)

**Set meaningful hostname:**
```bash
sudo raspi-config
# System Options → Hostname → Enter: "wm1302-repeater"
```

Or manually:
```bash
sudo hostnamectl set-hostname wm1302-repeater
```

---

## Firewall Configuration (Optional)

If using firewall, allow web dashboard:

```bash
# Using ufw
sudo ufw allow 8000/tcp
sudo ufw enable

# Using iptables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

---

## Troubleshooting Prerequisites

### SPI not showing up after enable

**Check kernel module loaded:**
```bash
lsmod | grep spi
```

Should show:
```
spi_bcm2835
```

**Manually load module:**
```bash
sudo modprobe spi_bcm2835
```

**Check config.txt:**
```bash
grep "dtparam=spi" /boot/firmware/config.txt
```

Should show:
```
dtparam=spi=on
```

### Permission denied errors

**Verify user in groups:**
```bash
id $USER
```

Should show `spi` and `gpio` in groups list.

**If missing, add again:**
```bash
sudo usermod -a -G spi,gpio,i2c $USER
```

**Then log out completely** (not just close terminal):
```bash
logout
# SSH back in or login again
```

### I2C not working

**Check if I2C device exists:**
```bash
ls -l /dev/i2c-*
```

**Check config.txt:**
```bash
grep "dtparam=i2c" /boot/firmware/config.txt
```

**Enable if missing:**
```bash
echo "dtparam=i2c_arm=on" | sudo tee -a /boot/firmware/config.txt
sudo reboot
```

### Package installation fails

**Update package database:**
```bash
sudo apt update
sudo apt upgrade
```

**Fix broken packages:**
```bash
sudo apt --fix-broken install
```

**Clear package cache:**
```bash
sudo apt clean
sudo apt autoclean
```

---

## After Prerequisites Complete

Once all prerequisites are met:

1. **Reboot the system:**
   ```bash
   sudo reboot
   ```

2. **Verify everything:**
   ```bash
   ls /dev/spidev0.0  # Should exist
   groups             # Should show spi, gpio, i2c
   ```

3. **Proceed to installation:**
   ```bash
   git clone https://github.com/rightup/pyMC_Repeater.git
   cd pyMC_Repeater
   sudo ./manage.sh
   ```

---

## Summary

**Required for all hardware:**
- ✅ SPI interface enabled
- ✅ User in spi, gpio groups
- ✅ System packages installed
- ✅ Python 3.8+

**Optional but recommended:**
- ⚪ I2C interface enabled (WM1302 only)
- ⚪ Static IP configured
- ⚪ Firewall rules for port 8000

**After setup:**
- 🔄 Reboot
- 👤 Re-login (for group changes)
- ✅ Run verification checklist

---

## Support

If prerequisites fail:
1. Check `/var/log/syslog` for hardware errors
2. Run `sudo dmesg | grep spi` for SPI issues
3. Verify Raspberry Pi OS is up to date
4. See main installation guide for additional help

**Ready to install?** See [INSTALL_WM1302.md](INSTALL_WM1302.md) or run `./manage.sh`
