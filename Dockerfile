FROM python:3.8

WORKDIR /app

# Install dependencies
ENV PIP_NO_CACHE_DIR=false
RUN pip install -U pip pipenv
COPY ["Pipfile", "Pipfile.lock", "./"]
RUN pipenv install --system --deploy --ignore-pipfile

# Copy code
COPY . ./

# Entry point
ENTRYPOINT ["python", "./server.py" ]