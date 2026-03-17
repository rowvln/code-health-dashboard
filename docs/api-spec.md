# API Spec

## POST /api/analyze
Uploads code and returns analysis results.

### Request
- Content type: multipart/form-data
- Field: `file`

### Response
```json
{
  "score": 78,
  "summary": {
    "issues": 12,
    "high_severity": 3,
    "files_analyzed": 2
  },
  "files": [
    {
      "name": "app.py",
      "score": 72,
      "issues": 4,
      "complexity": 11
    }
  ],
  "recommendations": [
    "Refactor nested loops in app.py",
    "Reduce function length in utils.py"
  ]
}
```
