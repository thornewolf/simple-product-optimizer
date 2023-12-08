# Use a slim version of the Python image to reduce size
FROM python:3.11-slim

# Copy the project files first to leverage Docker's cache
# Only the requirements file is needed for dependency installation
COPY poetry.lock pyproject.toml ./

# Install poetry in a single layer and do not store cache
RUN pip install --no-cache-dir poetry

# Install dependencies using poetry
# The `--no-root` flag skips the current project installation (since it's not yet copied)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-root

# Copy the rest of the project files
COPY . .

# Set the entrypoint to run the application
ENTRYPOINT ["poetry", "run", "streamlit", "run", "product_optimizer/main.py"]
