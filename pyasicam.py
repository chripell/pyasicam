import numpy as np
import os
import ctypes as c

CAMERA_ID_MAX = 128

BAYER_RG = 0
BAYER_BG = 1
BAYER_GR = 2
BAYER_GB = 3

IMG_RAW8 = 0
IMG_RGB24 = 1
IMG_RAW16 = 2
IMG_Y8 = 3
IMG_END = -1

GUIDE_NORTH = 0
GUIDE_SOUTH = 1
GUIDE_EAST = 2
GUIDE_WEST = 3

FLIP_NONE = 0
FLIP_HORIZ = 1
FLIP_VERT = 2
FLIP_BOTH = 3

MODE_NORMAL = 0
MODE_TRIG_SOFT_EDGE = 1
MODE_TRIG_RISE_EDGE = 2
MODE_TRIG_FALL_EDGE = 3
MODE_TRIG_SOFT_LEVE = 4
MODE_TRIG_HIGH_LEVEL = 5
MODE_TRIG_LOW_LEVEL = 6
MODE_END = -1

SUCCESS = 0
ERROR_INVALID_INDEX = 1
ERROR_INVALID_ID = 2
ERROR_INVALID_CONTROL_TYPE = 3
ERROR_CAMERA_CLOSED = 4
ERROR_CAMERA_REMOVED = 5
ERROR_INVALID_PATH = 6
ERROR_INVALID_FILEFORMAT = 7
ERROR_INVALID_SIZE = 8
ERROR_INVALID_IMGTYPE = 9
ERROR_OUTOF_BOUNDARY = 10 
ERROR_TIMEOUT = 11
ERROR_INVALID_SEQUENCE = 12
ERROR_BUFFER_TOO_SMALL = 13
ERROR_VIDEO_MODE_ACTIVE = 14
ERROR_EXPOSURE_IN_PROGRESS = 15
ERROR_GENERAL_ERROR = 16
ERROR_INVALID_MODE = 17
ERROR_END = 18

FALSE = 0
TRUE = 1

GAIN = 0
EXPOSURE = 1
GAMMA = 2
WB_R = 3
WB_B = 4
OFFSET = 5
BANDWIDTHOVERLOAD = 6
OVERCLOCK = 7
TEMPERATURE = 8
FLIP = 9
AUTO_MAX_GAIN = 10
AUTO_MAX_EXP = 11
AUTO_TARGET_BRIGHTNESS = 12
HARDWARE_BIN = 13
HIGH_SPEED_MODE = 14
COOLER_POWER_PERC = 15
TARGET_TEMP = 16
COOLER_ON = 17
MONO_BIN = 18
FAN_ON = 19
PATTERN_ADJUST = 20
ANTI_DEW_HEATER = 21

BRIGHTNESS = OFFSET
AUTO_MAX_BRIGHTNESS = AUTO_TARGET_BRIGHTNESS

EXP_IDLE = 0
EXP_WORKING = 1
EXP_SUCCESS = 2
EXP_FAILED = 3


class CAMERA_INFO(c.Structure):
    _fields_ = [
        ("Name", c.c_char * 64),
        ("CameraID", c.c_int),
        ("MaxHeight", c.c_long),
        ("MaxWidth", c.c_long),
        ("IsColorCam", c.c_int),
        ("BayerPattern", c.c_int),
        ("SupportedBins", c.c_int * 16),
        ("SupportedVideoFormat", c.c_int * 8),
        ("PixelSize", c.c_double),
        ("MechanicalShutter", c.c_int),
        ("ST4Port", c.c_int),
        ("IsCoolerCam", c.c_int),
        ("IsUSB3Host", c.c_int),
        ("IsUSB3Camera", c.c_int),
        ("ElecPerADU", c.c_float),
        ("BitDepth", c.c_int),
        ("IsTriggerCam", c.c_int),
        ("Unused", c.c_byte * 16),
    ]


