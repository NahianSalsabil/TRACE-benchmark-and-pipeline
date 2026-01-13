FROM ubuntu:22.04

USER root

RUN apt-get update

RUN apt-get install -y --no-install-recommends \
    wget \
    tar \
    python3-dev \
    python3-pip \
    python3-virtualenv \
    python3-setuptools \
    proj-bin \
    libproj-dev \
    xdg-user-dirs \
    x11-utils mesa-utils \
    libglvnd0 libgl1 libglx0 libegl1 \
    libsdl2-2.0 xserver-xorg libvulkan1

ENV NVIDIA_VISIBLE_DEVICES=all

ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics,display

ENV LD_LIBRARY_PATH=/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/lib/x86_64-linux-gnu:/usr/lib/i386-linux-gnu

ENV __GLX_VENDOR_LIBRARY_NAME=nvidia

# 2. Fix for "Can't find a compatible Vulkan driver (ICD)"
# The NVIDIA runtime mounts the config file here, but standard Ubuntu doesn't look here by default.
ENV VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json

RUN groupadd --gid 1000 carla \
    && useradd --uid 1000 --gid carla --shell /bin/bash --create-home carla

WORKDIR /home/carla

COPY --chown=carla:carla . /home/carla/app

USER carla

RUN python3 -m virtualenv /home/carla/env

ENV PATH="/home/carla/env/bin:$PATH"

RUN pip install -r /home/carla/app/requirements.txt

# RUN mkdir engine \
#     && cd engine \
#     && wget https://carla-releases.b-cdn.net/Linux/CARLA_0.9.15.tar.gz \
#     && tar -xvf CARLA_0.9.15.tar.gz \
#     && rm CARLA_0.9.15.tar.gz

# test
RUN mkdir engine \
    && cd engine \
    && mv /home/carla/app/CARLA_0.9.15.tar.gz . \
    && tar -xvf CARLA_0.9.15.tar.gz \
    && rm CARLA_0.9.15.tar.gz

CMD ["/bin/bash"]
