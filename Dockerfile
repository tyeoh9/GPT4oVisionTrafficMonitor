FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501
ENV STREAMLIT_SERVER_HEADLESS=true
CMD ["streamlit", "run", "GPT4V_Streamlit.py", "--server.port=8080", "--server.address=0.0.0.0"]
