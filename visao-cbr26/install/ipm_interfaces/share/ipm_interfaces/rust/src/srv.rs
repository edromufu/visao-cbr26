#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};




// Corresponds to ipm_interfaces__srv__MapPoint_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapPoint_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub plane: shape_msgs::msg::Plane,


    // This member is not documented.
    #[allow(missing_docs)]
    pub point: vision_msgs::msg::Point2D,


    // This member is not documented.
    #[allow(missing_docs)]
    pub time: builtin_interfaces::msg::Time,


    // This member is not documented.
    #[allow(missing_docs)]
    pub plane_frame_id: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub output_frame_id: std::string::String,

}



impl Default for MapPoint_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MapPoint_Request::default())
  }
}

impl rosidl_runtime_rs::Message for MapPoint_Request {
  type RmwMsg = super::srv::rmw::MapPoint_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        plane: shape_msgs::msg::Plane::into_rmw_message(std::borrow::Cow::Owned(msg.plane)).into_owned(),
        point: vision_msgs::msg::Point2D::into_rmw_message(std::borrow::Cow::Owned(msg.point)).into_owned(),
        time: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Owned(msg.time)).into_owned(),
        plane_frame_id: msg.plane_frame_id.as_str().into(),
        output_frame_id: msg.output_frame_id.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        plane: shape_msgs::msg::Plane::into_rmw_message(std::borrow::Cow::Borrowed(&msg.plane)).into_owned(),
        point: vision_msgs::msg::Point2D::into_rmw_message(std::borrow::Cow::Borrowed(&msg.point)).into_owned(),
        time: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Borrowed(&msg.time)).into_owned(),
        plane_frame_id: msg.plane_frame_id.as_str().into(),
        output_frame_id: msg.output_frame_id.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      plane: shape_msgs::msg::Plane::from_rmw_message(msg.plane),
      point: vision_msgs::msg::Point2D::from_rmw_message(msg.point),
      time: builtin_interfaces::msg::Time::from_rmw_message(msg.time),
      plane_frame_id: msg.plane_frame_id.to_string(),
      output_frame_id: msg.output_frame_id.to_string(),
    }
  }
}


// Corresponds to ipm_interfaces__srv__MapPoint_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapPoint_Response {
    /// Returned point is only valid if result equals RESULT_SUCCESS
    pub point: geometry_msgs::msg::PointStamped,


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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MapPoint_Response::default())
  }
}

impl rosidl_runtime_rs::Message for MapPoint_Response {
  type RmwMsg = super::srv::rmw::MapPoint_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        point: geometry_msgs::msg::PointStamped::into_rmw_message(std::borrow::Cow::Owned(msg.point)).into_owned(),
        result: msg.result,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        point: geometry_msgs::msg::PointStamped::into_rmw_message(std::borrow::Cow::Borrowed(&msg.point)).into_owned(),
      result: msg.result,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      point: geometry_msgs::msg::PointStamped::from_rmw_message(msg.point),
      result: msg.result,
    }
  }
}


// Corresponds to ipm_interfaces__srv__MapPointCloud2_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapPointCloud2_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub plane: shape_msgs::msg::Plane,


    // This member is not documented.
    #[allow(missing_docs)]
    pub points: sensor_msgs::msg::PointCloud2,


    // This member is not documented.
    #[allow(missing_docs)]
    pub plane_frame_id: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub output_frame_id: std::string::String,

}



impl Default for MapPointCloud2_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MapPointCloud2_Request::default())
  }
}

impl rosidl_runtime_rs::Message for MapPointCloud2_Request {
  type RmwMsg = super::srv::rmw::MapPointCloud2_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        plane: shape_msgs::msg::Plane::into_rmw_message(std::borrow::Cow::Owned(msg.plane)).into_owned(),
        points: sensor_msgs::msg::PointCloud2::into_rmw_message(std::borrow::Cow::Owned(msg.points)).into_owned(),
        plane_frame_id: msg.plane_frame_id.as_str().into(),
        output_frame_id: msg.output_frame_id.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        plane: shape_msgs::msg::Plane::into_rmw_message(std::borrow::Cow::Borrowed(&msg.plane)).into_owned(),
        points: sensor_msgs::msg::PointCloud2::into_rmw_message(std::borrow::Cow::Borrowed(&msg.points)).into_owned(),
        plane_frame_id: msg.plane_frame_id.as_str().into(),
        output_frame_id: msg.output_frame_id.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      plane: shape_msgs::msg::Plane::from_rmw_message(msg.plane),
      points: sensor_msgs::msg::PointCloud2::from_rmw_message(msg.points),
      plane_frame_id: msg.plane_frame_id.to_string(),
      output_frame_id: msg.output_frame_id.to_string(),
    }
  }
}


// Corresponds to ipm_interfaces__srv__MapPointCloud2_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MapPointCloud2_Response {
    /// Returned pointcloud is only valid if result equals RESULT_SUCCESS
    pub points: sensor_msgs::msg::PointCloud2,


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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MapPointCloud2_Response::default())
  }
}

impl rosidl_runtime_rs::Message for MapPointCloud2_Response {
  type RmwMsg = super::srv::rmw::MapPointCloud2_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        points: sensor_msgs::msg::PointCloud2::into_rmw_message(std::borrow::Cow::Owned(msg.points)).into_owned(),
        result: msg.result,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        points: sensor_msgs::msg::PointCloud2::into_rmw_message(std::borrow::Cow::Borrowed(&msg.points)).into_owned(),
      result: msg.result,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      points: sensor_msgs::msg::PointCloud2::from_rmw_message(msg.points),
      result: msg.result,
    }
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


