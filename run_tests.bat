@echo off
echo Running Under 1000 API Tests...
echo.
echo 1. Unit Tests...
pytest tests/test_unit.py -v
echo.
echo 2. Integration Tests...
pytest tests/test_integration.py -v
echo.
echo 3. End-to-End Tests...
pytest tests/test_e2e.py -v
echo.
echo 4. Security Tests...
pytest tests/test_security.py -v
echo.
echo 5. All Tests...
pytest tests/ -v --cov=app --cov-report=term-missing
echo.
echo All tests completed!
pause
