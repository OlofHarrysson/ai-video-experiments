# Build context: repository root. Model assets download to worker-local storage.
# The previous SDXL recipe is preserved in Dockerfile.sdxl.
FROM runpod/worker-comfyui:5.10.0-base@sha256:5e77b7d8ad559abcb02cca08165e400bef7372bdd9f599811c746019cb410de8

# Keep the upstream request handler; our adapter adds durable job archives.
RUN mv /handler.py /upstream_handler.py \
    && sed -i 's/--disable-auto-launch/--output-directory \/runpod-volume\/deforum --disable-auto-launch/g' /start.sh \
    && mv /start.sh /comfy-start.sh
COPY apps/deforum/serverless/handler.py /handler.py
COPY apps/deforum/serverless/prepare_models.py /prepare_models.py
COPY apps/deforum/serverless/modern-models.json /modern-models.json
COPY apps/deforum/serverless/start-modern.sh /start.sh
RUN chmod +x /start.sh \
    && python -c 'import huggingface_hub; from huggingface_hub import hf_hub_download; import hf_xet; print("Hugging Face loader:", huggingface_hub.__version__)' \
    && cd /comfyui && python main.py --quick-test-for-ci --cpu
ENV COMFY_LOG_LEVEL=INFO
