# Use Python 3.11.4 as a parent image
FROM python:3.11.4

# Set the working directory to /Module3 (matching your project structure)
WORKDIR /Module3

# Copy the Flask app code into the container
COPY Module3 /Module3

# Install any needed packages specified in requirements.txt
RUN pip install -r /Module3/requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run the Flask app when the container launches
CMD ["python", "/Module3/app.py"]
