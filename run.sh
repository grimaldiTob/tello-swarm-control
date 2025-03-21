docker run -it --rm --network=host --ipc=host \
    -v $PWD/src/djitello/:/ws/src/djitello/ \
    --name=ros2_node1 my_ros_image /bin/bash
