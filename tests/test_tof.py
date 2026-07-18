import time
import board
import busio
import adafruit_vl53l0x

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_vl53l0x.VL53L0X(i2c)

print("Reading distance (Ctrl+C to stop)...")
try:
    while True:
        print(f"Distance: {sensor.range} mm")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Stopping...")
