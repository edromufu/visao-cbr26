// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from soccer_vision_3d_msgs:msg/MarkingSegment.idl
// generated code does not contain a copyright notice

#include "soccer_vision_3d_msgs/msg/detail/marking_segment__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_soccer_vision_3d_msgs
const rosidl_type_hash_t *
soccer_vision_3d_msgs__msg__MarkingSegment__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xe7, 0xdb, 0xa0, 0x1e, 0xf4, 0x83, 0xa7, 0xf6,
      0x36, 0xfb, 0x32, 0x53, 0xd2, 0x97, 0x69, 0x8f,
      0xd0, 0xea, 0xde, 0xb2, 0x6d, 0xff, 0xb0, 0xed,
      0x01, 0x7f, 0xbe, 0xf5, 0x37, 0xf5, 0x9f, 0x1c,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
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
static const rosidl_type_hash_t soccer_vision_attribute_msgs__msg__Confidence__EXPECTED_HASH = {1, {
    0xce, 0xe2, 0xa6, 0x94, 0xf0, 0x23, 0xa8, 0x7b,
    0x53, 0xe9, 0xf4, 0x8d, 0x31, 0x04, 0xdf, 0x55,
    0x3a, 0x24, 0x3d, 0x8d, 0xd6, 0x55, 0x3b, 0xa2,
    0x74, 0x40, 0xa6, 0xbf, 0x0a, 0x57, 0x1a, 0xe7,
  }};
#endif

static char soccer_vision_3d_msgs__msg__MarkingSegment__TYPE_NAME[] = "soccer_vision_3d_msgs/msg/MarkingSegment";
static char geometry_msgs__msg__Point__TYPE_NAME[] = "geometry_msgs/msg/Point";
static char soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME[] = "soccer_vision_attribute_msgs/msg/Confidence";

// Define type names, field names, and default values
static char soccer_vision_3d_msgs__msg__MarkingSegment__FIELD_NAME__start[] = "start";
static char soccer_vision_3d_msgs__msg__MarkingSegment__FIELD_NAME__end[] = "end";
static char soccer_vision_3d_msgs__msg__MarkingSegment__FIELD_NAME__confidence[] = "confidence";

static rosidl_runtime_c__type_description__Field soccer_vision_3d_msgs__msg__MarkingSegment__FIELDS[] = {
  {
    {soccer_vision_3d_msgs__msg__MarkingSegment__FIELD_NAME__start, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_3d_msgs__msg__MarkingSegment__FIELD_NAME__end, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_3d_msgs__msg__MarkingSegment__FIELD_NAME__confidence, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME, 43, 43},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription soccer_vision_3d_msgs__msg__MarkingSegment__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME, 43, 43},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
soccer_vision_3d_msgs__msg__MarkingSegment__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {soccer_vision_3d_msgs__msg__MarkingSegment__TYPE_NAME, 40, 40},
      {soccer_vision_3d_msgs__msg__MarkingSegment__FIELDS, 3, 3},
    },
    {soccer_vision_3d_msgs__msg__MarkingSegment__REFERENCED_TYPE_DESCRIPTIONS, 2, 2},
  };
  if (!constructed) {
    assert(0 == memcmp(&geometry_msgs__msg__Point__EXPECTED_HASH, geometry_msgs__msg__Point__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = geometry_msgs__msg__Point__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&soccer_vision_attribute_msgs__msg__Confidence__EXPECTED_HASH, soccer_vision_attribute_msgs__msg__Confidence__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = soccer_vision_attribute_msgs__msg__Confidence__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Two points defining the ends of the segment.\n"
  "# The points should be located at the centre along the width of the segment marking.\n"
  "geometry_msgs/Point start\n"
  "geometry_msgs/Point end\n"
  "\n"
  "soccer_vision_attribute_msgs/Confidence confidence";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
soccer_vision_3d_msgs__msg__MarkingSegment__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {soccer_vision_3d_msgs__msg__MarkingSegment__TYPE_NAME, 40, 40},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 234, 234},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
soccer_vision_3d_msgs__msg__MarkingSegment__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[3];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 3, 3};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *soccer_vision_3d_msgs__msg__MarkingSegment__get_individual_type_description_source(NULL),
    sources[1] = *geometry_msgs__msg__Point__get_individual_type_description_source(NULL);
    sources[2] = *soccer_vision_attribute_msgs__msg__Confidence__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
