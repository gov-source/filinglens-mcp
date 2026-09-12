FROM python:3.12-slim
RUN pip install --no-cache-dir filinglens
ENTRYPOINT ["filinglens-mcp"]
