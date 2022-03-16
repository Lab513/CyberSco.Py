***********
pyAndorSDK3
***********

----

-----------
Information
-----------

Python Wrapper for Andor SDK3

Contains wrapper interface and SDK3 libraries

Supported platforms: Python3.5.1 +

------------
Installation
------------
Installation depending on your python installation:

Open command console within the same directory as the setup.py:

- python3 –m pip install .

Also:

- pip3 install .
- pip3 list
- pip3 uninstall pyAndorSDK3

'sudo' as necessary for Linux

Any errors or suggestions, please report.

----

---------------------------
Example Initialise and Open
---------------------------

Include and initialse AndorSDK3:

.. code-block:: python

    from pyAndorSDK3 include AndorSDK3
    sdk3 = pyAndorSDK3()

There are two ways to retrieve cameras

1 - Open and retrieve specific camera by index (e.g. for camera at index zero):

.. code-block:: python

    cam = sdk3.GetCamera(0)

2 - Open and retrieve a list of all cameras on the system:

.. code-block:: python

    cameras = sdk3.cameras
    cam1 = cameras[0]
    cam2 = cameras[1]

.. raw:: pdf

   PageBreak
---------------------------
Example Camera Object Usage
---------------------------

+-------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
| Example Code                                          | Description                                                                                                              |
+=======================================================+==========================================================================================================================+
| val = cam.FeatureName                                 | Gets the value of FeatureName                                                                                            |
+-------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
| cam.FeatureName = val                                 | Sets the FeatureName to the value held by the "val" variable                                                             |
+-------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
| val = cam.CmdFeatureName()                            | Executes the Command Feature with the name CmdFeatureName                                                                |
+-------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
| val = cam.max_FeatureName                             | Gets the maximum value of FeatureName                                                                                    |
+-------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
| val = cam.min_FeatureName                             | Gets the minimum value of FeatureName                                                                                    |
+-------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
| opts = cam.options_EnumFeatureName                    | Gets the list of legal options for the EnumFeatureName feature                                                           |
+-------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
| avail = cam.is_available_EnumFeatureName("EnumEntry") | Gets the availablity of a given EnumEntry for an EnumFeature (an EnumEntry maybe legal but unavailable at certain times) |
+-------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
| avail_opts = cam.available_options_EnumFeatureName    | Gets the list of available options for the EnumFeatureName feature                                                       |
+-------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+
| feat_type = cam.type_FeatureName                      | Gets the feature type of FeatureName (dictated by andor_strings.py)                                                      |
+-------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------+

.. raw:: pdf

   PageBreak

^^^^^^^^^
Acquiring
^^^^^^^^^

.. table::
    :widths: 36 40

    +----------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
    | Example Code                                 | Description                                                                                                                               |
    +==============================================+===========================================================================================================================================+
    | img = cam.acquire()                          | Acquires a single image - returns an Acquisition object                                                                                   |
    +----------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
    | imgs = cam.acquire_series()                  | Acquires <FrameCount> images and returns a list of Acquisition objects                                                                    |
    +----------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+
    | imgs = cam.get_previous_acquisition_series() | Returns the list of images from the previous acquire_series (useful for retrieval of images when acquire_series failed with an exception) |
    +----------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------+

With both the acquire and acquire_series it is possible to pass in features and values you wish to assign for the acquisition(s), and other keyword values for the acquisition. E.g.:

- img = cam.acquire(("ElectronicShutteringMode","Rolling"), timeout=1000)
- imgs = cam.acquire_series(("CycleMode","Fixed"),("FrameCount",100),timeout=5000, max_buf=10, circ_buf=True)

Optional keyword parameters for acquire_series

