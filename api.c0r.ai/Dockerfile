FROM python:3.11-slim
WORKDIR /app
COPY api.c0r.ai/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api.c0r.ai/app/ .
COPY assets ./assets
COPY common /common
COPY i18n ./i18n
RUN ln -s /common /app/common
CMD ["env", "PYTHONPATH=/common", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 