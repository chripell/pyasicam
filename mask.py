#!/usr/bin/env python
# car.py [exp] [gain] [mode: raw8, raw16, y8, rgb24]

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

exp = int(sys.argv[1])
gain = int(sys.argv[2])
mode = sys.argv[3]

setup(mode, exp, gain)
n = 100
im = cam.image().astype(np.float)
for i in xrange(n - 1):
    im += cam.image()
im /= n
if mode == "raw16":
    im /= 256;
elif mode == "rgb24":
    im = im.mean(axis = 2)
im = im.astype(np.uint8)
median = np.median(im)
std = im.std()
minv = im.min()
maxv = im.max()
print minv, " < ", im.mean(), " / ", median, " > ", maxv, " : ", std
IM = Image.fromarray(im)
IM.save("im_%s.png"%(mode));

lim = median + (maxv - median ) / 10
print "-------------- %d"%(lim)
ind = np.transpose(np.nonzero(im > lim))
n = 0
for x in ind:
    print "%d,%d=%d"%(x[0],x[1],im[x[0],x[1]])
    n += 1
print "-------------- %d"%(n)

