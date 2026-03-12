FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY phonebook.py .
COPY initialization.sql .

CMD ["python", "phonebook.py"]