.. table::
    :widths: 15 6 10 25

    +--------------------+-------+---------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
    | Keyword            | Type  | Default                               |Description                                                                                                                                      |
    +====================+=======+=======================================+=================================================================================================================================================+
    | timeout            | int   | max(5000, ceil(5000 / cam.FrameRate)) |  Sets the timeout of each image                                                                                                                 |
    +--------------------+-------+---------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
    | min_buf            | int   | 2                                     | Sets the minimum num buffers to be queued                                                                                                       |
    +--------------------+-------+---------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
    | max_buf            | int   | 25                                    | The maximum number of buffers to be assigned before acquisition begins (this is also the muber of buffers used when circular buffer is enabled) |
    +--------------------+-------+---------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
    | circ_buf           | bool  | False                                 | Use the assigned buffers in a circular fashion (normal running will create a new buffer for each new acquisition)                               |
    +--------------------+-------+---------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
    | print_frame        | bool  | False                                 | Print the data in the acquired frames as they are acquired                                                                                      |
    +--------------------+-------+---------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
    | print_fps          | bool  | False                                 | Enable to print Effective FrameRate during the acquisition series                                                                               |
    +--------------------+-------+---------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
    | print_fps_interval | int   | 1                                     | The number of frames to acquire before printing Effective FrameRate                                                                             |
    +--------------------+-------+---------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+
    | pause_after        | float | 0.0                                   | Pause for the specified num seconds after all acquisitions are acquirired                                                                       |
    +--------------------+-------+---------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------+

The acquire and acquire_series functions can used as a basis to build custom acquisition functions along with the example custom_acquisition.py

.. raw:: pdf

   PageBreak

Acquisition Object
------------------

The Acquisition objects can be interected with in the following ways:

+----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Example Code                           | Description                                                                                                                                                         |
+========================================+=====================================================================================================================================================================+
| img.image()                            | Returns a numpy array of the image acquired                                                                                                                         |
+----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| imgs[2].save("/path/to/file/filename") | Saves the second image in a series to path '/path/to/file' and file name "filename.fits" (Set optional param 'overwrite_if_exist' to True to force overwrite files) |
+----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| img.show()                             | Displays the image using matplotlib                                                                                                                                 |
+----------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Image Metadata
^^^^^^^^^^^^^^
 TimeStamp Metadata

+------------------------------+----------------------------------------+
| MetdataTimeStamp Options     | Description                            |
+==============================+========================================+
| val = img.metadata.timestamp | Returns the value of MetadataTimestamp |
+------------------------------+----------------------------------------+

 Frame Info Metadata

+----------------------------------+-------------------------------------------------------+
| MetatadaFrameInfo Options        | Description                                           |
+==================================+=======================================================+
| val = img.metadata.width         | Returns value of width from MetadataFrameInfo         |
+----------------------------------+-------------------------------------------------------+
| val = img.metadata.height        | Returns value of height from MetadataFrameInfo        |
+----------------------------------+-------------------------------------------------------+
| val = img.metadata.stride        | Returns value of stride from MetadataFrameInfo        |
+----------------------------------+-------------------------------------------------------+
| val = img.metadata.pixelencoding | Returns value of pixelencoding from MetadataFrameInfo |
+----------------------------------+-------------------------------------------------------+

 IRIG Metadata

+-------------------------------------+-------------------------------------------------+
| MetatadaIRIGB Options               | Description                                     |
+=====================================+=================================================+
| val = img.metadata.irig_nanoseconds | Returns value of nanoseconds from MetadataIRIGB |
+-------------------------------------+-------------------------------------------------+
| val = img.metadata.irig_seconds     | Returns value of seconds from MetadataIRIGB     |
+-------------------------------------+-------------------------------------------------+
| val = img.metadata.irig_minutes     | Returns value of minutes from MetadataIRIGB     |
+-------------------------------------+-------------------------------------------------+
| val = img.metadata.irig_hours       | Returns value of hours from MetadataIRIGB       |
+-------------------------------------+-------------------------------------------------+
| val = img.metadata.irig_days        | Returns value of days from MetadataIRIGB        |
+-------------------------------------+-------------------------------------------------+
| val = img.metadata.irig_years       | Returns value of years from MetadataIRIGB       |
+-------------------------------------+-------------------------------------------------+

----

For SDK3 usage or feature specific information please refer to the manual Andor Software Development Kit 3.pdf