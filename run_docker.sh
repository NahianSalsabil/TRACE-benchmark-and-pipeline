docker run -it \
    --privileged \
    --rm \
    --gpus all \
    --net=host \
    -e GEMINI_API_KEY=apikey \
    -e DISPLAY=$DISPLAY \
    -e NVIDIA_DRIVER_CAPABILITIES=all \
    -e VK_ICD_FILENAMES="/usr/share/vulkan/icd.d/nvidia_icd.json" \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v /usr/share/vulkan/icd.d:/usr/share/vulkan/icd.d:ro \
    carlatest:latest 
    haha