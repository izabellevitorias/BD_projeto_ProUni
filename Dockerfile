FROM python:3.11-bookworm

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/app

EXPOSE 8000
EXPOSE 8501

CMD bash -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run app/dashboard/dashboard.py --server.address=0.0.0.0 --server.port=8501"
