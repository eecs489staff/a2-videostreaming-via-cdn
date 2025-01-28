file(GLOB_RECURSE LOADBALANCER_SOURCES "*.cpp")
add_executable(loadBalancer ${LOADBALANCER_SOURCES})

target_link_libraries(loadBalancer PRIVATE cxxopts)
target_include_directories(loadBalancer PRIVATE ${CMAKE_SOURCE_DIR}/src/common)