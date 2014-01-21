
import numpy as np
import os
import ctypes
import __builtin__

_c = dict(
    gain = 0,
    exposure = 1,
    gamma = 2,
    wb_r = 3,
    wb_b = 4,
    brightness = 5,
    bandwidthoverload = 6,
)

_bayer_pattern = ("RG", "BG", "GR", "GB")

_im_types = dict(
    raw8 = 0,
    rgb24 = 1,
    raw16 = 2,
    y8 = 3,
)

_im_types2 = dict()
_im_Bpp = (1, 3, 2, 1)
_im_ds = (np.uint8, np.uint8, np.uint16, np.uint8)

_pulse = dict(
    N = 0,
    S = 1,
    E = 2,
    W = 3,
)

controls = []
is_color = None
pixel_size = None
bayer = None
maxWH = []
im_types = []
bins = []

_path = os.path.dirname('__file__')
lib = np.ctypeslib.load_library('libASICamera', _path)

lib.getNumberOfConnectedCameras.restype = ctypes.c_int
lib.getNumberOfConnectedCameras.argtypes = []

num = lib.getNumberOfConnectedCameras()

lib.openCamera.restype = ctypes.c_bool
lib.openCamera.argtypes = [ctypes.c_int]

lib.initCamera.restype = ctypes.c_bool
lib.initCamera.argtypes = []

lib.closeCamera.restype = None
lib.closeCamera.argtypes = []

lib.isColorCam.restype = ctypes.c_bool
lib.isColorCam.argtypes = []

lib.getPixelSize.restype = ctypes.c_double
lib.getPixelSize.argtypes = []

lib.getColorBayer.restype = ctypes.c_int
lib.getColorBayer.argtypes = []

lib.getCameraModel.restype = ctypes.c_char_p
lib.getCameraModel.argtypes = [ctypes.c_int]

lib.isAvailable.restype = ctypes.c_bool
lib.isAvailable.argtypes = [ctypes.c_int]

lib.isAutoSupported.restype = ctypes.c_bool
lib.isAutoSupported.argtypes = [ctypes.c_int]

requires = ('C', 'W', 'A')
lib.getValue.restype = ctypes.c_int
lib.getValue.argtypes = [ctypes.c_int, np.ctypeslib.ndpointer(dtype=np.uint8, ndim=1, shape=(1), flags=requires)]

lib.getMin.restype = ctypes.c_int
lib.getMin.argtypes = [ctypes.c_int]

lib.getMax.restype = ctypes.c_int
lib.getMax.argtypes = [ctypes.c_int]

lib.setValue.restype = None
lib.setValue.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_bool]

lib.getMaxWidth.restype = ctypes.c_int
lib.getMaxWidth.argtypes = []

lib.getMaxHeight.restype = ctypes.c_int
lib.getMaxHeight.argtypes = []

lib.getWidth.restype = ctypes.c_int
lib.getWidth.argtypes = []

lib.getHeight.restype = ctypes.c_int
lib.getHeight.argtypes = []

lib.getStartX.restype = ctypes.c_int
lib.getStartX.argtypes = []

lib.getStartY.restype = ctypes.c_int
lib.getStartY.argtypes = []

lib.getSensorTemp.restype = ctypes.c_float
lib.getSensorTemp.argtypes = []

lib.getDroppedFrames.restype = ctypes.c_ulong
lib.getDroppedFrames.argtypes = []

lib.SetMisc.restype = ctypes.c_bool
lib.SetMisc.argtypes = [ctypes.c_bool, ctypes.c_bool]

lib.GetMisc.restype = None
lib.GetMisc.argtypes = [np.ctypeslib.ndpointer(dtype=np.uint8, ndim=1, shape=(1), flags=requires),
                        np.ctypeslib.ndpointer(dtype=np.uint8, ndim=1, shape=(1), flags=requires)]

lib.isBinSupported.restype = ctypes.c_bool
lib.isBinSupported.argtypes = [ctypes.c_int]

lib.isImgTypeSupported.restype = ctypes.c_bool
lib.isImgTypeSupported.argtypes = [ctypes.c_int]

lib.getBin.restype = ctypes.c_int
lib.getBin.argtypes = []

lib.setStartPos.restype = ctypes.c_bool
lib.setStartPos.argtypes = [ctypes.c_int, ctypes.c_int]

lib.setImageFormat.restype = ctypes.c_bool
lib.setImageFormat.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]

