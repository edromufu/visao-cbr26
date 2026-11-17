# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target ipm_interfaces::ipm_interfaces
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${ipm_interfaces_TARGETS}.
if(ipm_interfaces_TARGETS AND NOT TARGET ipm_interfaces::ipm_interfaces)
  add_library(ipm_interfaces::ipm_interfaces INTERFACE IMPORTED)
  set_target_properties(ipm_interfaces::ipm_interfaces PROPERTIES
    INTERFACE_LINK_LIBRARIES "${ipm_interfaces_TARGETS}")
endif()
