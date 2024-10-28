# Use the specified pm4py image from Docker Hub
FROM pm4py/pm4py-core:latest

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Install additional Python dependencies
RUN pip install --no-cache-dir Flask

# Expose the port that the Flask app runs on
EXPOSE 8000

# Run the Flask app
CMD ["python", "app.py"]
