# Troubleshooting Guide - Lab 4

## Common Issues & Resolutions

### 1. SQLite Database Lock during Disaster Recovery
- **Issue**: Attempting to restore a database while an active file connection remains open throws `sqlite3.OperationalError: database is locked`.
- **Resolution**: Ensure all cursor and connection objects are explicitly closed with `conn.close()` before file operations. The `disaster_simulation.py` script enforces strict connection cleanup.

### 2. Pytest ModuleNotFoundError for App
- **Issue**: Running pytest directly without setting PYTHONPATH throws `ModuleNotFoundError: No module named 'app'`.
- **Resolution**: Use `python -m pytest question-2-automated-testing/tests` or run `python question-2-automated-testing/run_tests.py`, which injects the app folder into `sys.path`.

### 3. GitHub Actions Runner Permissions
- **Issue**: Workflow reports permission error when publishing artifacts.
- **Resolution**: `.github/workflows/ci-cd.yml` uses official GitHub Actions (`actions/checkout@v4`, `actions/upload-artifact@v4`) with standard repository permissions.
