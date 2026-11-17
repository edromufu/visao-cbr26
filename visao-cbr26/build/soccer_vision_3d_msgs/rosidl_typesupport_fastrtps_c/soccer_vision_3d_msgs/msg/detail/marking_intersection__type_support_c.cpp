// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from soccer_vision_3d_msgs:msg/MarkingIntersection.idl
// generated code does not contain a copyright notice
#include "soccer_vision_3d_msgs/msg/detail/marking_intersection__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "soccer_vision_3d_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "soccer_vision_3d_msgs/msg/detail/marking_intersection__struct.h"
#include "soccer_vision_3d_msgs/msg/detail/marking_intersection__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "geometry_msgs/msg/detail/point__functions.h"  // center
#include "geometry_msgs/msg/detail/vector3__functions.h"  // rays
#include "soccer_vision_attribute_msgs/msg/detail/confidence__functions.h"  // confidence

// forward declare type support functions

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
bool cdr_serialize_geometry_msgs__msg__Point(
  const geometry_msgs__msg__Point * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
bool cdr_deserialize_geometry_msgs__msg__Point(
  eprosima::fastcdr::Cdr & cdr,
  geometry_msgs__msg__Point * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
size_t get_serialized_size_geometry_msgs__msg__Point(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
size_t max_serialized_size_geometry_msgs__msg__Point(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
bool cdr_serialize_key_geometry_msgs__msg__Point(
  const geometry_msgs__msg__Point * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
size_t get_serialized_size_key_geometry_msgs__msg__Point(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
size_t max_serialized_size_key_geometry_msgs__msg__Point(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, geometry_msgs, msg, Point)();

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
bool cdr_serialize_geometry_msgs__msg__Vector3(
  const geometry_msgs__msg__Vector3 * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
bool cdr_deserialize_geometry_msgs__msg__Vector3(
  eprosima::fastcdr::Cdr & cdr,
  geometry_msgs__msg__Vector3 * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
size_t get_serialized_size_geometry_msgs__msg__Vector3(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
size_t max_serialized_size_geometry_msgs__msg__Vector3(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
bool cdr_serialize_key_geometry_msgs__msg__Vector3(
  const geometry_msgs__msg__Vector3 * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
size_t get_serialized_size_key_geometry_msgs__msg__Vector3(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
size_t max_serialized_size_key_geometry_msgs__msg__Vector3(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, geometry_msgs, msg, Vector3)();

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
bool cdr_serialize_soccer_vision_attribute_msgs__msg__Confidence(
  const soccer_vision_attribute_msgs__msg__Confidence * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
bool cdr_deserialize_soccer_vision_attribute_msgs__msg__Confidence(
  eprosima::fastcdr::Cdr & cdr,
  soccer_vision_attribute_msgs__msg__Confidence * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
size_t get_serialized_size_soccer_vision_attribute_msgs__msg__Confidence(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
size_t max_serialized_size_soccer_vision_attribute_msgs__msg__Confidence(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
bool cdr_serialize_key_soccer_vision_attribute_msgs__msg__Confidence(
  const soccer_vision_attribute_msgs__msg__Confidence * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
size_t get_serialized_size_key_soccer_vision_attribute_msgs__msg__Confidence(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
size_t max_serialized_size_key_soccer_vision_attribute_msgs__msg__Confidence(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_soccer_vision_3d_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, soccer_vision_attribute_msgs, msg, Confidence)();


using _MarkingIntersection__ros_msg_type = soccer_vision_3d_msgs__msg__MarkingIntersection;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_soccer_vision_3d_msgs
bool cdr_serialize_soccer_vision_3d_msgs__msg__MarkingIntersection(
  const soccer_vision_3d_msgs__msg__MarkingIntersection * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: center
  {
    cdr_serialize_geometry_msgs__msg__Point(
      &ros_message->center, cdr);
  }

  // Field name: num_rays
  {
    cdr << ros_message->num_rays;
  }

  // Field name: rays
  {
    size_t size = ros_message->rays.size;
    auto array_ptr = ros_message->rays.data;
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; ++i) {
      cdr_serialize_geometry_msgs__msg__Vector3(
        &array_ptr[i], cdr);
    }
  }

  // Field name: confidence
  {
    cdr_serialize_soccer_vision_attribute_msgs__msg__Confidence(
      &ros_message->confidence, cdr);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_soccer_vision_3d_msgs
bool cdr_deserialize_soccer_vision_3d_msgs__msg__MarkingIntersection(
  eprosima::fastcdr::Cdr & cdr,
  soccer_vision_3d_msgs__msg__MarkingIntersection * ros_message)
{
  // Field name: center
  {
    cdr_deserialize_geometry_msgs__msg__Point(cdr, &ros_message->center);
  }

  // Field name: num_rays
  {
    cdr >> ros_message->num_rays;
  }

  // Field name: rays
  {
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);

    // Check there are at least 'size' remaining bytes in the CDR stream before resizing
    auto old_state = cdr.get_state();
    bool correct_size = cdr.jump(size);
    cdr.set_state(old_state);
    if (!correct_size) {
      fprintf(stderr, "sequence size exceeds remaining buffer\n");
      return false;
    }

    if (ros_message->rays.data) {
      geometry_msgs__msg__Vector3__Sequence__fini(&ros_message->rays);
    }
    if (!geometry_msgs__msg__Vector3__Sequence__init(&ros_message->rays, size)) {
      fprintf(stderr, "failed to create array for field 'rays'");
      return false;
    }
    auto array_ptr = ros_message->rays.data;
    for (size_t i = 0; i < size; ++i) {
      cdr_deserialize_geometry_msgs__msg__Vector3(cdr, &array_ptr[i]);
    }
  }

  // Field name: confidence
  {
    cdr_deserialize_soccer_vision_attribute_msgs__msg__Confidence(cdr, &ros_message->confidence);
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_soccer_vision_3d_msgs
size_t get_serialized_size_soccer_vision_3d_msgs__msg__MarkingIntersection(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _MarkingIntersection__ros_msg_type * ros_message = static_cast<const _MarkingIntersection__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: center
  current_alignment += get_serialized_size_geometry_msgs__msg__Point(
    &(ros_message->center), current_alignment);

  // Field name: num_rays
  {
    size_t item_size = sizeof(ros_message->num_rays);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: rays
  {
    size_t array_size = ros_message->rays.size;
    auto array_ptr = ros_message->rays.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += get_serialized_size_geometry_msgs__msg__Vector3(
        &array_ptr[index], current_alignment);
    }
  }

  // Field name: confidence
  current_alignment += get_serialized_size_soccer_vision_attribute_msgs__msg__Confidence(
    &(ros_message->confidence), current_alignment);

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_soccer_vision_3d_msgs
size_t max_serialized_size_soccer_vision_3d_msgs__msg__MarkingIntersection(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // Field name: center
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_geometry_msgs__msg__Point(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: num_rays
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: rays
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: confidence
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_soccer_vision_attribute_msgs__msg__Confidence(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }


  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = soccer_vision_3d_msgs__msg__MarkingIntersection;
    is_plain =
      (
      offsetof(DataType, confidence) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_soccer_vision_3d_msgs
bool cdr_serialize_key_soccer_vision_3d_msgs__msg__MarkingIntersection(
  const soccer_vision_3d_msgs__msg__MarkingIntersection * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: center
  {
    cdr_serialize_key_geometry_msgs__msg__Point(
      &ros_message->center, cdr);
  }

  // Field name: num_rays
  {
    cdr << ros_message->num_rays;
  }

  // Field name: rays
  {
    size_t size = ros_message->rays.size;
    auto array_ptr = ros_message->rays.data;
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; ++i) {
      cdr_serialize_key_geometry_msgs__msg__Vector3(
        &array_ptr[i], cdr);
    }
  }

  // Field name: confidence
  {
    cdr_serialize_key_soccer_vision_attribute_msgs__msg__Confidence(
      &ros_message->confidence, cdr);
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_soccer_vision_3d_msgs
size_t get_serialized_size_key_soccer_vision_3d_msgs__msg__MarkingIntersection(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _MarkingIntersection__ros_msg_type * ros_message = static_cast<const _MarkingIntersection__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: center
  current_alignment += get_serialized_size_key_geometry_msgs__msg__Point(
    &(ros_message->center), current_alignment);

  // Field name: num_rays
  {
    size_t item_size = sizeof(ros_message->num_rays);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: rays
  {
    size_t array_size = ros_message->rays.size;
    auto array_ptr = ros_message->rays.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += get_serialized_size_key_geometry_msgs__msg__Vector3(
        &array_ptr[index], current_alignment);
    }
  }

  // Field name: confidence
  current_alignment += get_serialized_size_key_soccer_vision_attribute_msgs__msg__Confidence(
    &(ros_message->confidence), current_alignment);

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_soccer_vision_3d_msgs
size_t max_serialized_size_key_soccer_vision_3d_msgs__msg__MarkingIntersection(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;
  // Field name: center
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_geometry_msgs__msg__Point(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: num_rays
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: rays
  {
    size_t array_size = 0;
    full_bounded = false;
    is_plain = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: confidence
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_soccer_vision_attribute_msgs__msg__Confidence(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = soccer_vision_3d_msgs__msg__MarkingIntersection;
    is_plain =
      (
      offsetof(DataType, confidence) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _MarkingIntersection__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const soccer_vision_3d_msgs__msg__MarkingIntersection * ros_message = static_cast<const soccer_vision_3d_msgs__msg__MarkingIntersection *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_soccer_vision_3d_msgs__msg__MarkingIntersection(ros_message, cdr);
}

static bool _MarkingIntersection__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  soccer_vision_3d_msgs__msg__MarkingIntersection * ros_message = static_cast<soccer_vision_3d_msgs__msg__MarkingIntersection *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_soccer_vision_3d_msgs__msg__MarkingIntersection(cdr, ros_message);
}

static uint32_t _MarkingIntersection__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_soccer_vision_3d_msgs__msg__MarkingIntersection(
      untyped_ros_message, 0));
}

static size_t _MarkingIntersection__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_soccer_vision_3d_msgs__msg__MarkingIntersection(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_MarkingIntersection = {
  "soccer_vision_3d_msgs::msg",
  "MarkingIntersection",
  _MarkingIntersection__cdr_serialize,
  _MarkingIntersection__cdr_deserialize,
  _MarkingIntersection__get_serialized_size,
  _MarkingIntersection__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _MarkingIntersection__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_MarkingIntersection,
  get_message_typesupport_handle_function,
  &soccer_vision_3d_msgs__msg__MarkingIntersection__get_type_hash,
  &soccer_vision_3d_msgs__msg__MarkingIntersection__get_type_description,
  &soccer_vision_3d_msgs__msg__MarkingIntersection__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, soccer_vision_3d_msgs, msg, MarkingIntersection)() {
  return &_MarkingIntersection__type_support;
}

#if defined(__cplusplus)
}
#endif
