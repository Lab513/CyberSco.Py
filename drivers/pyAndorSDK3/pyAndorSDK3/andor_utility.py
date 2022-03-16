import sys
if sys.version < '3':
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x

class ATUtilityException(Exception): pass

class ATUtility(object):

    _ERRORS = {
        1002: "AT_ERR_INVALIDOUTPUTPIXELENCODING",
        1003: "AT_ERR_INVALIDINPUTPIXELENCODING",
        1004: "AT_ERR_INVALIDMETADATAINFO",
        1005: "AT_ERR_CORRUPTEDMETADATA",
        1006: "AT_ERR_METADATANOTFOUND",
        1008: "AT_ERR_INVALIDFORMAT",
        1009: "AT_ERR_INVALIDPATH",
        1010: "AT_ERR_NO_NEW_DATA",
        1011: "AT_ERR_SPOOLING_NOT_CONFIGURED",
   }
    __version__ = '0.1'
    LIBRARY_NAME = 'atutility'

    def __init__(self):
        from cffi import FFI
        self.ffi = FFI()
        self.ffi.set_unicode(True)
        self.C = self.ffi.cdef("""
        typedef long long AT_64;
        typedef unsigned char AT_U8;
        typedef wchar_t AT_WC;
        typedef int AT_H;

        int AT_ConvertBuffer(AT_U8* inputBuffer, AT_U8* outputBuffer, AT_64 width, AT_64 height, AT_64 stride, const AT_WC * inputPixelEncoding, const AT_WC * outputPixelEncoding);
        int AT_ConvertBufferUsingMetadata(AT_U8* inputBuffer, AT_U8* outputBuffer, AT_64 imagesizebytes, const AT_WC * outputPixelEncoding);

        int AT_GetWidthFromMetadata(AT_U8* inputBuffer, AT_64 imagesizebytes, AT_64* width);
        int AT_GetHeightFromMetadata(AT_U8* inputBuffer, AT_64 imagesizebytes, AT_64* height);
        int AT_GetStrideFromMetadata(AT_U8* inputBuffer, AT_64 imagesizebytes, AT_64* stride);
        int AT_GetPixelEncodingFromMetadata(AT_U8* inputBuffer, AT_64 imagesizebytes, AT_WC* pixelEncoding, AT_U8 pixelEncodingSize);
        int AT_GetTimeStampFromMetadata(AT_U8* inputBuffer, AT_64 imagesizebytes, AT_64* timeStamp);
        int AT_GetIRIGFromMetadata(AT_U8* inputBuffer, AT_64 imagesizebytes, AT_64* seconds, AT_64* minutes, AT_64* hours, AT_64* days, AT_64* years);
        int AT_GetExtendedIRIGFromMetadata(AT_U8* inputBuffer, AT_64 imagesizebytes, AT_64 clockfrequency, double* nanoseconds, AT_64* seconds, AT_64* minutes, AT_64* hours, AT_64* days, AT_64* years);

        //int AT_ConfigureSpooling(AT_H camera, const AT_WC* format, const AT_WC* path);
        //int AT_GetSpoolProgress(AT_H camera, int * imageNumber);
        //int AT_GetMostRecentImage(AT_H camera, AT_U8* buffer, int bufferSize);

        int AT_InitialiseUtilityLibrary();
        int AT_FinaliseUtilityLibrary();

        """)

        import os
