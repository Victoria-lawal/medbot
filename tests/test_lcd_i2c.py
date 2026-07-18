from RPLCD.i2c import CharLCD
import time

# Change 0x27 to 0x3F if i2cdetect shows a different address
lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2)

lcd.clear()
lcd.write_string("MedBot Online")
lcd.cursor_pos = (1, 0)
lcd.write_string("Patient ID: OK")

time.sleep(5)
lcd.clear()
