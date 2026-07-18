import time
import board
import busio
import adafruit_vl53l0x

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_vl53l0x.VL53L0X(i2c)

HAND_DETECT_THRESHOLD_MM = 60  # slightly above your tested 50mm, small margin for variation
STABLE_READS_REQUIRED = 5

def wait_for_hand(timeout=15):
    """Returns True if a hand is detected under the flap within timeout, False otherwise."""
    stable_count = 0
    start = time.time()
    while time.time() - start < timeout:
        distance = sensor.range
        if distance <= HAND_DETECT_THRESHOLD_MM:
            stable_count += 1
            if stable_count >= STABLE_READS_REQUIRED:
                return True
        else:
            stable_count = 0
        time.sleep(0.1)
    return False

if __name__ == "__main__":
    print("Waiting for hand under flap...")
    detected = wait_for_hand()
    if detected:
        print("Hand detected! Would trigger flap open here.")
    else:
        print("Timed out — no hand detected.")
