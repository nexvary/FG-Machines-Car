cmake_minimum_required(VERSION 3.22)
project(FGMachinesCarPrehardware LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(fg_prehardware_core
    src/virtual_vci.cpp
    src/virtual_ecu.cpp
    src/isotp.cpp
    src/uds.cpp
    src/coding.cpp
    src/coding_definition.cpp
    src/ecu_identity.cpp
    src/guarded_coding.cpp
    src/transaction_journal.cpp
    src/j2534.cpp
    src/j2534_registry.cpp
)

target_include_directories(fg_prehardware_core PUBLIC include)

if(MSVC)
    target_compile_options(fg_prehardware_core PRIVATE /W4 /permissive-)
    target_link_libraries(fg_prehardware_core PRIVATE Advapi32)
else()
    target_compile_options(fg_prehardware_core PRIVATE -Wall -Wextra -Wpedantic)
endif()

add_executable(fg_prehardware_tests tests/prehardware_tests.cpp)
target_link_libraries(fg_prehardware_tests PRIVATE fg_prehardware_core)

add_executable(fg_j2534_qualify tools/qualify_j2534.cpp)
target_link_libraries(fg_j2534_qualify PRIVATE fg_prehardware_core)

enable_testing()
add_test(NAME fg_prehardware_tests COMMAND fg_prehardware_tests)
