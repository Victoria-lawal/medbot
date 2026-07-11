import glob
import time

def find_sensor():
    devices = glob.glob('/sys/bus/w1/devices/28-*')
    if not devices:
        return None
    return devices[0] + '/w1_slave'

def read_temp_raw(sensor_path):
    with open(sensor_path, 'r') as f:
        return f.readlines()

def read_temperature(retries=3):
    sensor_path = find_sensor()
    if sensor_path is None:
        return None

    for _ in range(retries):
        lines = read_temp_raw(sensor_path)
        if lines[0].strip()[-3:] == 'YES':
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos + 2:]
                temp_c = float(temp_string) / 1000.0
                return round(temp_c, 1)
        time.sleep(0.2)  # brief retry delay if CRC failed
    return None

if __name__ == "__main__":
    temp = read_temperature()
    if temp is not None:
        print(f"Temperature: {temp}°C")
    else:
        print("Could not get a valid temperature reading")