class CONTROL_CAPS(c.Structure):
    _fields_ = [
        ("Name", c.c_char * 64),
        ("Description", c.c_char * 128),
        ("MaxValue", c.c_long),
        ("MinValue", c.c_long),
        ("DefaultValue", c.c_long),
        ("IsAutoSupported", c.c_int),
        ("IsWritable", c.c_int),
        ("ControlType", c.c_int),
        ("Unused", c.c_byte * 32),
    ]


class ID(c.Structure):
    _fields_ = [
        ("id", c.c_char * 8),
    ]


class SUPPORTED_MODE(c.Structure):
    _fields_ = [
        ("SupportedCameraMode", c.c_int * 16),
    ]


_im_Bpp = (1, 3, 2, 1)
_im_ds = (np.uint8, np.uint8, np.uint16, np.uint8)
requires = ('C', 'W', 'A')

my_path = os.path.dirname('__file__')
lib = np.ctypeslib.load_library('libASICamera2', my_path)

lib.ASIGetNumOfConnectedCameras.restype = c.c_int
lib.ASIGetNumOfConnectedCameras.argtypes = []

lib.ASIGetProductIDs.restype = c.c_int
lib.ASIGetProductIDs.argtypes = [c.POINTER(c.c_int)]

lib.ASIGetCameraProperty.restype = c.c_int
lib.ASIGetCameraProperty.argtypes = [c.POINTER(CAMERA_INFO), c.c_int]

lib.ASIOpenCamera.restype = c.c_int
lib.ASIOpenCamera.argtypes = [c.c_int]

lib.ASIInitCamera.restype = c.c_int
lib.ASIInitCamera.argtypes = [c.c_int]

lib.ASICloseCamera.restype = c.c_int
lib.ASICloseCamera.argtypes = [c.c_int]

lib.ASIGetNumOfControls.restype = c.c_int
lib.ASIGetNumOfControls.argtypes = [c.c_int, c.POINTER(c.c_int)]

lib.ASIGetControlCaps.restype = c.c_int
lib.ASIGetControlCaps.argtypes = [c.c_int, c.c_int, c.POINTER(CONTROL_CAPS)]

lib.ASIGetControlValue.restype = c.c_int
lib.ASIGetControlValue.argtypes = [c.c_int, c.c_int, c.POINTER(c.c_long),
                                   c.POINTER(c.c_int)]

lib.ASISetControlValue.restype = c.c_int
lib.ASISetControlValue.argtypes = [c.c_int, c.c_int, c.c_long, c.c_int]

lib.ASISetROIFormat.restype = c.c_int
lib.ASISetROIFormat.argtypes = [c.c_int, c.c_int, c.c_int, c.c_int, c.c_int]

lib.ASIGetROIFormat.restype = c.c_int
lib.ASIGetROIFormat.argtypes = [c.c_int, c.POINTER(c.c_int),
                                c.POINTER(c.c_int), c.POINTER(c.c_int),
                                c.POINTER(c.c_int)]

lib.ASISetStartPos.restype = c.c_int
lib.ASISetStartPos.argtypes = [c.c_int, c.c_int, c.c_int]

lib.ASIGetStartPos.restype = c.c_int
lib.ASIGetStartPos.argtypes = [c.c_int, c.POINTER(c.c_int), c.POINTER(c.c_int)]

lib.ASIGetDroppedFrames.restype = c.c_int
lib.ASIGetDroppedFrames.argtypes = [c.c_int, c.POINTER(c.c_int)]

lib.ASIEnableDarkSubtract.restype = c.c_int
lib.ASIEnableDarkSubtract.argtypes = [c.c_int, c.c_char_p]

lib.ASIDisableDarkSubtract.restype = c.c_int
lib.ASIDisableDarkSubtract.argtypes = [c.c_int]

lib.ASIStartVideoCapture.restype = c.c_int
lib.ASIStartVideoCapture.argtypes = [c.c_int]

lib.ASIStopVideoCapture.restype = c.c_int
lib.ASIStopVideoCapture.argtypes = [c.c_int]

lib.ASIGetVideoData.restype = c.c_int
lib.ASIGetVideoData.argtypes = [
    c.c_int, np.ctypeslib.ndpointer(dtype=np.uint8, ndim=1,
                                    flags=requires),
    c.c_long, c.c_int]

