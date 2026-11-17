# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target soccer_model_msgs::soccer_model_msgs
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${soccer_model_msgs_TARGETS}.
if(soccer_model_msgs_TARGETS AND NOT TARGET soccer_model_msgs::soccer_model_msgs)
  add_library(soccer_model_msgs::soccer_model_msgs INTERFACE IMPORTED)
  set_target_properties(soccer_model_msgs::soccer_model_msgs PROPERTIES
    INTERFACE_LINK_LIBRARIES "${soccer_model_msgs_TARGETS}")
endif()
