FROM python:3.13-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend/src
COPY pyproject.toml ./
COPY backend/src ./backend/src
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn","contract_reviewer.main:app","--host","0.0.0.0","--port","8000"]
