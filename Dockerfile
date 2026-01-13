FROM ubuntu:22.04

USER root

RUN apt-get update

RUN apt-get install -y \
    wget \
    tar \
    python3-dev \
    python3-pip \
    python3-virtualenv \
    python3-setuptools \
    proj-bin \
    libproj-dev \
    xdg-user-dirs

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
