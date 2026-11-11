python3 - <<'PY'
import midio.encoders_sx1509_poll as m
print("Loaded from:", m.__file__)
print("Available:", [n for n in dir(m) if n.startswith('SX')])
PY
