FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
EXPOSE 8501

CMD bash -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run app/dashboard/dashboard.py --server.address=0.0.0.0 --server.port=8501"