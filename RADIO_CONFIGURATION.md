# Radio Configuration Guide

Complete guide for configuring radio settings for pyMC_Repeater across different regions and use cases.

---

## Configuration File Location

The radio configuration is stored in:
```
/etc/pymc_repeater/config.yaml
```

**To edit:**
```bash
sudo nano /etc/pymc_repeater/config.yaml
```

**After editing, restart the service:**
```bash
sudo systemctl restart pymc-repeater
```

---

## Radio Settings Section

The `radio:` section in config.yaml controls all LoRa physical layer parameters:

```yaml
radio:
  frequency: 869618000      # Frequency in Hz
  tx_power: 26              # TX power in dBm
  bandwidth: 125000         # Bandwidth in Hz
  spreading_factor: 8       # SF7-SF12
  coding_rate: 8            # 5-8 (4/5, 4/6, 4/7, 4/8)
  preamble_length: 17       # Preamble symbols
  sync_word: 13380          # Network ID
  crc_enabled: true         # CRC checking
  implicit_header: false    # Header mode
```

---

## Regional Configurations

### EU868 (Europe)

**Standard MeshCore Settings:**
```yaml
radio:
  frequency: 869618000      # 869.618 MHz
  tx_power: 26              # Max 26 dBm (WM1302) / 22 dBm (SX1262)
  bandwidth: 125000         # 125 kHz
  spreading_factor: 8       # SF8
  coding_rate: 8            # 4/8
  preamble_length: 17
  sync_word: 13380          # 0x3444
  crc_enabled: true
  implicit_header: false
```

**Legal frequency ranges:**
- 863-870 MHz
- Max EIRP: 27 dBm (500 mW)
- Duty cycle: 1% on some channels, 10% on others

**Alternative frequencies:**
- 868.1 MHz: `868100000`
- 868.3 MHz: `868300000`
- 869.525 MHz: `869525000`

---

### US915 (United States)

**Standard MeshCore Settings:**
```yaml
radio:
  frequency: 915000000      # 915.0 MHz
  tx_power: 25              # Max 25 dBm (WM1302) / 22 dBm (SX1262)
  bandwidth: 125000         # 125 kHz
  spreading_factor: 8       # SF8
  coding_rate: 8            # 4/8
  preamble_length: 17
  sync_word: 13380          # 0x3444
  crc_enabled: true
  implicit_header: false
```

**Legal frequency ranges:**
- 902-928 MHz
- Max EIRP: 30 dBm (1 W)
- No duty cycle restrictions

**Alternative frequencies:**
- 903.0 MHz: `903000000`
- 904.0 MHz: `904000000`
- 915.2 MHz: `915200000`
- 923.3 MHz: `923300000`

---

### AU915 (Australia)

**Standard MeshCore Settings:**
```yaml
radio:
  frequency: 915800000      # 915.8 MHz
  tx_power: 25              # Max 25 dBm (WM1302) / 22 dBm (SX1262)
  bandwidth: 250000         # 250 kHz
  spreading_factor: 11      # SF11
  coding_rate: 5            # 4/5
  preamble_length: 16
  sync_word: 18             # 0x12
  crc_enabled: true
  implicit_header: false
```

**Legal frequency ranges:**
- 915-928 MHz
- Max EIRP: 30 dBm (1 W)
- No duty cycle restrictions

**Alternative frequencies:**
- 916.8 MHz: `916800000`
- 917.8 MHz: `917800000`
- 923.3 MHz: `923300000`

---

### AS923 (Asia-Pacific)

**Standard MeshCore Settings:**
```yaml
radio:
  frequency: 923200000      # 923.2 MHz
  tx_power: 14              # Max 14 dBm (25 mW)
  bandwidth: 125000         # 125 kHz
  spreading_factor: 8       # SF8
  coding_rate: 8            # 4/8
  preamble_length: 17
  sync_word: 13380          # 0x3444
  crc_enabled: true
  implicit_header: false
```

**Legal frequency ranges:**
- 920-923 MHz (AS923-1)
- 923-925 MHz (AS923-2)
- Max EIRP: 16 dBm (typical)

**Note:** Varies by country. Check local regulations.

---

### CN470 (China)

**Standard MeshCore Settings:**
```yaml
radio:
  frequency: 470300000      # 470.3 MHz
  tx_power: 17              # Max 17 dBm (50 mW)
  bandwidth: 125000         # 125 kHz
  spreading_factor: 8       # SF8
  coding_rate: 8            # 4/8
  preamble_length: 17
  sync_word: 13380          # 0x3444
  crc_enabled: true
  implicit_header: false
```

**Legal frequency ranges:**
- 470-510 MHz
- Max EIRP: 17 dBm (50 mW)

