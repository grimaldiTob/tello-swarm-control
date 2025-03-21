// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from custom_msgs:srv/StringCommand.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "custom_msgs/srv/string_command.hpp"


#ifndef CUSTOM_MSGS__SRV__DETAIL__STRING_COMMAND__BUILDER_HPP_
#define CUSTOM_MSGS__SRV__DETAIL__STRING_COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "custom_msgs/srv/detail/string_command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace custom_msgs
{

namespace srv
{

namespace builder
{

class Init_StringCommand_Request_command
{
public:
  Init_StringCommand_Request_command()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::custom_msgs::srv::StringCommand_Request command(::custom_msgs::srv::StringCommand_Request::_command_type arg)
  {
    msg_.command = std::move(arg);
    return std::move(msg_);
  }

private:
  ::custom_msgs::srv::StringCommand_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::custom_msgs::srv::StringCommand_Request>()
{
  return custom_msgs::srv::builder::Init_StringCommand_Request_command();
}

}  // namespace custom_msgs


namespace custom_msgs
{

namespace srv
{

namespace builder
{

class Init_StringCommand_Response_code
{
public:
  Init_StringCommand_Response_code()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::custom_msgs::srv::StringCommand_Response code(::custom_msgs::srv::StringCommand_Response::_code_type arg)
  {
    msg_.code = std::move(arg);
    return std::move(msg_);
  }

private:
  ::custom_msgs::srv::StringCommand_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::custom_msgs::srv::StringCommand_Response>()
{
  return custom_msgs::srv::builder::Init_StringCommand_Response_code();
}

}  // namespace custom_msgs


namespace custom_msgs
{

namespace srv
{

namespace builder
{

class Init_StringCommand_Event_response
{
public:
  explicit Init_StringCommand_Event_response(::custom_msgs::srv::StringCommand_Event & msg)
  : msg_(msg)
  {}
  ::custom_msgs::srv::StringCommand_Event response(::custom_msgs::srv::StringCommand_Event::_response_type arg)
  {
    msg_.response = std::move(arg);
    return std::move(msg_);
  }

private:
  ::custom_msgs::srv::StringCommand_Event msg_;
};

class Init_StringCommand_Event_request
{
public:
  explicit Init_StringCommand_Event_request(::custom_msgs::srv::StringCommand_Event & msg)
  : msg_(msg)
  {}
  Init_StringCommand_Event_response request(::custom_msgs::srv::StringCommand_Event::_request_type arg)
  {
    msg_.request = std::move(arg);
    return Init_StringCommand_Event_response(msg_);
  }

private:
  ::custom_msgs::srv::StringCommand_Event msg_;
};

class Init_StringCommand_Event_info
{
public:
  Init_StringCommand_Event_info()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StringCommand_Event_request info(::custom_msgs::srv::StringCommand_Event::_info_type arg)
  {
    msg_.info = std::move(arg);
    return Init_StringCommand_Event_request(msg_);
  }

private:
  ::custom_msgs::srv::StringCommand_Event msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::custom_msgs::srv::StringCommand_Event>()
{
  return custom_msgs::srv::builder::Init_StringCommand_Event_info();
}

}  // namespace custom_msgs

#endif  // CUSTOM_MSGS__SRV__DETAIL__STRING_COMMAND__BUILDER_HPP_
