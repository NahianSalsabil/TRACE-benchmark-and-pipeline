# Use the official CARLA 0.9.15 image as base
FROM carlasim/carla:0.9.15

USER root

RUN chown -R carla:carla /home/carla

COPY --chown=carla:carla . /home/carla/app

RUN mv /home/carla/app/scripts/* /home/carla/PythonAPI/util/ \
    && mv /home/carla/app/data /home/carla/PythonAPI/util/

RUN ln -s /home/carla/PythonAPI/carla/agents /home/carla/PythonAPI/util/agents

RUN apt-get update && apt-get install -y \
    wget \
    osmium-tool \
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

ENV PATH="$PATH:/home/carla/.local/bin:/home/carla/PythonAPI/carla"

ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/home/carla/app/lib"

WORKDIR /home/carla

RUN pip3.8 install -r app/requirements.txt

USER carla

# Define the entrypoint
CMD ["/bin/bash"]

