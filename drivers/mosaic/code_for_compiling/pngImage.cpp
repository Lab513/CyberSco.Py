// Wrapper class around the lodepng library to
// load in a .png file.
#include <iostream>
#include "pngImage.h"
#include "pngImage.h"

using namespace std;

// Default constructor just sets the dimensions to zero
PngImage::PngImage()
{
	width = 0;
	height = 0;
}

PngImage::~PngImage()
{
}

// This constructor loads in the image passed in
PngImage::PngImage(char *pathname)
{
	if (pathname[0] != '\0')
		loadImage(pathname);
}

// This uses the lodepng library to load in a PNG image
void PngImage::loadImage(char *pathname)
{
	vector<unsigned char> pngTemp;
	lodepng::load_file(pngTemp, pathname);
	unsigned error = lodepng::decode(img, width, height, pngTemp);
	if (error)
	{
		cout << "png Error: " << error << " " << lodepng_error_text(error) << endl;
		system("pause");
		exit(0);
	}
}
// Retrieve width of the loaded image
int PngImage::getWidth()
 {
	 return width;
 }

// Retrieve height of the loaded image
int PngImage::getHeight()
 {
	 return height;
 }

// Retrieve the RGB of a pixel (each R,G,B is in the range 0-255)
// of the pixel at coordinate x,y.  The RGB color is black if
// it is outside the dimensions of the loaded image.
void PngImage::getRGB(int x, int y, int &r, int &g, int &b)
 {
	if (x < 0 || y < 0 || x > width || y > height)
	{
		r = 0;
		g = 0;
		b = 0;
	}
	// This retrieves the color from the img loaded from
	// the lodepng library.  It ignored the alpha channel value
	// which controls transparency.
	if ((height > 0) && (width > 0))
	{
		r = img[4 * y*width + 4 * x + 0];
		g = img[4 * y*width + 4 * x + 1];
		b = img[4 * y*width + 4 * x + 2];
	}
 }

