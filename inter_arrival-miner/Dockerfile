# Dockerfile

FROM pm4py/pm4py-core:latest

# Set working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8003

# Command to run the application
CMD ["python", "api.py"]