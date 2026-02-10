# FastAPI + React Simulation UI - Setup & Run Guide

## Quick Start

### 1. Install API Dependencies
```powershell
cd simulation-engine/api
pip install -r requirements.txt
```

### 2. Install UI Dependencies
```powershell
cd simulation-engine/ui
npm install
```

### 3. Start the API Server
```powershell
cd simulation-engine/api
uvicorn main:app --reload --port 8000
```

API will be available at: http://localhost:8000
OpenAPI docs at: http://localhost:8000/docs

### 4. Start the React UI (in a new terminal)
```powershell
cd simulation-engine/ui
npm run dev
```

UI will be available at: http://localhost:5173

## Project Structure

```
simulation-engine/
├── api/                      # FastAPI REST API
│   ├── main.py              # API endpoints
│   ├── models.py            # Pydantic models
│   ├── templates.py         # Platelet template
│   ├── requirements.txt     # Python dependencies
│   └── tests/test_api.py    # API tests
│
├── ui/                       # React + Vite Frontend
│   ├── src/
│   │   ├── main.tsx         # Entry point
│   │   ├── App.tsx          # Main application
│   │   ├── App.css          # Styles
│   │   ├── types.ts         # TypeScript types
│   │   ├── api.ts           # API client
│   │   ├── ErrorBoundary.tsx# Error handling
│   │   └── components/
│   │       ├── ConfigForm.tsx    # Configuration editor
│   │       └── Results.tsx       # Results display
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
└── src/simulation_engine/   # Core engine (unchanged)
```

## Testing

### Run API Tests
```powershell
cd simulation-engine
python -m pytest api/tests/test_api.py -v
```

### Manual Testing
1. Open http://localhost:5173
2. The platelet pooling template loads automatically
3. Modify device capacities, process times, or simulation duration
4. Click "Run Simulation" to execute
5. View JSON results in the right panel

## API Endpoints

- `GET /` - API information
- `GET /templates/platelet-pooling` - Get platelet template
- `POST /scenarios` - Create scenario
- `GET /scenarios` - List all scenarios
- `GET /scenarios/{id}` - Get scenario by ID
- `PUT /scenarios/{id}` - Update scenario
- `DELETE /scenarios/{id}` - Delete scenario
- `POST /simulations/run` - Run simulation

## Environment Variables

Create `simulation-engine/ui/.env`:
```
VITE_API_URL=http://localhost:8000
```

## Implementation Notes

### Completed Features
- ✅ FastAPI REST API with CORS
- ✅ Pydantic validation with field validators
- ✅ Scenario CRUD endpoints
- ✅ Synchronous simulation execution
- ✅ Platelet pooling template
- ✅ React UI with TypeScript
- ✅ Configuration forms (devices, flows, simulation params)
- ✅ JSON results display
- ✅ Error boundary for crash protection
- ✅ API test suite (13 tests)

### Known Issues (Minor)
- Test database cleanup on Windows (file locking) - tests pass but cleanup fails
- Tag handling edge case with empty strings from DB

### Phase 2 Enhancements (Out of Scope for MVP)
- Async simulation execution with progress updates
- Results visualization (charts/graphs)
- Multiple scenario comparison
- Advanced UI component library
- Authentication/authorization
- Production deployment configuration
