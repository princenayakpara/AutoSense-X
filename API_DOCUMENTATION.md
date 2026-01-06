# AutoSense X - API Documentation

Base URL: `http://localhost:8000`

All authenticated endpoints require JWT token in header:
```
Authorization: Bearer <token>
```

## Authentication Endpoints

### Request OTP
```http
POST /api/auth/register/request-otp
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password",
  "otp": "123456"
}
```

### Login
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user&password=pass
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user"
  }
}
```

### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

### Google OAuth
```http
GET /api/auth/google
```

## AI System Brain

### Get Prediction
```http
GET /api/ai/predict
Authorization: Bearer <token>
```

Response:
```json
{
  "success": true,
  "prediction": {
    "risk_score": 0.65,
    "risk_level": "medium",
    "explanation": "System health risk is MEDIUM...",
    "recommendations": [
      "Close unnecessary applications",
      "Free up RAM"
    ],
    "features": {
      "cpu_percent": 75.5,
      "memory_percent": 82.3,
      "disk_percent": 65.0
    }
  }
}
```

### Auto Optimize
```http
POST /api/ai/auto-optimize
Authorization: Bearer <token>

{
  "force": false
}
```

### Generate PDF Report
```http
GET /api/ai/report
Authorization: Bearer <token>
```
Returns PDF file download.

## System Management

### Boost RAM
```http
POST /api/boost-ram
Authorization: Bearer <token>
```

Response:
```json
{
  "success": true,
  "memory_before": 82.5,
  "memory_after": 75.2,
  "freed_percent": 7.3
}
```

### Get Startup Apps
```http
GET /api/startup-apps
Authorization: Bearer <token>
```

### Scan Junk Files
```http
GET /api/junk-files/scan
Authorization: Bearer <token>
```

### Clean Junk Files
```http
POST /api/junk-files/clean
Authorization: Bearer <token>
```

### Get Alerts
```http
GET /api/alerts?resolved=false
Authorization: Bearer <token>
```

### Kill Process
```http
POST /api/processes/{pid}/kill
Authorization: Bearer <token>

{
  "force": false
}
```

## Disk Analysis

### Get Disk Map
```http
GET /api/disk-map?drive=C:&max_depth=4
Authorization: Bearer <token>
```

Response:
```json
{
  "success": true,
  "drive": "C:",
  "total_size": 500000000000,
  "used_size": 300000000000,
  "free_size": 200000000000,
  "treemap": {
    "name": "C:",
    "size": 500000000000,
    "children": [
      {
        "name": "Windows",
        "size": 20000000000,
        "children": [...]
      }
    ]
  }
}
```

## App Management

### List Installed Apps
```http
GET /api/apps
Authorization: Bearer <token>
```

### Uninstall App
```http
POST /api/apps/{app_name}/remove
Authorization: Bearer <token>
```

### Scan Leftovers
```http
GET /api/apps/{app_name}/leftovers
Authorization: Bearer <token>
```

### Force Remove
```http
POST /api/apps/{app_name}/force
Authorization: Bearer <token>
```

## Security Center

### Check Firewall
```http
GET /api/security/firewall
Authorization: Bearer <token>
```

### Get Open Ports
```http
GET /api/security/ports
Authorization: Bearer <token>
```

### Malware Scan
```http
POST /api/security/scan
Authorization: Bearer <token>
```

## Voice Assistant

### Activate
```http
POST /api/voice/activate
Authorization: Bearer <token>
```

### Deactivate
```http
POST /api/voice/deactivate
Authorization: Bearer <token>
```

### Get Status
```http
GET /api/voice/status
Authorization: Bearer <token>
```

## System Info (No Auth Required)

### Get System Info
```http
GET /api/system/info
```

## Error Responses

All endpoints may return errors in this format:

```json
{
  "success": false,
  "error": "Error message",
  "detail": "Detailed error information"
}
```

HTTP Status Codes:
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

Currently no rate limiting implemented. Recommended for production:
- 100 requests/minute per user
- 1000 requests/hour per user

## WebSocket Support

Future enhancement for real-time updates:
- System metrics streaming
- Live alerts
- Real-time optimization status

