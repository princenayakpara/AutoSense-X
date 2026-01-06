# 🔥 AutoSense X — Ultimate AI System Guardian

World's most advanced AI PC Guardian combining Microsoft PC Manager, WizTree Disk Analyzer, Revo Uninstaller Pro, and a self-healing AI brain.

## 🚀 Features

### 🧠 AI System Brain
- **Failure Prediction**: IsolationForest + LSTM models predict system degradation
- **Auto-Optimization**: Intelligent CPU/RAM/Disk optimization
- **PDF Reports**: Downloadable optimization reports
- **Plain English Explanations**: AI explains system health in human language

### 💻 Microsoft PC Manager Features
- One-Click RAM Boost
- Startup App Manager
- Junk File Cleaner
- Health Alerts
- Process Management

### 🌲 WizTree Disk Map Engine
- Interactive treemap visualization
- Color-coded size representation
- Drill-down folder exploration
- Real-time disk analysis

### 🗑️ Revo Uninstaller Pro
- Installed Apps Listing
- Smart Uninstall with leftover detection
- Force Remove capabilities
- Registry cleanup

### 🛡️ Advanced Security Center
- Firewall Status Monitoring
- Open Ports Detection
- AI-Powered Malware Scanning

### 📱 Mobile Companion App
- Live system monitoring
- Remote process management
- RAM boost on-the-go
- AI risk alerts
- Cloud sync

## 🛠️ Installation

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run migrations (if needed)
python -m alembic upgrade head

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

### Mobile App Setup

```bash
cd mobile
flutter pub get
flutter run
```

## 📡 API Endpoints

### AI System Brain
- `GET /api/ai/predict` - Get system health predictions
- `POST /api/ai/auto-optimize` - Trigger auto-optimization
- `GET /api/ai/report` - Download PDF report

### System Management
- `POST /api/boost-ram` - Boost system RAM
- `GET /api/startup-apps` - List startup applications
- `GET /api/junk-files/scan` - Scan for junk files
- `POST /api/junk-files/clean` - Clean junk files
- `GET /api/alerts` - Get health alerts
- `POST /api/processes/{pid}/kill` - Kill a process

### Disk Analysis
- `GET /api/disk-map` - Get disk treemap data

### App Management
- `GET /api/apps` - List installed apps
- `POST /api/apps/{name}/remove` - Uninstall app
- `GET /api/apps/{name}/leftovers` - Scan for leftovers
- `POST /api/apps/{name}/force` - Force remove app

### Security
- `GET /api/security/firewall` - Check firewall status
- `GET /api/security/ports` - List open ports
- `POST /api/security/scan` - Run malware scan

### Authentication
- `POST /api/auth/register` - Register with email OTP
- `POST /api/auth/login` - Login
- `POST /api/auth/google` - Google OAuth
- `GET /api/auth/me` - Get current user

## 🎨 UI Design

Premium Glassmorphism + Neon Dark Mode:
- Frosted glass cards
- Floating neon shadows
- Gradient borders
- Smooth transitions
- Cyberpunk aesthetic
- Mobile-first responsive

## 🔐 Security

- JWT-based authentication
- SQLite database for users
- Google OAuth integration
- Secure API endpoints
- Role-based access control

## 🏆 Hackathon Extras

- AI-generated PDF reports
- Email alerts for critical issues
- Voice assistant ("Hey AutoSense boost system")
- Offline fallback mode
- Cloud backup of history

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

