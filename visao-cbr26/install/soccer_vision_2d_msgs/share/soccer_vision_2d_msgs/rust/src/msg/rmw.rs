#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "soccer_vision_2d_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__Ball() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_2d_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_2d_msgs__msg__Ball__init(msg: *mut Ball) -> bool;
    fn soccer_vision_2d_msgs__msg__Ball__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Ball>, size: usize) -> bool;
    fn soccer_vision_2d_msgs__msg__Ball__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Ball>);
    fn soccer_vision_2d_msgs__msg__Ball__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Ball>, out_seq: *mut rosidl_runtime_rs::Sequence<Ball>) -> bool;
}

// Corresponds to soccer_vision_2d_msgs__msg__Ball
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Describes a detected ball from vision modules, in image coordinates.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Ball {
    /// A bounding box that surrounds the ball in the image, this does not have to include
    /// the whole ball, but only the part of the ball that was detected.
    pub bb: vision_msgs::msg::rmw::BoundingBox2D,

    /// Center point of the ball in pixel coordinates
    pub center: vision_msgs::msg::rmw::Point2D,

    /// Confidence that the detected object is a ball
    pub confidence: soccer_vision_attribute_msgs::msg::rmw::Confidence,

}



impl Default for Ball {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_vision_2d_msgs__msg__Ball__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_2d_msgs__msg__Ball__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Ball {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__Ball__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__Ball__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__Ball__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Ball {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Ball where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_2d_msgs/msg/Ball";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__Ball() }
  }
}


#[link(name = "soccer_vision_2d_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__BallArray() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_2d_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_2d_msgs__msg__BallArray__init(msg: *mut BallArray) -> bool;
    fn soccer_vision_2d_msgs__msg__BallArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<BallArray>, size: usize) -> bool;
    fn soccer_vision_2d_msgs__msg__BallArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<BallArray>);
    fn soccer_vision_2d_msgs__msg__BallArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<BallArray>, out_seq: *mut rosidl_runtime_rs::Sequence<BallArray>) -> bool;
}

// Corresponds to soccer_vision_2d_msgs__msg__BallArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// An array of balls with a header for global reference.
/// This msg type is used to publish all balls detected in an image.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct BallArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub balls: rosidl_runtime_rs::Sequence<super::super::msg::rmw::Ball>,

}



impl Default for BallArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_vision_2d_msgs__msg__BallArray__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_2d_msgs__msg__BallArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for BallArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__BallArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__BallArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__BallArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for BallArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for BallArray where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_2d_msgs/msg/BallArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__BallArray() }
  }
}


#[link(name = "soccer_vision_2d_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__FieldBoundary() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_2d_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_2d_msgs__msg__FieldBoundary__init(msg: *mut FieldBoundary) -> bool;
    fn soccer_vision_2d_msgs__msg__FieldBoundary__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<FieldBoundary>, size: usize) -> bool;
    fn soccer_vision_2d_msgs__msg__FieldBoundary__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<FieldBoundary>);
    fn soccer_vision_2d_msgs__msg__FieldBoundary__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<FieldBoundary>, out_seq: *mut rosidl_runtime_rs::Sequence<FieldBoundary>) -> bool;
}

// Corresponds to soccer_vision_2d_msgs__msg__FieldBoundary
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Describes a detected field boundary from vision modules, in image coordinates.
/// The field boundary is defined as the line that separates the field of play, to
/// outside the field of play. Field of play is a sports terminology.
/// Usually, this is where the field carpet ends, or meets a field border.
/// If no field boundary was detected, leave the "points" vector empty.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct FieldBoundary {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

    /// The points along the field boundary detected in the image, are stored as a line strip.
    /// You can think of the field boundary as a line between every two consecutive points,
    /// so 0-1, 1-2, 2-3, 3-4, 4-5...
    /// 2D points (in pixel)
    pub points: rosidl_runtime_rs::Sequence<vision_msgs::msg::rmw::Point2D>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: soccer_vision_attribute_msgs::msg::rmw::Confidence,

}



impl Default for FieldBoundary {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_vision_2d_msgs__msg__FieldBoundary__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_2d_msgs__msg__FieldBoundary__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for FieldBoundary {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__FieldBoundary__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__FieldBoundary__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__FieldBoundary__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for FieldBoundary {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for FieldBoundary where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_2d_msgs/msg/FieldBoundary";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__FieldBoundary() }
  }
}


#[link(name = "soccer_vision_2d_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__Goalpost() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_2d_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_2d_msgs__msg__Goalpost__init(msg: *mut Goalpost) -> bool;
    fn soccer_vision_2d_msgs__msg__Goalpost__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Goalpost>, size: usize) -> bool;
    fn soccer_vision_2d_msgs__msg__Goalpost__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Goalpost>);
    fn soccer_vision_2d_msgs__msg__Goalpost__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Goalpost>, out_seq: *mut rosidl_runtime_rs::Sequence<Goalpost>) -> bool;
}

