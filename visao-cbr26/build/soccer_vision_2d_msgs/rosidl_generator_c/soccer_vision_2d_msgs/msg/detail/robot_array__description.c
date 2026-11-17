// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from soccer_vision_2d_msgs:msg/RobotArray.idl
// generated code does not contain a copyright notice

#include "soccer_vision_2d_msgs/msg/detail/robot_array__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_soccer_vision_2d_msgs
const rosidl_type_hash_t *
soccer_vision_2d_msgs__msg__RobotArray__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x17, 0xc7, 0x9c, 0xb2, 0xa1, 0x64, 0x46, 0xe6,
      0xb9, 0x4e, 0x76, 0x79, 0x99, 0x04, 0x84, 0x7b,
      0x88, 0x23, 0x45, 0x3e, 0x52, 0x87, 0xe2, 0x6d,
      0x6d, 0x9c, 0x0a, 0x1f, 0xa0, 0x8b, 0xc0, 0xd5,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "soccer_vision_attribute_msgs/msg/detail/confidence__functions.h"
#include "std_msgs/msg/detail/header__functions.h"
#include "soccer_vision_2d_msgs/msg/detail/robot__functions.h"
#include "soccer_vision_attribute_msgs/msg/detail/robot__functions.h"
#include "vision_msgs/msg/detail/pose2_d__functions.h"
#include "builtin_interfaces/msg/detail/time__functions.h"
#include "vision_msgs/msg/detail/bounding_box2_d__functions.h"
#include "vision_msgs/msg/detail/point2_d__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t builtin_interfaces__msg__Time__EXPECTED_HASH = {1, {
    0xb1, 0x06, 0x23, 0x5e, 0x25, 0xa4, 0xc5, 0xed,
    0x35, 0x09, 0x8a, 0xa0, 0xa6, 0x1a, 0x3e, 0xe9,
    0xc9, 0xb1, 0x8d, 0x19, 0x7f, 0x39, 0x8b, 0x0e,
    0x42, 0x06, 0xce, 0xa9, 0xac, 0xf9, 0xc1, 0x97,
  }};
static const rosidl_type_hash_t soccer_vision_2d_msgs__msg__Robot__EXPECTED_HASH = {1, {
    0xb3, 0x6a, 0xc7, 0xf7, 0x99, 0xdb, 0x14, 0xc4,
    0x17, 0xd4, 0x90, 0xfb, 0xb5, 0xe7, 0xb8, 0xc6,
    0x8e, 0xb4, 0x73, 0x03, 0x87, 0xa3, 0x5f, 0x68,
    0x18, 0x3a, 0x00, 0x73, 0xff, 0xa7, 0xbb, 0x7a,
  }};
static const rosidl_type_hash_t soccer_vision_attribute_msgs__msg__Confidence__EXPECTED_HASH = {1, {
    0xce, 0xe2, 0xa6, 0x94, 0xf0, 0x23, 0xa8, 0x7b,
    0x53, 0xe9, 0xf4, 0x8d, 0x31, 0x04, 0xdf, 0x55,
    0x3a, 0x24, 0x3d, 0x8d, 0xd6, 0x55, 0x3b, 0xa2,
    0x74, 0x40, 0xa6, 0xbf, 0x0a, 0x57, 0x1a, 0xe7,
  }};
static const rosidl_type_hash_t soccer_vision_attribute_msgs__msg__Robot__EXPECTED_HASH = {1, {
    0x9c, 0x09, 0xf0, 0x33, 0x04, 0xe3, 0x5c, 0x3d,
    0xff, 0x01, 0x62, 0xc1, 0x57, 0x87, 0x00, 0xc9,
    0x11, 0xe9, 0x75, 0x78, 0x75, 0xc0, 0xef, 0x4b,
    0x34, 0xb3, 0x0d, 0x81, 0xe1, 0xf3, 0x28, 0xa4,
  }};
static const rosidl_type_hash_t std_msgs__msg__Header__EXPECTED_HASH = {1, {
    0xf4, 0x9f, 0xb3, 0xae, 0x2c, 0xf0, 0x70, 0xf7,
    0x93, 0x64, 0x5f, 0xf7, 0x49, 0x68, 0x3a, 0xc6,
    0xb0, 0x62, 0x03, 0xe4, 0x1c, 0x89, 0x1e, 0x17,
    0x70, 0x1b, 0x1c, 0xb5, 0x97, 0xce, 0x6a, 0x01,
  }};
static const rosidl_type_hash_t vision_msgs__msg__BoundingBox2D__EXPECTED_HASH = {1, {
    0x00, 0x8e, 0xac, 0xbb, 0x0c, 0xf8, 0xf2, 0x6e,
    0x83, 0x79, 0x55, 0x47, 0xbe, 0xd0, 0x13, 0xee,
    0xc3, 0x67, 0x54, 0x85, 0xef, 0x38, 0x6e, 0xc0,
    0x56, 0xd8, 0x0e, 0xaa, 0xf1, 0xc1, 0xce, 0x2f,
  }};
static const rosidl_type_hash_t vision_msgs__msg__Point2D__EXPECTED_HASH = {1, {
    0xea, 0xb0, 0xe8, 0x3f, 0x44, 0xab, 0x4d, 0xe9,
    0x2c, 0xea, 0xf7, 0x6d, 0xd7, 0xd0, 0xe7, 0x63,
    0x8f, 0x2b, 0xdd, 0x1d, 0x16, 0xff, 0xbe, 0x16,
    0xc7, 0xa1, 0x36, 0xc4, 0x8e, 0x40, 0x72, 0x47,
  }};