lib.getImgType.restype = ctypes.c_int
lib.getImgType.argtypes = []

lib.startCapture.restype = None
lib.startCapture.argtypes = []

lib.stopCapture.restype = None
lib.stopCapture.argtypes = []

lib.getImageData.restype = ctypes.c_bool
lib.getImageData.argtypes = [np.ctypeslib.ndpointer(dtype=np.uint8, ndim=1, flags=requires), ctypes.c_int, ctypes.c_int]

lib.pulseGuide.restype = None
lib.pulseGuide.argtypes = [ctypes.c_int, ctypes.c_int]

_camn = 0

def open(i):
    if not lib.openCamera(i):
        return False
    if not lib.initCamera(i):
        lib.closeCamera()
        return False
    global is_color, pixel_size, bayer, controls, maxWH, im_types, _camn
    _camn = i
    is_color = lib.isColorCam()
    pixel_size = lib.getPixelSize()
    bayer = _bayer_pattern[lib.getColorBayer()]
    for i in _c.keys():
        if lib.isAvailable(_c[i]):
            controls.append(i)
    maxWH = (lib.getMaxWidth(), lib.getMaxHeight())
    for i in _im_types.keys():
        if lib.isImgTypeSupported(_im_types[i]):
            im_types.append(i)
        _im_types2[_im_types[i]] = i
    for i in (0,1,2,3):
        if lib.isBinSupported(i):
            bins.append(i)
    load()
    return True

def name(i):
    return lib.getCameraModel(i)

def has_auto(i):
    return lib.isAutoSupported(_c[i])

def min_max(i):
    return lib.getMin(_c[i]), lib.getMax(_c[i])

def value(i):
    a = np.require(np.zeros(1), np.uint8, requires)
    v = lib.getValue(_c[i], a)
    return v, (a[0] != 0)

def set(i, v, a = False):
    lib.setValue(_c[i], v, a)

def WH():
    return (lib.getWidth(), lib.getHeight())

def XY():
    return (lib.getStartX(), lib.getStartY())

def temp():
    return lib.getSensorTemp()

def dropped():
    return lib.getDroppedFrames()

def set_flip(x, y):
    lib.SetMisc(x,y)

def get_flip():
    x = np.require(np.zeros(1), np.uint8, requires)
    y = np.require(np.zeros(1), np.uint8, requires)
    lib.getValue(x, y)
    return (x[0] != 0), (y[0] != 0)
    
def bin():
    return lib.getBin()

def set_XY(x, y):
    lib.setStartPos(x,y)

_width = 0
_height = 0
_bin = 0
_typ = 0

def format(width, height, cbin, typ):
    if (width * height) % 1024 != 0:
        raise Exception("width * height must be multiple of 1024")
    global _width, _height, _bin, _typ
    _width = width
    _height = height
    _bin = cbin
    _typ = _im_types[typ]
    lib.setImageFormat(width, height, cbin, _im_types[typ])

def typ():
    return _im_types2[lib.getImgType()]

def start():
    lib.startCapture()

def stop():
    lib.stopCapture()

def image(waitms = -1):
    t = _width * _height * _im_Bpp[_typ]
    x = np.require(np.zeros(t), np.uint8, requires)
    r = lib.getImageData(x, t, waitms)
    if r == 0:
        return None
    if _typ == 1:
        imr = x.reshape(_height, _width, 3)
        return imr[:,:,::-1]
    else:
        return x.view(dtype=_im_ds[_typ]).reshape(_height, _width)

def pulse(d, t_ms):
    lib.pulseGuide(_pulse[d], t_ms)

def load(i = False):
    global _width, _height, _bin, _typ
    home = os.path.expanduser("~")
    if not i:
        i = _camn
    try:
        with __builtin__.open(home + "/.ASICamera%d"%(i)) as f:
            sx, sy = [int(x) for x in f.readline().split()]
            _width, _height = [int(x) for x in f.readline().split()]
            fx, fy = [int(x) for x in f.readline().split()]
            _typ, _bin = [int(x) for x in f.readline().split()]
            lib.setImageFormat(_width, _height, _bin, _typ)
            lib.setStartPos(sx,sy)
            lib.SetMisc(fx != 0, fy != 0)
            for c in xrange(0,7):
                v, a = [int(x) for x in f.readline().split()]
                lib.setValue(c, v, a)
    except IOError:
        pass
