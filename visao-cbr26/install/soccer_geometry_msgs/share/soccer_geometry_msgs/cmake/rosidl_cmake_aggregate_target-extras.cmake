# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target soccer_geometry_msgs::soccer_geometry_msgs
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${soccer_geometry_msgs_TARGETS}.
if(soccer_geometry_msgs_TARGETS AND NOT TARGET soccer_geometry_msgs::soccer_geometry_msgs)
  add_library(soccer_geometry_msgs::soccer_geometry_msgs INTERFACE IMPORTED)
  set_target_properties(soccer_geometry_msgs::soccer_geometry_msgs PROPERTIES
    INTERFACE_LINK_LIBRARIES "${soccer_geometry_msgs_TARGETS}")
endif()
