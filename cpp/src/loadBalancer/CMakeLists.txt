file(GLOB_RECURSE NAMESERVER_SOURCES "*.cpp")
add_executable(nameserver ${NAMESERVER_SOURCES})

target_link_libraries(nameserver PRIVATE cxxopts)
target_include_directories(nameserver PRIVATE ${CMAKE_SOURCE_DIR}/src/common)