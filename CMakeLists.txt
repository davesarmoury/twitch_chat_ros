cmake_minimum_required(VERSION 3.0.2)
project(twitch_chat_ros)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  twitch_chat_ros
  message_generation
)

add_message_files(
  FILES
  twitch_message.msg
  twitch_tags.msg
)

generate_messages(
  DEPENDENCIES
  std_msgs
  twitch_chat_ros
)

catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES twitch_chat_ros
  CATKIN_DEPENDS message_runtime
#  DEPENDS system_lib
)

include_directories(
# include
# ${catkin_INCLUDE_DIRS}
)
