#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to soccer_vision_3d_msgs__msg__Ball
/// Describes a detected ball from vision modules, in 3d coordinates.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Ball {
    /// Center point of the ball (in meters)
    pub center: geometry_msgs::msg::Point,

    /// Confidence that the detected object is a ball
    pub confidence: soccer_vision_attribute_msgs::msg::Confidence,

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
        center: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(msg.center)).into_owned(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Owned(msg.confidence)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        center: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(&msg.center)).into_owned(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Borrowed(&msg.confidence)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      center: geometry_msgs::msg::Point::from_rmw_message(msg.center),
      confidence: soccer_vision_attribute_msgs::msg::Confidence::from_rmw_message(msg.confidence),
    }
  }
}


// Corresponds to soccer_vision_3d_msgs__msg__BallArray
/// An array of balls with a header for global reference.
/// This msg type is used to publish all balls detected.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct BallArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub balls: Vec<super::msg::Ball>,

}



impl Default for BallArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::BallArray::default())
  }
}

impl rosidl_runtime_rs::Message for BallArray {
  type RmwMsg = super::msg::rmw::BallArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        balls: msg.balls
          .into_iter()
          .map(|elem| super::msg::Ball::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        balls: msg.balls
          .iter()
          .map(|elem| super::msg::Ball::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      balls: msg.balls
          .into_iter()
          .map(super::msg::Ball::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to soccer_vision_3d_msgs__msg__FieldBoundary
/// Describes a detected field boundary from vision modules, in 3d coordinates.
/// The field boundary is defined as the line that separates the field of play, to
/// outside the field of play. Field of play is a sports terminology.
/// Usually, this is where the field carpet ends, or meets a field border.
/// If no field boundary was detected, leave the "points" vector empty.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct FieldBoundary {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,

    /// The points along the field boundary detected in 3d space, are stored as a line strip.
    /// You can think of the field boundary as a line between every two consecutive points,
    /// so 0-1, 1-2, 2-3, 3-4, 4-5...
    pub points: Vec<geometry_msgs::msg::Point>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: soccer_vision_attribute_msgs::msg::Confidence,

}



impl Default for FieldBoundary {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::FieldBoundary::default())
  }
}

impl rosidl_runtime_rs::Message for FieldBoundary {
  type RmwMsg = super::msg::rmw::FieldBoundary;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        points: msg.points
          .into_iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Owned(msg.confidence)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        points: msg.points
          .iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Borrowed(&msg.confidence)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      points: msg.points
          .into_iter()
          .map(geometry_msgs::msg::Point::from_rmw_message)
          .collect(),
      confidence: soccer_vision_attribute_msgs::msg::Confidence::from_rmw_message(msg.confidence),
    }
  }
}


// Corresponds to soccer_vision_3d_msgs__msg__Goalpost
/// A bounding box that surrounds the goalpost in 3d space.
/// This does not have to include the whole goalpost, but only the 
/// part of the goalpost that was detected.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Goalpost {

    // This member is not documented.
    #[allow(missing_docs)]
    pub bb: vision_msgs::msg::BoundingBox3D,


    // This member is not documented.
    #[allow(missing_docs)]
    pub attributes: soccer_vision_attribute_msgs::msg::Goalpost,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: soccer_vision_attribute_msgs::msg::Confidence,

}



impl Default for Goalpost {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Goalpost::default())
  }
}

impl rosidl_runtime_rs::Message for Goalpost {
  type RmwMsg = super::msg::rmw::Goalpost;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        bb: vision_msgs::msg::BoundingBox3D::into_rmw_message(std::borrow::Cow::Owned(msg.bb)).into_owned(),
        attributes: soccer_vision_attribute_msgs::msg::Goalpost::into_rmw_message(std::borrow::Cow::Owned(msg.attributes)).into_owned(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Owned(msg.confidence)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        bb: vision_msgs::msg::BoundingBox3D::into_rmw_message(std::borrow::Cow::Borrowed(&msg.bb)).into_owned(),
        attributes: soccer_vision_attribute_msgs::msg::Goalpost::into_rmw_message(std::borrow::Cow::Borrowed(&msg.attributes)).into_owned(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Borrowed(&msg.confidence)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      bb: vision_msgs::msg::BoundingBox3D::from_rmw_message(msg.bb),
      attributes: soccer_vision_attribute_msgs::msg::Goalpost::from_rmw_message(msg.attributes),
      confidence: soccer_vision_attribute_msgs::msg::Confidence::from_rmw_message(msg.confidence),
    }
  }
}


// Corresponds to soccer_vision_3d_msgs__msg__GoalpostArray
/// An array of goalposts with a header for global reference.
/// This msg type is used to publish all goalposts detected in 3d space.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GoalpostArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub posts: Vec<super::msg::Goalpost>,

}



