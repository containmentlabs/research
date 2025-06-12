FROM python:3.10-slim

WORKDIR /workspace

COPY base_executor.py /executor.py

RUN chmod +x /executor.py

CMD ["python", "/executor.py"] 