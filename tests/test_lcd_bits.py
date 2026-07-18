import smbus2
import time

I2C_ADDR = 0x27
bus = smbus2.SMBus(1)

# Test each bit position individually - one of these should visibly affect the LCD
for bit_position in range(8):
    value = 1 << bit_position
    print(f"Testing bit {bit_position} (value {value})...")
    bus.write_byte(I2C_ADDR, value)
    time.sleep(2)
    bus.write_byte(I2C_ADDR, 0x00)
    time.sleep(0.5)