lib.ASIPulseGuideOn.restype = c.c_int
lib.ASIPulseGuideOn.argtypes = [c.c_int, c.c_int]

lib.ASIPulseGuideOff.restype = c.c_int
lib.ASIPulseGuideOff.argtypes = [c.c_int, c.c_int]

lib.ASIStartExposure.restype = c.c_int
lib.ASIStartExposure.argtypes = [c.c_int, c.c_int]

lib.ASIStopExposure.restype = c.c_int
lib.ASIStopExposure.argtypes = [c.c_int]

lib.ASIGetExpStatus.restype = c.c_int
lib.ASIGetExpStatus.argtypes = [c.c_int, c.POINTER(c.c_int)]

lib.ASIGetDataAfterExp.restype = c.c_int
lib.ASIGetDataAfterExp.argtypes = [
    c.c_int, np.ctypeslib.ndpointer(dtype=np.uint8, ndim=1,
                                    flags=requires),
    c.c_int]

lib.ASIGetID.restype = c.c_int
lib.ASIGetID.argtypes = [c.c_int, c.POINTER(c.c_int)]

lib.ASISetID.restype = c.c_int
lib.ASISetID.argtypes = [c.c_int, c.c_int]

lib.ASIGetGainOffset.restype = c.c_int
lib.ASIGetGainOffset.argtypes = [c.c_int,
                                 c.POINTER(c.c_int), c.POINTER(c.c_int),
                                 c.POINTER(c.c_int), c.POINTER(c.c_int)]

lib.ASIGetSDKVersion.restype = c.c_char_p
lib.ASIGetSDKVersion.argtypes = []


def GetNumOfConnectedCameras():
    return lib.ASIGetNumOfConnectedCameras()


def GetProductIDs():
    pids = (c.c_int * CAMERA_ID_MAX)()
    n = lib.ASIGetProductIDs(pids)
    return pids[:n]


def GetSDKVersion():
    return lib.ASIGetSDKVersion()


class Error(Exception):
    def __init__(self, err):
        super().__init__("ASI Camera error: %d" % err)
        self.code = err