#        self.lib = self.ffi.verify('#include "atutility.h"', include_dirs=[os.path.dirname(__file__) + '/include'], library_dirs=[os.path.dirname(__file__) + '/libs'], libraries=["atutility"])
        self.lib = self.ffi.dlopen("C:\\Program Files\\Andor Mosaic 3 Driver Pack\\atutility.dll")

        self.handle_return(self.lib.AT_InitialiseUtilityLibrary())

    def __del__(self):
        self.handle_return(self.lib.AT_FinaliseUtilityLibrary())

    def handle_return(self,ret_value):
        if ret_value != 0:
            raise ATUtilityException('{} ({})'.format(ret_value, self._ERRORS[ret_value]))
        return ret_value

    def unpack (self, input_buf, output_buf, width, height, stride, in_format,
                out_format):
        self.handle_return(self.lib.AT_ConvertBuffer(self.ffi.cast("AT_U8 *", input_buf),
                                                     self.ffi.cast("AT_U8 *", output_buf),
                                                     width, height, stride, u(in_format),
                                                     u(out_format)))

    def getWidthFromMetadata(self, input_buf, imagesizebytes):
        """
        @return: width
        """
        result = self.ffi.new("AT_64 *")
        self.handle_return(self.lib.AT_GetWidthFromMetadata(self.ffi.cast("AT_U8 *", input_buf),
                                                            imagesizebytes,
                                                            result))
        return result[0]

    def getHeightFromMetadata(self, input_buf, imagesizebytes):
        """
        @return: height
        """
        result = self.ffi.new("AT_64 *")
        self.handle_return(self.lib.AT_GetHeightFromMetadata(self.ffi.cast("AT_U8 *", input_buf),
                                                             imagesizebytes,
                                                             result))
        return result[0]

    def getStrideFromMetadata(self, input_buf, imagesizebytes):
        """
        @return: stride
        """
        result = self.ffi.new("AT_64 *")
        self.handle_return(self.lib.AT_GetStrideFromMetadata(self.ffi.cast("AT_U8 *", input_buf),
                                                             imagesizebytes,
                                                             result))
        return result[0]

    def getPixelEncodingFromMetadata(self, input_buf, imagesizebytes):
        """
        @return: pixelEncoding
        """
        pixelEncodingSize = 32
        result = self.ffi.new("AT_WC [%s]" % pixelEncodingSize)
        self.handle_return(self.lib.AT_GetPixelEncodingFromMetadata(self.ffi.cast("AT_U8 *", input_buf),
                                                                    imagesizebytes,
                                                                    result,
                                                                    self.ffi.cast("AT_U8 ", pixelEncodingSize)))
        return self.ffi.string(result)

    def getTimeStampFromMetadata(self, input_buf, imagesizebytes):
        """
        @return: timeStamp
        """
        result = self.ffi.new("AT_64 *")
        self.handle_return(self.lib.AT_GetTimeStampFromMetadata(self.ffi.cast("AT_U8 *", input_buf),
                                                                imagesizebytes,
                                                                result))
        return result[0]

    def getIRIGDataFromMetadata(self, input_buf, imagesizebytes):
        """
        @return: seconds, minutes, hours, days, years
        """
        seconds = self.ffi.new("AT_64 *")
        minutes = self.ffi.new("AT_64 *")
        hours = self.ffi.new("AT_64 *")
        days = self.ffi.new("AT_64 *")
        years = self.ffi.new("AT_64 *")
        self.handle_return(self.lib.AT_GetIRIGFromMetadata(self.ffi.cast("AT_U8 *", input_buf),
                                                           imagesizebytes,
                                                           seconds,
                                                           minutes,
                                                           hours,
                                                           days,
                                                           years))
        return seconds[0], minutes[0], hours[0], days[0], years[0]

    def getExtendedIRIGDataFromMetadata(self, input_buf, imagesizebytes, clockfrequency):
        """
        @return: nanoseconds, seconds, minutes, hours, days, years
        """
        nanoseconds = self.ffi.new("double *")
        seconds = self.ffi.new("AT_64 *")
        minutes = self.ffi.new("AT_64 *")
        hours = self.ffi.new("AT_64 *")
        days = self.ffi.new("AT_64 *")
        years = self.ffi.new("AT_64 *")
        self.handle_return(self.lib.AT_GetExtendedIRIGFromMetadata(self.ffi.cast("AT_U8 *", input_buf),
                                                                    imagesizebytes,
                                                                    clockfrequency,
                                                                    nanoseconds,
                                                                    seconds,
                                                                    minutes,
                                                                    hours,
                                                                    days,
                                                                    years))
        return nanoseconds[0], seconds[0], minutes[0], hours[0], days[0], years[0]

    # def configureSpooling(self, cam, format, path):
    #     self.handle_return(self.lib.AT_ConfigureSpooling(cam,
    #                                                      self.ffi.cast("AT_WC *", format),
    #                                                      self.ffi.cast("AT_WC *", path)))

    # def getSpoolProgress(self, cam, imageNumber):
    #     self.handle_return(self.lib.AT_GetSpoolProgress(cam,
    #                                                     self.ffi.cast("int *", imageNumber)))

    # def getMostRecentImage(self, cam, input_buf, bufferSize):
    #     self.handle_return(self.lib.AT_GetMostRecentImage(cam,
    #                                                       self.ffi.cast("AT_U8 *", input_buf),
    #                                                       bufferSize))
