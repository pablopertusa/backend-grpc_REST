# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Create a non-root user
RUN useradd -m appuser

# Copy the current directory contents into the container at /app
ARG FOLDER

COPY ${FOLDER} /app
RUN mkdir -p proto_generated

# Copy proto definitions into the container
COPY ../proto_definitions /app/proto_definitions

# Change ownership of the working directory
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser
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