from RPLCD.i2c import CharLCD
import atexit
import threading
import time

lcd = None
_cycle_thread = None
_cycle_stop = threading.Event()

def init_lcd():
    global lcd
    try:
        lcd = CharLCD('PCF8574', 0x27, cols=16, rows=2)
        lcd.clear()
    except Exception as e:
        print(f"[LCD] Failed to initialize: {e}")
        lcd = None

def _write_lines(line1, line2=""):
    if lcd is None:
        return
    try:
        lcd.clear()
        lcd.write_string(line1[:16])
        if line2:
            lcd.cursor_pos = (1, 0)
            lcd.write_string(line2[:16])
    except Exception as e:
        print(f"[LCD] Write failed: {e}")

def show_text(line1, line2=""):
    """Shows a single static message (stops any ongoing cycling)."""
    _stop_cycle()
    print(f"[LCD] {line1} | {line2}")
    _write_lines(line1, line2)

def show_cycling_screens(screens, interval=2.5):
    """Cycles through a list of (line1, line2) tuples on the LCD, looping until replaced."""
    _stop_cycle()
    print(f"[LCD] Cycling: {screens}")

    global _cycle_thread
    _cycle_stop.clear()

    def _cycle():
        while not _cycle_stop.is_set():
            for line1, line2 in screens:
                if _cycle_stop.is_set():
                    return
                _write_lines(line1, line2)
                _cycle_stop.wait(interval)

    _cycle_thread = threading.Thread(target=_cycle, daemon=True)
    _cycle_thread.start()

def _stop_cycle():
    global _cycle_thread
    if _cycle_thread is not None and _cycle_thread.is_alive():
        _cycle_stop.set()
        _cycle_thread.join(timeout=1)
    _cycle_thread = None

def cleanup_lcd():
    _stop_cycle()
    if lcd is not None:
        try:
            lcd.clear()
        except Exception:
            pass

atexit.register(cleanup_lcd)
init_lcd()
