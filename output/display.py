from RPLCD.i2c import CharLCD

lcd = None

def init_lcd():
    global lcd
    try:
        lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2)
        lcd.clear()
    except Exception as e:
        print(f"[LCD] Failed to initialize: {e}")
        lcd = None

def show_text(line1, line2=""):
    print(f"[LCD] {line1} | {line2}")  # keep console output for debugging
    if lcd is None:
        return
    try:
        lcd.clear()
        lcd.write_string(line1[:16])  # truncate to fit 16-char width
        if line2:
            lcd.cursor_pos = (1, 0)
            lcd.write_string(line2[:16])
    except Exception as e:
        print(f"[LCD] Write failed: {e}")

init_lcd()
