// This is a wrapper class that uses the lodepng library to
// load in a .png image.  Load it in by passing in a pathname
// to the file in the constructor.  If you put the images in
// the "Visual Studio/Projects/MyProjectName/MyProjectName" folder 
// then you can just pass in the name of the file (e.g. "img1.png")
// and it will load in the file.
//
// Once an image is loaded use getWidth(), getHeight() and
// getRGB to retrieve the color of a pixel in the png file.
#pragma once
#include <vector>
#include "lodepng.h"
using namespace std;
class PngImage
{
public:
	PngImage();
	PngImage(char *pathname);
	~PngImage();
	void loadImage(char *pathname);
	int getWidth();
	int getHeight();
	void getRGB(int x, int y, int &r, int &g, int &b);
private:	
	vector<unsigned char> img;
	unsigned int width, height;
};

