/*
   FileName:      imageoutput.cpp

   Created Time:  2015-09-13

   Auther:        Cao Jiayin

   Email:         soraytrace@hotmail.com

   Location:      China, Shanghai

   Description:   SORT is short for Simple Open-source Ray Tracing. Anyone could checkout the source code from
                'sourceforge', https://soraytrace.svn.sourceforge.net/svnroot/soraytrace. And anyone is free to
                modify or publish the source code. It's cross platform. You could compile the source code in 
                linux and windows , g++ or visual studio 2008 is required.
*/

#include "imageoutput.h"

// allocate memory in sort
void ImageOutput::SetImageSize( int w , int h )
{
	SORTOutput::SetImageSize( w , h );

	m_rendertarget.SetSize( w , h );
}

// store pixel information
void ImageOutput::StorePixel( int x , int y , const Spectrum& color , const RenderTask& rt )
{
	m_rendertarget.SetColor( x , y , color );
}

// pre process
void ImageOutput::PreProcess()
{
}

// post process
void ImageOutput::PostProcess()
{
	m_rendertarget.Output("result.bmp");
}