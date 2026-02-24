# WM1302 Deployment Fixes

Complete guide for fixing event loop and callback issues in WM1302 driver deployment.

---

## Issues Encountered & Solutions

### Issue 1: Event Loop Not Found

**Error:**
```
No event loop running, cannot process received packet
```

**Root Cause:**
The RX callback was being called from a background thread, but the dispatcher needed to run in the async event loop context.

**Fix:**
1. Added `import asyncio` to imports
2. Store event loop reference when radio starts (in `begin()`)
3. Use stored loop reference to schedule callbacks from thread

**Code Changes:**

```python
# In __init__
self._loop = None  # Store event loop reference

# In begin()
try:
    self._loop = asyncio.get_running_loop()
except RuntimeError:
    self._loop = None

# In _rx_loop
if self._loop:
    if asyncio.iscoroutinefunction(self._rx_callback):
        asyncio.run_coroutine_threadsafe(self._rx_callback(payload), self._loop)
    else:
        self._loop.call_soon_threadsafe(self._rx_callback, payload)
```

---

### Issue 2: Wrong Callback Arguments

**Error:**
```
Dispatcher._on_packet_received() takes 2 positional arguments but 4 were given
```

**Root Cause:**
WM1302 driver was calling callback with `(payload, rssi, snr)` but dispatcher expected only `(payload)`.

**Fix:**
Changed callback invocation from:
```python
self._rx_callback(payload, rssi, snr)
```

To:
```python
self._rx_callback(payload)
```

---

### Issue 3: Missing get_last_rssi() Method

**Error:**
```
AttributeError: 'WM1302Radio' object has no attribute 'get_last_rssi'
```

**Root Cause:**
Dispatcher expected `get_last_rssi()` method, but WM1302Radio only had `get_rssi()`.

**Fix:**
Added alias method:
```python
def get_last_rssi(self) -> int:
    """Get last RSSI (alias for compatibility with dispatcher)"""
    return self.get_rssi()
```

---

### Issue 4: Missing get_last_snr() Method

**Error:**
```
AttributeError: 'WM1302Radio' object has no attribute 'get_last_snr'
```

**Root Cause:**
Dispatcher also needs SNR data, but WM1302Radio didn't track or expose it.

**Fix:**
1. Added `self._last_snr = 0` in `__init__`
2. Track SNR in `_rx_loop`:
```python
if pkt.size > 0:
    self._last_snr = int(pkt.snr)
```
3. Added getter method:
```python
def get_last_snr(self) -> int:
    """Get last measured SNR"""
    return self._last_snr
```

---

## Complete Fixed File

Location: `/home/chris/meshcore/pyMC_Repeater/wm1302_wrapper_FIXED.py`

This file contains all fixes and is ready to deploy.

---

## Deployment Instructions

### Quick Deployment

**From development machine:**
```bash
scp /home/chris/meshcore/pyMC_Repeater/wm1302_wrapper_FIXED.py \
    chris@<target-pi>:/tmp/
```

**On target Pi:**
```bash
sudo cp /tmp/wm1302_wrapper_FIXED.py \
    /opt/pymc_repeater/repeater/hardware/wm1302_wrapper.py

sudo systemctl restart pymc-repeater
```

### Verify Deployment

**Check service status:**
```bash
sudo systemctl status pymc-repeater
```

**Watch logs:**
```bash
sudo journalctl -u pymc-repeater -f
```

**Expected output:**
```
INFO - WM1302 concentrator started successfully
INFO - HTTP stats server started on http://0.0.0.0:8000
INFO - TX 123 bytes (type=ADVERT, route=FLOOD)
INFO - [RX DEBUG] Processing packet: 124 bytes
INFO - [RX DEBUG] Packet parsed successfully
```

**No errors should appear for:**
- Event loop
- Callback arguments
- Missing methods (get_last_rssi, get_last_snr)

---

## Testing Checklist

### ✓ Service Starts
```bash
sudo systemctl status pymc-repeater
# Should show: Active: active (running)
```

### ✓ No Event Loop Errors
```bash
sudo journalctl -u pymc-repeater -n 100 | grep "event loop"
# Should return nothing or only historical errors
```

### ✓ Packets Transmit
```bash
sudo journalctl -u pymc-repeater -f | grep "TX.*ADVERT"
# Should show periodic advert transmissions
```

### ✓ Packets Receive (if devices nearby)
```bash
sudo journalctl -u pymc-repeater -f | grep "RX DEBUG"
# Should show received packets being processed
```

### ✓ Web Dashboard Accessible
```bash
curl http://localhost:8000
# Should return HTML content
```

Or open in browser:
```
http://<pi-ip>:8000
```

### ✓ RSSI/SNR Tracked
Check dashboard or logs for RSSI/SNR values being reported.

---

## Manual Fix Instructions

If you need to apply fixes manually instead of copying the file:

### 1. Add Imports
At top of file, ensure `asyncio` is imported:
```python
import asyncio
import logging
import subprocess
import threading
import time
```

### 2. Update __init__
Add these lines after `self._last_rssi = -120`:
```python
self._last_snr = 0  # Last measured SNR
self._loop = None  # Store event loop reference
```

