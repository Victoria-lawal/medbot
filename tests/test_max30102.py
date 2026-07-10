import smbus2
import time

MAX30102_ADDR = 0x57

# Register addresses
REG_INTR_STATUS_1 = 0x00
REG_INTR_ENABLE_1 = 0x02
REG_FIFO_WR_PTR = 0x04
REG_OVF_COUNTER = 0x05
REG_FIFO_RD_PTR = 0x06
REG_FIFO_DATA = 0x07
REG_MODE_CONFIG = 0x09
REG_SPO2_CONFIG = 0x0A
REG_LED1_PA = 0x0C  # Red LED
REG_LED2_PA = 0x0D  # IR LED

bus = smbus2.SMBus(1)

def write_reg(reg, value):
    bus.write_byte_data(MAX30102_ADDR, reg, value)

def read_reg(reg):
    return bus.read_byte_data(MAX30102_ADDR, reg)

def setup_sensor():
    write_reg(REG_MODE_CONFIG, 0x40)  # reset
    time.sleep(0.1)
    write_reg(REG_INTR_ENABLE_1, 0x00)
    write_reg(REG_FIFO_WR_PTR, 0x00)
    write_reg(REG_OVF_COUNTER, 0x00)
    write_reg(REG_FIFO_RD_PTR, 0x00)
    write_reg(REG_SPO2_CONFIG, 0x27)  # SpO2 mode, 100 samples/sec, 411us pulse width
    write_reg(REG_LED1_PA, 0x24)  # Red LED current
    write_reg(REG_LED2_PA, 0x24)  # IR LED current
    write_reg(REG_MODE_CONFIG, 0x03)  # SpO2 mode

def read_fifo():
    data = bus.read_i2c_block_data(MAX30102_ADDR, REG_FIFO_DATA, 6)
    red = (data[0] << 16 | data[1] << 8 | data[2]) & 0x03FFFF
    ir = (data[3] << 16 | data[4] << 8 | data[5]) & 0x03FFFF
    return red, ir

def main():
    part_id = read_reg(0xFF)
    print(f"Part ID: {hex(part_id)} (should be 0x15 for MAX30102)")

    setup_sensor()
    print("Sensor configured. Place your finger on it...")
    print("Reading raw IR/Red values (Ctrl+C to stop):")
    try:
        while True:
            red, ir = read_fifo()
            print(f"Red: {red}  IR: {ir}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    main()