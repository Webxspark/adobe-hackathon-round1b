FROM --platform=linux/amd64 python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies and PyMuPDF in a single layer
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    && pip install --no-cache-dir PyMuPDF==1.24.14 \
    && apt-get remove -y gcc g++ python3-dev \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip cache purge

# Copy the processing script and data
COPY process_collections.py .
COPY ["Collection 1", "./Collection 1"]
COPY ["Collection 2", "./Collection 2"]
COPY ["Collection 3", "./Collection 3"]

# Set proper permissions
RUN chmod +x process_collections.py

# Run the script
CMD ["python", "process_collections.py"]
