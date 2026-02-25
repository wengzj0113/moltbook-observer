FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directory for SQLite db
RUN mkdir -p /data

# Use environment variable for DB path if needed, but for now default is fine
# ENV DATABASE_URL=sqlite:////data/moltbook.db

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
