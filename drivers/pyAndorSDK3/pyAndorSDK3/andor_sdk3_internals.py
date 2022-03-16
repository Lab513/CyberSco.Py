import sys
if sys.version < '3':
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x

class ATCoreException(Exception): pass

class ATCore(object):

    _ERRORS = {
        0: 'AT_SUCCESS',
        1: 'AT_ERR_NOTINITIALISED',
        2: 'AT_ERR_NOTIMPLEMENTED',
        3: 'AT_ERR_READONLY',
        4: 'AT_ERR_NOTREADABLE',
        5: 'AT_ERR_NOTWRITABLE',
        6: 'AT_ERR_OUTOFRANGE',
        7: 'AT_ERR_INDEXNOTAVAILABLE',
        8: 'AT_ERR_INDEXNOTIMPLEMENTED',
        9: 'AT_ERR_EXCEEDEDMAXSTRINGLENGTH',
        10: 'AT_ERR_CONNECTION',
        11: 'AT_ERR_NODATA',
        12: 'AT_ERR_INVALIDHANDLE',
        13: 'AT_ERR_TIMEDOUT',
        14: 'AT_ERR_BUFFERFULL',
        15: 'AT_ERR_INVALIDSIZE',
        16: 'AT_ERR_INVALIDALIGNMENT',
        17: 'AT_ERR_COMM',
        18: 'AT_ERR_STRINGNOTAVAILABLE',
        19: 'AT_ERR_STRINGNOTIMPLEMENTED',
        20: 'AT_ERR_NULL_FEATURE',
        21: 'AT_ERR_NULL_HANDLE',
        22: 'AT_ERR_NULL_IMPLEMENTED_VAR',
        23: 'AT_ERR_NULL_READABLE_VAR',
        24: 'AT_ERR_NULL_READONLY_VAR',
        25: 'AT_ERR_NULL_WRITABLE_VAR',
        26: 'AT_ERR_NULL_MINVALUE',
        27: 'AT_ERR_NULL_MAXVALUE',
        28: 'AT_ERR_NULL_VALUE',
        29: 'AT_ERR_NULL_STRING',
        30: 'AT_ERR_NULL_COUNT_VAR',
        31: 'AT_ERR_NULL_ISAVAILABLE_VAR',
        32: 'AT_ERR_NULL_MAXSTRINGLENGTH',
        33: 'AT_ERR_NULL_EVCALLBACK',
        34: 'AT_ERR_NULL_QUEUE_PTR',
        35: 'AT_ERR_NULL_WAIT_PTR',
        36: 'AT_ERR_NULL_PTRSIZE',
        37: 'AT_ERR_NOMEMORY',
        38: 'AT_AT_ERR_DEVICEINUSE',
        100: 'AT_ERR_HARDWARE_OVERFLOW',
   }
    __version__ = '0.1'
    LIBRARY_NAME = 'atcore'

    def __init__(self):
        from cffi import FFI
        self.ffi = FFI()
        self.ffi.set_unicode(True)
        self.C = self.ffi.cdef("""
        typedef int AT_H;
        typedef int AT_BOOL;
        typedef long long AT_64;
        typedef unsigned char AT_U8;
        typedef wchar_t AT_WC;

        int AT_InitialiseLibrary();
        int AT_FinaliseLibrary();

        int AT_Open(int CameraIndex, AT_H *Hndl);
        int AT_Close(AT_H Hndl);

        typedef int (*FeatureCallback)(AT_H Hndl, const AT_WC* Feature, void* Context);
        int AT_RegisterFeatureCallback(AT_H Hndl, const AT_WC* Feature, FeatureCallback EvCallback, void* Context);
        int AT_UnregisterFeatureCallback(AT_H Hndl, const AT_WC* Feature, FeatureCallback EvCallback, void* Context);

        int AT_IsImplemented(AT_H Hndl, const AT_WC* Feature, AT_BOOL* Implemented);
        int AT_IsReadable(AT_H Hndl, const AT_WC* Feature, AT_BOOL* Readable);
        int AT_IsWritable(AT_H Hndl, const AT_WC* Feature, AT_BOOL* Writable);
        int AT_IsReadOnly(AT_H Hndl, const AT_WC* Feature, AT_BOOL* ReadOnly);

        int AT_SetInt(AT_H Hndl, const AT_WC* Feature, AT_64 Value);
        int AT_GetInt(AT_H Hndl, const AT_WC* Feature, AT_64* Value);
        int AT_GetIntMax(AT_H Hndl, const AT_WC* Feature, AT_64* MaxValue);
        int AT_GetIntMin(AT_H Hndl, const AT_WC* Feature, AT_64* MinValue);

        int AT_SetFloat(AT_H Hndl, const AT_WC* Feature, double Value);
        int AT_GetFloat(AT_H Hndl, const AT_WC* Feature, double* Value);
        int AT_GetFloatMax(AT_H Hndl, const AT_WC* Feature, double* MaxValue);
        int AT_GetFloatMin(AT_H Hndl, const AT_WC* Feature, double* MinValue);

        int AT_SetBool(AT_H Hndl, const AT_WC* Feature, AT_BOOL Value);
        int AT_GetBool(AT_H Hndl, const AT_WC* Feature, AT_BOOL* Value);


        int AT_Command(AT_H Hndl, const AT_WC* Feature);

        int AT_SetString(AT_H Hndl, const AT_WC* Feature, const AT_WC* String);
        int AT_GetString(AT_H Hndl, const AT_WC* Feature, AT_WC* String, int StringLength);
        int AT_GetStringMaxLength(AT_H Hndl, const AT_WC* Feature, int* MaxStringLength);

        int AT_QueueBuffer(AT_H Hndl, AT_U8* Ptr, int PtrSize);
        int AT_WaitBuffer(AT_H Hndl, AT_U8** Ptr, int* PtrSize, unsigned int Timeout);
        int AT_Flush(AT_H Hndl);

        int AT_IsEnumIndexAvailable(AT_H Hndl, const AT_WC* Feature, int Index, AT_BOOL* Available);
        int AT_IsEnumIndexImplemented(AT_H Hndl, const AT_WC* Feature, int Index, AT_BOOL* Implemented);
        int AT_GetEnumIndex(AT_H Hndl, const AT_WC* Feature, int* Value);
        int AT_GetEnumStringByIndex(AT_H Hndl, const AT_WC* Feature, int Index, AT_WC* String, int StringLength);
        int AT_GetEnumCount(AT_H Hndl,const  AT_WC* Feature, int* Count);
        int AT_SetEnumIndex(AT_H Hndl, const AT_WC* Feature, int Value);
        int AT_SetEnumString(AT_H Hndl, const AT_WC* Feature, const AT_WC* String);
        
        """)

        #int AT_IsEnumeratedIndexAvailable(AT_H Hndl, const AT_WC* Feature, int Index, AT_BOOL* Available);
        #int AT_IsEnumeratedIndexImplemented(AT_H Hndl, const AT_WC* Feature, int Index, AT_BOOL* Implemented);
        #int AT_SetEnumerated(AT_H Hndl, const AT_WC* Feature, int Value);
        #int AT_SetEnumeratedString(AT_H Hndl, const AT_WC* Feature, const AT_WC* String);
        #int AT_GetEnumerated(AT_H Hndl, const AT_WC* Feature, int* Value);
        #int AT_GetEnumeratedCount(AT_H Hndl,const  AT_WC* Feature, int* Count);
        #int AT_GetEnumeratedString(AT_H Hndl, const AT_WC* Feature, int Index, AT_WC* String, int StringLength);


        import os