---

## Parameter Explanations

### Frequency
- **Units:** Hz (not MHz!)
- **Format:** Integer value
- **Example:** `869618000` = 869.618 MHz
- **Must match:** All nodes in your mesh network

### TX Power
- **Units:** dBm
- **Range:** 2-30 dBm (hardware and region dependent)
- **WM1302 max:** 26 dBm (EU), 25 dBm (US/AU)
- **SX1262 max:** 22 dBm (typical)
- **Higher = longer range but more power consumption**

### Bandwidth
- **Units:** Hz
- **Valid values:**
  - `62500` = 62.5 kHz (long range, slow)
  - `125000` = 125 kHz (standard)
  - `250000` = 250 kHz (faster, shorter range)
  - `500000` = 500 kHz (fastest, shortest range)
- **Trade-off:** Wider bandwidth = faster data rate but shorter range

### Spreading Factor (SF)
- **Range:** 7-12
- **Higher SF = longer range but slower**
- **Common values:**
  - SF7: Fastest, shortest range
  - SF8: Good balance
  - SF10: Long range
  - SF12: Maximum range, slowest

**Airtime comparison (125kHz, 20 byte packet):**
- SF7: ~41 ms
- SF8: ~72 ms
- SF10: ~247 ms
- SF12: ~991 ms

### Coding Rate (CR)
- **Range:** 5-8
- **Represents:** 4/5, 4/6, 4/7, 4/8 error correction
- **Higher = more error correction but slower**
- **Config value 8 = CR 4/8** (most error correction)
- **Config value 5 = CR 4/5** (least error correction)

### Preamble Length
- **Range:** 6-65535 symbols
- **Standard:** 8 or 17
- **Must match** between all nodes
- **Longer = easier detection but more overhead**

### Sync Word
- **Format:** Integer (decimal) or hex
- **Purpose:** Network identifier
- **Must match** across all mesh nodes
- **Common values:**
  - `13380` (0x3444) - Standard MeshCore
  - `18` (0x12) - Alternative
  - `52` (0x34) - LoRaWAN public

---

## Hardware-Specific Limits

### WM1302 Concentrator

**TX Power by Region:**
```yaml
# EU868
tx_power: 26    # Max 26 dBm

# US915 / AU915
tx_power: 25    # Max 25 dBm

# AS923
tx_power: 14    # Max 14 dBm (regional limit)
```

**Supported Bandwidths:**
- All: 62.5kHz, 125kHz, 250kHz, 500kHz

**Notes:**
- Higher power consumption than SX1262
- Better sensitivity (-139 dBm @ SF12)

### SX1262 Transceiver

**TX Power:**
```yaml
# Most hardware
tx_power: 22    # Max 22 dBm

# High-power versions (e.g., PiMesh-1W)
tx_power: 30    # Max 30 dBm (US only)
```

**Supported Bandwidths:**
- All: 62.5kHz, 125kHz, 250kHz, 500kHz

**Notes:**
- Lower power consumption
- Good sensitivity (-148 dBm @ SF12)

---

## Matching Settings Across Network

**Critical - Must Match:**
- ✅ Frequency (exact)
- ✅ Bandwidth
- ✅ Spreading Factor
- ✅ Coding Rate
- ✅ Sync Word
- ✅ Preamble Length

**Can Differ:**
- TX Power (each node can use different power)
- CRC enabled (but keep enabled)

**If settings don't match, nodes cannot communicate!**

---

## Range Optimization

### Maximum Range Settings

For maximum range (slower data rate):
```yaml
radio:
  frequency: 869618000      # Your region
  tx_power: 26              # Maximum allowed
  bandwidth: 62500          # Narrowest bandwidth
  spreading_factor: 12      # Maximum SF
  coding_rate: 8            # Maximum error correction
  preamble_length: 17
```

**Expected range:** 20-30+ km line of sight

### Balanced Settings

Good balance of range and speed:
```yaml
radio:
  frequency: 869618000
  tx_power: 22
  bandwidth: 125000
  spreading_factor: 8
  coding_rate: 8
  preamble_length: 17
```

**Expected range:** 10-15 km line of sight

### Fast Settings

Faster data rate (shorter range):
```yaml
radio:
  frequency: 869618000
  tx_power: 20
  bandwidth: 250000
  spreading_factor: 7
  coding_rate: 5
  preamble_length: 8
```

**Expected range:** 5-8 km line of sight

---

## Testing Configuration

### Test Connectivity
```bash
# Watch logs for packet reception
sudo journalctl -u pymc-repeater -f
```

Look for:
```
Received packet: <size> bytes, RSSI: -XX dBm, SNR: XX dB
```

### Check RSSI/SNR

