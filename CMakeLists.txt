cmake_minimum_required(VERSION 3.14 FATAL_ERROR)
project(MyViewerProc)
set(CMAKE_CXX_STANDARD 17)


find_package(ILCUTIL REQUIRED COMPONENTS ILCSOFT_CMAKE_MODULES)
include(ilcsoft_default_settings)

# Remove this ugly warning
set(CMAKE_BUILD_TYPE Debug)


include_directories(${PROJECT_SOURCE_DIR}/include)
add_library(${PROJECT_NAME} SHARED
    ${PROJECT_SOURCE_DIR}/src/MyViewerProc.cc
    ${PROJECT_SOURCE_DIR}/src/utils.cc
)

### DEPENDENCIES ###
find_package(Marlin REQUIRED)
find_package(MarlinUtil REQUIRED)
#find_package(MarlinTrk REQUIRED)

FOREACH(pkg Marlin MarlinUtil) #MarlinTrk
   include_directories(${${pkg}_INCLUDE_DIRS})
   target_link_libraries(${PROJECT_NAME} ${${pkg}_LIBRARIES})
ENDFOREACH()

#  this is fixed in MarlinUtil 1.17.01
# find_package( DD4hep REQUIRED COMPONENTS DDRec)
# INCLUDE_DIRECTORIES( SYSTEM ${DD4hep_INCLUDE_DIRS} )
# target_link_libraries(${PROJECT_NAME} ${DD4hep_COMPONENT_LIBRARIES})

install(TARGETS ${PROJECT_NAME} DESTINATION ${PROJECT_SOURCE_DIR}/lib)