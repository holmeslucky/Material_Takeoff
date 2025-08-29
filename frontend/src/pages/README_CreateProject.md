# CreateProject.tsx (Drop-in for Claude Code)

This component is a hardened, a11y-friendly "Create Project" form designed for a React + React Router app with Tailwind classes and lucide-react icons.

## Files
- `CreateProject.tsx` — the component
- Use anywhere in your routes (example below).

## Install prerequisites
```bash
npm i react-router-dom lucide-react
# or
yarn add react-router-dom lucide-react
```

## Add a route
```tsx
import { createBrowserRouter } from 'react-router-dom'
import CreateProject from './CreateProject'

const router = createBrowserRouter([
  // ...other routes
  { path: '/projects/new', element: <CreateProject /> },
])
```

## Backend expectation
POST `/api/v1/projects/` with JSON body:
```json
{
  "project_id": "25-0001",
  "name": "My Project",
  "client": "Customer, Inc.",
  "quote_number": "25-0001",
  "date": "2025-08-22",
  "estimator": "Blake",
  "location": "Phoenix, AZ",
  "description": "Optional notes"
}
```
- On success: return `200/201` with `{ "id": "<uuid or numeric id>", ... }` so the client can `navigate(/projects/:id)`.
- On duplicate `project_id`, prefer `409 Conflict` with `{ "detail": "Project ID already exists" }`.
- On validation errors, use `422 Unprocessable Entity` with `{ "detail": "..." }`.

## Notes
- Uses **local time** for `<input type="date">` (avoids UTC off-by-one from `toISOString()`).
- Handles aborting in-flight requests on unmount and double submit.
- Disables submit until the form is valid; inline errors have proper `aria-*` attributes.
