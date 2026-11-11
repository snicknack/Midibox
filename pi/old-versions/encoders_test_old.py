# encoders_test.py - uses the new polling driver + ADS1115 (optional)
import sys, os, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from midio.encoders_sx1509_driver import SX1509Encoders

# If you want ADS values alongside, uncomment the next two lines:
# from midio.ads1115_mod import ADS1115Reader
# ads = ADS1115Reader(addr=0x48, rate_hz=100, channels=(0,1,2,3))

ENCODER_TO_WIDGET = {0:"uic_t1Arc1",1:"uic_t1Arc2",2:"uic_t1Arc3",3:"uic_t1Arc4",4:"uic_t1Arc5Tempo"}
params = {"uic_t1Arc1":64,"uic_t1Arc2":64,"uic_t1Arc3":64,"uic_t1Arc4":64,"uic_t1Arc5Tempo":120}

def apply_delta(w, d):
    if w == "uic_t1Arc5Tempo":
        params[w] = max(20, min(300, params[w] + d))
    else:
        params[w] = max(0, min(127, params[w] + d))
    print(f"[GUI] {w} -> {params[w]}")

def main():
    enc = SX1509Encoders(addr=0x3E, pairs=[(0,1),(3,4),(6,7),(9,10),(12,13)], poll_hz=500).begin()
    # ads.begin()  # if using ADS

    print("Rotate encoders… Ctrl+C to exit.")
    try:
        while True:
            for idx, delta, _ in enc.read_and_zero():
                w = ENCODER_TO_WIDGET.get(idx)
                if w:
                    apply_delta(w, delta)
                else:
                    print(f"[ENC] {idx}: Δ{delta}")
            # print("ADS:", ads.values_cc)  # if using ADS
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        enc.close()
        # ads.close()
        print("Done.")

if __name__ == "__main__":
    main()
