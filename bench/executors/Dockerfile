FROM python:3.10-slim

WORKDIR /workspace

RUN pip install --no-cache-dir \
    langchain>=0.1.0 \
    langchain-community>=0.1.0 \
    pydantic>=2.0.0

COPY base.py /executor.py
COPY agent.py /agent.py

RUN chmod +x /executor.py /agent.py

CMD ["python", "/agent.py"] 