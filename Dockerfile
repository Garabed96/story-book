# Use an official Python runtime as the base image
FROM python:3.10.8-slim-buster

# All subsequent requests will be send to /portfolio directory in Docker filesystem...
# Set the working directory in the container image.
WORKDIR /portfolio

# Copy the requirements file into the container
COPY requirements.txt .

# Install the application's dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /portfolio

# Expose the port that the application will run on
EXPOSE 1122

#ENTRYPOINT ["python"]

# Run the application
CMD ["python", "main.py", "--host=0.0.0.0"]



docker run -p 3000:80 -d --name feedback-app --rm feedback-node