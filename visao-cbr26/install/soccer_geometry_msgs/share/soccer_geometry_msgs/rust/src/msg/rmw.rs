#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "soccer_geometry_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__soccer_geometry_msgs__msg__PointWithCovariance() -> *const std::ffi::c_void;
}

#[link(name = "soccer_geometry_msgs__rosidl_generator_c")]
extern "C" {
    fn soccer_geometry_msgs__msg__PointWithCovariance__init(msg: *mut PointWithCovariance) -> bool;
    fn soccer_geometry_msgs__msg__PointWithCovariance__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<PointWithCovariance>, size: usize) -> bool;
    fn soccer_geometry_msgs__msg__PointWithCovariance__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<PointWithCovariance>);
    fn soccer_geometry_msgs__msg__PointWithCovariance__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<PointWithCovariance>, out_seq: *mut rosidl_runtime_rs::Sequence<PointWithCovariance>) -> bool;
}

// Corresponds to soccer_geometry_msgs__msg__PointWithCovariance
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// This represents a point in free space with uncertainty.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct PointWithCovariance {

    // This member is not documented.
    #[allow(missing_docs)]
    pub point: geometry_msgs::msg::rmw::Point,

    /// Row-major representation of the 3x3 covariance matrix
    /// The orientation parameters use a fixed-axis representation.
    /// In order, the parameters are:
    /// (x, y, z)
    pub covariance: [f64; 9],

}



impl Default for PointWithCovariance {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !soccer_geometry_msgs__msg__PointWithCovariance__init(&mut msg as *mut _) {
        panic!("Call to soccer_geometry_msgs__msg__PointWithCovariance__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for PointWithCovariance {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_geometry_msgs__msg__PointWithCovariance__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_geometry_msgs__msg__PointWithCovariance__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { soccer_geometry_msgs__msg__PointWithCovariance__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for PointWithCovariance {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for PointWithCovariance where Self: Sized {
  const TYPE_NAME: &'static str = "soccer_geometry_msgs/msg/PointWithCovariance";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__soccer_geometry_msgs__msg__PointWithCovariance() }
  }
}


