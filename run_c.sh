docker run -it --rm --network=host --ipc=host \
    -v $PWD/src/djitello/:/ws/src/djitello/ \
    --name=container_node my_ros_image /bin/bash