class Camera:

    def __init__(self, i):
        self.i = i
        self.width = -1
        self.height = -1
        self.img_type = -1

    def GetCameraProperty(self):
        info = CAMERA_INFO()
        err = lib.ASIGetCameraProperty(c.byref(info), self.i)
        if err != 0:
            raise Error(err)
        return info

    def OpenCamera(self):
        err = lib.ASIOpenCamera(self.i)
        if err != 0:
            raise Error(err)

    def InitCamera(self):
        err = lib.ASIInitCamera(self.i)
        if err != 0:
            raise Error(err)

    def CloseCamera(self):
        err = lib.ASICloseCamera(self.i)
        if err != 0:
            raise Error(err)

    def GetNumOfControls(self):
        n = c.c_int()
        err = lib.ASIGetNumOfControls(self.i, c.byref(n))
        if err != 0:
            raise Error(err)
        return n.value

    def GetControlCaps(self, idx):
        caps = CONTROL_CAPS()
        err = lib.ASIGetControlCaps(self.i, idx, c.byref(caps))
        if err != 0:
            raise Error(err)
        return caps

    def GetControlValue(self, idx):
        val = c.c_long()
        auto = c.c_int()
        err = lib.ASIGetControlValue(self.i, idx, c.byref(val), c.byref(auto))
        if err != 0:
            raise Error(err)
        return (val.value, bool(auto.value))

    def SetControlValue(self, idx, val, auto):
        err = lib.ASISetControlValue(self.i, idx, c.c_long(val), c.c_int(auto))
        if err != 0:
            raise Error(err)

    def SetROIFormat(self, width, height, binning, img_type):
        err = lib.ASISetROIFormat(self.i, width, height, binning, img_type)
        if err != 0:
            raise Error(err)
        self.width = width
        self.height = height
        self.img_type = img_type

    def GetROIFormat(self):
        width = c.c_int()
        height = c.c_int()
        binning = c.c_int()
        img_type = c.c_int()
        err = lib.ASIGetROIFormat(self.i, c.byref(width), c.byref(height),
                                  c.byref(binning), c.byref(img_type))
        if err != 0:
            raise Error(err)
        self.width = width.value
        self.height = height.value
        self.img_type = img_type.value
        return (width.value, height.value, binning.value, img_type.value)

    def SetStartPos(self, x, y):
        err = lib.ASISetStartPos(self.i, x, y)
        if err != 0:
            raise Error(err)

    def GetStartPos(self):
        x = c.c_int()
        y = c.c_int()
        err = lib.ASIGetStartPos(self.i, c.byref(x), c.byref(y))
        if err != 0:
            raise Error(err)
        return x.value, y.value

    def GetDroppedFrames(self):
        dropped = c.c_int()
        err = lib.ASIGetDroppedFrames(self.i, c.byref(dropped))
        if err != 0:
            raise Error(err)
        return dropped.value

    def EnableDarkSubtract(self, fname):
        err = lib.ASIEnableDarkSubtract(self.i, fname)
        if err != 0:
            raise Error(err)

    def DisableDarkSubtract(self):
        err = lib.ASIDisableDarkSubtract(self.i)
        if err != 0:
            raise Error(err)

    def StartVideoCapture(self):
        err = lib.ASIStartVideoCapture(self.i)
        if err != 0:
            raise Error(err)

    def StopVideoCapture(self):
        err = lib.ASIStopVideoCapture(self.i)
        if err != 0:
            raise Error(err)

    def convert(self, x):
        if self.img_type == -1:
            self.GetROIFormat()
        if self.img_type == 1:
            imr = x.reshape(self.height, self.width, 3)
            return imr[:, :, ::-1]
        else:
            return x.view(
                dtype=_im_ds[self.img_type]).reshape(
                    self.height, self.width)

    def bufAlloc(self):
        if self.img_type == -1:
            self.GetROIFormat()
        t = self.width * self.height * _im_Bpp[self.img_type]
        return (np.require(np.zeros(t), np.uint8, requires), t)

    def GetVideoData(self, wait):
        (b, l) = self.bufAlloc()
        err = lib.ASIGetVideoData(self.i, b, l, wait)
        if err != 0:
            raise Error(err)
        return self.convert(b)

    def PulseGuideOn(self, dire):
        err = lib.ASIPulseGuideOn(self.i, dire)
        if err != 0:
            raise Error(err)

    def PulseGuideOff(self, dire):
        err = lib.ASIPulseGuideOff(self.i, dire)
        if err != 0:
            raise Error(err)

    def StartExposure(self, dark):
        err = lib.ASIStartExposure(self.i, c.c_int(dark))
        if err != 0:
            raise Error(err)

    def StopExposure(self):
        err = lib.ASIStopExposure(self.i)
        if err != 0:
            raise Error(err)

    def GetExpStatus(self):
        st = c.c_int()
        err = lib.ASIGetExpStatus(self.i, c.byref(st))
        if err != 0:
            raise Error(err)
        return st.value

    def GetDataAfterExp(self):
        (b, l) = self.bufAlloc()
        err = lib.ASIGetDataAfterExp(self.i, b, l)
        if err != 0:
            raise Error(err)
        return self.convert(b)

    def GetID(self):
        id = c.c_int()
        err = lib.ASIGetID(self.i, c.byref(id))
        if err != 0:
            raise Error(err)
        return id.value

    def SetID(self, id):
        err = lib.ASISetID(self.i, id)
        if err != 0:
            raise Error(err)

    def GetGainOffset(self):
        d1 = c.c_int()
        d2 = c.c_int()
        d3 = c.c_int()
        d4 = c.c_int()
        err = lib.ASIGetGainOffset(self.i, c.byref(d1), c.byref(d2),
                                   c.byref(d3), c.byref(d4))
        if err != 0:
            raise Error(err)
        return d1.value, d2.value, d3.value, d4.value
