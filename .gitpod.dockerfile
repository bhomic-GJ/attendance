FROM gitpod/workspace-mysql

RUN sudo apt-get update \
 && sudo apt-get install -y \
    mysql \
 && sudo rm -rf /var/lib/apt/lists/*