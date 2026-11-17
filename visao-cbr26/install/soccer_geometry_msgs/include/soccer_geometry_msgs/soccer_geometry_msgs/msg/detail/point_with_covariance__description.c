// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from soccer_geometry_msgs:msg/PointWithCovariance.idl
// generated code does not contain a copyright notice

#include "soccer_geometry_msgs/msg/detail/point_with_covariance__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_soccer_geometry_msgs
const rosidl_type_hash_t *
soccer_geometry_msgs__msg__PointWithCovariance__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x71, 0xad, 0x31, 0x34, 0x76, 0x71, 0x5d, 0x2a,
      0x95, 0x0b, 0xc8, 0x43, 0x3b, 0x9e, 0xfa, 0x00,
      0x9a, 0x90, 0x74, 0x9d, 0xa6, 0xf0, 0xc0, 0xc6,
      0x4e, 0xb9, 0xc8, 0xd1, 0x2d, 0xe4, 0x62, 0x9a,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "geometry_msgs/msg/detail/point__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t geometry_msgs__msg__Point__EXPECTED_HASH = {1, {
    0x69, 0x63, 0x08, 0x48, 0x42, 0xa9, 0xb0, 0x44,
    0x94, 0xd6, 0xb2, 0x94, 0x1d, 0x11, 0x44, 0x47,
    0x08, 0xd8, 0x92, 0xda, 0x2f, 0x4b, 0x09, 0x84,
    0x3b, 0x9c, 0x43, 0xf4, 0x2a, 0x7f, 0x68, 0x81,
  }};
#endif

static char soccer_geometry_msgs__msg__PointWithCovariance__TYPE_NAME[] = "soccer_geometry_msgs/msg/PointWithCovariance";
static char geometry_msgs__msg__Point__TYPE_NAME[] = "geometry_msgs/msg/Point";

// Define type names, field names, and default values
static char soccer_geometry_msgs__msg__PointWithCovariance__FIELD_NAME__point[] = "point";
static char soccer_geometry_msgs__msg__PointWithCovariance__FIELD_NAME__covariance[] = "covariance";

static rosidl_runtime_c__type_description__Field soccer_geometry_msgs__msg__PointWithCovariance__FIELDS[] = {
  {
    {soccer_geometry_msgs__msg__PointWithCovariance__FIELD_NAME__point, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_geometry_msgs__msg__PointWithCovariance__FIELD_NAME__covariance, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE_ARRAY,
      9,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription soccer_geometry_msgs__msg__PointWithCovariance__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
soccer_geometry_msgs__msg__PointWithCovariance__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {soccer_geometry_msgs__msg__PointWithCovariance__TYPE_NAME, 44, 44},
      {soccer_geometry_msgs__msg__PointWithCovariance__FIELDS, 2, 2},
    },
    {soccer_geometry_msgs__msg__PointWithCovariance__REFERENCED_TYPE_DESCRIPTIONS, 1, 1},
  };
  if (!constructed) {
    assert(0 == memcmp(&geometry_msgs__msg__Point__EXPECTED_HASH, geometry_msgs__msg__Point__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = geometry_msgs__msg__Point__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# This represents a point in free space with uncertainty.\n"
  "geometry_msgs/Point point\n"
  "\n"
  "# Row-major representation of the 3x3 covariance matrix\n"
  "# The orientation parameters use a fixed-axis representation.\n"
  "# In order, the parameters are:\n"
  "# (x, y, z)\n"
  "float64[9] covariance";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
soccer_geometry_msgs__msg__PointWithCovariance__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {soccer_geometry_msgs__msg__PointWithCovariance__TYPE_NAME, 44, 44},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 269, 269},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
soccer_geometry_msgs__msg__PointWithCovariance__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[2];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 2, 2};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *soccer_geometry_msgs__msg__PointWithCovariance__get_individual_type_description_source(NULL),
    sources[1] = *geometry_msgs__msg__Point__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
