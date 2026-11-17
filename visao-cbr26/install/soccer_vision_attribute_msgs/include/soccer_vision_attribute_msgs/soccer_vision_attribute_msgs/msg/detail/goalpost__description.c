// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from soccer_vision_attribute_msgs:msg/Goalpost.idl
// generated code does not contain a copyright notice

#include "soccer_vision_attribute_msgs/msg/detail/goalpost__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_soccer_vision_attribute_msgs
const rosidl_type_hash_t *
soccer_vision_attribute_msgs__msg__Goalpost__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xcd, 0xe3, 0xa3, 0xb3, 0xba, 0xd6, 0x37, 0x77,
      0x0f, 0x0a, 0xc1, 0xbd, 0x00, 0x4a, 0xed, 0x9c,
      0x09, 0xc9, 0x45, 0xd3, 0x74, 0xea, 0x4f, 0xae,
      0xf9, 0xd1, 0xdc, 0x07, 0x2b, 0x20, 0xf9, 0x5b,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char soccer_vision_attribute_msgs__msg__Goalpost__TYPE_NAME[] = "soccer_vision_attribute_msgs/msg/Goalpost";

// Define type names, field names, and default values
static char soccer_vision_attribute_msgs__msg__Goalpost__FIELD_NAME__side[] = "side";
static char soccer_vision_attribute_msgs__msg__Goalpost__FIELD_NAME__team[] = "team";

static rosidl_runtime_c__type_description__Field soccer_vision_attribute_msgs__msg__Goalpost__FIELDS[] = {
  {
    {soccer_vision_attribute_msgs__msg__Goalpost__FIELD_NAME__side, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {soccer_vision_attribute_msgs__msg__Goalpost__FIELD_NAME__team, 4, 4},
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
soccer_vision_attribute_msgs__msg__Goalpost__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {soccer_vision_attribute_msgs__msg__Goalpost__TYPE_NAME, 41, 41},
      {soccer_vision_attribute_msgs__msg__Goalpost__FIELDS, 2, 2},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 SIDE_UNKNOWN=0\n"
  "uint8 SIDE_LEFT=1\n"
  "uint8 SIDE_RIGHT=2\n"
  "\n"
  "uint8 TEAM_UNKNOWN=0\n"
  "uint8 TEAM_OWN=1\n"
  "uint8 TEAM_OPPONENT=2\n"
  "\n"
  "# Whether the post is a left or right post, when looking INTO the goal.\n"
  "# Value can be SIDE_UNKNOWN, SIDE_LEFT or SIDE_RIGHT\n"
  "uint8 side\n"
  "\n"
  "# Which team's goal, the goalpost is part of. A team's goal is the one\n"
  "# they have to defend. This can be useful if the two goals have different colors,\n"
  "# and you know whether you're looking at your own or opponent's goal.\n"
  "# Value can be TEAM_UNKNOWN, TEAM_OWN or TEAM_OPPONENT\n"
  "uint8 team";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
soccer_vision_attribute_msgs__msg__Goalpost__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {soccer_vision_attribute_msgs__msg__Goalpost__TYPE_NAME, 41, 41},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 546, 546},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
soccer_vision_attribute_msgs__msg__Goalpost__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *soccer_vision_attribute_msgs__msg__Goalpost__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
