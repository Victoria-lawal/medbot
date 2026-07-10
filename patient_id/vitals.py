import smbus2
import time
import numpy as np
from collections import deque

MAX30102_ADDR = 0x57
REG_INTR_ENABLE_1 = 0x02
REG_FIFO_WR_PTR = 0x04
REG_OVF_COUNTER = 0x05
REG_FIFO_RD_PTR = 0x06
REG_FIFO_DATA = 0x07
REG_MODE_CONFIG = 0x09
REG_SPO2_CONFIG = 0x0A
REG_LED1_PA = 0x0C
REG_LED2_PA = 0x0D

bus = smbus2.SMBus(1)

def write_reg(reg, value):
    bus.write_byte_data(MAX30102_ADDR, reg, value)

def read_reg(reg):
    return bus.read_byte_data(MAX30102_ADDR, reg)

def setup_sensor():
    write_reg(REG_MODE_CONFIG, 0x40)
    time.sleep(0.1)
    write_reg(REG_INTR_ENABLE_1, 0x00)
    write_reg(REG_FIFO_WR_PTR, 0x00)
    write_reg(REG_OVF_COUNTER, 0x00)
    write_reg(REG_FIFO_RD_PTR, 0x00)
    write_reg(REG_SPO2_CONFIG, 0x27)
    write_reg(REG_LED1_PA, 0x24)
    write_reg(REG_LED2_PA, 0x24)
    write_reg(REG_MODE_CONFIG, 0x03)

def read_fifo():
    data = bus.read_i2c_block_data(MAX30102_ADDR, REG_FIFO_DATA, 6)
    red = (data[0] << 16 | data[1] << 8 | data[2]) & 0x03FFFF
    ir = (data[3] << 16 | data[4] << 8 | data[5]) & 0x03FFFF
    return red, ir

def detect_finger(ir_value, threshold=20000):
    """Simple presence check — baseline IR with no finger is ~3000, with finger it jumps well above this."""
    return ir_value > threshold

def calc_bpm(ir_window, sample_rate=25):
    ir_arr = np.array(ir_window)
    baseline = np.convolve(ir_arr, np.ones(15)/15, mode='same')
    ac_signal = ir_arr - baseline

    edge_trim = 15
    ac_signal = ac_signal[edge_trim:-edge_trim]

    std = np.std(ac_signal)
    print(f"[DEBUG] AC signal std: {std:.2f}, min: {ac_signal.min():.2f}, max: {ac_signal.max():.2f}")

    min_distance_samples = int(sample_rate * 0.4)  # ~150 bpm max, refuse anything faster
    threshold = std * 1.2  # stricter amplitude requirement

    peaks = []
    last_peak = -min_distance_samples
    for i in range(1, len(ac_signal) - 1):
        if (ac_signal[i] > ac_signal[i-1] and ac_signal[i] > ac_signal[i+1]
                and ac_signal[i] > threshold
                and (i - last_peak) >= min_distance_samples):
            peaks.append(i)
            last_peak = i

    print(f"[DEBUG] Peaks found: {len(peaks)} at indices {peaks}")

    if len(peaks) < 2:
        return None

    intervals = np.diff(peaks) / sample_rate
    avg_interval = np.mean(intervals)
    print(f"[DEBUG] Intervals (sec): {intervals}, avg: {avg_interval:.3f}")

    if avg_interval <= 0:
        return None
    bpm = 60.0 / avg_interval
    print(f"[DEBUG] Raw BPM before range check: {bpm:.1f}")
    if 40 <= bpm <= 180:
        return round(bpm, 1)
    return None

def calc_spo2(red_window, ir_window):
    """Standard empirical Red/IR ratio-of-ratios approximation."""
    red_arr = np.array(red_window)
    ir_arr = np.array(ir_window)

    red_dc = np.mean(red_arr)
    ir_dc = np.mean(ir_arr)
    red_ac = np.std(red_arr)
    ir_ac = np.std(ir_arr)

    if red_dc == 0 or ir_dc == 0 or ir_ac == 0:
        return None

    r_ratio = (red_ac / red_dc) / (ir_ac / ir_dc)
    spo2 = 110 - 25 * r_ratio  # empirical approximation, not clinically calibrated
    spo2 = max(0, min(100, spo2))
    return round(spo2, 1)

def read_vitals(duration=10, sample_rate=25, settle_time=2):
    """Collects samples for `duration` seconds (plus a settle_time discard period), returns (bpm, spo2)."""
    setup_sensor()
    ir_window = deque(maxlen=duration * sample_rate)
    red_window = deque(maxlen=duration * sample_rate)

    start = time.time()
    finger_detected_count = 0
    total_samples = 0

    while time.time() - start < (duration + settle_time):
        red, ir = read_fifo()
        elapsed = time.time() - start
        total_samples += 1
        if detect_finger(ir):
            finger_detected_count += 1
            if elapsed >= settle_time:  # discard the settling period
                ir_window.append(ir)
                red_window.append(red)
        time.sleep(1.0 / sample_rate)

    if total_samples == 0 or finger_detected_count / total_samples < 0.7:
        return None, None
    if len(ir_window) < sample_rate * 3:
        return None, None

    bpm = calc_bpm(list(ir_window), sample_rate)
    spo2 = calc_spo2(list(red_window), list(ir_window))
    return bpm, spo2

if __name__ == "__main__":
    print("Place your finger on the sensor. Settling, then reading for 10 seconds...")
    bpm, spo2 = read_vitals(duration=10, sample_rate=25, settle_time=4)
    print(f"BPM: {bpm}, SpO2: {spo2}")
