FROM python:3.11-slim

WORKDIR /app

COPY pay.c0r.ai/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pay.c0r.ai/app/ .
COPY common /common

# Create symlink for common module
RUN ln -s /common /app/common

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"] 