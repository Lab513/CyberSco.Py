from pyAndorSDK3.andor_camera import CameraException


class AndorSDK3(object):

    AT_HANDLE_SYSTEM = 1

    def __init__(self):
        from pyAndorSDK3.andor_sdk3_internals import ATCore
        self._lib = ATCore()

    @property
    def cameras(self):
        from pyAndorSDK3.andor_camera import Camera
        cam_list = []
        for i in range(self.DeviceCount):
            cam_list.append(Camera(self._lib, i))
        return cam_list

    def Reinitialise(self):
        self._lib.finalise()
        self._lib.initialise()

    @property
    def DeviceCount(self):
        return self._lib.get_int(self.AT_HANDLE_SYSTEM, "DeviceCount")

    @property
    def SoftwareVersion(self):
        return self._lib.get_string(self.AT_HANDLE_SYSTEM, "SoftwareVersion")

    def GetCamera(self, i):
        from pyAndorSDK3.andor_camera import Camera
        return Camera(self._lib, i)

    def event_callback(self, func):
        from functools import wraps
        from cffi import FFI
        ffi = FFI()
        ffi.set_unicode(True)
        @wraps(func)
        def _func(handle, result, ctxt):
            func(ffi.string(result))
            return 0
        return self._lib.build_callback(_func)

