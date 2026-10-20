# Toolchain for tools/prev.py: builds a bootable GRUB ISO and screenshots it
# in QEMU. Lets the previews be rebuilt from Windows or macOS too.
#
#   docker build -t grubbox tools/grubbox
#   docker run --rm -v "$PWD:/work" grubbox python3 tools/prev.py --all
#
# QEMU falls back to software emulation when /dev/kvm is not exposed, which is
# the usual case on Docker Desktop. It still works, it is just slower: GRUB
# draws after 15-20 s instead of 2-3 s, and prev.py waits for the frame rather
# than for the clock.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        grub-common \
        grub-pc-bin \
        grub-efi-amd64-bin \
        xorriso \
        mtools \
        qemu-system-x86 \
        imagemagick \
        fonts-dejavu-core \
        python3 \
        python3-pil \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
