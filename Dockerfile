# Use the official CARLA 0.9.15 image as base
FROM carlasim/carla:0.9.15

# Switch to root to install extra packages if needed
USER root

# (Optional) Copy your custom project files here
# COPY ./my_project /home/carla/my_project

# Ensure the carla user owns the home directory adjustments
RUN chown -R carla:carla /home/carla

# RUN add-apt-repository universe

RUN apt-get update && apt-get install -y \
    xdg-user-dirs \
    libvulkan1 \
    mesa-vulkan-drivers \
    vulkan-utils \
    && rm -rf /var/lib/apt/lists/*

USER carla

# Switch back to the carla user for safety
USER carla

# Define the entrypoint (starts CARLA automatically)
CMD ["/bin/bash"]

