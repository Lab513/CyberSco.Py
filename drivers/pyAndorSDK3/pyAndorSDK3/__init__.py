__title__ = 'pyAndorSDK3'

__authors__ = 'Andor SDK3 team'
__email__ = "scmossupport@andor.com"

__license__ = 'Andor internal'
__copyright__ = 'Copyright 2017 Andor'

import os, sys
_path = os.path.dirname(__file__) + '/libs;' + os.environ['PATH']
os.environ['PATH'] = _path

from pyAndorSDK3._version import __version__, __version_info__

from pyAndorSDK3.andor_sdk3 import AndorSDK3
from pyAndorSDK3.andor_camera import CameraException
from pyAndorSDK3.andor_acquisition import Acquisition

__all__ = [
    'AndorSDK3', 'CameraException', 'Acquisition',
    '__title__', '__authors__', '__email__',
    '__license__', '__copyright__', '__version__', '__version_info__',
]

