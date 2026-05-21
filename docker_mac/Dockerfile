FROM tiryoh/ros-desktop-vnc:melodic

ENV DEBIAN_FRONTEND=noninteractive

# Install essential tools in one step and clean up to save space
RUN apt update && apt install -y --no-install-recommends \
    --option=Dpkg::Use-Pty=0 \
    --option=Acquire::Retries=5 \
    --option=Acquire::http::Timeout=120 \
    build-essential \
    libc6-dev \
    python3-dev \
    openjdk-17-jdk \
    openjdk-11-jdk \
    lsb-release \
    gnupg \
    ant \
    wget \
    unzip \
    git \
    ros-melodic-rosbridge-server \
    ros-melodic-navigation \
    ros-melodic-jackal-* \
    ros-melodic-teleop-twist-keyboard \
    ros-melodic-pcl-ros \
    ros-melodic-velodyne \
    ros-melodic-velocity-controllers \
    ros-melodic-teb-local-planner \
    ros-melodic-pointcloud-to-laserscan \
    ros-melodic-gazebo-ros-pkgs \
    ros-melodic-velodyne-gazebo-plugins \
    ros-melodic-joint-state-publisher-gui \ 
    ros-melodic-ros-controllers \
    ros-melodic-openslam-gmapping \
    && apt clean && rm -rf /var/lib/apt/lists/*


# Create the ubuntu user if it does not exist
RUN id ubuntu || ( \
    useradd -m -s /bin/bash ubuntu && \
    echo "ubuntu:ubuntu" | chpasswd \
)

# Create the Desktop directory and set proper ownership
RUN mkdir -p /home/ubuntu/Desktop && chown -R ubuntu:ubuntu /home/ubuntu


## Seem to need to set the locale to get mvn and ant to recoginse some characters
USER root
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.en
ENV LC_ALL=en_US.UTF-8

## Switch to the ubuntu user for subsequent build steps
USER ubuntu
WORKDIR /home/ubuntu


# Install Gazebo and required ROS packages
USER root
RUN sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list' && \
    curl -sSL https://packages.osrfoundation.org/gazebo.key | apt-key add - && \
    apt update && apt install -y ros-melodic-gazebo-ros && \
    apt clean && rm -rf /var/lib/apt/lists/*



## Install IntelliJ IDEA (Community Edition)
WORKDIR /tmp
RUN wget https://download.jetbrains.com/idea/ideaIC-2024.3.3-aarch64.tar.gz
RUN tar -xzf ideaIC-*.tar.gz -C /opt


RUN ln -s /opt/idea-IC-*/bin/idea.sh /usr/local/bin/intellij

## Cleanup
RUN rm -rf /tmp/ideaIC-2024.3.3.tar.gz

#FOR MCAPL
RUN mkdir -p ~/.jpf && echo "mcapl = /home/ubuntu/mcapl" > ~/.jpf/site.properties
ENV AJPF_HOME=/home/ubuntu/mcapl
ENV CLASSPATH=/home/ubuntu/mcapl/bin

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]




    


    