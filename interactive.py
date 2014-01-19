#!/usr/bin/env python

import pyasicam as cam
import numpy as np
import Tkinter
import Image
import ImageTk

root = Tkinter.Tk()
label = Tkinter.Label(root)
label.pack()
img = None
tkimg = [None]  # This, or something like it, is necessary because if you do not keep a reference to PhotoImage instances, they get garbage collected.

print "num: ",cam.num
print "name: ", cam.name(0)
cam.open(0)

cam.set("exposure", 100*1000, True)
cam.set("gain", 50, True)

cam.format(cam.maxWH[0], cam.maxWH[1], 1, "rgb24")
cam.start()

delay = 10   # in milliseconds
def loopCapture():
    im = cam.image()
    if im != None :
        img = Image.fromarray(im)
        tkimg[0] = ImageTk.PhotoImage(img)
        label.config(image=tkimg[0])
        root.update_idletasks()
    root.after(delay, loopCapture)

loopCapture()
root.mainloop()
