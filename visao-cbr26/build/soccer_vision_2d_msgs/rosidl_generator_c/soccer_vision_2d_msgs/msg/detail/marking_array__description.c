// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from soccer_vision_2d_msgs:msg/MarkingArray.idl
// generated code does not contain a copyright notice

#include "soccer_vision_2d_msgs/msg/detail/marking_array__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_soccer_vision_2d_msgs
const rosidl_type_hash_t *
soccer_vision_2d_msgs__msg__MarkingArray__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x85, 0x32, 0xe3, 0x2a, 0x8b, 0x63, 0xa8, 0x23,
      0x73, 0x0d, 0x6f, 0xef, 0xe2, 0xef, 0xb3, 0xab,
      0x75, 0xd7, 0xce, 0xd9, 0x8c, 0x1b, 0x9e, 0x9a,
      0x98, 0x15, 0x26, 0xe9, 0xfd, 0x3d, 0xa8, 0xae,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "soccer_vision_attribute_msgs/msg/detail/confidence__functions.h"
#include "std_msgs/msg/detail/header__functions.h"
#include "vision_msgs/msg/detail/point2_d__functions.h"
#include "vision_msgs/msg/detail/pose2_d__functions.h"
#include "builtin_interfaces/msg/detail/time__functions.h"
#include "soccer_vision_2d_msgs/msg/detail/marking_intersection__functions.h"
#include "vision_msgs/msg/detail/bounding_box2_d__functions.h"
#include "soccer_vision_2d_msgs/msg/detail/marking_segment__functions.h"
#include "soccer_vision_2d_msgs/msg/detail/marking_ellipse__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t builtin_interfaces__msg__Time__EXPECTED_HASH = {1, {
    0xb1, 0x06, 0x23, 0x5e, 0x25, 0xa4, 0xc5, 0xed,
    0x35, 0x09, 0x8a, 0xa0, 0xa6, 0x1a, 0x3e, 0xe9,
    0xc9, 0xb1, 0x8d, 0x19, 0x7f, 0x39, 0x8b, 0x0e,
    0x42, 0x06, 0xce, 0xa9, 0xac, 0xf9, 0xc1, 0x97,
  }};
static const rosidl_type_hash_t soccer_vision_2d_msgs__msg__MarkingEllipse__EXPECTED_HASH = {1, {
    0xdb, 0x08, 0x07, 0xec, 0xc1, 0xbc, 0x75, 0x3d,
    0x4d, 0x39, 0x8b, 0x76, 0x3c, 0xd1, 0x83, 0xdd,
    0x35, 0x07, 0xf2, 0x6d, 0x9e, 0xab, 0xc7, 0xb4,
    0x26, 0x49, 0x3c, 0x69, 0xf9, 0x3f, 0x4a, 0x89,
  }};
static const rosidl_type_hash_t soccer_vision_2d_msgs__msg__MarkingIntersection__EXPECTED_HASH = {1, {
    0x34, 0x15, 0xec, 0x9c, 0x7c, 0x85, 0xa4, 0x85,
    0x3e, 0x5c, 0x06, 0x9c, 0x69, 0x7a, 0xa1, 0x56,
    0xa2, 0xf2, 0x81, 0xfc, 0x97, 0xd3, 0xd4, 0x62,
    0xbc, 0xd4, 0xdc, 0x28, 0xd3, 0x2c, 0xc2, 0x1e,
  }};
