#!/usr/bin/python3

import os
import pyasicam as pc
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk, Gio, GObject


class Camera(pc.Camera):

    def __init__(self, i):
        super().__init__(i)
        self.mean = 1
        self.done = 0
        self.OpenCamera()
        self.InitCamera()
        self.set_exposure_ms(1000)
        caps = self.GetCameraProperty()
        self.SetROIFormat(caps.MaxWidth, caps.MaxHeight, 1, pc.IMG_Y8)
        # Trick to make ASI120MC work for short exposures.
        # if self.GetCameraProperty().IsUSB3Camera == 0:
        #    self.SetControlValue(pc.BANDWIDTHOVERLOAD, 20, False)

    def capture(self):
        self.StartExposure(False)

    def get_image(self):
        st = self.GetExpStatus()
        if st == pc.EXP_FAILED:
            # raise RuntimeError("Exposure failed")
            print("Exposure failed")
            self.capture()
            return None
        if st == pc.EXP_IDLE:
            raise RuntimeError("Exposure not started")
        if self.GetExpStatus() == pc.EXP_WORKING:
            return None
        img = self.GetDataAfterExp()
        if self.mean <= 1:
            return img

    def set_exposure_ms(self, ms):
        self.SetControlValue(pc.EXPOSURE, int(ms*1000), False)

    def get_exposure_ms(self):
        return self.GetControlValue(pc.EXPOSURE)[0] / 1000.0

    def set_gain(self, gain):
        self.SetControlValue(pc.GAIN, gain, False)

    def get_gain(self):
        return self.GetControlValue(pc.GAIN)[0]


class Mainwindow(Gtk.Window):

    def __init__(self, cam, *args, **kwargs):
        Gtk.Window.__init__(
            self, default_width=800, default_height=600,
            title="PYASICAM", *args, **kwargs)
        self.cam = cam
        self.pix = None
        cam.capture()
        scrolledImage = Gtk.ScrolledWindow()
        self.image = Gtk.DrawingArea()
        self.image.connect("draw", self.draw)
        self.image.connect("configure-event", self.configure)
        scrolledImage.add(self.image)
        mainHBox = Gtk.HBox()
        mainHBox.pack_start(scrolledImage, True, True, 0)
        controlsBox = Gtk.VBox()
        mainHBox.pack_start(controlsBox, False, False, 0)
        self.add_controls(controlsBox)
        self.add(mainHBox)
        self.connect("delete-event", Gtk.main_quit)
        self.periodic = GLib.timeout_add(100, self.get_image)
        self.show_all()

    def get_image(self):
        im = self.cam.get_image()
        if im is not None:
            self.publish_image(im)
            self.cam.capture()
        self.periodic = GLib.timeout_add(100, self.get_image)

    def publish_image(self, im):
        loader = GdkPixbuf.PixbufLoader.new_with_type('pnm')
        loader.write(b'P5\n%d %d\n255\n' % (im.shape[1], im.shape[0]))
        loader.write(im.tobytes())
        loader.close()
        self.pix = loader.get_pixbuf()
        self.image.set_size_request(im.shape[1], im.shape[0])
        self.image.queue_draw()

    def draw(self, w, cr):
        if not self.pix:
            return
        Gdk.cairo_set_source_pixbuf(cr, self.pix, 0, 0)
        cr.paint()

    def configure(self, w, ev):
        if not self.pix:
            return
        self.image.queue_draw()

    def create_text_control(self, text, ini, cb):
        box = Gtk.HBox()
        label = Gtk.Label()
        label.set_markup(text)
        label.set_justify(Gtk.Justification.RIGHT)
        box.pack_start(label, False, False, 0)
        entry = Gtk.Entry()
        entry.set_text(ini)
        entry.connect("activate", cb)
        box.pack_start(entry, True, False, 0)
        return box

    def add_controls(self, box):
        exp_ms = self.create_text_control(
            "Exposure (ms):",
            "%.2f" % self.cam.get_exposure_ms(),
            self.set_exposure_ms)
        box.pack_start(exp_ms, False, False, 0)
        gain = self.create_text_control(
            "Gain:",
            "%d" % self.cam.get_gain(),
            self.set_gain)
        box.pack_start(gain, False, False, 0)

    def set_exposure_ms(self, e):
        try:
            self.cam.set_exposure_ms(float(e.get_text()))
        except:
            pass
        e.set_text("%.2f" % self.cam.get_exposure_ms())

    def set_gain(self, e):
        try:
            self.cam.set_gain(int(e.get_text()))
        except:
            pass
        e.set_text("%d" % self.cam.get_gain())


if len(sys.argv) < 2:
    print("Usage: %s [list/camera no.]" % sys.argv[0])
    sys.exit(1)

n = pc.GetNumOfConnectedCameras()
if sys.argv[1] == "list":
    for i in range(n):
        c = pc.Camera(i)
        prop = c.GetCameraProperty()
        print("%d: %s" % (i, prop.Name.decode("utf-8")))
    sys.exit(0)

cam = Camera(int(sys.argv[1]))
window = Mainwindow(cam)
Gtk.main()
