docker run -it --rm --network=host --ipc=host \
    -v $PWD/src/:/ws/src/ \
    --name=logger_node my_ros_image /bin/bash