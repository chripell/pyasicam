#!/usr/bin/env python
# car.py [t start] [t end] [t n] [gain] [mode: raw8, raw16]

import pyasicam as cam
import numpy as np
import matplotlib.pyplot as plt
import sys
import Image

def setup(mode, exp, gain):
    cam.stop()
    cam.format(cam.maxWH[0], cam.maxWH[1], 1, mode)
    cam.set("exposure", exp)
    cam.set("gain", gain)
    cam.set_XY(0,0)
    cam.start()
    # flush buffer
    for i in xrange(5):
        cam.image()

cam.open(0)

tstart = int(sys.argv[1])
tend = int(sys.argv[2])
tn = int(sys.argv[3])
gain = int(sys.argv[4])
mode = sys.argv[5]
tstep = (tend - tstart) / (tn - 1)

times = []
sigma_dn = []

for t in np.linspace(tstart, tend, tn):
    times.append(t)
    setup(mode, int(t), gain)
    p1 = cam.image().astype(np.float)
    p2 = cam.image().astype(np.float)
    sigma = np.std(p1 - p2) / np.sqrt(2)
    print t, " ", sigma

#raw_input("Press Enter to continue...")
