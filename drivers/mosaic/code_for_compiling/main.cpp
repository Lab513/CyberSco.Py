#include "atcore.h"
#include <iostream>
#include <conio.h>
#include "main.h"
#include "pngImage.h"
#include <windows.h>

using namespace std;

// loading png image on the DMD

AT_H Handle;
AT_64 i64_sensorWidth;
AT_64 i64_sensorHeight;

unsigned char* UserBuffer;
int BufferSize;
PngImage image;

void load_image_for_infos(){

	image.loadImage( (char*)"image_for_mosaic.png" );

	memset(UserBuffer, 0, BufferSize );

	std::cout << "image.getHeight(): " << image.getHeight()  << std::endl;
	std::cout << "image.getWidth(): " << image.getWidth()  << std::endl;

}

void watch_Buffer(){

	for (int i=0; i < BufferSize; i++){
		std::cout << UserBuffer[i] << std::endl;
	 }

}

void load_Buffer()
{

	  load_image_for_infos();

		for (int j = 0; j < image.getHeight(); j++)
			for (int i = 0; i < image.getWidth(); i++)
			{
				int r, g, b;
				image.getRGB(i, j, r, g, b);
				if ((i>136) && (i < 215) && (j > 366) && (j<492))
				{
					if ((g - 30 > r) && (g - 30 > b))
					{
						g = g / 3;
						r = r * 3;
					}
				}
			UserBuffer[j*image.getWidth()+i] = r;
			//std::cout << r << std::endl;
			}

}

void ClearMemory()
{
  AT_Command(Handle, L"ClearSequenceMemory");
  AT_Command(Handle, L"ClearFrameMemory");
}

void UploadGrayScaleImage()

{
  int retCode = AT_SetFloat(Handle, L"GrayScaleExposureTime", 0.05);
  retCode = AT_SetEnumString(Handle, L"GrayScaleSequenceEncoding", L"8BitDIP");
  retCode = AT_Command(Handle, L"UploadGrayScaleImage");
}

int char_to_digit(char* c) {
	  char** words = new char* [strlen(c)];
		float val = atof(c);
    return val;
}

void DisplayGrayScaleImage( float exptime )
{
  int retCode = AT_SetInt(Handle, L"SequenceStartIndex", 0);
  retCode = AT_SetInt(Handle, L"SequenceLoopLength", 8);
  //retCode = AT_SetEnumString(Handle, L"OperationMode", L"ContinuousFrameSequence");
	AT_SetFloat(Handle, L"ExposureTime", exptime);                                           // Exposure time
  retCode = AT_Command(Handle, L"Expose");
}

int main( int argc, char* argv[] )
{

  AT_InitialiseLibrary();
  AT_Open(0, &Handle);

  //Get the sensor width
  AT_GetInt(Handle, L"SensorWidth", &i64_sensorWidth);

  //Get the sensor height
  AT_GetInt(Handle, L"SensorHeight", &i64_sensorHeight);

  AT_64 ImageSizeBytes;
  //Get the number of bytes required to store one frame
  AT_GetInt(Handle, L"ImageSizeBytes", &ImageSizeBytes);

	BufferSize = static_cast<int>( ImageSizeBytes );
	std::cout << "ImageSizeBytes " << ImageSizeBytes << endl;

  //Allocate a memory buffer to store one frame
  UserBuffer = new unsigned char[BufferSize];

  AT_QueueBuffer(Handle, UserBuffer, BufferSize);    //Pass this buffer to the SDK

  //Clear existing frames in memory
  ClearMemory();

  //Load a gray scale image to the user buffer
	load_Buffer();

  // watch_Buffer()

  //Upload the gray scale image to Frame Memory and Sequence Memory
  UploadGrayScaleImage();

  //Display the gray scale image
	std::cout << "Exposure time is  " << argv[1] << " seconds  " << endl;
  DisplayGrayScaleImage( char_to_digit( argv[1] ) );

	AT_BOOL IsExposing;
	do {
		AT_GetBool(Handle, L"IsExposing", &IsExposing);
	}
	while (IsExposing == TRUE);

	delete [] UserBuffer;

  AT_Close(Handle);
  AT_FinaliseLibrary();

}
