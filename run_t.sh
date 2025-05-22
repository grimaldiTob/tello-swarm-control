xhost +
docker run -it --rm --network=host --ipc=host \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ~/.Xauthority:/root/.Xauthority \
    -e DISPLAY=$DISPLAY \
    -e XAUTHORITY=$XAUTHORITY \
    -v $PWD/src/:/ws/src/ \
    --name=test_node my_ros_image /bin/bash