static const rosidl_type_hash_t vision_msgs__msg__Pose2D__EXPECTED_HASH = {1, {
    0xb0, 0xb5, 0xd1, 0xd7, 0xb4, 0xc2, 0x0d, 0xd4,
    0xfc, 0xde, 0x3e, 0xd1, 0xd4, 0xb2, 0x89, 0xa9,
    0x19, 0x29, 0x05, 0x72, 0x00, 0x7d, 0x67, 0xa9,
    0x70, 0x43, 0x81, 0x4d, 0xb2, 0x5d, 0x36, 0x48,
  }};
#endif

static char soccer_vision_2d_msgs__msg__RobotArray__TYPE_NAME[] = "soccer_vision_2d_msgs/msg/RobotArray";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char soccer_vision_2d_msgs__msg__Robot__TYPE_NAME[] = "soccer_vision_2d_msgs/msg/Robot";
static char soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME[] = "soccer_vision_attribute_msgs/msg/Confidence";
static char soccer_vision_attribute_msgs__msg__Robot__TYPE_NAME[] = "soccer_vision_attribute_msgs/msg/Robot";
static char std_msgs__msg__Header__TYPE_NAME[] = "std_msgs/msg/Header";
static char vision_msgs__msg__BoundingBox2D__TYPE_NAME[] = "vision_msgs/msg/BoundingBox2D";
static char vision_msgs__msg__Point2D__TYPE_NAME[] = "vision_msgs/msg/Point2D";
static char vision_msgs__msg__Pose2D__TYPE_NAME[] = "vision_msgs/msg/Pose2D";

// Define type names, field names, and default values
static char soccer_vision_2d_msgs__msg__RobotArray__FIELD_NAME__header[] = "header";
static char soccer_vision_2d_msgs__msg__RobotArray__FIELD_NAME__robots[] = "robots";

static rosidl_runtime_c__type_description__Field soccer_vision_2d_msgs__msg__RobotArray__FIELDS[] = {
  {
    {soccer_vision_2d_msgs__msg__RobotArray__FIELD_NAME__header, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_2d_msgs__msg__RobotArray__FIELD_NAME__robots, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {soccer_vision_2d_msgs__msg__Robot__TYPE_NAME, 31, 31},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription soccer_vision_2d_msgs__msg__RobotArray__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {soccer_vision_2d_msgs__msg__Robot__TYPE_NAME, 31, 31},
    {NULL, 0, 0},
  },
  {
    {soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME, 43, 43},
    {NULL, 0, 0},
  },
  {
    {soccer_vision_attribute_msgs__msg__Robot__TYPE_NAME, 38, 38},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    {NULL, 0, 0},
  },
  {
    {vision_msgs__msg__BoundingBox2D__TYPE_NAME, 29, 29},
    {NULL, 0, 0},
  },
  {
    {vision_msgs__msg__Point2D__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {vision_msgs__msg__Pose2D__TYPE_NAME, 22, 22},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
soccer_vision_2d_msgs__msg__RobotArray__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {soccer_vision_2d_msgs__msg__RobotArray__TYPE_NAME, 36, 36},
      {soccer_vision_2d_msgs__msg__RobotArray__FIELDS, 2, 2},
    },
    {soccer_vision_2d_msgs__msg__RobotArray__REFERENCED_TYPE_DESCRIPTIONS, 8, 8},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&soccer_vision_2d_msgs__msg__Robot__EXPECTED_HASH, soccer_vision_2d_msgs__msg__Robot__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = soccer_vision_2d_msgs__msg__Robot__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&soccer_vision_attribute_msgs__msg__Confidence__EXPECTED_HASH, soccer_vision_attribute_msgs__msg__Confidence__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = soccer_vision_attribute_msgs__msg__Confidence__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&soccer_vision_attribute_msgs__msg__Robot__EXPECTED_HASH, soccer_vision_attribute_msgs__msg__Robot__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = soccer_vision_attribute_msgs__msg__Robot__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[4].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&vision_msgs__msg__BoundingBox2D__EXPECTED_HASH, vision_msgs__msg__BoundingBox2D__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[5].fields = vision_msgs__msg__BoundingBox2D__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&vision_msgs__msg__Point2D__EXPECTED_HASH, vision_msgs__msg__Point2D__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[6].fields = vision_msgs__msg__Point2D__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&vision_msgs__msg__Pose2D__EXPECTED_HASH, vision_msgs__msg__Pose2D__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[7].fields = vision_msgs__msg__Pose2D__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# An array of robots with a header for global reference.\n"
  "# This msg type is used to publish all robots detected in an image.\n"
  "\n"
  "std_msgs/Header header\n"
  "soccer_vision_2d_msgs/Robot[]  robots";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
soccer_vision_2d_msgs__msg__RobotArray__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {soccer_vision_2d_msgs__msg__RobotArray__TYPE_NAME, 36, 36},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 187, 187},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
soccer_vision_2d_msgs__msg__RobotArray__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[9];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 9, 9};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *soccer_vision_2d_msgs__msg__RobotArray__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *soccer_vision_2d_msgs__msg__Robot__get_individual_type_description_source(NULL);
    sources[3] = *soccer_vision_attribute_msgs__msg__Confidence__get_individual_type_description_source(NULL);
    sources[4] = *soccer_vision_attribute_msgs__msg__Robot__get_individual_type_description_source(NULL);
    sources[5] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    sources[6] = *vision_msgs__msg__BoundingBox2D__get_individual_type_description_source(NULL);
    sources[7] = *vision_msgs__msg__Point2D__get_individual_type_description_source(NULL);
    sources[8] = *vision_msgs__msg__Pose2D__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
