/*
    This file is a part of SORT(Simple Open Ray Tracing), an open-source cross
    platform physically based renderer.
 
    Copyright (c) 2011-2018 by Cao Jiayin - All rights reserved.
 
    SORT is a free software written for educational purpose. Anyone can distribute
    or modify it under the the terms of the GNU General Public License Version 3 as
    published by the Free Software Foundation. However, there is NO warranty that
    all components are functional in a perfect manner. Without even the implied
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
    General Public License for more details.
 
    You should have received a copy of the GNU General Public License along with
    this program. If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
 */

// include the header file
#include "sort.h"
#include "system.h"
#include "log/log.h"
#include "utility/stats.h"
#include "utility/profile.h"
#include "utility/path.h"

// the global system
System g_System;

extern bool g_bBlenderMode;

#include "easy/profiler.h"

// the main func
#ifdef SORT_IN_WINDOWS
int __cdecl main( int argc , char** argv )
#elif defined(SORT_IN_LINUX) || defined(SORT_IN_MAC)
int main(int argc, char** argv)
#endif
{
    addLogDispatcher(new StdOutLogDispatcher());
    addLogDispatcher(new FileLogDispatcher("log.txt"));

    // enable profiler
    SORT_PROFILE_ENABLE;
    SORT_PROFILE("Main Thread");

    string commandline = "Command line arguments: \t";
    for (int i = 0; i < argc; ++i) {
        commandline += string(argv[i]);
        commandline += " ";
    }

    slog(INFO, GENERAL, commandline);
    if (SORT_PROFILE_ISENABLED)
        slog(INFO, GENERAL, "Easy profiler is enabled.");
    else
        slog(INFO, GENERAL, "Easy profiler is disabled.");

    // check if there is file argument
    if (argc < 2)
    {
        slog(WARNING, GENERAL, "Miss file argument.");

        SORT_PROFILE_END; // Main Thread
        if (SORT_PROFILE_ISENABLED) {
            const std::string filename("sort.prof");
            uint32_t blocks = SORT_PROFILE_DUMP(filename.c_str());
            slog(INFO, GENERAL, stringFormat("Easy profiler file dumpped \"%s\".", GetFullPath(filename).c_str()));
        }
        slog(INFO, GENERAL, stringFormat("Log file: \"%s\"", GetFullPath("log.txt").c_str()));
        return 0;
    }

    slog(INFO, GENERAL, "Number of CPU cores " + to_string(NumSystemCores()));
    slog(INFO, GENERAL, "Scene file (" + std::string(argv[1]) + ")");

    // enable blender mode if possible
    if (argc > 2)
    {
        if (strcmp(argv[2], "blendermode") == 0)
            g_bBlenderMode = true;
    }

    // setup the system
    if (g_System.Setup(argv[1]))
    {
        // do ray tracing
        g_System.Render();
    }
    
    // Flush main thread data
    SortStatsFlushData(true);
    // Output stats data
    SortStatsPrintData();

    // unitialize the system
    g_System.Uninit();

    SORT_PROFILE_END; // Main Thread

    // dump profile data
    if (SORT_PROFILE_ISENABLED){
        const std::string filename("sort.prof");
        uint32_t blocks = SORT_PROFILE_DUMP(filename.c_str());
        slog(INFO, GENERAL, stringFormat("Profiling file: \"%s\"", GetFullPath(filename).c_str()));
    }
    slog(INFO, GENERAL, stringFormat("Log file: \"%s\"", GetFullPath("log.txt").c_str()));

	return 0;
}
