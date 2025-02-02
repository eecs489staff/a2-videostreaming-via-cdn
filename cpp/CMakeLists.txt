
cmake_minimum_required(VERSION 3.15)
project(eecs489-project2-wn25)

# Specify the C++ standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_BUILD_TYPE Debug)

# Ensure that output executables are in the build/bin directory
SET(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin)


# Fetch the required dependencies
include(FetchContent)

FetchContent_Declare(
    pugixml
    GIT_REPOSITORY https://github.com/zeux/pugixml.git
    GIT_TAG master
)
FetchContent_MakeAvailable(pugixml)

FetchContent_Declare(
        spdlog
        GIT_REPOSITORY https://github.com/gabime/spdlog.git
        GIT_TAG v1.14.1
)
FetchContent_MakeAvailable(spdlog)

FetchContent_Declare(cxxopts
        GIT_REPOSITORY https://github.com/jarro2783/cxxopts.git
        GIT_TAG master
)
FetchContent_MakeAvailable(cxxopts)

find_package(Boost REQUIRED COMPONENTS regex)

# Recurse through the subdirectories
add_subdirectory(src)