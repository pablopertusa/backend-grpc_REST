# Use an official Python runtime as a parent image
FROM python:3.12-slim

RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --create-home appuser

# Cambia al usuario no root
USER appuser

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
ARG FOLDER

COPY --chown=appuser:appgroup ${FOLDER} /app
RUN mkdir -p proto_generated

# Copy proto definitions into the container
COPY --chown=appuser:appgroup ../proto_definitions /app/proto_definitions

# Generate the Python files from the .proto files
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m grpc_tools.protoc \
    -I./proto_definitions \
    --python_out=./proto_generated \
    --grpc_python_out=./proto_generated \
    ./proto_definitions/message.proto && \
    python -m grpc_tools.protoc \
    -I./proto_definitions \
    --python_out=./proto_generated \
    --grpc_python_out=./proto_generated \
    ./proto_definitions/user.proto && \
    python -m grpc_tools.protoc \
    -I./proto_definitions \
    --python_out=./proto_generated \
    --grpc_python_out=./proto_generated \
    ./proto_definitions/notification.proto
    
ENV PYTHONPATH="/app/proto_generated:${PYTHONPATH}"

# Run user service http and grpc when the container starts
CMD ["python","app.py"]


