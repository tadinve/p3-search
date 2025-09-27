# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app


# Copy the dependencies file to the working directory
COPY requirements.txt .
RUN pip install --upgrade pip
# Install any needed packages specified in requirements.txt as the non-root user
RUN pip install  -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Add the user's local bin to the PATH and run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]