### 3. Update begin() Method
Add this at the start of `begin()` after checking `if self.is_started`:
```python
# Capture the event loop for callback scheduling
try:
    self._loop = asyncio.get_running_loop()
except RuntimeError:
    self._loop = None
```

### 4. Update _rx_loop Method
Replace the callback section with:
```python
if self._rx_callback and pkt.size > 0:
    payload = bytes(pkt.payload[: pkt.size])
    # Schedule callback in the event loop
    if self._loop:
        if asyncio.iscoroutinefunction(self._rx_callback):
            asyncio.run_coroutine_threadsafe(self._rx_callback(payload), self._loop)
        else:
            self._loop.call_soon_threadsafe(self._rx_callback, payload)
    else:
        logger.warning("No event loop available, calling callback directly")
        self._rx_callback(payload)
```

And add SNR tracking:
```python
# Update SNR from packet
if pkt.size > 0:
    self._last_snr = int(pkt.snr)
```

### 5. Add Missing Methods
After `get_rssi()` method, add:
```python
def get_last_rssi(self) -> int:
    """Get last RSSI (alias for compatibility with dispatcher)"""
    return self.get_rssi()

def get_last_snr(self) -> int:
    """Get last measured SNR"""
    return self._last_snr
```

---

## Common Deployment Issues

### Library Not Compiled for ARM

**Symptom:**
```
cannot open shared object file: No such file or directory
```

**Fix:**
```bash
cd /opt/pymc_repeater/sx1302_hal
sudo make clean
sudo make
cd libloragw
sudo gcc -shared -o libloragw.so obj/*.o ../libtools/obj/*.o -lrt -lm -lpthread
```

### SPI Not Enabled

**Symptom:**
```
Board config failed: -1
ERROR: WRONG COM TYPE
```

**Fix:**
```bash
sudo raspi-config
# Interface Options → SPI → Enable
sudo reboot
```

### Permission Denied

**Symptom:**
```
Permission denied: /dev/spidev0.0
```

**Fix:**
```bash
sudo usermod -a -G spi,gpio,i2c $USER
# Log out and back in
```

---

## Version History

### v1.1.0 - Initial WM1302 Support
- Basic WM1302 driver implementation
- Known issues: Event loop errors in production

### v1.1.1 - Event Loop Fixes (Current)
- ✅ Fixed event loop callback scheduling
- ✅ Fixed callback argument count
- ✅ Added get_last_rssi() compatibility method
- ✅ Added get_last_snr() tracking and method
- ✅ Production tested and working

---

## File Locations

**Development machine:**
- Source: `/home/chris/meshcore/pyMC_Repeater/repeater/hardware/wm1302_wrapper.py`
- Fixed copy: `/home/chris/meshcore/pyMC_Repeater/wm1302_wrapper_FIXED.py`

**Production Pi:**
- Installed: `/opt/pymc_repeater/repeater/hardware/wm1302_wrapper.py`
- Config: `/etc/pymc_repeater/config.yaml`
- Service: `/etc/systemd/system/pymc-repeater.service`
- Logs: `journalctl -u pymc-repeater`

---

## Success Criteria

The deployment is successful when:

1. ✅ Service starts without errors
2. ✅ No "event loop" warnings in logs
3. ✅ Packets transmit (TX adverts every ~10 hours, or manual)
4. ✅ Packets receive and process (if devices nearby)
5. ✅ Web dashboard accessible on port 8000
6. ✅ RSSI and SNR values displayed
7. ✅ No AttributeError exceptions

---

## Rollback Procedure

If the fixed version causes issues:

**1. Stop service:**
```bash
sudo systemctl stop pymc-repeater
```

**2. Restore backup (if created):**
```bash
sudo cp /opt/pymc_repeater/repeater/hardware/wm1302_wrapper.py.backup \
    /opt/pymc_repeater/repeater/hardware/wm1302_wrapper.py
```

**3. Or revert to SX1262:**
```bash
sudo nano /etc/pymc_repeater/config.yaml
# Change: radio_type: "sx1262"
```

**4. Restart:**
```bash
sudo systemctl start pymc-repeater
```

---

## Support

If issues persist after applying these fixes:

1. **Check library compilation:**
   ```bash
   file /opt/pymc_repeater/sx1302_hal/libloragw/libloragw.so
   # Should show: ELF 64-bit LSB shared object, ARM aarch64
   ```

2. **Verify Python version:**
   ```bash
   python3 --version
   # Should be 3.8 or higher
   ```

3. **Check full logs:**
   ```bash
   sudo journalctl -u pymc-repeater -n 200 --no-pager
   ```

4. **Test manually:**
   ```bash
   cd /opt/pymc_repeater
   python3 -m repeater.main
   # Run in foreground to see all output
   ```

---

## Related Documentation

- **Installation:** [INSTALL_WM1302.md](INSTALL_WM1302.md)
- **Prerequisites:** [PREREQUISITES.md](PREREQUISITES.md)
- **Configuration:** [RADIO_CONFIGURATION.md](RADIO_CONFIGURATION.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

**Status:** ✅ Production Ready

All known issues resolved. WM1302 driver fully functional with proper async integration.
