import sys, pathlib, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from leds.max7219_display import Max7219Display

def step_sequencer_demo():
    disp = Max7219Display(num_matrices=4, brightness=3)
    pattern = [1,0,0,1,0,1,0,0,1,0,1,0,0,1,0,0]
    playhead = 0
    try:
        disp.scroll_text("SEQ DEMO  ")
        while True:
            cols = []
            for i in range(16):
                cols.append(8 if i == playhead else (5 if pattern[i] else 0))
            while len(cols) < disp.cols:
                cols.append(0)
            disp.draw_columns(cols)
            time.sleep(0.12)
            playhead = (playhead + 1) % 16
    except KeyboardInterrupt:
        pass
    finally:
        disp.clear()

if __name__ == "__main__":
    d = Max7219Display(num_matrices=4, brightness=8)
    try:
        d.scroll_text("MIDIBOX HELLO  ")
        for v in [0.0, 0.25, 0.5, 0.75, 1.0]:
            d.draw_bargraph(v)
            time.sleep(0.5)
    finally:
        d.clear()
    step_sequencer_demo()