impl Default for GoalpostArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::GoalpostArray::default())
  }
}

impl rosidl_runtime_rs::Message for GoalpostArray {
  type RmwMsg = super::msg::rmw::GoalpostArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        posts: msg.posts
          .into_iter()
          .map(|elem| super::msg::Goalpost::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        posts: msg.posts
          .iter()
          .map(|elem| super::msg::Goalpost::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      posts: msg.posts
          .into_iter()
          .map(super::msg::Goalpost::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to soccer_vision_3d_msgs__msg__MarkingEllipse
/// Describes a detected ellipse marking from vision modules, in 3d coordinates.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MarkingEllipse {
    /// The diameter of the ellipse marking in meters
    pub diameter: f64,

    /// Center pose of the ellipse, where a zero orientation is defined
    /// as looking directly down at an ellipse marking on the ground.
    pub center: geometry_msgs::msg::Pose,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: soccer_vision_attribute_msgs::msg::Confidence,

}



impl Default for MarkingEllipse {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::MarkingEllipse::default())
  }
}

impl rosidl_runtime_rs::Message for MarkingEllipse {
  type RmwMsg = super::msg::rmw::MarkingEllipse;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        diameter: msg.diameter,
        center: geometry_msgs::msg::Pose::into_rmw_message(std::borrow::Cow::Owned(msg.center)).into_owned(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Owned(msg.confidence)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      diameter: msg.diameter,
        center: geometry_msgs::msg::Pose::into_rmw_message(std::borrow::Cow::Borrowed(&msg.center)).into_owned(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Borrowed(&msg.confidence)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      diameter: msg.diameter,
      center: geometry_msgs::msg::Pose::from_rmw_message(msg.center),
      confidence: soccer_vision_attribute_msgs::msg::Confidence::from_rmw_message(msg.confidence),
    }
  }
}


// Corresponds to soccer_vision_3d_msgs__msg__MarkingIntersection
/// Describes a detected marking intersection from vision modules, in 3d coordinates.
/// An intersection is defined as a point where two or more line markings intersect.
/// The term ray is used to describe the outgoing rays from the center of the
/// intersection.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MarkingIntersection {
    /// Center point of the intersection
    pub center: geometry_msgs::msg::Point,

    /// The number of rays outgoing from an intersection. This is 3 for a T-Junction and
    /// 4 for an X-Junction
    pub num_rays: i32,

    /// NOTE: The length of the array should either:
    /// - Match the number of rays specified with num_rays OR
    /// - Be empty, if the headings are unknown
    pub rays: Vec<geometry_msgs::msg::Vector3>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: soccer_vision_attribute_msgs::msg::Confidence,

}



impl Default for MarkingIntersection {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::MarkingIntersection::default())
  }
}

impl rosidl_runtime_rs::Message for MarkingIntersection {
  type RmwMsg = super::msg::rmw::MarkingIntersection;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        center: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(msg.center)).into_owned(),
        num_rays: msg.num_rays,
        rays: msg.rays
          .into_iter()
          .map(|elem| geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Owned(msg.confidence)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        center: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(&msg.center)).into_owned(),
      num_rays: msg.num_rays,
        rays: msg.rays
          .iter()
          .map(|elem| geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Borrowed(&msg.confidence)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      center: geometry_msgs::msg::Point::from_rmw_message(msg.center),
      num_rays: msg.num_rays,
      rays: msg.rays
          .into_iter()
          .map(geometry_msgs::msg::Vector3::from_rmw_message)
          .collect(),
      confidence: soccer_vision_attribute_msgs::msg::Confidence::from_rmw_message(msg.confidence),
    }
  }
}


// Corresponds to soccer_vision_3d_msgs__msg__MarkingSegment
/// Two points defining the ends of the segment.
/// The points should be located at the centre along the width of the segment marking.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MarkingSegment {

    // This member is not documented.
    #[allow(missing_docs)]
    pub start: geometry_msgs::msg::Point,


    // This member is not documented.
    #[allow(missing_docs)]
    pub end: geometry_msgs::msg::Point,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: soccer_vision_attribute_msgs::msg::Confidence,

}



impl Default for MarkingSegment {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::MarkingSegment::default())
  }
}

impl rosidl_runtime_rs::Message for MarkingSegment {
  type RmwMsg = super::msg::rmw::MarkingSegment;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        start: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(msg.start)).into_owned(),
        end: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(msg.end)).into_owned(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Owned(msg.confidence)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        start: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(&msg.start)).into_owned(),
        end: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(&msg.end)).into_owned(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Borrowed(&msg.confidence)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      start: geometry_msgs::msg::Point::from_rmw_message(msg.start),
      end: geometry_msgs::msg::Point::from_rmw_message(msg.end),
      confidence: soccer_vision_attribute_msgs::msg::Confidence::from_rmw_message(msg.confidence),
    }
  }
}


