docker run -it --rm --network=host --ipc=host \
    -v $PWD/src/:/ws/src/ \
    --name=ros2_node1 my_ros_image /bin/bash
