#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to soccer_geometry_msgs__msg__PointWithCovariance
/// This represents a point in free space with uncertainty.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct PointWithCovariance {

    // This member is not documented.
    #[allow(missing_docs)]
    pub point: geometry_msgs::msg::Point,

    /// Row-major representation of the 3x3 covariance matrix
    /// The orientation parameters use a fixed-axis representation.
    /// In order, the parameters are:
    /// (x, y, z)
    pub covariance: [f64; 9],

}



impl Default for PointWithCovariance {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::PointWithCovariance::default())
  }
}

impl rosidl_runtime_rs::Message for PointWithCovariance {
  type RmwMsg = super::msg::rmw::PointWithCovariance;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        point: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(msg.point)).into_owned(),
        covariance: msg.covariance,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        point: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(&msg.point)).into_owned(),
        covariance: msg.covariance,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      point: geometry_msgs::msg::Point::from_rmw_message(msg.point),
      covariance: msg.covariance,
    }
  }
}


