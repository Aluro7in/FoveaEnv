# Dockerfile — Hugging Face Spaces ready for FoveaEnv
# Uses the FastAPI app entrypoint defined in app.py and exposes port 7860.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/user/.local/bin:$PATH"

RUN useradd -m -u 1000 user
USER user

WORKDIR /app

COPY --chown=user:group requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY --chown=user:group . /app

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
