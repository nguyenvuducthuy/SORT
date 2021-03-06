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

#include "task.h"

//! @brief  Loading_Task is responsible for loading data to initialize the system.
class Loading_Task : public Task{
public:
    //! @brief Constructor.
    //!
    //! @param  scene     Scene to be filled during loading.
    Loading_Task( class Scene& scene , class IStreamBase& stream , const char* name , unsigned int priority ,
                  const Task::Task_Container& dependencies ) :
        Task( name , DEFAULT_TASK_PRIORITY , dependencies ) , m_scene(scene) , m_stream(stream) {}

    //! @brief  Load data from input file.
    void        Execute() override;

private:
    /**< The scene description to be filled with during loading. */
    class Scene&            m_scene;
    class IStreamBase&      m_stream;
};

//! @brief  Spatial acceleration data structure construction pass.
class SpatialAccelerationConstruction_Task : public Task{
public:
    //! @brief Constructor.
    //!
    //! @param  scene     Scene to be filled during loading.
    SpatialAccelerationConstruction_Task( class Scene& scene, const char* name ,
                 unsigned int priority , const Task::Task_Container& dependencies ) :
        Task( name , DEFAULT_TASK_PRIORITY, dependencies  ) , m_scene(scene) {}

    //! @brief  Load data from input file.
    void        Execute() override;

private:
    /**< The scene description to be filled with during loading. */
    class Scene&      m_scene;
};
