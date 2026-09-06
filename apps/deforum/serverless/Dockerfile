# Build context: repository root. RunPod's GitHub builder targets linux/amd64.
FROM runpod/worker-comfyui:5.10.0-base@sha256:5e77b7d8ad559abcb02cca08165e400bef7372bdd9f599811c746019cb410de8

RUN git clone https://github.com/chillithebillis/Difforum.git /comfyui/custom_nodes/difforum \
    && git -C /comfyui/custom_nodes/difforum checkout --detach 1d750efd3c1d1dda792b8ef6c14b06a14a69f879 \
    && git clone https://github.com/kijai/ComfyUI-DepthAnythingV2.git /comfyui/custom_nodes/depth-anything-v2 \
    && git -C /comfyui/custom_nodes/depth-anything-v2 checkout --detach 553187872eeb1d52e50dc53209fa57e569609a72 \
    && uv pip install -r /comfyui/custom_nodes/difforum/requirements.txt \
        -r /comfyui/custom_nodes/depth-anything-v2/requirements.txt

RUN mkdir -p /comfyui/models/checkpoints /comfyui/models/depthanything \
    && wget -q -O /comfyui/models/checkpoints/sd_xl_base_1.0.safetensors \
      https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/462165984030d82259a11f4367a4eed129e94a7b/sd_xl_base_1.0.safetensors \
    && echo '31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b  /comfyui/models/checkpoints/sd_xl_base_1.0.safetensors' | sha256sum -c - \
    && wget -q -O /comfyui/models/depthanything/depth_anything_v2_vits_fp32.safetensors \
      https://huggingface.co/Kijai/DepthAnythingV2-safetensors/resolve/5aa7ab578df757d94c743998b157a0204ff29215/depth_anything_v2_vits_fp32.safetensors \
    && echo 'cb2d537ed6e45921f27f61f0b605dcfafb6b97c7d1a15e551280bdd867605c86  /comfyui/models/depthanything/depth_anything_v2_vits_fp32.safetensors' | sha256sum -c -

# Keep the upstream request handler; our adapter adds durable job archives.
RUN mv /handler.py /upstream_handler.py \
    && sed -i 's/--disable-auto-launch/--output-directory \/runpod-volume\/deforum --disable-auto-launch/g' /start.sh
COPY apps/deforum/serverless/handler.py /handler.py
RUN cd /comfyui && python main.py --quick-test-for-ci --cpu
ENV COMFY_LOG_LEVEL=INFO

