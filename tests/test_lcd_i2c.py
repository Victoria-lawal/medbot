from RPLCD.i2c import CharLCD
import time

lcd = CharLCD(
    i2c_expander='PCF8574',
    address=0x27,
    port=1,
    cols=16, rows=2,
    dotsize=8,
    charmap='A00',
    auto_linebreaks=True
)

lcd.clear()
time.sleep(0.5)
lcd.write_string("MedBot Online")
lcd.cursor_pos = (1, 0)
lcd.write_string("Patient ID: OK")

time.sleep(5)
lcd.clear()
