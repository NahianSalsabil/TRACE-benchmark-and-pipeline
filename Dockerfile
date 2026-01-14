# Use the official CARLA 0.9.15 image as base
FROM carlasim/carla:0.9.15

USER root

RUN chown -R carla:carla /home/carla

COPY --chown=carla:carla . /home/carla/app

RUN apt-get update && apt-get install -y \
    wget \
    xdg-user-dirs \
    libvulkan1 \
    mesa-vulkan-drivers \
    vulkan-utils \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

RUN add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y \
    python3.8 \
    python3.8-dev \
    python3.8-distutils

RUN wget https://bootstrap.pypa.io/pip/3.8/get-pip.py \
    && python3.8 get-pip.py \
    && rm get-pip.py 

ENV PATH="$PATH:/home/carla/.local/bin"

WORKDIR /home/carla

RUN pip3.8 install -r app/requirements.txt

USER carla

# Define the entrypoint (starts CARLA automatically)
CMD ["/bin/bash"]

