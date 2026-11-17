#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to soccer_vision_attribute_msgs__msg__Confidence

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Confidence::default())
  }
}

impl rosidl_runtime_rs::Message for Confidence {
  type RmwMsg = super::msg::rmw::Confidence;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        confidence: msg.confidence,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      confidence: msg.confidence,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      confidence: msg.confidence,
    }
  }
}


// Corresponds to soccer_vision_attribute_msgs__msg__Goalpost

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Goalpost::default())
  }
}

impl rosidl_runtime_rs::Message for Goalpost {
  type RmwMsg = super::msg::rmw::Goalpost;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        side: msg.side,
        team: msg.team,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      side: msg.side,
      team: msg.team,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      side: msg.side,
      team: msg.team,
    }
  }
}


// Corresponds to soccer_vision_attribute_msgs__msg__Robot

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Robot::default())
  }
}

impl rosidl_runtime_rs::Message for Robot {
  type RmwMsg = super::msg::rmw::Robot;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        player_number: msg.player_number,
        team: msg.team,
        state: msg.state,
        facing: msg.facing,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      player_number: msg.player_number,
      team: msg.team,
      state: msg.state,
      facing: msg.facing,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      player_number: msg.player_number,
      team: msg.team,
      state: msg.state,
      facing: msg.facing,
    }
  }
}


