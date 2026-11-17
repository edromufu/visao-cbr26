#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



#[link(name = "ipm_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__ipm_interfaces__srv__MapPoint_Request() -> *const std::ffi::c_void;
}

#[link(name = "ipm_interfaces__rosidl_generator_c")]
extern "C" {
    fn ipm_interfaces__srv__MapPoint_Request__init(msg: *mut MapPoint_Request) -> bool;
    fn ipm_interfaces__srv__MapPoint_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MapPoint_Request>, size: usize) -> bool;
    fn ipm_interfaces__srv__MapPoint_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MapPoint_Request>);
    fn ipm_interfaces__srv__MapPoint_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MapPoint_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<MapPoint_Request>) -> bool;
}

// Corresponds to ipm_interfaces__srv__MapPoint_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapPoint_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub plane: shape_msgs::msg::rmw::Plane,


    // This member is not documented.
    #[allow(missing_docs)]
    pub point: vision_msgs::msg::rmw::Point2D,


    // This member is not documented.
    #[allow(missing_docs)]
    pub time: builtin_interfaces::msg::rmw::Time,


    // This member is not documented.
    #[allow(missing_docs)]
    pub plane_frame_id: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub output_frame_id: rosidl_runtime_rs::String,

}



impl Default for MapPoint_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !ipm_interfaces__srv__MapPoint_Request__init(&mut msg as *mut _) {
        panic!("Call to ipm_interfaces__srv__MapPoint_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MapPoint_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { ipm_interfaces__srv__MapPoint_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { ipm_interfaces__srv__MapPoint_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { ipm_interfaces__srv__MapPoint_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MapPoint_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MapPoint_Request where Self: Sized {
  const TYPE_NAME: &'static str = "ipm_interfaces/srv/MapPoint_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__ipm_interfaces__srv__MapPoint_Request() }
  }
}


#[link(name = "ipm_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__ipm_interfaces__srv__MapPoint_Response() -> *const std::ffi::c_void;
}

#[link(name = "ipm_interfaces__rosidl_generator_c")]
extern "C" {
    fn ipm_interfaces__srv__MapPoint_Response__init(msg: *mut MapPoint_Response) -> bool;
    fn ipm_interfaces__srv__MapPoint_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MapPoint_Response>, size: usize) -> bool;
    fn ipm_interfaces__srv__MapPoint_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MapPoint_Response>);
    fn ipm_interfaces__srv__MapPoint_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MapPoint_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<MapPoint_Response>) -> bool;
}

// Corresponds to ipm_interfaces__srv__MapPoint_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapPoint_Response {
    /// Returned point is only valid if result equals RESULT_SUCCESS
    pub point: geometry_msgs::msg::rmw::PointStamped,


    // This member is not documented.
    #[allow(missing_docs)]
    pub result: u8,

}

impl MapPoint_Response {

    // This constant is not documented.
    #[allow(missing_docs)]
    pub const RESULT_SUCCESS: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const RESULT_NO_CAMERA_INFO: u8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const RESULT_INVALID_PLANE: u8 = 2;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const RESULT_NO_INTERSECTION: u8 = 3;

}


impl Default for MapPoint_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !ipm_interfaces__srv__MapPoint_Response__init(&mut msg as *mut _) {
        panic!("Call to ipm_interfaces__srv__MapPoint_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MapPoint_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { ipm_interfaces__srv__MapPoint_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { ipm_interfaces__srv__MapPoint_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { ipm_interfaces__srv__MapPoint_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MapPoint_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MapPoint_Response where Self: Sized {
  const TYPE_NAME: &'static str = "ipm_interfaces/srv/MapPoint_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__ipm_interfaces__srv__MapPoint_Response() }
  }
}


#[link(name = "ipm_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__ipm_interfaces__srv__MapPointCloud2_Request() -> *const std::ffi::c_void;
}

#[link(name = "ipm_interfaces__rosidl_generator_c")]
extern "C" {
    fn ipm_interfaces__srv__MapPointCloud2_Request__init(msg: *mut MapPointCloud2_Request) -> bool;
    fn ipm_interfaces__srv__MapPointCloud2_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MapPointCloud2_Request>, size: usize) -> bool;
    fn ipm_interfaces__srv__MapPointCloud2_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MapPointCloud2_Request>);
    fn ipm_interfaces__srv__MapPointCloud2_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MapPointCloud2_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<MapPointCloud2_Request>) -> bool;
}