static const rosidl_type_hash_t soccer_vision_2d_msgs__msg__MarkingSegment__EXPECTED_HASH = {1, {
    0x6a, 0x5a, 0xb5, 0xf1, 0x46, 0xce, 0x5e, 0x0e,
    0x3e, 0xd8, 0x58, 0xbc, 0x4c, 0x03, 0x82, 0x5d,
    0x00, 0x59, 0x9a, 0x14, 0x2a, 0x8d, 0x11, 0x06,
    0xdf, 0xda, 0x0c, 0x63, 0x34, 0xbf, 0x63, 0x4b,
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

static char soccer_vision_2d_msgs__msg__MarkingArray__TYPE_NAME[] = "soccer_vision_2d_msgs/msg/MarkingArray";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char soccer_vision_2d_msgs__msg__MarkingEllipse__TYPE_NAME[] = "soccer_vision_2d_msgs/msg/MarkingEllipse";
static char soccer_vision_2d_msgs__msg__MarkingIntersection__TYPE_NAME[] = "soccer_vision_2d_msgs/msg/MarkingIntersection";
static char soccer_vision_2d_msgs__msg__MarkingSegment__TYPE_NAME[] = "soccer_vision_2d_msgs/msg/MarkingSegment";
static char soccer_vision_attribute_msgs__msg__Confidence__TYPE_NAME[] = "soccer_vision_attribute_msgs/msg/Confidence";
static char std_msgs__msg__Header__TYPE_NAME[] = "std_msgs/msg/Header";
static char vision_msgs__msg__BoundingBox2D__TYPE_NAME[] = "vision_msgs/msg/BoundingBox2D";
static char vision_msgs__msg__Point2D__TYPE_NAME[] = "vision_msgs/msg/Point2D";
static char vision_msgs__msg__Pose2D__TYPE_NAME[] = "vision_msgs/msg/Pose2D";

// Define type names, field names, and default values
static char soccer_vision_2d_msgs__msg__MarkingArray__FIELD_NAME__header[] = "header";
static char soccer_vision_2d_msgs__msg__MarkingArray__FIELD_NAME__ellipses[] = "ellipses";
static char soccer_vision_2d_msgs__msg__MarkingArray__FIELD_NAME__intersections[] = "intersections";
static char soccer_vision_2d_msgs__msg__MarkingArray__FIELD_NAME__segments[] = "segments";

static rosidl_runtime_c__type_description__Field soccer_vision_2d_msgs__msg__MarkingArray__FIELDS[] = {
  {
    {soccer_vision_2d_msgs__msg__MarkingArray__FIELD_NAME__header, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_2d_msgs__msg__MarkingArray__FIELD_NAME__ellipses, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {soccer_vision_2d_msgs__msg__MarkingEllipse__TYPE_NAME, 40, 40},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_2d_msgs__msg__MarkingArray__FIELD_NAME__intersections, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {soccer_vision_2d_msgs__msg__MarkingIntersection__TYPE_NAME, 45, 45},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_2d_msgs__msg__MarkingArray__FIELD_NAME__segments, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {soccer_vision_2d_msgs__msg__MarkingSegment__TYPE_NAME, 40, 40},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription soccer_vision_2d_msgs__msg__MarkingArray__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {soccer_vision_2d_msgs__msg__MarkingEllipse__TYPE_NAME, 40, 40},
    {NULL, 0, 0},
  },
  {
    {soccer_vision_2d_msgs__msg__MarkingIntersection__TYPE_NAME, 45, 45},
    {NULL, 0, 0},
  },
  {
    {soccer_vision_2d_msgs__msg__MarkingSegment__TYPE_NAME, 40, 40},
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
soccer_vision_2d_msgs__msg__MarkingArray__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {soccer_vision_2d_msgs__msg__MarkingArray__TYPE_NAME, 38, 38},
      {soccer_vision_2d_msgs__msg__MarkingArray__FIELDS, 4, 4},
    },
    {soccer_vision_2d_msgs__msg__MarkingArray__REFERENCED_TYPE_DESCRIPTIONS, 9, 9},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&soccer_vision_2d_msgs__msg__MarkingEllipse__EXPECTED_HASH, soccer_vision_2d_msgs__msg__MarkingEllipse__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = soccer_vision_2d_msgs__msg__MarkingEllipse__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&soccer_vision_2d_msgs__msg__MarkingIntersection__EXPECTED_HASH, soccer_vision_2d_msgs__msg__MarkingIntersection__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = soccer_vision_2d_msgs__msg__MarkingIntersection__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&soccer_vision_2d_msgs__msg__MarkingSegment__EXPECTED_HASH, soccer_vision_2d_msgs__msg__MarkingSegment__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = soccer_vision_2d_msgs__msg__MarkingSegment__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&soccer_vision_attribute_msgs__msg__Confidence__EXPECTED_HASH, soccer_vision_attribute_msgs__msg__Confidence__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[4].fields = soccer_vision_attribute_msgs__msg__Confidence__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[5].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&vision_msgs__msg__BoundingBox2D__EXPECTED_HASH, vision_msgs__msg__BoundingBox2D__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[6].fields = vision_msgs__msg__BoundingBox2D__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&vision_msgs__msg__Point2D__EXPECTED_HASH, vision_msgs__msg__Point2D__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[7].fields = vision_msgs__msg__Point2D__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&vision_msgs__msg__Pose2D__EXPECTED_HASH, vision_msgs__msg__Pose2D__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[8].fields = vision_msgs__msg__Pose2D__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# An array of markings with a header for global reference.\n"
  "# This msg type is used to publish all markings detected in an image.\n"
  "\n"
  "std_msgs/Header header\n"
  "soccer_vision_2d_msgs/MarkingEllipse[] ellipses\n"
  "soccer_vision_2d_msgs/MarkingIntersection[] intersections\n"
  "soccer_vision_2d_msgs/MarkingSegment[] segments";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
soccer_vision_2d_msgs__msg__MarkingArray__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {soccer_vision_2d_msgs__msg__MarkingArray__TYPE_NAME, 38, 38},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 307, 307},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
soccer_vision_2d_msgs__msg__MarkingArray__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[10];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 10, 10};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *soccer_vision_2d_msgs__msg__MarkingArray__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *soccer_vision_2d_msgs__msg__MarkingEllipse__get_individual_type_description_source(NULL);
    sources[3] = *soccer_vision_2d_msgs__msg__MarkingIntersection__get_individual_type_description_source(NULL);
    sources[4] = *soccer_vision_2d_msgs__msg__MarkingSegment__get_individual_type_description_source(NULL);
    sources[5] = *soccer_vision_attribute_msgs__msg__Confidence__get_individual_type_description_source(NULL);
    sources[6] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    sources[7] = *vision_msgs__msg__BoundingBox2D__get_individual_type_description_source(NULL);
    sources[8] = *vision_msgs__msg__Point2D__get_individual_type_description_source(NULL);
    sources[9] = *vision_msgs__msg__Pose2D__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
