import time

class SwipeDetector:
    def __init__(self, min_dist=50, max_time=0.6):
        self.min_dist = min_dist
        self.max_time = max_time
        self._start = {}  # tid -> (x,y,t)

    def start(self, tid, x, y):
        self._start[tid] = (x, y, time.time())

    def move(self, tid, x, y):
        # not needed for basic detection, kept for future (velocity/angle)
        pass

    def end(self, tid, x, y):
        info = self._start.pop(tid, None)
        if not info:
            return None
        x0, y0, t0 = info
        dt = time.time() - t0
        dx = x - x0
        dy = y - y0
        if abs(dx) >= self.min_dist and dt <= self.max_time:
            return (dx, dy, dt)
        return None