// Corresponds to soccer_vision_3d_msgs__msg__MarkingArray
/// An array of markings with a header for global reference.
/// This msg type is used to publish all markings detected in 3d space.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MarkingArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub ellipses: Vec<super::msg::MarkingEllipse>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub intersections: Vec<super::msg::MarkingIntersection>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub segments: Vec<super::msg::MarkingSegment>,

}



impl Default for MarkingArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::MarkingArray::default())
  }
}

impl rosidl_runtime_rs::Message for MarkingArray {
  type RmwMsg = super::msg::rmw::MarkingArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        ellipses: msg.ellipses
          .into_iter()
          .map(|elem| super::msg::MarkingEllipse::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
        intersections: msg.intersections
          .into_iter()
          .map(|elem| super::msg::MarkingIntersection::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
        segments: msg.segments
          .into_iter()
          .map(|elem| super::msg::MarkingSegment::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        ellipses: msg.ellipses
          .iter()
          .map(|elem| super::msg::MarkingEllipse::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
        intersections: msg.intersections
          .iter()
          .map(|elem| super::msg::MarkingIntersection::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
        segments: msg.segments
          .iter()
          .map(|elem| super::msg::MarkingSegment::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      ellipses: msg.ellipses
          .into_iter()
          .map(super::msg::MarkingEllipse::from_rmw_message)
          .collect(),
      intersections: msg.intersections
          .into_iter()
          .map(super::msg::MarkingIntersection::from_rmw_message)
          .collect(),
      segments: msg.segments
          .into_iter()
          .map(super::msg::MarkingSegment::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to soccer_vision_3d_msgs__msg__Obstacle
/// Describes a detected obstacle from vision modules, in 3d coordinates.
/// An Obstacle is defined as anything observed on the field that could not be classified as
/// one of the known types (such as Robot or Goalpost).

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Obstacle {
    /// A bounding box that surrounds the obstacle, this does not have to include
    /// the whole obstacle, but only the part of the obstacle that was detected.
    pub bb: vision_msgs::msg::BoundingBox3D,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: soccer_vision_attribute_msgs::msg::Confidence,

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
        bb: vision_msgs::msg::BoundingBox3D::into_rmw_message(std::borrow::Cow::Owned(msg.bb)).into_owned(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Owned(msg.confidence)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        bb: vision_msgs::msg::BoundingBox3D::into_rmw_message(std::borrow::Cow::Borrowed(&msg.bb)).into_owned(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Borrowed(&msg.confidence)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      bb: vision_msgs::msg::BoundingBox3D::from_rmw_message(msg.bb),
      confidence: soccer_vision_attribute_msgs::msg::Confidence::from_rmw_message(msg.confidence),
    }
  }
}


// Corresponds to soccer_vision_3d_msgs__msg__ObstacleArray
/// An array of obstacles with a header for global reference.
/// This msg type is used to publish all obstacles detected.

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


// Corresponds to soccer_vision_3d_msgs__msg__Robot
/// Describes a detected robot from vision modules, in 3d coordinates.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Robot {
    /// A bounding box that surrounds the robot, this does not have to include
    /// the whole robot, but only the part of the robot that was detected.
    pub bb: vision_msgs::msg::BoundingBox3D,


    // This member is not documented.
    #[allow(missing_docs)]
    pub attributes: soccer_vision_attribute_msgs::msg::Robot,


    // This member is not documented.
    #[allow(missing_docs)]
    pub confidence: soccer_vision_attribute_msgs::msg::Confidence,

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
        bb: vision_msgs::msg::BoundingBox3D::into_rmw_message(std::borrow::Cow::Owned(msg.bb)).into_owned(),
        attributes: soccer_vision_attribute_msgs::msg::Robot::into_rmw_message(std::borrow::Cow::Owned(msg.attributes)).into_owned(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Owned(msg.confidence)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        bb: vision_msgs::msg::BoundingBox3D::into_rmw_message(std::borrow::Cow::Borrowed(&msg.bb)).into_owned(),
        attributes: soccer_vision_attribute_msgs::msg::Robot::into_rmw_message(std::borrow::Cow::Borrowed(&msg.attributes)).into_owned(),
        confidence: soccer_vision_attribute_msgs::msg::Confidence::into_rmw_message(std::borrow::Cow::Borrowed(&msg.confidence)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      bb: vision_msgs::msg::BoundingBox3D::from_rmw_message(msg.bb),
      attributes: soccer_vision_attribute_msgs::msg::Robot::from_rmw_message(msg.attributes),
      confidence: soccer_vision_attribute_msgs::msg::Confidence::from_rmw_message(msg.confidence),
    }
  }
}


// Corresponds to soccer_vision_3d_msgs__msg__RobotArray
/// An array of robots with a header for global reference.
/// This msg type is used to publish all robots detected.

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


