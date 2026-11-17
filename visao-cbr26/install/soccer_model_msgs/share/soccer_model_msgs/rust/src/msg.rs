#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to soccer_model_msgs__msg__Ball
/// Describes a filtered ball from modelling modules, in 3d coordinates, with a header for global reference.
/// This msg type is used to publish all filtered balls from modelling modules.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Ball {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub point: soccer_geometry_msgs::msg::PointWithCovariance,


    // This member is not documented.
    #[allow(missing_docs)]
    pub twist: geometry_msgs::msg::TwistWithCovariance,

}



impl Default for Ball {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Ball::default())
  }
}

impl rosidl_runtime_rs::Message for Ball {
  type RmwMsg = super::msg::rmw::Ball;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        point: soccer_geometry_msgs::msg::PointWithCovariance::into_rmw_message(std::borrow::Cow::Owned(msg.point)).into_owned(),
        twist: geometry_msgs::msg::TwistWithCovariance::into_rmw_message(std::borrow::Cow::Owned(msg.twist)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        point: soccer_geometry_msgs::msg::PointWithCovariance::into_rmw_message(std::borrow::Cow::Borrowed(&msg.point)).into_owned(),
        twist: geometry_msgs::msg::TwistWithCovariance::into_rmw_message(std::borrow::Cow::Borrowed(&msg.twist)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      point: soccer_geometry_msgs::msg::PointWithCovariance::from_rmw_message(msg.point),
      twist: geometry_msgs::msg::TwistWithCovariance::from_rmw_message(msg.twist),
    }
  }
}


// Corresponds to soccer_model_msgs__msg__Obstacle
/// Describes a filtered obstacle from modelling modules, in 3d coordinates.
/// An Obstacle is defined as anything on the field that could not be classified as
/// one of the known types (such as Robot or Goalpost).

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Obstacle {

    // This member is not documented.
    #[allow(missing_docs)]
    pub pose: geometry_msgs::msg::PoseWithCovariance,


    // This member is not documented.
    #[allow(missing_docs)]
    pub twist: geometry_msgs::msg::TwistWithCovariance,

}



impl Default for Obstacle {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Obstacle::default())
  }
}

impl rosidl_runtime_rs::Message for Obstacle {
  type RmwMsg = super::msg::rmw::Obstacle;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        pose: geometry_msgs::msg::PoseWithCovariance::into_rmw_message(std::borrow::Cow::Owned(msg.pose)).into_owned(),
        twist: geometry_msgs::msg::TwistWithCovariance::into_rmw_message(std::borrow::Cow::Owned(msg.twist)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        pose: geometry_msgs::msg::PoseWithCovariance::into_rmw_message(std::borrow::Cow::Borrowed(&msg.pose)).into_owned(),
        twist: geometry_msgs::msg::TwistWithCovariance::into_rmw_message(std::borrow::Cow::Borrowed(&msg.twist)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      pose: geometry_msgs::msg::PoseWithCovariance::from_rmw_message(msg.pose),
      twist: geometry_msgs::msg::TwistWithCovariance::from_rmw_message(msg.twist),
    }
  }
}


// Corresponds to soccer_model_msgs__msg__ObstacleArray
/// An array of obstacles with a header for global reference.
/// This msg type is used to publish all filtered obstacles from modelling modules.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ObstacleArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub obstacles: Vec<super::msg::Obstacle>,

}



impl Default for ObstacleArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::ObstacleArray::default())
  }
}

impl rosidl_runtime_rs::Message for ObstacleArray {
  type RmwMsg = super::msg::rmw::ObstacleArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        obstacles: msg.obstacles
          .into_iter()
          .map(|elem| super::msg::Obstacle::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        obstacles: msg.obstacles
          .iter()
          .map(|elem| super::msg::Obstacle::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      obstacles: msg.obstacles
          .into_iter()
          .map(super::msg::Obstacle::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to soccer_model_msgs__msg__Robot
/// Describes a filtered robot from modelling modules, in 3d coordinates.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Robot {

    // This member is not documented.
    #[allow(missing_docs)]
    pub pose: geometry_msgs::msg::PoseWithCovariance,


    // This member is not documented.
    #[allow(missing_docs)]
    pub twist: geometry_msgs::msg::TwistWithCovariance,


    // This member is not documented.
    #[allow(missing_docs)]
    pub attributes: soccer_vision_attribute_msgs::msg::Robot,

}



impl Default for Robot {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Robot::default())
  }
}

impl rosidl_runtime_rs::Message for Robot {
  type RmwMsg = super::msg::rmw::Robot;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        pose: geometry_msgs::msg::PoseWithCovariance::into_rmw_message(std::borrow::Cow::Owned(msg.pose)).into_owned(),
        twist: geometry_msgs::msg::TwistWithCovariance::into_rmw_message(std::borrow::Cow::Owned(msg.twist)).into_owned(),
        attributes: soccer_vision_attribute_msgs::msg::Robot::into_rmw_message(std::borrow::Cow::Owned(msg.attributes)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        pose: geometry_msgs::msg::PoseWithCovariance::into_rmw_message(std::borrow::Cow::Borrowed(&msg.pose)).into_owned(),
        twist: geometry_msgs::msg::TwistWithCovariance::into_rmw_message(std::borrow::Cow::Borrowed(&msg.twist)).into_owned(),
        attributes: soccer_vision_attribute_msgs::msg::Robot::into_rmw_message(std::borrow::Cow::Borrowed(&msg.attributes)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      pose: geometry_msgs::msg::PoseWithCovariance::from_rmw_message(msg.pose),
      twist: geometry_msgs::msg::TwistWithCovariance::from_rmw_message(msg.twist),
      attributes: soccer_vision_attribute_msgs::msg::Robot::from_rmw_message(msg.attributes),
    }
  }
}


// Corresponds to soccer_model_msgs__msg__RobotArray
/// An array of robots with a header for global reference.
/// This msg type is used to publish all filtered robots from modelling modules.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RobotArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub robots: Vec<super::msg::Robot>,

}



impl Default for RobotArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::RobotArray::default())
  }
}

impl rosidl_runtime_rs::Message for RobotArray {
  type RmwMsg = super::msg::rmw::RobotArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        robots: msg.robots
          .into_iter()
          .map(|elem| super::msg::Robot::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        robots: msg.robots
          .iter()
          .map(|elem| super::msg::Robot::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      robots: msg.robots
          .into_iter()
          .map(super::msg::Robot::from_rmw_message)
          .collect(),
    }
  }
}