// Corresponds to ipm_interfaces__srv__MapPointCloud2_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapPointCloud2_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub plane: shape_msgs::msg::rmw::Plane,


    // This member is not documented.
    #[allow(missing_docs)]
    pub points: sensor_msgs::msg::rmw::PointCloud2,


    // This member is not documented.
    #[allow(missing_docs)]
    pub plane_frame_id: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub output_frame_id: rosidl_runtime_rs::String,

}



impl Default for MapPointCloud2_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !ipm_interfaces__srv__MapPointCloud2_Request__init(&mut msg as *mut _) {
        panic!("Call to ipm_interfaces__srv__MapPointCloud2_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MapPointCloud2_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { ipm_interfaces__srv__MapPointCloud2_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { ipm_interfaces__srv__MapPointCloud2_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { ipm_interfaces__srv__MapPointCloud2_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MapPointCloud2_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MapPointCloud2_Request where Self: Sized {
  const TYPE_NAME: &'static str = "ipm_interfaces/srv/MapPointCloud2_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__ipm_interfaces__srv__MapPointCloud2_Request() }
  }
}


#[link(name = "ipm_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__ipm_interfaces__srv__MapPointCloud2_Response() -> *const std::ffi::c_void;
}

#[link(name = "ipm_interfaces__rosidl_generator_c")]
extern "C" {
    fn ipm_interfaces__srv__MapPointCloud2_Response__init(msg: *mut MapPointCloud2_Response) -> bool;
    fn ipm_interfaces__srv__MapPointCloud2_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MapPointCloud2_Response>, size: usize) -> bool;
    fn ipm_interfaces__srv__MapPointCloud2_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MapPointCloud2_Response>);
    fn ipm_interfaces__srv__MapPointCloud2_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MapPointCloud2_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<MapPointCloud2_Response>) -> bool;
}

// Corresponds to ipm_interfaces__srv__MapPointCloud2_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapPointCloud2_Response {
    /// Returned pointcloud is only valid if result equals RESULT_SUCCESS
    pub points: sensor_msgs::msg::rmw::PointCloud2,


    // This member is not documented.
    #[allow(missing_docs)]
    pub result: u8,

}

impl MapPointCloud2_Response {

    // This constant is not documented.
    #[allow(missing_docs)]
    pub const RESULT_SUCCESS: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const RESULT_NO_CAMERA_INFO: u8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const RESULT_INVALID_PLANE: u8 = 2;

}


impl Default for MapPointCloud2_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !ipm_interfaces__srv__MapPointCloud2_Response__init(&mut msg as *mut _) {
        panic!("Call to ipm_interfaces__srv__MapPointCloud2_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MapPointCloud2_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { ipm_interfaces__srv__MapPointCloud2_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { ipm_interfaces__srv__MapPointCloud2_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { ipm_interfaces__srv__MapPointCloud2_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MapPointCloud2_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MapPointCloud2_Response where Self: Sized {
  const TYPE_NAME: &'static str = "ipm_interfaces/srv/MapPointCloud2_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__ipm_interfaces__srv__MapPointCloud2_Response() }
  }
}






#[link(name = "ipm_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__ipm_interfaces__srv__MapPoint() -> *const std::ffi::c_void;
}

// Corresponds to ipm_interfaces__srv__MapPoint
#[allow(missing_docs, non_camel_case_types)]
pub struct MapPoint;

impl rosidl_runtime_rs::Service for MapPoint {
    type Request = MapPoint_Request;
    type Response = MapPoint_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__ipm_interfaces__srv__MapPoint() }
    }
}




#[link(name = "ipm_interfaces__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__ipm_interfaces__srv__MapPointCloud2() -> *const std::ffi::c_void;
}

// Corresponds to ipm_interfaces__srv__MapPointCloud2
#[allow(missing_docs, non_camel_case_types)]
pub struct MapPointCloud2;

impl rosidl_runtime_rs::Service for MapPointCloud2 {
    type Request = MapPointCloud2_Request;
    type Response = MapPointCloud2_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__ipm_interfaces__srv__MapPointCloud2() }
    }
}


