$env:PYTHONPATH="$pwd;"

# Run Alembic migrations
alembic upgrade head

# Run pytest
pytest --junitxml=report.xml