#        self.lib = self.ffi.verify('#include "atutility.h"', include_dirs=[os.path.dirname(__file__) + '/include'], library_dirs=[os.path.dirname(__file__) + '/libs'], libraries=["atcore"])
        self.lib = self.ffi.dlopen('atcore')

        self.handle_return(self.lib.AT_InitialiseLibrary())
        self.__updated_features = []

    def __del__(self):
        self.handle_return(self.lib.AT_FinaliseLibrary())

    def __feature_updated(self, feature_name):
        if feature_name not in self.__updated_features:
            self.__updated_features.append(feature_name)
    
    def get_updated_features(self):
        return self.__updated_features

    def handle_return(self,ret_value):
        if ret_value != 0:
            raise ATCoreException('{} ({})'.format(ret_value, self._ERRORS[ret_value]))
        return ret_value

    def get_version(self):
        return self.__version__

    def open(self, index):
        """Open camera AT_H.
        """
        result = self.ffi.new("AT_H *")
        self.handle_return(self.lib.AT_Open(index, result))

        return result[0]

    def close(self, AT_H):
        """Close camera AT_H.
        """
        self.handle_return(self.lib.AT_Close(AT_H))

    def initialise(self):
        """Initialise the SDK.
        """
        self.handle_return(self.lib.AT_InitialiseLibrary())
    
    def finalise(self):
        """Finalise the SDK.
        """
        self.handle_return(self.lib.AT_FinaliseLibrary())

    def is_implemented(self, AT_H, command):
        """Checks if command is implemented.
        """
        result = self.ffi.new("AT_BOOL *")
        self.handle_return(self.lib.AT_IsImplemented(AT_H, u(command), result))
        return result[0]

    def is_readable(self, AT_H, command):
        """Checks if command is readable.
        """
        result = self.ffi.new("AT_BOOL *")
        self.handle_return(self.lib.AT_IsReadable(AT_H, u(command), result))
        return result[0]

    def is_writable(self, AT_H, command):
        """Checks if command is writable.
        """
        result = self.ffi.new("AT_BOOL *")
        self.handle_return(self.lib.AT_IsWritable(AT_H, u(command), result))
        return result[0]

    def is_readonly(self, AT_H, command):
        """Checks if command is read only.
        """
        result = self.ffi.new("AT_BOOL *")
        self.handle_return(self.lib.AT_IsReadOnly(AT_H, u(command), result))
        return result[0]

    def set_int(self, AT_H, command, value):
        """SetInt function.
        """
        self.__feature_updated(command)
        self.handle_return(self.lib.AT_SetInt(AT_H, u(command), value))

    def get_int(self, AT_H, command):
        """Run command and get Int return value.
        """
        result = self.ffi.new("AT_64 *")
        self.handle_return(self.lib.AT_GetInt(AT_H, u(command), result))
        return result[0]

    def get_int_max(self, AT_H, command):
        """Run command and get maximum Int return value.
        """
        result = self.ffi.new("AT_64 *")
        self.handle_return(self.lib.AT_GetIntMax(AT_H, u(command), result))
        return result[0]

    def get_int_min(self, AT_H, command):
        """Run command and get minimum Int return value.
        """
        result = self.ffi.new("AT_64 *")
        self.handle_return(self.lib.AT_GetIntMin(AT_H, u(command), result))
        return result[0]

    def set_float(self, AT_H, command, value):
        """Set command with Float value parameter.
        """
        self.__feature_updated(command)
        self.handle_return(self.lib.AT_SetFloat(AT_H, u(command), value))

    def get_float(self, AT_H, command):
        """Run command and get float return value.
        """
        result = self.ffi.new("double *")
        self.handle_return(self.lib.AT_GetFloat(AT_H, u(command), result))
        return result[0]

    def get_float_max(self, AT_H, command):
        """Run command and get maximum float return value.
        """
        result = self.ffi.new("double *")
        self.handle_return(self.lib.AT_GetFloatMax(AT_H, u(command), result))
        return result[0]

    def get_float_min(self, AT_H, command):
        """Run command and get minimum float return value.
        """
        result = self.ffi.new("double *")
        self.handle_return(self.lib.AT_GetFloatMin(AT_H, u(command), result))
        return result[0]

    def get_bool(self, AT_H, command):
        """Run command and get Bool return value.
        """
        result = self.ffi.new("AT_BOOL *")
        self.handle_return(self.lib.AT_GetBool(AT_H, u(command), result))
        return result[0]

    def set_bool(self, AT_H, command, value):
        """Set command with Bool value parameter.
        """
        self.__feature_updated(command)
        self.handle_return(self.lib.AT_SetBool(AT_H, u(command), value))

    def set_enumerated(self, AT_H, command, value):
        """Set command with Enumerated value parameter.
        """
        self.__feature_updated(command)
        self.handle_return(self.lib.AT_SetEnumerated(AT_H, u(command), value))

    def set_enumerated_string(self, AT_H, command, item):
        """Set command with EnumeratedString value parameter.
        """
        self.__feature_updated(command)
        self.handle_return(self.lib.AT_SetEnumString(AT_H, u(command), u(item)))

    def get_enumerated(self, AT_H, command):
        """Run command and set Enumerated return value.
        """
        result = self.ffi.new("int *")
        self.handle_return(self.lib.AT_GetEnumIndex(AT_H, u(command), result))
        return result[0]

    def get_enumerated_string_options(self, AT_H, command) :
        """Get list of option strings
        """
        count = self.get_enumerated_count(AT_H, command)
        strings = []
        for i in range(0, count):
            strings.append(self.get_enumerated_string_by_index(AT_H, u(command),i))
        return strings

    def get_enumerated_string(self, AT_H, command, result_length=128):
        """Run command and set Enumerated return value.
        """
        ret = self.get_enumerated(AT_H, command)
        return self.get_enumerated_string_by_index(AT_H, u(command), ret)

    def get_enumerated_count(self, AT_H, command):
        """Run command and set Enumerated return value.
        """
        result = self.ffi.new("int *")
        self.handle_return(self.lib.AT_GetEnumCount(AT_H, u(command), result))
        return result[0]

    def is_enumerated_index_available(self, AT_H, command, index):
        """Check if enumerated index is available
        """
        result = self.ffi.new("AT_BOOL *")
        self.handle_return(self.lib.AT_IsEnumIndexAvailable(AT_H, u(command), index, result))
        return result[0]

    def get_enumerated_index_by_string(self, AT_H, command, item):
        """Get enumerated index of particular string.
        """
        result = self.ffi.new("int *")
        count = self.get_enumerated_count(AT_H, command)
        for i in range(0, count):
            if self.get_enumerated_string_by_index(AT_H, u(command),i) == item:
                return i

        return -1

    def is_enumerated_string_available(self, AT_H, command, item):
        """Check if enumerated string is available
        """
        result = self.ffi.new("AT_BOOL *")
        index = self.get_enumerated_index_by_string(AT_H, command, item)
        self.handle_return(self.lib.AT_IsEnumIndexAvailable(AT_H, u(command), index, result))
        return result[0]

    def is_enumerated_index_implemented(self, AT_H, command, index):
        """Check if enumerated index is implemented
        """
        result = self.ffi.new("AT_BOOL *")
        self.handle_return(self.lib.AT_IsEnumIndexImplemented(AT_H, u(command), index, result))
        return result[0]

    def get_enumerated_string_by_index(self, AT_H, command, index, result_length=128):
        """Get command with EnumeratedString value parameter.
        """
        result = self.ffi.new("AT_WC [%s]" % result_length)
        self.handle_return(self.lib.AT_GetEnumStringByIndex(AT_H, u(command), index, result, result_length))
        return self.ffi.string(result)

    def command(self, AT_H, command):
        """Run command.
        """
        self.handle_return(self.lib.AT_Command(AT_H, u(command)))

    def set_string(self, AT_H, command, strvalue):
        """SetString function.
        """
        self.__feature_updated(command)
        self.handle_return(self.lib.AT_SetString(AT_H, u(command), u(strvalue)))

    def get_string(self, AT_H, command, result_length=0):
        """Run command and get string return value.
        """
        if result_length == 0 :
            result_length = self.get_string_max_length(AT_H, command)
        result = self.ffi.new("AT_WC [%s]" % result_length)
        self.handle_return(self.lib.AT_GetString(AT_H, u(command), result, result_length))
        return self.trim_bom(result)

    def trim_bom(self, result):
        try:
            return self.ffi.string(result)
        except ValueError as e:
            return self.trim_bom(result[1:len(result)-1])

    def get_string_max_length(self, AT_H, command):
        """Run command and get maximum Int return value.
        """
        result = self.ffi.new("int *")
        self.handle_return(self.lib.AT_GetStringMaxLength(AT_H, command, result))
        return result[0]

    def queue_buffer(self, AT_H, buf_ptr, buffer_size):
        """Put buffer in queue.
        """
        self.handle_return(self.lib.AT_QueueBuffer(AT_H, self.ffi.cast("AT_U8 *", buf_ptr), buffer_size))

    def wait_buffer(self, AT_H, timeout=20000):
        """Wait for next buffer to fill.
        """
        buf_ptr = self.ffi.new("AT_U8 **")
        buffer_size = self.ffi.new("int *")
        self.handle_return(self.lib.AT_WaitBuffer(AT_H, buf_ptr, buffer_size, int(timeout)))
        return (buf_ptr, buffer_size[0])

    def flush(self, AT_H):
        self.handle_return(self.lib.AT_Flush(AT_H))

    def build_callback(self, func):
        return self.ffi.callback("int(*)(AT_H, AT_WC *, void *)", func)

    def register_feature_callback(self, AT_H, feature, func):
        """RegisterFeatureCallback function.
        """
        self.handle_return(self.lib.AT_RegisterFeatureCallback(AT_H, u(feature), func,
                                                                   self.ffi.NULL))

    def unregister_feature_callback(self, AT_H, feature, func):
        """RegisterFeatureCallback function.
        """
        self.handle_return(self.lib.AT_UnregisterFeatureCallback(AT_H, u(feature), func,
                                                                   self.ffi.NULL))
