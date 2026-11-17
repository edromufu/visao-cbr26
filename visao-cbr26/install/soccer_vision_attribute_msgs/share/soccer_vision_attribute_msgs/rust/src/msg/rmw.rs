#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "soccer_vision_attribute_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_attribute_msgs__msg__Confidence() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_attribute_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_attribute_msgs__msg__Confidence__init(msg: *mut Confidence) -> bool;
    fn soccer_vision_attribute_msgs__msg__Confidence__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Confidence>, size: usize) -> bool;
    fn soccer_vision_attribute_msgs__msg__Confidence__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Confidence>);
    fn soccer_vision_attribute_msgs__msg__Confidence__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Confidence>, out_seq: *mut rosidl_runtime_rs::Sequence<Confidence>) -> bool;
}

// Corresponds to soccer_vision_attribute_msgs__msg__Confidence
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Confidence {
    /// A confidence rating in the range, or -1.0(CONFIDENCE_UNKNOWN) by default.
    /// 0.0 - detection module is 0% sure
    /// 1.0 - detection module is 100% sure
    pub confidence: f32,

}

impl Confidence {

    // This constant is not documented.
    #[allow(missing_docs)]
    pub const CONFIDENCE_UNKNOWN: f32 = -1.0;

}


impl Default for Confidence {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_vision_attribute_msgs__msg__Confidence__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_attribute_msgs__msg__Confidence__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Confidence {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_attribute_msgs__msg__Confidence__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_attribute_msgs__msg__Confidence__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_attribute_msgs__msg__Confidence__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Confidence {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Confidence where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_attribute_msgs/msg/Confidence";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_attribute_msgs__msg__Confidence() }
  }
}


#[link(name = "soccer_vision_attribute_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_attribute_msgs__msg__Goalpost() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_attribute_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_attribute_msgs__msg__Goalpost__init(msg: *mut Goalpost) -> bool;
    fn soccer_vision_attribute_msgs__msg__Goalpost__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Goalpost>, size: usize) -> bool;
    fn soccer_vision_attribute_msgs__msg__Goalpost__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Goalpost>);
    fn soccer_vision_attribute_msgs__msg__Goalpost__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Goalpost>, out_seq: *mut rosidl_runtime_rs::Sequence<Goalpost>) -> bool;
}

// Corresponds to soccer_vision_attribute_msgs__msg__Goalpost
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Goalpost {
    /// Whether the post is a left or right post, when looking INTO the goal.
    /// Value can be SIDE_UNKNOWN, SIDE_LEFT or SIDE_RIGHT
    pub side: u8,

    /// Which team's goal, the goalpost is part of. A team's goal is the one
    /// they have to defend. This can be useful if the two goals have different colors,
    /// and you know whether you're looking at your own or opponent's goal.
    /// Value can be TEAM_UNKNOWN, TEAM_OWN or TEAM_OPPONENT
    pub team: u8,

}

impl Goalpost {

    // This constant is not documented.
    #[allow(missing_docs)]
    pub const SIDE_UNKNOWN: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const SIDE_LEFT: u8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const SIDE_RIGHT: u8 = 2;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const TEAM_UNKNOWN: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const TEAM_OWN: u8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const TEAM_OPPONENT: u8 = 2;

}


impl Default for Goalpost {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_vision_attribute_msgs__msg__Goalpost__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_attribute_msgs__msg__Goalpost__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Goalpost {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_attribute_msgs__msg__Goalpost__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_attribute_msgs__msg__Goalpost__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_attribute_msgs__msg__Goalpost__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Goalpost {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Goalpost where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_attribute_msgs/msg/Goalpost";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_attribute_msgs__msg__Goalpost() }
  }
}


#[link(name = "soccer_vision_attribute_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_attribute_msgs__msg__Robot() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_attribute_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_attribute_msgs__msg__Robot__init(msg: *mut Robot) -> bool;
    fn soccer_vision_attribute_msgs__msg__Robot__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Robot>, size: usize) -> bool;
    fn soccer_vision_attribute_msgs__msg__Robot__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Robot>);
    fn soccer_vision_attribute_msgs__msg__Robot__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Robot>, out_seq: *mut rosidl_runtime_rs::Sequence<Robot>) -> bool;
}

// Corresponds to soccer_vision_attribute_msgs__msg__Robot
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Robot {
    /// The number of the robot, if it can be read from the image.
    /// Values can range from NUMBER_UNKNOWN(0) up to 255.
    pub player_number: u8,

    /// Which team's robot it is.
    /// Value can be TEAM_UNKNOWN, TEAM_OWN or TEAM_OPPONENT
    pub team: u8,

    /// State of the robot.
    /// Value can be one of the STATE_* constants defined in this msg
    pub state: u8,

    /// An approximate direction the robot is facing in the image.
    /// Value can be one of the FACING_* constants defined in this msg
    pub facing: u8,

}

impl Robot {

    // This constant is not documented.
    #[allow(missing_docs)]
    pub const NUMBER_UNKNOWN: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const TEAM_UNKNOWN: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const TEAM_OWN: u8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const TEAM_OPPONENT: u8 = 2;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const STATE_UNKNOWN: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const STATE_STANDING: u8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const STATE_FALLEN: u8 = 2;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const STATE_KICKING: u8 = 3;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const STATE_INACTIVE: u8 = 4;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const FACING_UNKNOWN: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const FACING_THIS_WAY: u8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const FACING_AWAY: u8 = 2;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const FACING_LEFT: u8 = 3;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const FACING_RIGHT: u8 = 4;

}


impl Default for Robot {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_vision_attribute_msgs__msg__Robot__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_attribute_msgs__msg__Robot__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Robot {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_attribute_msgs__msg__Robot__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_attribute_msgs__msg__Robot__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_attribute_msgs__msg__Robot__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Robot {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Robot where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_attribute_msgs/msg/Robot";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_attribute_msgs__msg__Robot() }
  }
}


