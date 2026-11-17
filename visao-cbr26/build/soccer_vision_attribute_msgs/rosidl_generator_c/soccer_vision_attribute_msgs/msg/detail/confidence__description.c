// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from soccer_vision_attribute_msgs:msg/Confidence.idl
// generated code does not contain a copyright notice

#include "soccer_vision_attribute_msgs/msg/detail/confidence__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_soccer_vision_attribute_msgs
const rosidl_type_hash_t *
soccer_vision_attribute_msgs__msg__Confidence__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xce, 0xe2, 0xa6, 0x94, 0xf0, 0x23, 0xa8, 0x7b,
      0x53, 0xe9, 0xf4, 0x8d, 0x31, 0x04, 0xdf, 0x55,
      0x3a, 0x24, 0x3d, 0x8d, 0xd6, 0x55, 0x3b, 0xa2,
      0x74, 0x40, 0xa6, 0xbf, 0x0a, 0x57, 0x1a, 0xe7,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME[] = "soccer_vision_attribute_msgs/msg/Confidence";

// Define type names, field names, and default values
static char soccer_vision_attribute_msgs__msg__Confidence__FIELD_NAME__confidence[] = "confidence";
static char soccer_vision_attribute_msgs__msg__Confidence__DEFAULT_VALUE__confidence[] = "-1.0";

static rosidl_runtime_c__type_description__Field soccer_vision_attribute_msgs__msg__Confidence__FIELDS[] = {
  {
    {soccer_vision_attribute_msgs__msg__Confidence__FIELD_NAME__confidence, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {soccer_vision_attribute_msgs__msg__Confidence__DEFAULT_VALUE__confidence, 4, 4},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
soccer_vision_attribute_msgs__msg__Confidence__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME, 43, 43},
      {soccer_vision_attribute_msgs__msg__Confidence__FIELDS, 1, 1},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "float32 CONFIDENCE_UNKNOWN=-1.0\n"
  "\n"
  "# A confidence rating in the range [0.0 - 1.0], or -1.0(CONFIDENCE_UNKNOWN) by default.\n"
  "# 0.0 - detection module is 0% sure\n"
  "# 1.0 - detection module is 100% sure\n"
  "float32 confidence -1.0";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
soccer_vision_attribute_msgs__msg__Confidence__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME, 43, 43},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 219, 219},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
soccer_vision_attribute_msgs__msg__Confidence__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *soccer_vision_attribute_msgs__msg__Confidence__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
