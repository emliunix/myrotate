FROM debian:12

RUN sed -i "s|http://deb.debian.org/debian|http://mirror.sjtu.edu.cn/debian|g" /etc/apt/sources.list.d/debian.sources && \
    apt update && apt -y install build-essential cmake git python3 python3-pip device-tree-compiler && \
    apt -y clean all
RUN pip3 install --break-system-packages -i https://mirror.sjtu.edu.cn/pypi/web/simple west
RUN apt -y install file wget curl xz-utils && apt -y clean all
RUN apt -y install ninja-build && apt -y clean all
RUN pip3 install --break-system-packages -i https://mirror.sjtu.edu.cn/pypi/web/simple pyelftools
ENV PATH="/opt/aarch64-zephyr-elf/bin:${PATH}"
