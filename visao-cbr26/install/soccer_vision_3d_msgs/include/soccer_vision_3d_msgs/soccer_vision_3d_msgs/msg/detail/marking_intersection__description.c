// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from soccer_vision_3d_msgs:msg/MarkingIntersection.idl
// generated code does not contain a copyright notice

#include "soccer_vision_3d_msgs/msg/detail/marking_intersection__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_soccer_vision_3d_msgs
const rosidl_type_hash_t *
soccer_vision_3d_msgs__msg__MarkingIntersection__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x06, 0xb0, 0x31, 0x50, 0x4c, 0x95, 0xc3, 0x0a,
      0xde, 0xc9, 0xea, 0x04, 0x28, 0x15, 0xa3, 0x14,
      0x82, 0xe7, 0x31, 0x2a, 0x33, 0x7a, 0xd8, 0x31,
      0xc6, 0xc4, 0xca, 0xb3, 0xf5, 0x0f, 0xb8, 0x43,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "geometry_msgs/msg/detail/vector3__functions.h"
#include "geometry_msgs/msg/detail/point__functions.h"
#include "soccer_vision_attribute_msgs/msg/detail/confidence__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t geometry_msgs__msg__Point__EXPECTED_HASH = {1, {
    0x69, 0x63, 0x08, 0x48, 0x42, 0xa9, 0xb0, 0x44,
    0x94, 0xd6, 0xb2, 0x94, 0x1d, 0x11, 0x44, 0x47,
    0x08, 0xd8, 0x92, 0xda, 0x2f, 0x4b, 0x09, 0x84,
    0x3b, 0x9c, 0x43, 0xf4, 0x2a, 0x7f, 0x68, 0x81,
  }};
static const rosidl_type_hash_t geometry_msgs__msg__Vector3__EXPECTED_HASH = {1, {
    0xcc, 0x12, 0xfe, 0x83, 0xe4, 0xc0, 0x27, 0x19,
    0xf1, 0xce, 0x80, 0x70, 0xbf, 0xd1, 0x4a, 0xec,
    0xd4, 0x0f, 0x75, 0xa9, 0x66, 0x96, 0xa6, 0x7a,
    0x2a, 0x1f, 0x37, 0xf7, 0xdb, 0xb0, 0x76, 0x5d,
  }};
static const rosidl_type_hash_t soccer_vision_attribute_msgs__msg__Confidence__EXPECTED_HASH = {1, {
    0xce, 0xe2, 0xa6, 0x94, 0xf0, 0x23, 0xa8, 0x7b,
    0x53, 0xe9, 0xf4, 0x8d, 0x31, 0x04, 0xdf, 0x55,
    0x3a, 0x24, 0x3d, 0x8d, 0xd6, 0x55, 0x3b, 0xa2,
    0x74, 0x40, 0xa6, 0xbf, 0x0a, 0x57, 0x1a, 0xe7,
  }};
#endif

static char soccer_vision_3d_msgs__msg__MarkingIntersection__TYPE_NAME[] = "soccer_vision_3d_msgs/msg/MarkingIntersection";
static char geometry_msgs__msg__Point__TYPE_NAME[] = "geometry_msgs/msg/Point";
static char geometry_msgs__msg__Vector3__TYPE_NAME[] = "geometry_msgs/msg/Vector3";
static char soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME[] = "soccer_vision_attribute_msgs/msg/Confidence";

// Define type names, field names, and default values
static char soccer_vision_3d_msgs__msg__MarkingIntersection__FIELD_NAME__center[] = "center";
static char soccer_vision_3d_msgs__msg__MarkingIntersection__FIELD_NAME__num_rays[] = "num_rays";
static char soccer_vision_3d_msgs__msg__MarkingIntersection__FIELD_NAME__rays[] = "rays";
static char soccer_vision_3d_msgs__msg__MarkingIntersection__FIELD_NAME__confidence[] = "confidence";

static rosidl_runtime_c__type_description__Field soccer_vision_3d_msgs__msg__MarkingIntersection__FIELDS[] = {
  {
    {soccer_vision_3d_msgs__msg__MarkingIntersection__FIELD_NAME__center, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_3d_msgs__msg__MarkingIntersection__FIELD_NAME__num_rays, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_3d_msgs__msg__MarkingIntersection__FIELD_NAME__rays, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_3d_msgs__msg__MarkingIntersection__FIELD_NAME__confidence, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME, 43, 43},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription soccer_vision_3d_msgs__msg__MarkingIntersection__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    {NULL, 0, 0},
  },
  {
    {soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME, 43, 43},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
soccer_vision_3d_msgs__msg__MarkingIntersection__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {soccer_vision_3d_msgs__msg__MarkingIntersection__TYPE_NAME, 45, 45},
      {soccer_vision_3d_msgs__msg__MarkingIntersection__FIELDS, 4, 4},
    },
    {soccer_vision_3d_msgs__msg__MarkingIntersection__REFERENCED_TYPE_DESCRIPTIONS, 3, 3},
  };
  if (!constructed) {
    assert(0 == memcmp(&geometry_msgs__msg__Point__EXPECTED_HASH, geometry_msgs__msg__Point__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = geometry_msgs__msg__Point__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Vector3__EXPECTED_HASH, geometry_msgs__msg__Vector3__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = geometry_msgs__msg__Vector3__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&soccer_vision_attribute_msgs__msg__Confidence__EXPECTED_HASH, soccer_vision_attribute_msgs__msg__Confidence__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = soccer_vision_attribute_msgs__msg__Confidence__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Describes a detected marking intersection from vision modules, in 3d coordinates.\n"
  "# An intersection is defined as a point where two or more line markings intersect.\n"
  "# The term ray is used to describe the outgoing rays from the center of the\n"
  "# intersection.\n"
  "\n"
  "# Center point of the intersection\n"
  "geometry_msgs/Point center \n"
  "\n"
  "# The number of rays outgoing from an intersection. This is 3 for a T-Junction and \n"
  "# 4 for an X-Junction\n"
  "int32 num_rays\n"
  "\n"
  "# NOTE: The length of the array should either:\n"
  "# - Match the number of rays specified with num_rays OR\n"
  "# - Be empty, if the headings are unknown\n"
  "geometry_msgs/Vector3[] rays\n"
  "\n"
  "soccer_vision_attribute_msgs/Confidence confidence";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
soccer_vision_3d_msgs__msg__MarkingIntersection__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {soccer_vision_3d_msgs__msg__MarkingIntersection__TYPE_NAME, 45, 45},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 672, 672},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
soccer_vision_3d_msgs__msg__MarkingIntersection__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[4];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 4, 4};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *soccer_vision_3d_msgs__msg__MarkingIntersection__get_individual_type_description_source(NULL),
    sources[1] = *geometry_msgs__msg__Point__get_individual_type_description_source(NULL);
    sources[2] = *geometry_msgs__msg__Vector3__get_individual_type_description_source(NULL);
    sources[3] = *soccer_vision_attribute_msgs__msg__Confidence__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
