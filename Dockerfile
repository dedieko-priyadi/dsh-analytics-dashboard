FROM python:3.11-slim
RUN pip install streamlit pandas plotly
WORKDIR /app
COPY app.py .
CMD ["streamlit", "run", "app.py", "--server.port=8541", "--server.address=0.0.0.0", "--server.baseUrlPath=/dsh-analytics"]
