FROM python:3.10-slim

WORKDIR /app

COPY grade.py /grade.py

RUN chmod +x /grade.py

ENTRYPOINT ["python", "/grade.py"] 