// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from soccer_vision_2d_msgs:msg/MarkingIntersection.idl
// generated code does not contain a copyright notice

#include "soccer_vision_2d_msgs/msg/detail/marking_intersection__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_soccer_vision_2d_msgs
const rosidl_type_hash_t *
soccer_vision_2d_msgs__msg__MarkingIntersection__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x34, 0x15, 0xec, 0x9c, 0x7c, 0x85, 0xa4, 0x85,
      0x3e, 0x5c, 0x06, 0x9c, 0x69, 0x7a, 0xa1, 0x56,
      0xa2, 0xf2, 0x81, 0xfc, 0x97, 0xd3, 0xd4, 0x62,
      0xbc, 0xd4, 0xdc, 0x28, 0xd3, 0x2c, 0xc2, 0x1e,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "vision_msgs/msg/detail/point2_d__functions.h"
#include "soccer_vision_attribute_msgs/msg/detail/confidence__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t soccer_vision_attribute_msgs__msg__Confidence__EXPECTED_HASH = {1, {
    0xce, 0xe2, 0xa6, 0x94, 0xf0, 0x23, 0xa8, 0x7b,
    0x53, 0xe9, 0xf4, 0x8d, 0x31, 0x04, 0xdf, 0x55,
    0x3a, 0x24, 0x3d, 0x8d, 0xd6, 0x55, 0x3b, 0xa2,
    0x74, 0x40, 0xa6, 0xbf, 0x0a, 0x57, 0x1a, 0xe7,
  }};
static const rosidl_type_hash_t vision_msgs__msg__Point2D__EXPECTED_HASH = {1, {
    0xea, 0xb0, 0xe8, 0x3f, 0x44, 0xab, 0x4d, 0xe9,
    0x2c, 0xea, 0xf7, 0x6d, 0xd7, 0xd0, 0xe7, 0x63,
    0x8f, 0x2b, 0xdd, 0x1d, 0x16, 0xff, 0xbe, 0x16,
    0xc7, 0xa1, 0x36, 0xc4, 0x8e, 0x40, 0x72, 0x47,
  }};
#endif

static char soccer_vision_2d_msgs__msg__MarkingIntersection__TYPE_NAME[] = "soccer_vision_2d_msgs/msg/MarkingIntersection";
static char soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME[] = "soccer_vision_attribute_msgs/msg/Confidence";
static char vision_msgs__msg__Point2D__TYPE_NAME[] = "vision_msgs/msg/Point2D";

// Define type names, field names, and default values
static char soccer_vision_2d_msgs__msg__MarkingIntersection__FIELD_NAME__center[] = "center";
static char soccer_vision_2d_msgs__msg__MarkingIntersection__FIELD_NAME__num_rays[] = "num_rays";
static char soccer_vision_2d_msgs__msg__MarkingIntersection__FIELD_NAME__heading_rays[] = "heading_rays";
static char soccer_vision_2d_msgs__msg__MarkingIntersection__FIELD_NAME__confidence[] = "confidence";

static rosidl_runtime_c__type_description__Field soccer_vision_2d_msgs__msg__MarkingIntersection__FIELDS[] = {
  {
    {soccer_vision_2d_msgs__msg__MarkingIntersection__FIELD_NAME__center, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {vision_msgs__msg__Point2D__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_2d_msgs__msg__MarkingIntersection__FIELD_NAME__num_rays, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_2d_msgs__msg__MarkingIntersection__FIELD_NAME__heading_rays, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_2d_msgs__msg__MarkingIntersection__FIELD_NAME__confidence, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME, 43, 43},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription soccer_vision_2d_msgs__msg__MarkingIntersection__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME, 43, 43},
    {NULL, 0, 0},
  },
  {
    {vision_msgs__msg__Point2D__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
soccer_vision_2d_msgs__msg__MarkingIntersection__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {soccer_vision_2d_msgs__msg__MarkingIntersection__TYPE_NAME, 45, 45},
      {soccer_vision_2d_msgs__msg__MarkingIntersection__FIELDS, 4, 4},
    },
    {soccer_vision_2d_msgs__msg__MarkingIntersection__REFERENCED_TYPE_DESCRIPTIONS, 2, 2},
  };
  if (!constructed) {
    assert(0 == memcmp(&soccer_vision_attribute_msgs__msg__Confidence__EXPECTED_HASH, soccer_vision_attribute_msgs__msg__Confidence__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = soccer_vision_attribute_msgs__msg__Confidence__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&vision_msgs__msg__Point2D__EXPECTED_HASH, vision_msgs__msg__Point2D__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = vision_msgs__msg__Point2D__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Describes a detected marking intersection from vision modules, in image coordinates.\n"
  "# An intersection is defined as a point where two or more line markings intersect.\n"
  "# The term ray is used to describe the outgoing rays from the center of the\n"
  "# intersection.\n"
  "#\n"
  "# For example, looking down at a perfectly upright T-intersection on the ground from above, you would have:\n"
  "# - num_rays = 3\n"
  "# - heading_rays = [0, pi / 2, pi]\n"
  "\n"
  "# Center point of the intersection, in pixel coordinates\n"
  "vision_msgs/Point2D center\n"
  "\n"
  "# The number of rays outgoing from an intersection. This is 3 for a T-Junction and \n"
  "# 4 for an X-Junction\n"
  "int32 num_rays\n"
  "\n"
  "# NOTE: The length of the array should either:\n"
  "# - Match the number of rays specified with num_rays OR\n"
  "# - Be empty, if the headings are unknown\n"
  "# Heading is defined as 0 along the +x axis, and pi / 2 along the +y axis.\n"
  "# Headings should:\n"
  "# - have an interval of [0, 2pi)\n"
  "# - be stored in ascending order\n"
  "float64[] heading_rays\n"
  "\n"
  "soccer_vision_attribute_msgs/Confidence confidence";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
soccer_vision_2d_msgs__msg__MarkingIntersection__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {soccer_vision_2d_msgs__msg__MarkingIntersection__TYPE_NAME, 45, 45},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 1012, 1012},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
soccer_vision_2d_msgs__msg__MarkingIntersection__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[3];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 3, 3};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *soccer_vision_2d_msgs__msg__MarkingIntersection__get_individual_type_description_source(NULL),
    sources[1] = *soccer_vision_attribute_msgs__msg__Confidence__get_individual_type_description_source(NULL);
    sources[2] = *vision_msgs__msg__Point2D__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
