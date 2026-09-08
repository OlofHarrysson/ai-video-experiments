# Build context: repository root. Native ComfyUI nodes; original image recipe is Dockerfile.sdxl.
FROM runpod/worker-comfyui:5.10.0-base@sha256:5e77b7d8ad559abcb02cca08165e400bef7372bdd9f599811c746019cb410de8

RUN mkdir -p /comfyui/models/diffusion_models \
    && wget -q -O /comfyui/models/diffusion_models/flux-2-klein-4b.safetensors \
      https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-4b/resolve/5f526678002e43af5551dadb73ce2e8c91b43afe/split_files/diffusion_models/flux-2-klein-4b.safetensors \
    && echo 'ec3d4e733a771f61c052fb4856c48b336c55eaf2c65487c2a1faeb9bbda7a343  /comfyui/models/diffusion_models/flux-2-klein-4b.safetensors' | sha256sum -c -

RUN mkdir -p /comfyui/models/text_encoders \
    && wget -q -O /comfyui/models/text_encoders/qwen_3_4b.safetensors \
      https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-4b/resolve/5f526678002e43af5551dadb73ce2e8c91b43afe/split_files/text_encoders/qwen_3_4b.safetensors \
    && echo '6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a  /comfyui/models/text_encoders/qwen_3_4b.safetensors' | sha256sum -c -

RUN mkdir -p /comfyui/models/vae \
    && wget -q -O /comfyui/models/vae/flux2-vae.safetensors \
      https://huggingface.co/Comfy-Org/vae-text-encorder-for-flux-klein-4b/resolve/5f526678002e43af5551dadb73ce2e8c91b43afe/split_files/vae/flux2-vae.safetensors \
    && echo '868fe7b343cc8f3a19dbcfcafbc3d5f888802be3f89bd81b65b3621a066ce8f3  /comfyui/models/vae/flux2-vae.safetensors' | sha256sum -c -

RUN mkdir -p /comfyui/models/diffusion_models \
    && wget -q -O /comfyui/models/diffusion_models/krea2_turbo_fp8_scaled.safetensors \
      https://huggingface.co/Comfy-Org/Krea-2/resolve/e5ea8b4dd7f38f348b138eb0fe29f92c0e367e96/diffusion_models/krea2_turbo_fp8_scaled.safetensors \
    && echo 'eb4dd8c612cfd10f64f25b057e6e6bbcb5737c94a7372177e456dbf7579502f1  /comfyui/models/diffusion_models/krea2_turbo_fp8_scaled.safetensors' | sha256sum -c -

RUN mkdir -p /comfyui/models/text_encoders \
    && wget -q -O /comfyui/models/text_encoders/qwen3vl_4b_fp8_scaled.safetensors \
      https://huggingface.co/Comfy-Org/Krea-2/resolve/e5ea8b4dd7f38f348b138eb0fe29f92c0e367e96/text_encoders/qwen3vl_4b_fp8_scaled.safetensors \
    && echo '54bd5144df0bbc25dd6ccadfcb826b521445a1b06ae5a42570bdd2974ca87094  /comfyui/models/text_encoders/qwen3vl_4b_fp8_scaled.safetensors' | sha256sum -c -

RUN mkdir -p /comfyui/models/vae \
    && wget -q -O /comfyui/models/vae/qwen_image_vae.safetensors \
      https://huggingface.co/Comfy-Org/Krea-2/resolve/e5ea8b4dd7f38f348b138eb0fe29f92c0e367e96/vae/qwen_image_vae.safetensors \
    && echo 'a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f  /comfyui/models/vae/qwen_image_vae.safetensors' | sha256sum -c -

# Keep the upstream request handler; our adapter adds durable job archives.
RUN mv /handler.py /upstream_handler.py \
    && sed -i 's/--disable-auto-launch/--output-directory \/runpod-volume\/deforum --disable-auto-launch/g' /start.sh
COPY apps/deforum/serverless/handler.py /handler.py
RUN cd /comfyui && python main.py --quick-test-for-ci --cpu
ENV COMFY_LOG_LEVEL=INFO
