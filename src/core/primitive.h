/*
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
 */

#pragma once

#include "math/bbox.h"
#include "material/material.h"
#include "math/interaction.h"
#include "shape/shape.h"
#include "material/matmanager.h"

class Light;

//! @brief  Primitive of SORT world.
/**
 * Like primitives in rasterization program, which are usually triangle, point and lines, primitives can have many more different shapes.
 * Common ones are triangles, disk, quad, splines, quadric curves. Each primitive is attached with a specific material, may also be
 * missive, which means that they are attached with a 'light source'.
 * A primitive is the basic unit for spatial data structure. It is more of a lower level concept comparing with Entity.
 */
class   Primitive{
public:
    //! @brief Constructor of Primitive.
    //!
    //! @param  mat     Material attached to the primitive.
    //! @param  shape   Shape of the material.
    //! @param  light   Light source attached to the material.
    Primitive( Material* mat , Shape* shape , class Light* light = nullptr ):
        m_mat(mat), m_shape(shape), m_light(light){}

    //! @brief  Get the intersection between a ray and the primitive.
    //!
    //! @param  r           Ray to be tested against the primitive. The input ray is in world space.
    //! @param  intersect   Intersected result. If nullptr is passed in, the algorithm could be a little more performant.
    //!                     The information of the intersection is also returned in world space.
    //! @return             Whether the ray intersects the primitive.
    SORT_FORCEINLINE bool GetIntersect( const Ray& r , SurfaceInteraction* intersect ) const{
        auto ret = m_shape->GetIntersect( r , intersect );
        if( ret && intersect ){
            intersect->primitive = this;
            return true;
        }
        return ret;
    }

    //! @brief  Get the intersection between an AABB and the primitive.
    //!
    //! Unlike the ray/primitive intersection test interface, this interface is generally used as an optimization to reject
    //! false-positives during spatial data structure construction process. A conservative algorithm could also be accepted.
    //!
    //! @param  box     Axis aligned bounding box in world space.
    //! @return         Whether the primitive intersects the primitive.
    SORT_FORCEINLINE bool GetIntersect( const BBox& box ) const {
        return m_shape->GetIntersect( box );
    }

    //! @brief  Get the axis aligned bounding box of the primitive in world space.
    //!
    //! @return         AABB in world space.
    SORT_FORCEINLINE const BBox&  GetBBox() const {
        return m_shape->GetBBox();
    }

    //! @brief  Get the surface area of the primitive.
    //!
    //! @return         Surface area of the primitive.
    SORT_FORCEINLINE float    SurfaceArea() const{
        return m_shape->SurfaceArea();
    }

    //! @brief  Get the material of the primitive.
    //!
    //! A default red material will be used for primitives with no materials or invalid materials.
    //!
    //! @return         Material attached to the primitives.
    SORT_FORCEINLINE Material* GetMaterial() const{
        return m_mat == nullptr ? MatManager::GetSingleton().GetDefaultMat() : m_mat;
    }

    //! @brief  Get the light source of the primitive if there is one.
    //!
    //! Most primitives doesn't have light attached to it.
    //!
    //! @return         Light attached to the primitive. 'nullptr' means this is not an missive primitive.
    SORT_FORCEINLINE Light* GetLight() const {
        return m_light;
    }
    
    //! @brief  Get the type of the shape attached to the primitive.
    //!
    //! @return         Type of the attached shape.
    SORT_FORCEINLINE SHAPE_TYPE GetShapeType() const {
        return m_shape->GetShapeType();
    }

    //! @brief  Get the shape of the primitive.
    //!
    //! @return         The shape of the primitive.
    SORT_FORCEINLINE const Shape*    GetShape() const{
        return m_shape;
    }

private:
    Material*       m_mat;      /**< The material attached to the primitive. */
    Shape*          m_shape;    /**< The shape of the primitive. */
    class Light*    m_light;    /**< Light source attached to the primitive. */
};
