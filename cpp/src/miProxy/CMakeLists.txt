file(GLOB_RECURSE MIPROXY_SOURCES "*.cpp")
add_executable(miProxy ${MIPROXY_SOURCES})

target_link_libraries(miProxy PRIVATE pugixml cxxopts)
target_include_directories(miProxy PRIVATE ${CMAKE_SOURCE_DIR}/src/common)

message("CMAKE_SOURCE_DIR: ${CMAKE_SOURCE_DIR}")