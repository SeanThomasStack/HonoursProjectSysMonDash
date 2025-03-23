# Use an official Python image as base
FROM python:3.9-slim

# Install dependencies: Git (for cloning) and any required system dependencies
RUN apt-get update && apt-get install -y git

# Set working directory
WORKDIR /app

# Clone the repository if it does not already exist
RUN git clone https://github.com/SeanThomasStack/HonoursProjectSysMonDash.git /app/sysmondashDocker; 


# Move into the repo directory
WORKDIR /app/sysmondashDocker

# Ensure the 'templates' directory exists
RUN mkdir -p templates

# Move HTML files into the 'templates' directory
RUN mv -f *.html templates/ || true  # Ignore errors if no HTML files exist

# Install Python dependencies if requirements.txt exists
RUN if [ -f "requirements.txt" ]; then \
        pip install -r requirements.txt; \
    fi

# Expose port 5000 for Flask
EXPOSE 5000

# Run the Flask application
CMD ["python3", "SysMonDash.py"]