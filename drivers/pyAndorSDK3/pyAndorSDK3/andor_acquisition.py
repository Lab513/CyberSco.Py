from math import ceil
import numpy as np
import matplotlib.pyplot as plt
import os

import warnings
warnings.filterwarnings('ignore', 'PyFITS is deprecated')
#import pyfits as fits
import astropy.io.fits as fits

from pyAndorSDK3.utils import lazy_prop, dyn_prop
from pyAndorSDK3.andor_utility import ATUtility

atutil = ATUtility()

class Acquisition(object):

    def __init__(self, np_data, config):
        self._np_data = np_data
        self._config = config

        if config['MetadataEnable']:
            self.metadata = Metadata(np_data, config)

    @lazy_prop

    # image function needs to be improved as it doesn't work smoothly (np_d.reshape cuasing some issues)
    def image(self):
        np_d = self._correct_for_encoding(self._np_data[0:self._config['aoiheight'] * self._config['aoistride']])
        np_d = np_d.reshape(self._config['aoiheight'], np_d.size//self._config['aoiheight'])
        return np_d[0:self._config['aoiheight'], 0:self._config['aoiwidth']]

    def _correct_for_encoding(self, np_arr):
        if self._config["pixelencoding"].lower() in ("mono12", "mono16"):
            return np_arr.view(dtype='H')
        elif self._config["pixelencoding"].lower() == "mono32":
            return np_arr.view(dtype='I')
        elif self._config["pixelencoding"].lower() == "mono12packed":
            if not hasattr(self, "_np_unpacked"):
                self._np_unpacked = np.empty((self._config['aoiheight'] *
                                              self._config['aoiwidth'] * 2), dtype='B')
                atutil.unpack(np_arr.ctypes.data, self._np_unpacked.ctypes.data,
                              self._config['aoiwidth'], self._config['aoiheight'],
                              self._config['aoistride'], "Mono12Packed", "Mono16")
            return self._np_unpacked.view(dtype='H')

    def save(self, path, overwrite_if_exist=False):
        if  path.split('.')[-1] == 'fits':
            hdu = fits.PrimaryHDU(self.image)
            hdulist= fits.HDUList([hdu])
            for k,v in self._config.items():
                try:
                    hdulist[0].header["HIERARCH " + k.upper()] = v
                except:
                    pass

            if overwrite_if_exist:
                try:
                    os.remove(path)
                except Exception:
                    pass
            hdulist.writeto(path)
        else:
            raise NotImplementedError

    def show(self, cmap="Greys_r"):
        plt.imshow(np.fliplr(np.rot90(self.image, 3)), cmap=cmap)


class Metadata(object):

    def __init__(self, np_data, config):
        self._np_data = np_data
        self._config = config

        if self._config['MetadataTimestamp']:
            self.timestamp = self.get_timestamp()

        if self._config['MetadataIRIG']:
            if 'IRIGClockFrequency' in self._config:
                self.irig_nanoseconds, self.irig_seconds, self.irig_minutes, self.irig_hours, self.irig_days, self.irig_years = self.get_extended_irig()
            else :
                self.irig_seconds, self.irig_minutes, self.irig_hours, self.irig_days, self.irig_years = self.get_irig()
                self.irig_nanoseconds = 0

        if self._config['MetadataFrameInfo']:
            self.width = self.get_width()
            self.height = self.get_height()
            self.stride = self.get_stride()
            self.pixelencoding = self.get_pixel_encoding()

    def get_timestamp(self):
        return atutil.getTimeStampFromMetadata(self._np_data.ctypes.data, self._config['imagesizebytes'])

    def get_extended_irig(self):
        return atutil.getExtendedIRIGDataFromMetadata(self._np_data.ctypes.data, self._config['imagesizebytes'], self._config['irigclockfrequency'])

    def get_irig(self):
        return atutil.getIRIGDataFromMetadata(self._np_data.ctypes.data, self._config['imagesizebytes'])

    def get_width(self):
        return atutil.getWidthFromMetadata(self._np_data.ctypes.data, self._config['imagesizebytes'])

    def get_height(self):
        return atutil.getHeightFromMetadata(self._np_data.ctypes.data, self._config['imagesizebytes'])

    def get_stride(self):
        return atutil.getStrideFromMetadata(self._np_data.ctypes.data, self._config['imagesizebytes'])

    def get_pixel_encoding(self):
        return atutil.getPixelEncodingFromMetadata(self._np_data.ctypes.data, self._config['imagesizebytes'])
