# 🚀 AutoSense X - Quick Start Guide

## Prerequisites

- Python 3.8+
- Node.js (for frontend development, optional)
- Flutter SDK (for mobile app, optional)
- Windows OS (for full feature support)

## Installation

### 1. Clone/Setup Project

```bash
# Navigate to project directory
cd Autosense-X

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Run setup script
python setup.py
```

### 3. Configure Environment

```bash
# Copy environment template
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env
```

Edit `.env` file with your configuration:
- Set `SECRET_KEY` (generate a random string)
- Configure SMTP settings for email alerts (optional)
- Set Google OAuth credentials (optional)

### 4. Initialize Database

```bash
# Database will be created automatically on first run
# Or run setup.py which initializes it
python setup.py
```

## Running the Application

### Start Backend Server

```bash
python start_server.py
```

Or directly:
```bash
uvicorn main:app --reload
```

Server will start on `http://localhost:8000`

### Access the Application

1. **API Documentation**: http://localhost:8000/docs
2. **Frontend**: Open `frontend/index.html` in your browser
3. **Mobile App**: Run Flutter app (see mobile section)

## First Time Setup

### 1. Register a User

1. Open frontend or use API
2. Click "Register" or use `/api/auth/register/request-otp`
3. Enter email to receive OTP
4. Complete registration with OTP

### 2. Login

1. Use registered credentials
2. Or use Google OAuth (if configured)

### 3. Explore Features

- **Dashboard**: View system stats
- **AI Brain**: Get health predictions
- **Disk Map**: Explore disk usage
- **Apps**: Manage installed applications
- **Security**: Check firewall and ports

## Mobile App Setup

### Prerequisites
- Flutter SDK installed
- Android Studio / Xcode (for mobile development)

### Run Mobile App

```bash
cd mobile
flutter pub get
flutter run
```

**Note**: Update `baseUrl` in `mobile/lib/services/api_service.dart` to match your server IP if testing on physical device.

## Testing Features

### 1. System Monitoring
```bash
# Check system info (no auth required)
curl http://localhost:8000/api/system/info
```

### 2. AI Prediction (requires auth)
```bash
# Login first to get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -d "username=youruser&password=yourpass" \
  | jq -r '.access_token')

# Get AI prediction
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/ai/predict
```

### 3. Boost RAM
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/boost-ram
```

## Voice Assistant

### Activate Voice Assistant

1. Click "Activate Voice Assistant" in Settings
2. Say "Hey AutoSense" to wake up
3. Commands:
   - "Boost RAM" / "Boost memory"
   - "Optimize system"
   - "Clean junk files"
   - "Check status" / "System health"
   - "Generate report"

## Email Alerts

### Setup Email Alerts

1. Configure SMTP in `.env`:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   EMAIL_FROM=your-email@gmail.com
   ```

2. Enable monitoring (in code or via API)

## Troubleshooting

### Port Already in Use
```bash
# Change port in .env or use different port
uvicorn main:app --port 8001
```

### Database Errors
```bash
# Delete existing database and reinitialize
rm autosense.db
python setup.py
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Windows-Specific Issues
- Some features require administrator privileges
- Process killing may need elevated permissions
- Firewall checks work best on Windows

## Development

### Project Structure
See `PROJECT_STRUCTURE.md` for detailed structure.

### Adding New Features

1. Create router in `routers/`
2. Add endpoints
3. Update frontend if needed
4. Test via `/docs` interface

### API Testing
Use Swagger UI at `/docs` for interactive API testing.

## Production Deployment

### Security Checklist
- [ ] Change `SECRET_KEY` to strong random value
- [ ] Set `DEBUG=False`
- [ ] Configure proper CORS origins
- [ ] Use HTTPS
- [ ] Set up proper database (PostgreSQL recommended)
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging

### Deployment Options
- Docker (create Dockerfile)
- Cloud platforms (AWS, Azure, GCP)
- VPS with Nginx reverse proxy

## Support

For issues or questions:
1. Check `README.md` for detailed documentation
2. Review `PROJECT_STRUCTURE.md` for architecture
3. Check API docs at `/docs`

## Next Steps

1. ✅ Complete setup
2. ✅ Test basic features
3. ✅ Configure email alerts
4. ✅ Set up mobile app
5. ✅ Customize for your needs
6. ✅ Deploy to production

Happy optimizing! 🔥

