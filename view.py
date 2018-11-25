#!/usr/bin/python3

import datetime
import os
import pyasicam as pc
import sys
import numpy as np
import cairo

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk, Gio, GObject


def gamma_stretch(im, gamma):
    if im.dtype != np.float:
        im = im.astype(np.float)
    im /= 255.0
    im = im ** gamma
    return im * 255.0


class Camera(pc.Camera):

    def __init__(self, i):
        super().__init__(i)
        self.mean = 1
        self.im_num = 0
        self.im_mean = None
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
        self.capture()
        if self.mean <= 1:
            return img
        self.im_num += 1
        if self.im_num == 1:
            self.im_mean = img.astype(np.float)
        else:
            self.im_mean += img
        if self.im_num >= self.mean:
            self.im_num = 0
            return self.im_mean / self.mean

    def set_exposure_ms(self, ms):
        self.SetControlValue(pc.EXPOSURE, int(ms*1000), False)

    def get_exposure_ms(self):
        return self.GetControlValue(pc.EXPOSURE)[0] / 1000.0

    def set_gain(self, gain):
        self.SetControlValue(pc.GAIN, gain, False)

    def get_gain(self):
        return self.GetControlValue(pc.GAIN)[0]


class Histo:

    def __init__(self):
        self.data = None
        self.stretch = 0
        self.stretch_from = 0
        self.stretch_to = 127
        self.bins = [2*i - 0.5 for i in range(129)]

    def get(self):
        self.histo = Gtk.DrawingArea()
        self.histo.connect("draw", self.draw)
        self.histo.set_property("height-request", 100)
        return self.histo

    def draw(self, w, cr):
        if self.data is None:
            return
        width = w.get_allocated_width()
        height = w.get_allocated_height()
        cr.set_source_rgb(0.7, 0.1, 0.1)
        cr.move_to(0, 0)
        cr.line_to(width, 0)
        cr.line_to(width, height)
        cr.line_to(0, height)
        cr.line_to(0, 0)
        cr.stroke()
        xscale = width / 127.0
        yscale = float(height) / np.max(self.data)
        if self.stretch_from >= 0:
            cr.set_source_rgb(0.9, 0.6, 0.6)
            cr.rectangle(self.stretch_from * xscale, 0,
                         (self.stretch_to - self.stretch_from) * xscale,
                         height)
            cr.fill()
        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.new_path()
        cr.move_to(0, height - 0)
        cr.line_to(0, height - self.data[0] * yscale)
        for i in range(1, 128):
            cr.line_to(i * xscale, height - self.data[i] * yscale)
        cr.line_to(width, height - 0)
        cr.close_path()
        cr.fill()

    def apply(self, im):
        size = im.shape[0]
        if im.shape[1] > size:
            size = im.shape[1]
        n = 1
        while size > 256:
            size /= 2
            n *= 2
        self.data = np.histogram(im[::n, ::n], bins=self.bins)[0]
        if self.stretch > 0 and self.stretch < 100:
            cs = np.cumsum(self.data)/np.sum(self.data) * 100
            self.stretch_from = len(cs[cs <= self.stretch])
            self.stretch_to = len(cs[cs <= 100 - self.stretch])
            s_to = self.stretch_to / 127.0 * 255.0
            s_from = self.stretch_from / 127.0 * 255.0
            scale = 255.0 / (s_to - s_from)
            im = np.clip((im - s_from) * scale, 0, 255)
        else:
            self.stretch_from = 0
            self.stretch_to = 127
        self.histo.queue_draw()
        return im


class Mainwindow(Gtk.Window):

    def __init__(self, cam, *args, **kwargs):
        Gtk.Window.__init__(
            self, default_width=800, default_height=600,
            title="PYASICAM", *args, **kwargs)
        self.cam = cam
        self.surface = None
        self.gamma = 1.0
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

    def process_image(self, im):
        im = self.histo.apply(im)
        if self.gamma != 1.0:
            im = gamma_stretch(im, self.gamma)
        self.publish_image(im)

    def get_image(self):
        im = self.cam.get_image()
        if im is not None:
            self.im = im
            self.process_image(im)
        self.periodic = GLib.timeout_add(100, self.get_image)

    def publish_image(self, im):
        if im.dtype != np.uint8:
            im = im.astype(np.uint8)
        im32 = np.dstack((im, im, im, im))
        self.surface = cairo.ImageSurface.create_for_data(
            im32, cairo.FORMAT_RGB24, im.shape[1], im.shape[0])
        self.image.set_size_request(im.shape[1], im.shape[0])
        self.image.queue_draw()

    def draw(self, w, cr):
        if not self.surface:
            return
        cr.set_source_surface(self.surface, 0, 0)
        cr.paint()

    def configure(self, w, ev):
        if not self.surface:
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
        self.histo = Histo()
        box.pack_start(self.histo.get(), False, False, 0)
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
        mean = self.create_text_control(
            "Mean:",
            "%d" % self.cam.mean,
            self.set_mean)
        box.pack_start(mean, False, False, 0)
        stretch = self.create_text_control(
            "Stretch:",
            "%d" % self.histo.stretch,
            self.set_stretch)
        box.pack_start(stretch, False, False, 0)
        gamma = self.create_text_control(
            "Gamma:",
            "%d" % self.gamma,
            self.set_gamma)
        box.pack_start(gamma, False, False, 0)

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

    def set_mean(self, e):
        try:
            self.cam.mean = int(e.get_text())
        except:
            pass
        e.set_text("%d" % self.cam.mean)

    def set_stretch(self, e):
        try:
            self.histo.stretch = int(e.get_text())
        except:
            pass
        e.set_text("%d" % self.histo.stretch)

    def set_gamma(self, e):
        try:
            self.gamma = float(e.get_text())
        except:
            pass
        e.set_text("%f" % self.gamma)


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
