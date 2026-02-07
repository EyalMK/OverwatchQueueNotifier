# Contributing

## Workflow
1. Pick a ticket from `SDD/specs/backlog.md`
2. Create a branch from `develop`: `feat/<ticket-id>-<desc>`
3. Implement with tests
4. Run lint/typecheck/tests
5. Open a PR to `develop`

## Commit Format
`type(scope): subject`

Examples:
```
feat(backend): implement gate logic
test(frontend): add game store tests
```

## Testing
```bash
cd backend
pytest

cd frontend
npm run test
```

## ONNX Models
- Sprint 1 ships ONNX models in-repo; no download step is required.
- Paths:
  - `backend/models/Shufflenet-v2.onnx` (primary tiny classifier)
  - `backend/models/efficientnet-lite4-11.onnx` (escalation classifier)
- Run `python backend/scripts/verify_models.py` to validate model loading and baseline latency.
