import time
import numpy as np
import mss
import serial
from serial.tools import list_ports

NUM_LEDS = 34
FPS = 30
BRIGHTNESS = 0.80
SMOOTHING = 0.5
USE_GAMMA = True
GAMMA = 2.2

R_GAIN = 1.0
G_GAIN = 1.0
B_GAIN = 1.0

BLACK_CUTOFF = 12

def find_arduino_port():
    ports = list_ports.comports()
    for p in ports:
        if "arduino" in p.description.lower():
            return p.device
    return ports[0].device

def apply_gamma(v):
    if not USE_GAMMA:
        return v
    x = max(0.0, min(1.0, v / 255.0))
    x = x ** (1.0 / GAMMA)
    return int(x * 255 + 0.5)

def main():
    port = find_arduino_port()
    ser = serial.Serial(port, 115200)
    time.sleep(2)

    sct = mss.mss()
    monitor = sct.monitors[1]

    prev = np.zeros((NUM_LEDS, 3))
    frame_time = 1.0 / FPS

    while True:
        start = time.time()

        img = np.array(sct.grab(monitor))
        h, w, _ = img.shape

        band = img[int(h * 0.3):int(h * 0.7), :, :]
        colors = np.zeros((NUM_LEDS, 3))

        for i in range(NUM_LEDS):
            x0 = int(i * w / NUM_LEDS)
            x1 = int((i + 1) * w / NUM_LEDS)
            seg = band[:, x0:x1, :]

            b = np.mean(seg[:, :, 0])
            g = np.mean(seg[:, :, 1])
            r = np.mean(seg[:, :, 2])

            colors[i] = (
                r * BRIGHTNESS * R_GAIN,
                g * BRIGHTNESS * G_GAIN,
                b * BRIGHTNESS * B_GAIN
            )

        colors = prev * SMOOTHING + colors * (1 - SMOOTHING)
        prev = colors

        frame = bytearray()
        for i in range(NUM_LEDS):
            idx = NUM_LEDS - 1 - i
            r, g, b = colors[idx]
            avg = (r + g + b) / 3

            if avg < BLACK_CUTOFF:
                frame.extend((0, 0, 0))
            else:
                frame.extend((
                    apply_gamma(int(r)),
                    apply_gamma(int(g)),
                    apply_gamma(int(b))
                ))

        ser.write(frame)
        time.sleep(max(0, frame_time - (time.time() - start)))

if __name__ == "__main__":
    main()
