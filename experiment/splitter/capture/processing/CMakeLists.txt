CMAKE_MINIMUM_REQUIRED(VERSION 3.11)
project(TimestampingTools)

SET(CMAKE_CXX_FLAGS "-Wall -Wextra -O3 -std=gnu++20")

add_executable(processing
    processing.cpp
    importer.cpp
    utils.cpp
)
target_link_libraries(processing pthread)