// Corresponds to soccer_vision_2d_msgs__msg__Goalpost
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Describes a detected goalpost from vision modules, in image coordinates.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Goalpost {
    /// A bounding box that surrounds the goalpost in the image, that can be rotated about its center.
    /// This does not have to include the whole goalpost, but only the
    /// part of the goalpost that was detected.
    /// The rotation of the bounding box should be 0 when the goalpost appears upright in the image.
    pub bb: vision_msgs::msg::rmw::BoundingBox2D,


    // This member is not documented.
    #[allow(missing_docs)]
    pub attributes: soccer_vision_attribute_msgs::msg::rmw::Goalpost,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: soccer_vision_attribute_msgs::msg::rmw::Confidence,

}



impl Default for Goalpost {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_vision_2d_msgs__msg__Goalpost__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_2d_msgs__msg__Goalpost__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Goalpost {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__Goalpost__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__Goalpost__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__Goalpost__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Goalpost {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Goalpost where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_2d_msgs/msg/Goalpost";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__Goalpost() }
  }
}


#[link(name = "soccer_vision_2d_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__GoalpostArray() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_2d_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_2d_msgs__msg__GoalpostArray__init(msg: *mut GoalpostArray) -> bool;
    fn soccer_vision_2d_msgs__msg__GoalpostArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GoalpostArray>, size: usize) -> bool;
    fn soccer_vision_2d_msgs__msg__GoalpostArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GoalpostArray>);
    fn soccer_vision_2d_msgs__msg__GoalpostArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GoalpostArray>, out_seq: *mut rosidl_runtime_rs::Sequence<GoalpostArray>) -> bool;
}

// Corresponds to soccer_vision_2d_msgs__msg__GoalpostArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// An array of goalposts with a header for global reference.
/// This msg type is used to publish all goalposts detected in an image.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GoalpostArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub posts: rosidl_runtime_rs::Sequence<super::super::msg::rmw::Goalpost>,

}



impl Default for GoalpostArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_vision_2d_msgs__msg__GoalpostArray__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_2d_msgs__msg__GoalpostArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GoalpostArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__GoalpostArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__GoalpostArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__GoalpostArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GoalpostArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GoalpostArray where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_2d_msgs/msg/GoalpostArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__GoalpostArray() }
  }
}


#[link(name = "soccer_vision_2d_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__MarkingEllipse() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_2d_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_2d_msgs__msg__MarkingEllipse__init(msg: *mut MarkingEllipse) -> bool;
    fn soccer_vision_2d_msgs__msg__MarkingEllipse__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MarkingEllipse>, size: usize) -> bool;
    fn soccer_vision_2d_msgs__msg__MarkingEllipse__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MarkingEllipse>);
    fn soccer_vision_2d_msgs__msg__MarkingEllipse__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MarkingEllipse>, out_seq: *mut rosidl_runtime_rs::Sequence<MarkingEllipse>) -> bool;
}

// Corresponds to soccer_vision_2d_msgs__msg__MarkingEllipse
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Describes a detected ellipse marking from vision modules, in image coordinates.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MarkingEllipse {
    /// A bounding box that surrounds the ellipse in the image, this does not have to include
    /// the whole ellipse, but only the part of the ellipse that was detected.
    pub bb: vision_msgs::msg::rmw::BoundingBox2D,

    /// Center point of the ellipse in pixel coordinates
    pub center: vision_msgs::msg::rmw::Point2D,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: soccer_vision_attribute_msgs::msg::rmw::Confidence,

}



impl Default for MarkingEllipse {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_vision_2d_msgs__msg__MarkingEllipse__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_2d_msgs__msg__MarkingEllipse__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MarkingEllipse {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__MarkingEllipse__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__MarkingEllipse__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__MarkingEllipse__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MarkingEllipse {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MarkingEllipse where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_2d_msgs/msg/MarkingEllipse";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__MarkingEllipse() }
  }
}


#[link(name = "soccer_vision_2d_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__MarkingIntersection() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_2d_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_2d_msgs__msg__MarkingIntersection__init(msg: *mut MarkingIntersection) -> bool;
    fn soccer_vision_2d_msgs__msg__MarkingIntersection__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MarkingIntersection>, size: usize) -> bool;
    fn soccer_vision_2d_msgs__msg__MarkingIntersection__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MarkingIntersection>);
    fn soccer_vision_2d_msgs__msg__MarkingIntersection__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MarkingIntersection>, out_seq: *mut rosidl_runtime_rs::Sequence<MarkingIntersection>) -> bool;
}

