try:
    from smbus import SMBus
except ImportError:
    from smbus2 import SMBus

I2C_BUS = 1
FT_ADDR = 0x38
REG_TD_STATUS = 0x02

class Touch:
    def __init__(self, rotation_180=True):
        self.bus = SMBus(I2C_BUS)
        # raw panel reports 0..239, 0..319 on your module
        self.RAW_MAX_X = 239
        self.RAW_MAX_Y = 319
        # For rotation=180 on display, invert both axes
        self.SWAP_XY  = False
        self.INVERT_X = rotation_180
        self.INVERT_Y = rotation_180

    def read_touches(self):
        """Return up to two touches: [{'id','x','y','event'}]"""
        d1 = self.bus.read_i2c_block_data(FT_ADDR, REG_TD_STATUS, 7)
        n = d1[0] & 0x0F
        out = []
        if n >= 1:
            xh, xl, yh, yl = d1[1], d1[2], d1[3], d1[4]
            event = (xh >> 6) & 0x03
            x = ((xh & 0x0F) << 8) | xl
            y = ((yh & 0x0F) << 8) | yl
            tid = d1[5] & 0x0F
            out.append({"id": tid, "x": x, "y": y, "event": event})
        if n >= 2:
            d2 = self.bus.read_i2c_block_data(FT_ADDR, 0x09, 6)
            xh, xl, yh, yl = d2[0], d2[1], d2[2], d2[3]
            event = (xh >> 6) & 0x03
            x = ((xh & 0x0F) << 8) | xl
            y = ((yh & 0x0F) << 8) | yl
            tid = d2[4] & 0x0F
            out.append({"id": tid, "x": x, "y": y, "event": event})
        return out

    def map_to_screen(self, tx, ty, W, H):
        # optional swap
        if self.SWAP_XY:
            tx, ty = ty, tx
        # flips for 180°
        if self.INVERT_X:
            tx = self.RAW_MAX_X - tx
        if self.INVERT_Y:
            ty = self.RAW_MAX_Y - ty
        tx = max(0, min(self.RAW_MAX_X, tx))
        ty = max(0, min(self.RAW_MAX_Y, ty))
        sx = int(tx * (W-1) / self.RAW_MAX_X)
        sy = int(ty * (H-1) / self.RAW_MAX_Y)
        return sx, sy
