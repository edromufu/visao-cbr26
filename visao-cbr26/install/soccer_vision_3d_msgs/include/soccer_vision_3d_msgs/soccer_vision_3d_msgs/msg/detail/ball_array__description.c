// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from soccer_vision_3d_msgs:msg/BallArray.idl
// generated code does not contain a copyright notice

#include "soccer_vision_3d_msgs/msg/detail/ball_array__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_soccer_vision_3d_msgs
const rosidl_type_hash_t *
soccer_vision_3d_msgs__msg__BallArray__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x09, 0x87, 0x76, 0xc1, 0xa1, 0x50, 0x93, 0x40,
      0x07, 0x4e, 0xe1, 0xd3, 0x0b, 0x65, 0x88, 0xb2,
      0x4b, 0x5c, 0xab, 0x8c, 0x3b, 0x49, 0x07, 0x04,
      0xe6, 0x19, 0x4c, 0xfd, 0x3f, 0xab, 0xc8, 0x45,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "geometry_msgs/msg/detail/point__functions.h"
#include "builtin_interfaces/msg/detail/time__functions.h"
#include "soccer_vision_attribute_msgs/msg/detail/confidence__functions.h"
#include "soccer_vision_3d_msgs/msg/detail/ball__functions.h"
#include "std_msgs/msg/detail/header__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t builtin_interfaces__msg__Time__EXPECTED_HASH = {1, {
    0xb1, 0x06, 0x23, 0x5e, 0x25, 0xa4, 0xc5, 0xed,
    0x35, 0x09, 0x8a, 0xa0, 0xa6, 0x1a, 0x3e, 0xe9,
    0xc9, 0xb1, 0x8d, 0x19, 0x7f, 0x39, 0x8b, 0x0e,
    0x42, 0x06, 0xce, 0xa9, 0xac, 0xf9, 0xc1, 0x97,
  }};
static const rosidl_type_hash_t geometry_msgs__msg__Point__EXPECTED_HASH = {1, {
    0x69, 0x63, 0x08, 0x48, 0x42, 0xa9, 0xb0, 0x44,
    0x94, 0xd6, 0xb2, 0x94, 0x1d, 0x11, 0x44, 0x47,
    0x08, 0xd8, 0x92, 0xda, 0x2f, 0x4b, 0x09, 0x84,
    0x3b, 0x9c, 0x43, 0xf4, 0x2a, 0x7f, 0x68, 0x81,
  }};
static const rosidl_type_hash_t soccer_vision_3d_msgs__msg__Ball__EXPECTED_HASH = {1, {
    0x06, 0x23, 0xd6, 0x69, 0x3e, 0x76, 0x50, 0xfd,
    0x29, 0xa8, 0xb7, 0xad, 0x64, 0xc2, 0xda, 0x12,
    0x1d, 0x51, 0x9d, 0x18, 0x6d, 0xee, 0xe6, 0x5a,
    0x74, 0x12, 0x88, 0xad, 0x14, 0x37, 0xb7, 0xc7,
  }};
static const rosidl_type_hash_t soccer_vision_attribute_msgs__msg__Confidence__EXPECTED_HASH = {1, {
    0xce, 0xe2, 0xa6, 0x94, 0xf0, 0x23, 0xa8, 0x7b,
    0x53, 0xe9, 0xf4, 0x8d, 0x31, 0x04, 0xdf, 0x55,
    0x3a, 0x24, 0x3d, 0x8d, 0xd6, 0x55, 0x3b, 0xa2,
    0x74, 0x40, 0xa6, 0xbf, 0x0a, 0x57, 0x1a, 0xe7,
  }};
static const rosidl_type_hash_t std_msgs__msg__Header__EXPECTED_HASH = {1, {
    0xf4, 0x9f, 0xb3, 0xae, 0x2c, 0xf0, 0x70, 0xf7,
    0x93, 0x64, 0x5f, 0xf7, 0x49, 0x68, 0x3a, 0xc6,
    0xb0, 0x62, 0x03, 0xe4, 0x1c, 0x89, 0x1e, 0x17,
    0x70, 0x1b, 0x1c, 0xb5, 0x97, 0xce, 0x6a, 0x01,
  }};
#endif

static char soccer_vision_3d_msgs__msg__BallArray__TYPE_NAME[] = "soccer_vision_3d_msgs/msg/BallArray";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char geometry_msgs__msg__Point__TYPE_NAME[] = "geometry_msgs/msg/Point";
static char soccer_vision_3d_msgs__msg__Ball__TYPE_NAME[] = "soccer_vision_3d_msgs/msg/Ball";
static char soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME[] = "soccer_vision_attribute_msgs/msg/Confidence";
static char std_msgs__msg__Header__TYPE_NAME[] = "std_msgs/msg/Header";

// Define type names, field names, and default values
static char soccer_vision_3d_msgs__msg__BallArray__FIELD_NAME__header[] = "header";
static char soccer_vision_3d_msgs__msg__BallArray__FIELD_NAME__balls[] = "balls";

static rosidl_runtime_c__type_description__Field soccer_vision_3d_msgs__msg__BallArray__FIELDS[] = {
  {
    {soccer_vision_3d_msgs__msg__BallArray__FIELD_NAME__header, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_3d_msgs__msg__BallArray__FIELD_NAME__balls, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {soccer_vision_3d_msgs__msg__Ball__TYPE_NAME, 30, 30},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription soccer_vision_3d_msgs__msg__BallArray__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {soccer_vision_3d_msgs__msg__Ball__TYPE_NAME, 30, 30},
    {NULL, 0, 0},
  },
  {
    {soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME, 43, 43},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
soccer_vision_3d_msgs__msg__BallArray__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {soccer_vision_3d_msgs__msg__BallArray__TYPE_NAME, 35, 35},
      {soccer_vision_3d_msgs__msg__BallArray__FIELDS, 2, 2},
    },
    {soccer_vision_3d_msgs__msg__BallArray__REFERENCED_TYPE_DESCRIPTIONS, 5, 5},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Point__EXPECTED_HASH, geometry_msgs__msg__Point__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = geometry_msgs__msg__Point__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&soccer_vision_3d_msgs__msg__Ball__EXPECTED_HASH, soccer_vision_3d_msgs__msg__Ball__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = soccer_vision_3d_msgs__msg__Ball__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&soccer_vision_attribute_msgs__msg__Confidence__EXPECTED_HASH, soccer_vision_attribute_msgs__msg__Confidence__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = soccer_vision_attribute_msgs__msg__Confidence__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[4].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# An array of balls with a header for global reference.\n"
  "# This msg type is used to publish all balls detected.\n"
  "\n"
  "std_msgs/Header header\n"
  "soccer_vision_3d_msgs/Ball[] balls";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
soccer_vision_3d_msgs__msg__BallArray__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {soccer_vision_3d_msgs__msg__BallArray__TYPE_NAME, 35, 35},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 170, 170},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
soccer_vision_3d_msgs__msg__BallArray__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[6];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 6, 6};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *soccer_vision_3d_msgs__msg__BallArray__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *geometry_msgs__msg__Point__get_individual_type_description_source(NULL);
    sources[3] = *soccer_vision_3d_msgs__msg__Ball__get_individual_type_description_source(NULL);
    sources[4] = *soccer_vision_attribute_msgs__msg__Confidence__get_individual_type_description_source(NULL);
    sources[5] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
