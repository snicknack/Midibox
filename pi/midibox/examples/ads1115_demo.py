import os, time
from midibox.io.ads1115_reader import ADS1115Reader

CAL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "ads1115_cal.json")

def main():
    ads = ADS1115Reader(address=0x48, channels=(0,1,2,3), ema_alpha=0.2, cal_path=CAL_PATH)
    print("Reading ADS1115 with calibration… Ctrl+C to quit.")
    last = {}
    names = {0:"Pitch", 1:"Mod", 2:"FaderA", 3:"FaderB"}
    while True:
        cc = ads.read_cc()  # already calibrated 0..127
        for ch, val in cc.items():
            if last.get(ch) != val:
                print(f"{names.get(ch, ch)}: {val:3d}")
        last = cc
        time.sleep(0.01)

if __name__ == "__main__":
    main()
