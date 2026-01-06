# AutoSense X - Project Structure

## 📁 Directory Structure

```
Autosense-X/
├── main.py                 # FastAPI main application
├── database.py             # Database models and session management
├── ai_engine.py            # AI System Brain (IsolationForest + LSTM)
├── auth.py                 # Authentication and JWT utilities
├── voice_assistant.py      # Voice assistant module
├── email_alerts.py         # Email alert service
├── offline_mode.py         # Offline fallback mode
├── setup.py                # Setup script
├── start_server.py         # Server startup script
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── README.md               # Main documentation
├── PROJECT_STRUCTURE.md    # This file
│
├── routers/                # API route modules
│   ├── __init__.py
│   ├── ai.py               # AI System Brain endpoints
│   ├── system.py           # System management endpoints
│   ├── disk.py             # Disk map endpoints
│   ├── apps.py             # App management endpoints
│   ├── security.py         # Security center endpoints
│   ├── auth_router.py      # Authentication endpoints
│   └── voice.py            # Voice assistant endpoints
│
├── frontend/               # Web frontend
│   ├── index.html          # Main HTML file
│   ├── styles.css          # Glassmorphism + Neon Dark Mode styles
│   └── app.js              # Frontend JavaScript
│
├── mobile/                 # Flutter mobile app
│   ├── pubspec.yaml        # Flutter dependencies
│   └── lib/
│       ├── main.dart       # App entry point
│       ├── providers/      # State management
│       │   ├── auth_provider.dart
│       │   └── system_provider.dart
│       ├── services/       # API services
│       │   └── api_service.dart
│       └── screens/        # UI screens
│           ├── login_screen.dart
│           └── dashboard_screen.dart
│
├── models/                 # AI model storage (created at runtime)
├── temp/                   # Temporary files (PDFs, etc.)
├── cache/                  # Offline mode cache
└── logs/                   # Application logs
```

## 🔧 Core Modules

### Backend (Python/FastAPI)

1. **main.py** - FastAPI application entry point
   - CORS configuration
   - Router registration
   - Error handlers

2. **database.py** - SQLAlchemy models
   - User management
   - System metrics storage
   - AI predictions history
   - Optimization history
   - Alerts storage

3. **ai_engine.py** - AI System Brain
   - IsolationForest for anomaly detection
   - LSTM for time-series prediction
   - System health prediction
   - Auto-optimization logic
   - Feature collection and analysis

4. **auth.py** - Authentication
   - JWT token management
   - Password hashing
   - OTP email sending
   - Google OAuth support

5. **routers/** - API endpoints
   - `/api/ai/*` - AI predictions and optimization
   - `/api/boost-ram` - RAM boost
   - `/api/startup-apps` - Startup management
   - `/api/junk-files/*` - Junk file cleaner
   - `/api/alerts` - System alerts
   - `/api/processes/{pid}/kill` - Process management
   - `/api/disk-map` - Disk treemap
   - `/api/apps/*` - App uninstaller
   - `/api/security/*` - Security center
   - `/api/auth/*` - Authentication
   - `/api/voice/*` - Voice assistant

### Frontend (HTML/CSS/JavaScript)

1. **index.html** - Main UI structure
   - Dashboard
   - AI Brain section
   - Disk Map explorer
   - Apps manager
   - Security center
   - Settings

2. **styles.css** - Premium UI styling
   - Glassmorphism effects
   - Neon dark mode theme
   - Responsive design
   - Smooth animations

3. **app.js** - Frontend logic
   - API communication
   - Chart.js integration
   - Real-time updates
   - Voice assistant integration

### Mobile (Flutter)

1. **main.dart** - App entry point
2. **providers/** - State management with Provider
3. **services/** - API communication
4. **screens/** - UI screens

## 🚀 API Endpoints Summary

### Authentication
- `POST /api/auth/register/request-otp` - Request OTP
- `POST /api/auth/register` - Register with OTP
- `POST /api/auth/login` - Login
- `GET /api/auth/google` - Google OAuth
- `GET /api/auth/me` - Get current user

### AI System Brain
- `GET /api/ai/predict` - Get health prediction
- `POST /api/ai/auto-optimize` - Auto optimize
- `GET /api/ai/report` - Generate PDF report

### System Management
- `POST /api/boost-ram` - Boost RAM
- `GET /api/startup-apps` - List startup apps
- `GET /api/junk-files/scan` - Scan junk files
- `POST /api/junk-files/clean` - Clean junk files
- `GET /api/alerts` - Get alerts
- `POST /api/processes/{pid}/kill` - Kill process

### Disk Analysis
- `GET /api/disk-map` - Get disk treemap

### App Management
- `GET /api/apps` - List installed apps
- `POST /api/apps/{name}/remove` - Uninstall app
- `GET /api/apps/{name}/leftovers` - Scan leftovers
- `POST /api/apps/{name}/force` - Force remove

### Security
- `GET /api/security/firewall` - Check firewall
- `GET /api/security/ports` - List open ports
- `POST /api/security/scan` - Malware scan

### Voice Assistant
- `POST /api/voice/activate` - Activate voice assistant
- `POST /api/voice/deactivate` - Deactivate
- `GET /api/voice/status` - Get status

## 🎨 Design System

### Colors
- Primary Background: `#0a0e27`
- Secondary Background: `#16213e`
- Tertiary Background: `#1a1a2e`
- Neon Cyan: `#00ffff`
- Neon Pink: `#ff00ff`
- Neon Blue: `#0066ff`

### Glassmorphism
- Background: `rgba(255, 255, 255, 0.05)`
- Border: `rgba(255, 255, 255, 0.1)`
- Backdrop Filter: `blur(20px)`

## 📱 Mobile App Features

- Live system monitoring
- Remote process management
- RAM boost
- Disk cleanup
- AI risk alerts
- Cloud sync (future)

## 🔐 Security Features

- JWT authentication
- Password hashing (bcrypt)
- Google OAuth
- Role-based access control
- Secure API endpoints

## 🏆 Hackathon Extras

- ✅ AI-generated PDF reports
- ✅ Email alerts for critical issues
- ✅ Voice assistant ("Hey AutoSense")
- ✅ Offline fallback mode
- ✅ Cloud backup (structure ready)

