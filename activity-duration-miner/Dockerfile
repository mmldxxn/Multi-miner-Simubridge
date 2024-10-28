# Use an official Python runtime as a parent image
FROM pm4py/pm4py-core:latest


# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8002 available to the world outside this container
EXPOSE 8002

# Define environment variable
ENV FLASK_APP=api.py

# Run api.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=8002"]