**Good signal:**
- RSSI: > -100 dBm
- SNR: > 5 dB

**Marginal signal:**
- RSSI: -100 to -120 dBm
- SNR: 0 to 5 dB

**Poor signal:**
- RSSI: < -120 dBm
- SNR: < 0 dB

**If signal is poor:**
1. Increase TX power
2. Increase spreading factor
3. Improve antenna placement
4. Reduce obstacles

---

## Common Configuration Scenarios

### Gateway/Repeater (Fixed Location)

Optimize for maximum coverage:
```yaml
radio:
  frequency: 869618000
  tx_power: 26              # Maximum power
  bandwidth: 125000         # Standard
  spreading_factor: 10      # Long range
  coding_rate: 8
```

### Mobile Node (Battery Powered)

Optimize for power efficiency:
```yaml
radio:
  frequency: 869618000
  tx_power: 14              # Lower power
  bandwidth: 125000
  spreading_factor: 7       # Faster = less airtime
  coding_rate: 5            # Less overhead
```

### High-Density Network

Faster data rate to reduce collisions:
```yaml
radio:
  frequency: 869618000
  tx_power: 20
  bandwidth: 250000         # Wider bandwidth
  spreading_factor: 7       # Fast transmission
  coding_rate: 5
```

### Rural/Long Distance

Maximum range configuration:
```yaml
radio:
  frequency: 869618000
  tx_power: 26
  bandwidth: 62500          # Narrow for sensitivity
  spreading_factor: 12      # Maximum range
  coding_rate: 8
```

---

## Advanced Settings

### Multiple Channels (Future)

Currently pyMC_Repeater uses single channel mode. Multi-channel support may be added in future versions.

### CAD (Channel Activity Detection)

Not supported by WM1302 concentrator hardware. SX1262 supports CAD but it's not currently used.

### Listen Before Talk (LBT)

For regulatory compliance in some regions. Not currently implemented.

---

## Configuration Template

Copy this template to quickly configure different regions:

```yaml
# ===== RADIO CONFIGURATION =====
# Uncomment and use the appropriate section for your region

# --- EU868 ---
#radio:
#  frequency: 869618000
#  tx_power: 26
#  bandwidth: 125000
#  spreading_factor: 8
#  coding_rate: 8
#  preamble_length: 17
#  sync_word: 13380

# --- US915 ---
#radio:
#  frequency: 915000000
#  tx_power: 25
#  bandwidth: 125000
#  spreading_factor: 8
#  coding_rate: 8
#  preamble_length: 17
#  sync_word: 13380

# --- AU915 ---
radio:
  frequency: 915800000
  tx_power: 25
  bandwidth: 250000
  spreading_factor: 11
  coding_rate: 5
  preamble_length: 16
  sync_word: 18

# --- AS923 ---
#radio:
#  frequency: 923200000
#  tx_power: 14
#  bandwidth: 125000
#  spreading_factor: 8
#  coding_rate: 8
#  preamble_length: 17
#  sync_word: 13380

# ===== COMMON SETTINGS =====
radio:
  crc_enabled: true
  implicit_header: false
```

---

## Troubleshooting

### No packets received

1. **Check frequency matches** other nodes
2. **Check all parameters match** (BW, SF, CR, sync word)
3. **Check TX power** isn't too low
4. **Check antenna** is connected properly
5. **Check logs** for errors

### Poor range

1. **Increase TX power** to maximum allowed
2. **Increase spreading factor** (slower but longer range)
3. **Decrease bandwidth** to 62.5kHz
4. **Improve antenna** placement (higher, no obstacles)
5. **Check cable/connector** losses

### Packets corrupted (CRC errors)

1. **Increase coding rate** for more error correction
2. **Reduce range** or increase TX power
3. **Check for interference** on frequency
4. **Try different spreading factor**

---

## Quick Reference Commands

```bash
# Edit configuration
sudo nano /etc/pymc_repeater/config.yaml

# Restart service
sudo systemctl restart pymc-repeater

# View logs
sudo journalctl -u pymc-repeater -f

# Check current config
cat /etc/pymc_repeater/config.yaml | grep -A 10 "^radio:"

# Test web interface
curl http://localhost:8000
```

---

## Support

For more information:
- **Installation:** See [INSTALL_WM1302.md](INSTALL_WM1302.md)
- **Prerequisites:** See [PREREQUISITES.md](PREREQUISITES.md)
- **Changelog:** See [CHANGELOG.md](CHANGELOG.md)

**Legal Compliance:**
Always check and comply with your local radio regulations regarding:
- Frequency bands
- TX power limits
- Duty cycle restrictions
- Licensing requirements

---

**Configure wisely, transmit legally! 📡**
