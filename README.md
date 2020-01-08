<!--
    This file is a part of SORT(Simple Open Ray Tracing), an open-source cross
    platform physically based renderer.

    Copyright (c) 2011-2020 by Jiayin Cao - All rights reserved.

    SORT is a free software written for educational purpose. Anyone can distribute
    or modify it under the the terms of the GNU General Public License Version 3 as
    published by the Free Software Foundation. However, there is NO warranty that
    all components are functional in a perfect manner. Without even the implied
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License along with
    this program. If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
-->

# SORT
<!--
Hide them until I am sure Github Action is reliable.
[![Build status](https://travis-ci.org/JiayinCao/SORT.svg?branch=master)](https://travis-ci.org/JiayinCao/SORT)
[![Build status](https://ci.appveyor.com/api/projects/status/la6ixha9tqe52qyr?svg=true)](https://ci.appveyor.com/project/JiayinCao/sort)
-->
[![Action status](https://github.com/JiayinCao/SORT/workflows/Build%20SORT/badge.svg)](https://actions-badge.atrox.dev/Jiayincao/SORT/goto)
[![Build status](https://travis-ci.org/JiayinCao/SORT.svg?branch=master)](https://travis-ci.org/JiayinCao/SORT)
[![License](https://img.shields.io/badge/License-GPL3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)


## Introduction
SORT, short for Simple Open-source Ray Tracing, is my personal cross platform ray tracing renderer. It is a standalone ray tracing program, while works well in Blender as a renderer plugin. Simliar to other open source ray tracer, like PBRT, luxrenderer, SORT is also a physically based renderer. However, since it is a solo project that I worked on in my spare time, it is way simpler comparing with its peers.

This is just a brief introduction of SORT. For further detail, please check out [SORT main page](https://sort-renderer.com).

## Features

Here are the features implemented so far:
  - Integrator. (Whitted ray tracing, direct lighting, path tracing, light tracing, bidirectional path tracing, instant radiosity, ambient occlusion)
  - Spatial acceleration structure. (OBVH, QBVH, BVH, KD-Tree, Uniform grid, OcTree)
  - BXDF. (Disney BRDF, Lambert, LambertTransmission, Oran Nayar, MicroFacet Reflection, Microfacet Transmission, MERL, Fourier, AshikhmanShirley, Modified Phong, Coat, Blend, Double-Sided, DistributionBRDF, DreamWorks Fabric BRDF)
  - Subsurface Scattering
  - Fur, Hair
  - Support Open Shading Language.
  - Depth of Field.
  - Multi-thread rendering, SIMD(SSE,AVX) optimized.
  - Blender 2.8 plugin.

## Images
Following are some examples of images generated by SORT
![Image](http://sort-renderer.com/assets/gallery/san_miguel_0.png)
Asset courtesy of [Morgan McGuire](https://casual-effects.com/data/).
![Image](http://sort-renderer.com/old/assets/main_page/human.png)
![Image](http://sort-renderer.com/old/assets/main_page/curly%20hair.png)
Asset courtesy of [rico cilliers](https://www.artstation.com/ricocilliers).
![Image](http://sort-renderer.com/old/assets/main_page/car.png)
Asset courtesy of [Christophe Desse](https://www.artstation.com/christophe-desse).
![Image](http://sort-renderer.com/old/assets/main_page/stormtrooper.png)
Asset courtesy of [ScottGraham](https://www.blendswap.com/blend/13953). The above rendered image is not used for any commercial purposes.
![Image](http://sort-renderer.com/old/assets/main_page/sss_dragon.png)
![Image](http://sort-renderer.com/old/assets/main_page/dinning%20room.png)
![Image](http://sort-renderer.com/old/assets/main_page/living%20room.png)
![Image](http://sort-renderer.com/old/assets/main_page/table.png)
