#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "soccer_model_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_model_msgs__msg__Ball() -> *const std::ffi::c_void;
}

#[link(name = "soccer_model_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_model_msgs__msg__Ball__init(msg: *mut Ball) -> bool;
    fn soccer_model_msgs__msg__Ball__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Ball>, size: usize) -> bool;
    fn soccer_model_msgs__msg__Ball__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Ball>);
    fn soccer_model_msgs__msg__Ball__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Ball>, out_seq: *mut rosidl_runtime_rs::Sequence<Ball>) -> bool;
}

// Corresponds to soccer_model_msgs__msg__Ball
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Describes a filtered ball from modelling modules, in 3d coordinates, with a header for global reference.
/// This msg type is used to publish all filtered balls from modelling modules.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Ball {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub point: soccer_geometry_msgs::msg::rmw::PointWithCovariance,


    // This member is not documented.
    #[allow(missing_docs)]
    pub twist: geometry_msgs::msg::rmw::TwistWithCovariance,

}



impl Default for Ball {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_model_msgs__msg__Ball__init(&mut msg as *mut _) {
        panic!("Call to soccer_model_msgs__msg__Ball__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Ball {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__Ball__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__Ball__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__Ball__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Ball {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Ball where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_model_msgs/msg/Ball";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_model_msgs__msg__Ball() }
  }
}


#[link(name = "soccer_model_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_model_msgs__msg__Obstacle() -> *const std::ffi::c_void;
}

#[link(name = "soccer_model_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_model_msgs__msg__Obstacle__init(msg: *mut Obstacle) -> bool;
    fn soccer_model_msgs__msg__Obstacle__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Obstacle>, size: usize) -> bool;
    fn soccer_model_msgs__msg__Obstacle__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Obstacle>);
    fn soccer_model_msgs__msg__Obstacle__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Obstacle>, out_seq: *mut rosidl_runtime_rs::Sequence<Obstacle>) -> bool;
}

// Corresponds to soccer_model_msgs__msg__Obstacle
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Describes a filtered obstacle from modelling modules, in 3d coordinates.
/// An Obstacle is defined as anything on the field that could not be classified as
/// one of the known types (such as Robot or Goalpost).

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Obstacle {

    // This member is not documented.
    #[allow(missing_docs)]
    pub pose: geometry_msgs::msg::rmw::PoseWithCovariance,


    // This member is not documented.
    #[allow(missing_docs)]
    pub twist: geometry_msgs::msg::rmw::TwistWithCovariance,

}



impl Default for Obstacle {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_model_msgs__msg__Obstacle__init(&mut msg as *mut _) {
        panic!("Call to soccer_model_msgs__msg__Obstacle__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Obstacle {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__Obstacle__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__Obstacle__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__Obstacle__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Obstacle {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Obstacle where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_model_msgs/msg/Obstacle";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_model_msgs__msg__Obstacle() }
  }
}


#[link(name = "soccer_model_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_model_msgs__msg__ObstacleArray() -> *const std::ffi::c_void;
}

#[link(name = "soccer_model_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_model_msgs__msg__ObstacleArray__init(msg: *mut ObstacleArray) -> bool;
    fn soccer_model_msgs__msg__ObstacleArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ObstacleArray>, size: usize) -> bool;
    fn soccer_model_msgs__msg__ObstacleArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ObstacleArray>);
    fn soccer_model_msgs__msg__ObstacleArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ObstacleArray>, out_seq: *mut rosidl_runtime_rs::Sequence<ObstacleArray>) -> bool;
}

// Corresponds to soccer_model_msgs__msg__ObstacleArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// An array of obstacles with a header for global reference.
/// This msg type is used to publish all filtered obstacles from modelling modules.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ObstacleArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub obstacles: rosidl_runtime_rs::Sequence<super::super::msg::rmw::Obstacle>,

}



impl Default for ObstacleArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_model_msgs__msg__ObstacleArray__init(&mut msg as *mut _) {
        panic!("Call to soccer_model_msgs__msg__ObstacleArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ObstacleArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__ObstacleArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__ObstacleArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__ObstacleArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ObstacleArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ObstacleArray where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_model_msgs/msg/ObstacleArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_model_msgs__msg__ObstacleArray() }
  }
}


#[link(name = "soccer_model_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_model_msgs__msg__Robot() -> *const std::ffi::c_void;
}

#[link(name = "soccer_model_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_model_msgs__msg__Robot__init(msg: *mut Robot) -> bool;
    fn soccer_model_msgs__msg__Robot__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Robot>, size: usize) -> bool;
    fn soccer_model_msgs__msg__Robot__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Robot>);
    fn soccer_model_msgs__msg__Robot__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Robot>, out_seq: *mut rosidl_runtime_rs::Sequence<Robot>) -> bool;
}

// Corresponds to soccer_model_msgs__msg__Robot
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Describes a filtered robot from modelling modules, in 3d coordinates.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Robot {

    // This member is not documented.
    #[allow(missing_docs)]
    pub pose: geometry_msgs::msg::rmw::PoseWithCovariance,


    // This member is not documented.
    #[allow(missing_docs)]
    pub twist: geometry_msgs::msg::rmw::TwistWithCovariance,


    // This member is not documented.
    #[allow(missing_docs)]
    pub attributes: soccer_vision_attribute_msgs::msg::rmw::Robot,

}



impl Default for Robot {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_model_msgs__msg__Robot__init(&mut msg as *mut _) {
        panic!("Call to soccer_model_msgs__msg__Robot__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Robot {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__Robot__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__Robot__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__Robot__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Robot {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Robot where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_model_msgs/msg/Robot";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_model_msgs__msg__Robot() }
  }
}


#[link(name = "soccer_model_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_model_msgs__msg__RobotArray() -> *const std::ffi::c_void;
}

#[link(name = "soccer_model_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_model_msgs__msg__RobotArray__init(msg: *mut RobotArray) -> bool;
    fn soccer_model_msgs__msg__RobotArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<RobotArray>, size: usize) -> bool;
    fn soccer_model_msgs__msg__RobotArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<RobotArray>);
    fn soccer_model_msgs__msg__RobotArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<RobotArray>, out_seq: *mut rosidl_runtime_rs::Sequence<RobotArray>) -> bool;
}

// Corresponds to soccer_model_msgs__msg__RobotArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// An array of robots with a header for global reference.
/// This msg type is used to publish all filtered robots from modelling modules.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RobotArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub robots: rosidl_runtime_rs::Sequence<super::super::msg::rmw::Robot>,

}



impl Default for RobotArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_model_msgs__msg__RobotArray__init(&mut msg as *mut _) {
        panic!("Call to soccer_model_msgs__msg__RobotArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for RobotArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__RobotArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__RobotArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_model_msgs__msg__RobotArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for RobotArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for RobotArray where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_model_msgs/msg/RobotArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_model_msgs__msg__RobotArray() }
  }
}


