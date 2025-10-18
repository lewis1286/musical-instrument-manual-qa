# Testing Guide

This document describes the testing infrastructure and how to run tests for the Musical Instrument Manual Q&A System.

## Overview

The project uses different testing frameworks for backend and frontend:

- **Backend**: pytest (Python)
- **Frontend**: Vitest + React Testing Library (TypeScript)

## Backend Testing (Python/pytest)

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest backend/tests/test_pdf_extractor.py

# Run with coverage report
poetry run pytest --cov=app --cov-report=html --cov-report=term

# Run only unit tests
poetry run pytest -m unit

# Run only integration tests
poetry run pytest -m integration

# Run tests in parallel (install pytest-xdist first)
poetry run pytest -n auto
```

### Test Structure

```
backend/tests/
├── conftest.py                    # Shared fixtures and configuration
├── test_pdf_extractor.py          # PDF processing tests
├── test_chroma_manager.py         # Vector database tests (TODO)
├── test_qa_system.py              # RAG pipeline tests (TODO)
└── test_api/
    ├── test_manuals_routes.py     # Manual API endpoint tests
    ├── test_qa_routes.py          # Q&A API endpoint tests (TODO)
    └── test_stats_routes.py       # Stats API endpoint tests (TODO)
```

### Available Fixtures

- `test_client`: FastAPI test client
- `pdf_extractor`: PDFExtractor instance
- `temp_pdf_file`: Temporary PDF file for testing
- `sample_manual_metadata`: Sample metadata dictionary
- `mock_chroma_manager`: Mocked ChromaManager

### Test Markers

- `@pytest.mark.unit`: Unit tests (fast, no external dependencies)
- `@pytest.mark.integration`: Integration tests (may use database, slower)
- `@pytest.mark.slow`: Slow tests (can be excluded in CI)

### Writing New Tests

Example unit test:

```python
import pytest
from app.services.pdf_processor.pdf_extractor import PDFExtractor

@pytest.mark.unit
def test_extract_manufacturer(pdf_extractor):
    filename = "Moog-Minimoog.pdf"
    text = ""
    manufacturer = pdf_extractor._extract_manufacturer(filename, text)
    assert manufacturer == "Moog"
```

Example API test:

```python
import pytest

@pytest.mark.integration
def test_upload_manual(test_client, temp_pdf_file):
    with open(temp_pdf_file, 'rb') as f:
        files = {"file": ("test.pdf", f, "application/pdf")}
        response = test_client.post("/api/manuals/process", files=files)

    assert response.status_code == 200
    assert "metadata" in response.json()
```

## Frontend Testing (Vitest + React Testing Library)

### Running Tests

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with UI
npm test:ui

# Run with coverage
npm test:coverage

# Run specific test file
npm test -- useQA.test.ts
```

### Test Structure

```
frontend/src/
├── hooks/
│   ├── useManuals.test.ts
│   ├── useQA.test.ts
│   └── useStats.test.ts
├── services/
│   └── api.test.ts
├── test/
│   └── setup.ts                    # Test environment setup
└── App.test.tsx                     # Component tests (TODO)
```

### Writing New Tests

Example hook test:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useStats } from './useStats';
import { api } from '../services/api';

vi.mock('../services/api');

describe('useStats Hook', () => {
  it('should load stats on mount', async () => {
    const mockStats = {
      total_manuals: 5,
      total_chunks: 100,
      manufacturers: ['Moog'],
      instrument_types: ['synthesizer'],
      section_types: [],
    };

    vi.mocked(api.getStats).mockResolvedValueOnce(mockStats);

    const { result } = renderHook(() => useStats());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.stats).toEqual(mockStats);
  });
});
```

Example component test:

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';

describe('App Component', () => {
  it('should render tabs', () => {
    render(<App />);
    expect(screen.getByText('Ask Questions')).toBeInTheDocument();
    expect(screen.getByText(/Manage Manuals/)).toBeInTheDocument();
  });
});
```

## Coverage Reports

### Backend Coverage

After running `poetry run pytest --cov=app --cov-report=html`, open:
```
backend/htmlcov/index.html
```

### Frontend Coverage

After running `npm test:coverage`, open:
```
frontend/coverage/index.html
```

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Backend CI
poetry run pytest --cov=app --cov-report=xml -m "not slow"

# Frontend CI
cd frontend && npm test -- --run --coverage
```

## Best Practices

### Backend
1. **Mock external dependencies**: Use pytest-mock for OpenAI, ChromaDB in unit tests
2. **Use fixtures**: Share common test data via conftest.py
3. **Test error cases**: Always test both success and failure paths
4. **Keep tests fast**: Mark slow tests with `@pytest.mark.slow`
5. **Use descriptive names**: `test_upload_invalid_file_returns_400` not `test_upload_1`

### Frontend
1. **Mock API calls**: Always mock the API client in hook/component tests
2. **Test user interactions**: Use `userEvent` for realistic interactions
3. **Avoid implementation details**: Test behavior, not internal state
4. **Use waitFor**: Handle async operations properly
5. **Clean up**: The setup file handles cleanup, but be aware of side effects

## Troubleshooting

### Backend

**Import errors**:
```bash
# Make sure you're in the right directory
cd backend
poetry run pytest
```

**OpenAI API key errors**:
The conftest.py sets a test key automatically. If you see real API calls, check your mocks.

**Database errors**:
Tests use in-memory database by default. Check `CHROMA_DB_PATH` in conftest.py.

### Frontend

**Module not found**:
```bash
# Reinstall dependencies
cd frontend
npm install
```

**Tests timing out**:
Increase timeout in vitest.config.ts or use `waitFor` with longer timeout.

**Can't find element**:
Use `screen.debug()` to see the rendered HTML.

## TODO: Additional Tests Needed

### Backend
- [ ] test_chroma_manager.py - Vector database operations
- [ ] test_qa_system.py - RAG pipeline and Q&A logic
- [ ] test_api/test_qa_routes.py - Q&A endpoints
- [ ] test_api/test_stats_routes.py - Complete stats endpoint tests

### Frontend
- [ ] useManuals.test.ts - Manual upload/management hooks
- [ ] App.test.tsx - Main component integration tests
- [ ] End-to-end tests with Playwright/Cypress

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Vitest documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