// Corresponds to soccer_vision_2d_msgs__msg__MarkingIntersection
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Describes a detected marking intersection from vision modules, in image coordinates.
/// An intersection is defined as a point where two or more line markings intersect.
/// The term ray is used to describe the outgoing rays from the center of the
/// intersection.
///
/// For example, looking down at a perfectly upright T-intersection on the ground from above, you would have:
/// - num_rays = 3
/// - heading_rays = [0, pi / 2, pi]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MarkingIntersection {
    /// Center point of the intersection, in pixel coordinates
    pub center: vision_msgs::msg::rmw::Point2D,

    /// The number of rays outgoing from an intersection. This is 3 for a T-Junction and
    /// 4 for an X-Junction
    pub num_rays: i32,

    /// NOTE: The length of the array should either:
    /// - Match the number of rays specified with num_rays OR
    /// - Be empty, if the headings are unknown
    /// Heading is defined as 0 along the +x axis, and pi / 2 along the +y axis.
    /// Headings should:
    /// - have an interval of [0, 2pi)
    /// - be stored in ascending order
    pub heading_rays: rosidl_runtime_rs::Sequence<f64>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: soccer_vision_attribute_msgs::msg::rmw::Confidence,

}



impl Default for MarkingIntersection {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_vision_2d_msgs__msg__MarkingIntersection__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_2d_msgs__msg__MarkingIntersection__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MarkingIntersection {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__MarkingIntersection__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__MarkingIntersection__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__MarkingIntersection__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MarkingIntersection {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MarkingIntersection where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_2d_msgs/msg/MarkingIntersection";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__MarkingIntersection() }
  }
}


#[link(name = "soccer_vision_2d_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__MarkingSegment() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_2d_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_2d_msgs__msg__MarkingSegment__init(msg: *mut MarkingSegment) -> bool;
    fn soccer_vision_2d_msgs__msg__MarkingSegment__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MarkingSegment>, size: usize) -> bool;
    fn soccer_vision_2d_msgs__msg__MarkingSegment__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MarkingSegment>);
    fn soccer_vision_2d_msgs__msg__MarkingSegment__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MarkingSegment>, out_seq: *mut rosidl_runtime_rs::Sequence<MarkingSegment>) -> bool;
}

// Corresponds to soccer_vision_2d_msgs__msg__MarkingSegment
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Describes a detected straight segment marking from vision modules, in image coordinates.
/// Note that curved segments can be approximated with a number of small segments, using
/// this msg.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MarkingSegment {
    /// Two points defining the ends of the segment.
    /// The points should be located at the centre along the width of the segment marking.
    pub start: vision_msgs::msg::rmw::Point2D,


    // This member is not documented.
    #[allow(missing_docs)]
    pub end: vision_msgs::msg::rmw::Point2D,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: soccer_vision_attribute_msgs::msg::rmw::Confidence,

}



impl Default for MarkingSegment {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_vision_2d_msgs__msg__MarkingSegment__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_2d_msgs__msg__MarkingSegment__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MarkingSegment {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__MarkingSegment__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__MarkingSegment__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__MarkingSegment__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MarkingSegment {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MarkingSegment where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_2d_msgs/msg/MarkingSegment";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__MarkingSegment() }
  }
}


#[link(name = "soccer_vision_2d_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__MarkingArray() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_2d_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_2d_msgs__msg__MarkingArray__init(msg: *mut MarkingArray) -> bool;
    fn soccer_vision_2d_msgs__msg__MarkingArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MarkingArray>, size: usize) -> bool;
    fn soccer_vision_2d_msgs__msg__MarkingArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MarkingArray>);
    fn soccer_vision_2d_msgs__msg__MarkingArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MarkingArray>, out_seq: *mut rosidl_runtime_rs::Sequence<MarkingArray>) -> bool;
}

// Corresponds to soccer_vision_2d_msgs__msg__MarkingArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// An array of markings with a header for global reference.
/// This msg type is used to publish all markings detected in an image.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MarkingArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub ellipses: rosidl_runtime_rs::Sequence<super::super::msg::rmw::MarkingEllipse>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub intersections: rosidl_runtime_rs::Sequence<super::super::msg::rmw::MarkingIntersection>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub segments: rosidl_runtime_rs::Sequence<super::super::msg::rmw::MarkingSegment>,

}



impl Default for MarkingArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_vision_2d_msgs__msg__MarkingArray__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_2d_msgs__msg__MarkingArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MarkingArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__MarkingArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__MarkingArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__MarkingArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MarkingArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MarkingArray where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_2d_msgs/msg/MarkingArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__MarkingArray() }
  }
}


#[link(name = "soccer_vision_2d_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__Obstacle() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_2d_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_2d_msgs__msg__Obstacle__init(msg: *mut Obstacle) -> bool;
    fn soccer_vision_2d_msgs__msg__Obstacle__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Obstacle>, size: usize) -> bool;
    fn soccer_vision_2d_msgs__msg__Obstacle__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Obstacle>);
    fn soccer_vision_2d_msgs__msg__Obstacle__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Obstacle>, out_seq: *mut rosidl_runtime_rs::Sequence<Obstacle>) -> bool;
}

