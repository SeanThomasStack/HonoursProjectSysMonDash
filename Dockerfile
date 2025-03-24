# Use Python image for the container
FROM python:3.9-slim

# Install Git for cloning the repository and required system dependencies
RUN apt-get update && apt-get install -y git

# Set the used directory
WORKDIR /app

# Clone the repository for the required files to run the web
RUN git clone https://github.com/SeanThomasStack/HonoursProjectSysMonDash.git /app/sysmondashDocker; 


# Move into the repo directory
WORKDIR /app/sysmondashDocker

# creates the templates directory and ensures its parent directory exists
RUN mkdir -p templates

# Move HTML files into the templates directory
RUN mv -f *.html templates/ || true  # || true means it will ignore errors if the HTML files do not exist

# Install Python modules if requirements.txt exists
RUN if [ -f "requirements.txt" ]; then \
        pip install -r requirements.txt; \
    fi

# Ensure port 5000 is open for connections to the flask site 
EXPOSE 5000

# Run the flask python script
CMD ["python3", "SysMonDash.py"]
