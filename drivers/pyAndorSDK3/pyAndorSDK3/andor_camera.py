from functools import wraps
try:
    from queue import Queue
except ImportError:
    from Queue import Queue
import time
from math import ceil

import numpy as np
from collections import OrderedDict, deque

from pyAndorSDK3.utils import CaseInsensitiveDict
from pyAndorSDK3.andor_acquisition import Acquisition
from pyAndorSDK3.andor_sdk3_internals import ATCoreException

class CameraException(Exception):

    def __init__(self, value):
        self.value = value

    def _get_message(self):
        return self.value

class Feature:
    def __init__(self, func, execute=False):
        self.func=func
        self.execute=execute

class Camera(object):

    _queued_buffers = Queue()
    _registered_callbacks = []
    _original_register_values = {}
    _features_type={}
    _feature_funcs = ["min_", "max_", "options_", "is_available_", "type_", "available_options_"]
    _current_config = CaseInsensitiveDict()
    _prev_acq = []

    _lib = None
    _index = None
    _handle = 0

    def __init__(self, lib, index):
        self._lib = lib
        self._index = index
        try:
            self._handle = self._lib.open(self._index)
        except ATCoreException as e:
            raise CameraException(str(e))
        if self._lib.get_bool(self._handle, "CameraAcquiring"):
            self.AcquisitionStop()
        self._flush()
        self._populate_config()

    def camera(self):
        # exists for backwards compatibility
        return self

    def __del__(self):
        if self._handle != 0:
            self._lib.close(self._handle)
            self._handle = 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        for a, b in self._registered_callbacks:
            self.unregister_feature_callback(a, b)
        self._registered_callbacks = []

    def open(self):
        if self._handle == 0:
            try:
                self._handle = self._lib.open(self._index)
            except ATCoreException as e:
                raise CameraException(str(e))

    def close(self):
        self._lib.close(self._handle)
        self._handle = 0

    def _raise_attribute_error(self, feature_name):
        raise AttributeError("Camera has no Feature '{0}'".format(feature_name))

    def _create_func(self, command, feature_name):
        @wraps(command)
        def f(*args, **kwargs):
            try:
                return command(self._handle, feature_name, *args, **kwargs)
            except ATCoreException as e:
                raise CameraException(str(e) + feature_name + ("%s" % str(args)))
        return f

    def _setup_feature_type(self, feature_name):
        if feature_name not in self._features_type:
            if not self._lib.is_implemented(self._handle, feature_name):
                self._raise_attribute_error(feature_name)

            types_to_check = ["int","float","bool","enumerated_string","string"]
            for feature_type in types_to_check:
                try:
                    getattr(self._lib, "get_"+feature_type)(self._handle, feature_name)
                    self._features_type[feature_name] = feature_type
                    return
                except ATCoreException as e:
                    if ("AT_ERR_NOTIMPLEMENTED" not in str(e)):
                        self._features_type[feature_name] = feature_type
                        return
            self._features_type[feature_name] = "command"

    def _get_feature_available_options(self, handle, feature_name):
        option_list = []
        for option in getattr(self, "options_"+feature_name):
            if getattr(self, "is_available_"+feature_name)(option):
                option_list.append(option)
        return option_list

    def _create_feature_function(self, feature_name, begin_text, stripped_feature_name):
        self._setup_feature_type(stripped_feature_name)
        feat_type = self._features_type[stripped_feature_name]
        feature = None
        if begin_text == "type_":
            feature = Feature(feat_type)
        else:
            func_map = {"min_":"_min", "max_":"_max", "options_":"_options"}
            try:
                if begin_text == "is_available_":
                    feature = Feature(self._create_func(self._lib.is_enumerated_string_available, stripped_feature_name))
                elif begin_text == "available_options_":
                    feature = Feature(self._create_func(self._get_feature_available_options, stripped_feature_name), True)
                else:
                    feature = Feature(self._create_func(getattr(self._lib, "get_"+feat_type+func_map[begin_text]), stripped_feature_name), True)
            except AttributeError:
                raise AttributeError("Cannot use the '{}' function for feature '{}' with the type '{}'".format(begin_text, stripped_feature_name, self._features_type[stripped_feature_name]))
            return feature

    def __getattr__(self, feature_name):
        split_feature_name = feature_name.split("_")
        text = "_".join(split_feature_name[0:-1])+"_"
        feature = None
        if text in self._feature_funcs:
            feature = self._create_feature_function(feature_name, text, split_feature_name[-1])
        else:
            self._setup_feature_type(feature_name)
            if self._features_type[feature_name] != "command":
                feature = Feature(self._create_func(getattr(self._lib, "get_"+self._features_type[feature_name]), feature_name), True)
            else:
                feature = Feature(self._create_func(self._lib.command, feature_name))
        return feature.func() if feature.execute else feature.func

    def __setattr__(self, feature_name, value):
        if feature_name in dir(self): # is not a feature
            super().__setattr__(feature_name, value)
            return

        text = feature_name.split("_")[0]
        if text in self._feature_funcs:
            raise AttributeError("Cannot use set on Feature Function {} ".format(text))

        self._setup_feature_type(feature_name)
        set_func = self._create_func(getattr(self._lib, "set_"+self._features_type[feature_name]), feature_name)
        set_func(value)

    def _queue_buffer(self, buffer_size):
        buf = np.empty((buffer_size,), dtype='B')
        self._queued_buffers.put(buf)
        self._lib.queue_buffer(self._handle, buf.ctypes.data, buffer_size)

    def _flush(self):
        self._lib.flush(self._handle)
        self._queued_buffers = Queue()

    def _acquire(self, timeout):
        try:
            (buf_ptr, buffer_size) = self._lib.wait_buffer(self._handle,timeout=int(timeout))
        except Exception as e:
            raise CameraException(str(e))
        return Acquisition(self._queued_buffers.get(), self._current_config)

    def queue(self, the_buffer, size):
        self._queued_buffers.put(the_buffer)
        self._lib.queue_buffer(self._handle, the_buffer.ctypes.data, size)

    def get_previous_acquisition_series(self):
        return self._prev_acq

    def acquire_series(self, *args, **kwargs):
        self.configure(*args)
        timeout = kwargs.pop('timeout', max(5000, ceil(5 * 1000 / self.FrameRate)))
        min_buf = kwargs.pop('min_buf', 2)
        max_buf = kwargs.pop('max_buf', 25)
        circ_buf = kwargs.pop('circ_buf', False)
        print_frame = kwargs.pop('print_frame', False)
        print_fps = kwargs.pop('print_fps', False)
        print_fps_interval = kwargs.pop('print_fps_interval', 1)
        pause_after = kwargs.pop('pause_after', 0.0)
        sw_trigger = self.TriggerMode == "Software"

        if self.CycleMode == "Fixed":
            accumulate_available = True
            try:
                acc = self.AccumulateCount
            except:
                accumulate_available = False
            if accumulate_available and self.AccumulateCount > 1: # if doing accumulation, num_images = framecount/accumulatecount
                fc = int(kwargs.pop('frame_count', self.FrameCount) / self.AccumulateCount)
            else:
                fc = self.FrameCount = kwargs.pop('frame_count', self.FrameCount)
            buf_count = max(min(max_buf, fc), min_buf)
        else:
            fc = kwargs.pop('frame_count', 0)# if you don't specify frame_count while in continuous mode fc will default to 0 and acquire_series will acquire forever
            if fc > 0:
                buf_count = max(min(max_buf, fc), min_buf)
            else:
                buf_count = max(max_buf, min_buf)
        imgsize = self.ImageSizeBytes
        for _ in range(0, buf_count):
            self._queue_buffer(imgsize)

        series = deque()
        frame=None
        update_count = 0
        time_start = None
        prev_time = None
        try:
            self.AcquisitionStart()
            time_start = time.time()
            prev_time = time_start
            frame = 0
            while(True):
                if self._queued_buffers.qsize() == 0:
                    if circ_buf :
                        self.queue(series.popleft()._np_data, imgsize)
                    else:
                        self._queue_buffer(imgsize)
                if sw_trigger : self.SoftwareTrigger()
                acq = self._acquire(timeout)
                series.append(acq)

                if print_frame:
                    print(acq.image)
                frame += 1
                if fc != 0:
                    if frame == fc:
                        break
                if print_fps:
                    update_count += 1
                    if update_count >= print_fps_interval:
                        prev_time = time.time()
                        print("Effective FrameRate : {} fps".format(frame / (prev_time - time_start + 0.00001)))
                        update_count = 0
        except Exception as e:
            if frame != None:
                print("Error on frame "+str(frame))
                if print_fps:
                    print("Effective FrameRate of Failed Series : {} fps".format(frame / (prev_time - time_start + 0.00001)))
            self.AcquisitionStop()
            self._flush()
            raise e
        finally:
            self._prev_acq = list(series)
        if print_fps:
            print("Effective FrameRate of Completed Series : {} fps".format(frame / (time.time() - time_start + 0.00001)))
        if(pause_after > 0):
            time.sleep(pause_after)
        self.AcquisitionStop()
        self._flush()
        return list(series)

    def acquire(self, *args, **kwargs):
        self.configure(*args)
        timeout = kwargs.pop('timeout', max(5000, ceil(5 * 1000 / self.FrameRate)))
        min_buf = kwargs.pop('min_buf', 2)
        pause_after = kwargs.pop('pause_after', 0.0)
        sw_trigger = self.TriggerMode == "SoftwareTrigger"
        for _ in range(0, min_buf):
            self._queue_buffer(self.ImageSizeBytes)
        try:
            self.AcquisitionStart()
            if sw_trigger : self.SoftwareTrigger()
            acq = self._acquire(timeout)
        except Exception as e:
            self.AcquisitionStop()
            self._flush()
            raise e
        if(pause_after > 0):
            time.sleep(pause_after)
        self.AcquisitionStop()
        self._flush()
        return acq

    def configure(self, *args):
        for (k, v) in args:
            try:
                setattr(self, k, v)
            except Exception as e:
                raise e
        self._populate_config()

    def _populate_config(self, force=False):
        for k in ["AOIHeight", "AOIWidth", "AOIStride", "PixelEncoding", "ImageSizeBytes", "MetadataEnable"]:
            if self._lib.is_readable(self._handle, k):
                self._current_config[k] = getattr(self, k)

        if self._current_config["MetadataEnable"]:
            for k in ["MetadataTimestamp", "MetadataIRIG", "MetadataFrameInfo", "IRIGClockFrequency"]:
                if hasattr(self, k) and self._lib.is_readable(self._handle, k):
                    self._current_config[k] = getattr(self, k)

    def register_feature_callback(self, feature, func):
        self._registered_callbacks.append((feature, func))
        self._lib.register_feature_callback(self._handle, feature, func)

    def unregister_feature_callback(self, feature, func):
        self._lib.unregister_feature_callback(self._handle, feature, func)
        self._registered_callbacks.remove((feature, func))

    def register_write(self, addr, payload):
        if (hasattr(payload, "__iter__") is False):
            payload = [payload,]
        if addr not in self._original_register_values:
            self._original_register_values[addr] = self.register_read(addr, len(payload))
        self.__register_write(addr, payload)


    def __register_write(self, addr, payload):
        self.RegisterAddress = addr
        if (hasattr(payload, "__iter__") is False):
            payload = [payload,]

        self.RegisterCount = len(payload)

        for i in range(0, len(payload)):
            self.RegisterIndex = i
            self.RegisterValue = payload[i]
            self.RegisterWrite()

    def restore_registers(self):
        for addr, payload in self._original_register_values.items():
            self.__register_write(addr, payload)
        self._original_register_values.clear()

    def register_read(self, addr, count=1):
        self.RegisterAddress = addr
        self.RegisterCount = count
        self.RegisterRead()
        acc = np.empty((count,), dtype='I')
        for i in range(0, count):
            self.RegisterIndex = i
            acc[i] = self.RegisterValue
        if len(acc) == 1:
            return acc[0]
        else:
            return acc

    def get_updated_features(self):
        return self._lib.get_updated_features()

