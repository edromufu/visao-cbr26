# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target soccer_vision_attribute_msgs::soccer_vision_attribute_msgs
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${soccer_vision_attribute_msgs_TARGETS}.
if(soccer_vision_attribute_msgs_TARGETS AND NOT TARGET soccer_vision_attribute_msgs::soccer_vision_attribute_msgs)
  add_library(soccer_vision_attribute_msgs::soccer_vision_attribute_msgs INTERFACE IMPORTED)
  set_target_properties(soccer_vision_attribute_msgs::soccer_vision_attribute_msgs PROPERTIES
    INTERFACE_LINK_LIBRARIES "${soccer_vision_attribute_msgs_TARGETS}")
endif()
