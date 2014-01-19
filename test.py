#!/usr/bin/env python

import pyasicam as cam
import numpy as np
import Image

print "num: ",cam.num
print "name: ", cam.name(0)
print "open: ", cam.open(0)
print "color: ", cam.is_color
print "pixel size: ", cam.pixel_size
print "bayer pattern: ", cam.bayer
c = cam.controls

for i in c:
    print i,":"
    print " auto: ", cam.has_auto(i)
    print " minmax: ", cam.min_max(i)
    print " value: ", cam.value(i)

cam.set("exposure", 100*1000, False)
print cam.value("exposure")
cam.set("exposure", 100*1000, True)
print cam.value("exposure")
cam.set("exposure", 100*1000, False)
print cam.value("exposure")

print "WH: ", cam.WH()
print "Max WH: ", cam.maxWH
print "XY: ", cam.XY()

print "temp: ", cam.temp()
print "dropped: ", cam.dropped()
print "flip: ", cam.get_flip()
cam.set_flip(True, True)
print "flip: ", cam.get_flip()
cam.set_flip(False, False)
print "flip: ", cam.get_flip()

print "im_types: ", cam.im_types
print "bins: ", cam.bins
print "bin: ", cam.bin()

cam.set_XY(100,100)
print "XY: ", cam.XY()

cam.format(1024, 512, 1, "y8")
print cam.WH(), cam.bin(), cam.typ()
cam.format(640, 480, 2, "rgb24")
print cam.WH(), cam.bin(), cam.typ()

cam.set_XY(0,0)
cam.format(cam.maxWH[0], cam.maxWH[1], 1, "rgb24")

cam.start()
im = cam.image()
print im.shape, " ",im.dtype, " ", im.min(), "-", im.max()
IM = Image.fromarray(im)
IM.save("rgb24.png");
cam.stop()

cam.format(cam.maxWH[0], cam.maxWH[1], 1, "y8")

cam.start()
im = cam.image()
print im.shape, " ",im.dtype, " ", im.min(), "-", im.max()
IM = Image.fromarray(im)
IM.save("y8.png");
cam.stop()

cam.format(cam.maxWH[0], cam.maxWH[1], 1, "raw8")

cam.start()
im = cam.image()
print im.shape, " ",im.dtype, " ", im.min(), "-", im.max()
IM = Image.fromarray(im)
IM.save("raw8.png");
cam.stop()

cam.format(cam.maxWH[0], cam.maxWH[1], 1, "raw16")

cam.start()
im = cam.image()
print im.shape, " ",im.dtype, " ", im.min(), "-", im.max()
im = im/256
im = im.astype(np.uint8)
IM = Image.fromarray(im)
IM.save("raw16.png");
cam.stop()

cam.pulse("N", 100)
cam.pulse("E", 100)
cam.pulse("S", 100)
cam.pulse("W", 100)
