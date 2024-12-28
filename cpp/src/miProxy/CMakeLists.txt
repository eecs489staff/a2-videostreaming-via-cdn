file(GLOB_RECURSE MIPROXY_SOURCES "*.cpp")
add_executable(MiProxy ${MIPROXY_SOURCES})

target_link_libraries(MiProxy PRIVATE pugixml cxxopts)
target_include_directories(MiProxy PRIVATE ${CMAKE_SOURCE_DIR}/src/common)

message("CMAKE_SOURCE_DIR: ${CMAKE_SOURCE_DIR}")