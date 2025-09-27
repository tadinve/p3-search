# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app



# Copy the dependencies file to the working directory
COPY requirements.txt .


RUN pip install --upgrade pip
# Install any needed packages specified in requirements.txt as the non-root user
# The --user flag ensures packages are installed in the user's home directory
RUN pip install  -r requirements.txt

# --- Download and cache the model during the build ---
# Copy the download script
COPY download_model.py .

# Create a directory for the models and run the download script
RUN mkdir /app/models && python download_model.py

# Copy the rest of the application code
COPY . .

# Make port 8001 available to the world outside this container
EXPOSE 8001

# Use the PORT environment variable provided by Cloud Run
CMD uvicorn main:app --host 0.0.0.0 --port $PORT