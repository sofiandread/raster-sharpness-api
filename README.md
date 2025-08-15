# Raster Sharpness API

POST `/raster-quality` (multipart/form-data):
- `image`: raster image file (PNG/JPEG)
- (optional) `printWIn`, `printHIn`, `dpiMin` for context (numbers)

**Response**
```json
{
  "sharpness": { "lapVar": 180.4, "decision": "warn", "bullet": "..." },
  "context": { "printWIn": 7, "printHIn": 7.17, "dpiMin": 260 }
}
