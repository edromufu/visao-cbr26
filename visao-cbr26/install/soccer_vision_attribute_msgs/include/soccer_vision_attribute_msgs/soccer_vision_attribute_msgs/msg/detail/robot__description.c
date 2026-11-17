// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from soccer_vision_attribute_msgs:msg/Robot.idl
// generated code does not contain a copyright notice

#include "soccer_vision_attribute_msgs/msg/detail/robot__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_soccer_vision_attribute_msgs
const rosidl_type_hash_t *
soccer_vision_attribute_msgs__msg__Robot__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x9c, 0x09, 0xf0, 0x33, 0x04, 0xe3, 0x5c, 0x3d,
      0xff, 0x01, 0x62, 0xc1, 0x57, 0x87, 0x00, 0xc9,
      0x11, 0xe9, 0x75, 0x78, 0x75, 0xc0, 0xef, 0x4b,
      0x34, 0xb3, 0x0d, 0x81, 0xe1, 0xf3, 0x28, 0xa4,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char soccer_vision_attribute_msgs__msg__Robot__TYPE_NAME[] = "soccer_vision_attribute_msgs/msg/Robot";

// Define type names, field names, and default values
static char soccer_vision_attribute_msgs__msg__Robot__FIELD_NAME__player_number[] = "player_number";
static char soccer_vision_attribute_msgs__msg__Robot__FIELD_NAME__team[] = "team";
static char soccer_vision_attribute_msgs__msg__Robot__FIELD_NAME__state[] = "state";
static char soccer_vision_attribute_msgs__msg__Robot__FIELD_NAME__facing[] = "facing";

static rosidl_runtime_c__type_description__Field soccer_vision_attribute_msgs__msg__Robot__FIELDS[] = {
  {
    {soccer_vision_attribute_msgs__msg__Robot__FIELD_NAME__player_number, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_attribute_msgs__msg__Robot__FIELD_NAME__team, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_attribute_msgs__msg__Robot__FIELD_NAME__state, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_attribute_msgs__msg__Robot__FIELD_NAME__facing, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
soccer_vision_attribute_msgs__msg__Robot__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {soccer_vision_attribute_msgs__msg__Robot__TYPE_NAME, 38, 38},
      {soccer_vision_attribute_msgs__msg__Robot__FIELDS, 4, 4},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 NUMBER_UNKNOWN=0\n"
  "\n"
  "uint8 TEAM_UNKNOWN=0\n"
  "uint8 TEAM_OWN=1\n"
  "uint8 TEAM_OPPONENT=2\n"
  "\n"
  "uint8 STATE_UNKNOWN=0\n"
  "uint8 STATE_STANDING=1\n"
  "uint8 STATE_FALLEN=2\n"
  "uint8 STATE_KICKING=3\n"
  "uint8 STATE_INACTIVE=4\n"
  "\n"
  "uint8 FACING_UNKNOWN=0\n"
  "uint8 FACING_THIS_WAY=1\n"
  "uint8 FACING_AWAY=2\n"
  "uint8 FACING_LEFT=3\n"
  "uint8 FACING_RIGHT=4\n"
  "\n"
  "# The number of the robot, if it can be read from the image.\n"
  "# Values can range from NUMBER_UNKNOWN(0) up to 255.\n"
  "uint8 player_number\n"
  "\n"
  "# Which team's robot it is. \n"
  "# Value can be TEAM_UNKNOWN, TEAM_OWN or TEAM_OPPONENT\n"
  "uint8 team\n"
  "\n"
  "# State of the robot.\n"
  "# Value can be one of the STATE_* constants defined in this msg\n"
  "uint8 state\n"
  "\n"
  "# An approximate direction the robot is facing in the image.\n"
  "# Value can be one of the FACING_* constants defined in this msg\n"
  "uint8 facing";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
soccer_vision_attribute_msgs__msg__Robot__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {soccer_vision_attribute_msgs__msg__Robot__TYPE_NAME, 38, 38},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 775, 775},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
soccer_vision_attribute_msgs__msg__Robot__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *soccer_vision_attribute_msgs__msg__Robot__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
