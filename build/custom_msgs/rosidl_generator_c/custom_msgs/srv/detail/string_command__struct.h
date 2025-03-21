// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from custom_msgs:srv/StringCommand.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "custom_msgs/srv/string_command.h"


#ifndef CUSTOM_MSGS__SRV__DETAIL__STRING_COMMAND__STRUCT_H_
#define CUSTOM_MSGS__SRV__DETAIL__STRING_COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'command'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/StringCommand in the package custom_msgs.
typedef struct custom_msgs__srv__StringCommand_Request
{
  rosidl_runtime_c__String command;
} custom_msgs__srv__StringCommand_Request;

// Struct for a sequence of custom_msgs__srv__StringCommand_Request.
typedef struct custom_msgs__srv__StringCommand_Request__Sequence
{
  custom_msgs__srv__StringCommand_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} custom_msgs__srv__StringCommand_Request__Sequence;

// Constants defined in the message

/// Struct defined in srv/StringCommand in the package custom_msgs.
typedef struct custom_msgs__srv__StringCommand_Response
{
  bool code;
} custom_msgs__srv__StringCommand_Response;

// Struct for a sequence of custom_msgs__srv__StringCommand_Response.
typedef struct custom_msgs__srv__StringCommand_Response__Sequence
{
  custom_msgs__srv__StringCommand_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} custom_msgs__srv__StringCommand_Response__Sequence;

// Constants defined in the message

// Include directives for member types
// Member 'info'
#include "service_msgs/msg/detail/service_event_info__struct.h"

// constants for array fields with an upper bound
// request
enum
{
  custom_msgs__srv__StringCommand_Event__request__MAX_SIZE = 1
};
// response
enum
{
  custom_msgs__srv__StringCommand_Event__response__MAX_SIZE = 1
};

/// Struct defined in srv/StringCommand in the package custom_msgs.
typedef struct custom_msgs__srv__StringCommand_Event
{
  service_msgs__msg__ServiceEventInfo info;
  custom_msgs__srv__StringCommand_Request__Sequence request;
  custom_msgs__srv__StringCommand_Response__Sequence response;
} custom_msgs__srv__StringCommand_Event;

// Struct for a sequence of custom_msgs__srv__StringCommand_Event.
typedef struct custom_msgs__srv__StringCommand_Event__Sequence
{
  custom_msgs__srv__StringCommand_Event * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} custom_msgs__srv__StringCommand_Event__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // CUSTOM_MSGS__SRV__DETAIL__STRING_COMMAND__STRUCT_H_
