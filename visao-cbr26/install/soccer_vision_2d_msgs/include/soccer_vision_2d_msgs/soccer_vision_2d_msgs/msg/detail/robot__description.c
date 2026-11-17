// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from soccer_vision_2d_msgs:msg/Robot.idl
// generated code does not contain a copyright notice

#include "soccer_vision_2d_msgs/msg/detail/robot__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_soccer_vision_2d_msgs
const rosidl_type_hash_t *
soccer_vision_2d_msgs__msg__Robot__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xb3, 0x6a, 0xc7, 0xf7, 0x99, 0xdb, 0x14, 0xc4,
      0x17, 0xd4, 0x90, 0xfb, 0xb5, 0xe7, 0xb8, 0xc6,
      0x8e, 0xb4, 0x73, 0x03, 0x87, 0xa3, 0x5f, 0x68,
      0x18, 0x3a, 0x00, 0x73, 0xff, 0xa7, 0xbb, 0x7a,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "soccer_vision_attribute_msgs/msg/detail/confidence__functions.h"
#include "soccer_vision_attribute_msgs/msg/detail/robot__functions.h"
#include "vision_msgs/msg/detail/pose2_d__functions.h"
#include "vision_msgs/msg/detail/bounding_box2_d__functions.h"
#include "vision_msgs/msg/detail/point2_d__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
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

static char soccer_vision_2d_msgs__msg__Robot__TYPE_NAME[] = "soccer_vision_2d_msgs/msg/Robot";
static char soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME[] = "soccer_vision_attribute_msgs/msg/Confidence";
static char soccer_vision_attribute_msgs__msg__Robot__TYPE_NAME[] = "soccer_vision_attribute_msgs/msg/Robot";
static char vision_msgs__msg__BoundingBox2D__TYPE_NAME[] = "vision_msgs/msg/BoundingBox2D";
static char vision_msgs__msg__Point2D__TYPE_NAME[] = "vision_msgs/msg/Point2D";
static char vision_msgs__msg__Pose2D__TYPE_NAME[] = "vision_msgs/msg/Pose2D";

// Define type names, field names, and default values
static char soccer_vision_2d_msgs__msg__Robot__FIELD_NAME__bb[] = "bb";
static char soccer_vision_2d_msgs__msg__Robot__FIELD_NAME__attributes[] = "attributes";
static char soccer_vision_2d_msgs__msg__Robot__FIELD_NAME__confidence[] = "confidence";

static rosidl_runtime_c__type_description__Field soccer_vision_2d_msgs__msg__Robot__FIELDS[] = {
  {
    {soccer_vision_2d_msgs__msg__Robot__FIELD_NAME__bb, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {vision_msgs__msg__BoundingBox2D__TYPE_NAME, 29, 29},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_2d_msgs__msg__Robot__FIELD_NAME__attributes, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {soccer_vision_attribute_msgs__msg__Robot__TYPE_NAME, 38, 38},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_2d_msgs__msg__Robot__FIELD_NAME__confidence, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME, 43, 43},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription soccer_vision_2d_msgs__msg__Robot__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME, 43, 43},
    {NULL, 0, 0},
  },
  {
    {soccer_vision_attribute_msgs__msg__Robot__TYPE_NAME, 38, 38},
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
soccer_vision_2d_msgs__msg__Robot__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {soccer_vision_2d_msgs__msg__Robot__TYPE_NAME, 31, 31},
      {soccer_vision_2d_msgs__msg__Robot__FIELDS, 3, 3},
    },
    {soccer_vision_2d_msgs__msg__Robot__REFERENCED_TYPE_DESCRIPTIONS, 5, 5},
  };
  if (!constructed) {
    assert(0 == memcmp(&soccer_vision_attribute_msgs__msg__Confidence__EXPECTED_HASH, soccer_vision_attribute_msgs__msg__Confidence__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = soccer_vision_attribute_msgs__msg__Confidence__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&soccer_vision_attribute_msgs__msg__Robot__EXPECTED_HASH, soccer_vision_attribute_msgs__msg__Robot__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = soccer_vision_attribute_msgs__msg__Robot__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&vision_msgs__msg__BoundingBox2D__EXPECTED_HASH, vision_msgs__msg__BoundingBox2D__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = vision_msgs__msg__BoundingBox2D__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&vision_msgs__msg__Point2D__EXPECTED_HASH, vision_msgs__msg__Point2D__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = vision_msgs__msg__Point2D__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&vision_msgs__msg__Pose2D__EXPECTED_HASH, vision_msgs__msg__Pose2D__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[4].fields = vision_msgs__msg__Pose2D__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Describes a detected robot from vision modules, in image coordinates.\n"
  "\n"
  "# A bounding box that surrounds the robot in the image, this does not have to include\n"
  "# the whole robot, but only the part of the robot that was detected.\n"
  "vision_msgs/BoundingBox2D bb\n"
  "\n"
  "soccer_vision_attribute_msgs/Robot attributes\n"
  "\n"
  "soccer_vision_attribute_msgs/Confidence confidence";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
soccer_vision_2d_msgs__msg__Robot__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {soccer_vision_2d_msgs__msg__Robot__TYPE_NAME, 31, 31},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 356, 356},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
soccer_vision_2d_msgs__msg__Robot__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[6];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 6, 6};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *soccer_vision_2d_msgs__msg__Robot__get_individual_type_description_source(NULL),
    sources[1] = *soccer_vision_attribute_msgs__msg__Confidence__get_individual_type_description_source(NULL);
    sources[2] = *soccer_vision_attribute_msgs__msg__Robot__get_individual_type_description_source(NULL);
    sources[3] = *vision_msgs__msg__BoundingBox2D__get_individual_type_description_source(NULL);
    sources[4] = *vision_msgs__msg__Point2D__get_individual_type_description_source(NULL);
    sources[5] = *vision_msgs__msg__Pose2D__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