// Corresponds to soccer_vision_2d_msgs__msg__Obstacle
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Describes a detected obstacle from vision modules, in image coordinates.
/// An Obstacle is defined as anything observed on the field that could not be classified as
/// one of the known types (such as Robot or Goalpost).

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Obstacle {
    /// A bounding box that surrounds the obstacle in the image, this does not have to include
    /// the whole obstacle, but only the part of the obstacle that was detected.
    pub bb: vision_msgs::msg::rmw::BoundingBox2D,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: soccer_vision_attribute_msgs::msg::rmw::Confidence,

}



impl Default for Obstacle {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_vision_2d_msgs__msg__Obstacle__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_2d_msgs__msg__Obstacle__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Obstacle {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__Obstacle__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__Obstacle__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__Obstacle__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Obstacle {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Obstacle where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_2d_msgs/msg/Obstacle";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__Obstacle() }
  }
}


#[link(name = "soccer_vision_2d_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__ObstacleArray() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_2d_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_2d_msgs__msg__ObstacleArray__init(msg: *mut ObstacleArray) -> bool;
    fn soccer_vision_2d_msgs__msg__ObstacleArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ObstacleArray>, size: usize) -> bool;
    fn soccer_vision_2d_msgs__msg__ObstacleArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ObstacleArray>);
    fn soccer_vision_2d_msgs__msg__ObstacleArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ObstacleArray>, out_seq: *mut rosidl_runtime_rs::Sequence<ObstacleArray>) -> bool;
}

// Corresponds to soccer_vision_2d_msgs__msg__ObstacleArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// An array of obstacles with a header for global reference.
/// This msg type is used to publish all obstacles detected in an image.

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
      if !soccer_vision_2d_msgs__msg__ObstacleArray__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_2d_msgs__msg__ObstacleArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ObstacleArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__ObstacleArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__ObstacleArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__ObstacleArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ObstacleArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ObstacleArray where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_2d_msgs/msg/ObstacleArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__ObstacleArray() }
  }
}


#[link(name = "soccer_vision_2d_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__Robot() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_2d_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_2d_msgs__msg__Robot__init(msg: *mut Robot) -> bool;
    fn soccer_vision_2d_msgs__msg__Robot__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Robot>, size: usize) -> bool;
    fn soccer_vision_2d_msgs__msg__Robot__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Robot>);
    fn soccer_vision_2d_msgs__msg__Robot__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Robot>, out_seq: *mut rosidl_runtime_rs::Sequence<Robot>) -> bool;
}

// Corresponds to soccer_vision_2d_msgs__msg__Robot
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Describes a detected robot from vision modules, in image coordinates.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Robot {
    /// A bounding box that surrounds the robot in the image, this does not have to include
    /// the whole robot, but only the part of the robot that was detected.
    pub bb: vision_msgs::msg::rmw::BoundingBox2D,


    // This member is not documented.
    #[allow(missing_docs)]
    pub attributes: soccer_vision_attribute_msgs::msg::rmw::Robot,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: soccer_vision_attribute_msgs::msg::rmw::Confidence,

}



impl Default for Robot {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_vision_2d_msgs__msg__Robot__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_2d_msgs__msg__Robot__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Robot {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__Robot__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__Robot__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__Robot__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Robot {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Robot where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_2d_msgs/msg/Robot";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__Robot() }
  }
}


#[link(name = "soccer_vision_2d_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__RobotArray() -> *const std::ffi::c_void;
}

#[link(name = "soccer_vision_2d_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_vision_2d_msgs__msg__RobotArray__init(msg: *mut RobotArray) -> bool;
    fn soccer_vision_2d_msgs__msg__RobotArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<RobotArray>, size: usize) -> bool;
    fn soccer_vision_2d_msgs__msg__RobotArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<RobotArray>);
    fn soccer_vision_2d_msgs__msg__RobotArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<RobotArray>, out_seq: *mut rosidl_runtime_rs::Sequence<RobotArray>) -> bool;
}

// Corresponds to soccer_vision_2d_msgs__msg__RobotArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// An array of robots with a header for global reference.
/// This msg type is used to publish all robots detected in an image.

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
      if !soccer_vision_2d_msgs__msg__RobotArray__init(&mut msg as *mut _) {
        panic!("Call to soccer_vision_2d_msgs__msg__RobotArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for RobotArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__RobotArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__RobotArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_vision_2d_msgs__msg__RobotArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for RobotArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for RobotArray where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_vision_2d_msgs/msg/RobotArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_vision_2d_msgs__msg__RobotArray() }
  }
}


