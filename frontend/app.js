// ===== GOOGLE OAUTH AUTO LOGIN BRIDGE =====
(function () {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    if (token) {
        console.log("🔐 Google Login Successful. Token stored.");
        localStorage.setItem("authToken", token);

        // Clean URL
        window.history.replaceState({}, document.title, "/");
    }
})();
// AutoSense X - Enhanced Frontend Application Logic

const API_BASE = 'http://localhost:8000';
let authToken = localStorage.getItem('authToken') || null;
let charts = {};
let updateInterval = null;
let autoRefreshEnabled = true;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    hideLoadingScreen();
    bootstrapApp();
    setupEventListeners();
    checkServerStatus();
});

// 👁 5️⃣ Pause Monitoring when Tab Hidden
document.addEventListener("visibilitychange", () => {
    if (document.hidden) stopSystemMonitoring();
    else if (autoRefreshEnabled) startSystemMonitoring();
});

// Bootstraps application initial state
function bootstrapApp() {
    autoRefreshEnabled = localStorage.getItem('autoRefresh') !== 'false';
    const autoRefreshToggle = document.getElementById('autoRefreshToggle');
    if (autoRefreshToggle) autoRefreshToggle.checked = autoRefreshEnabled;

    const notificationsToggle = document.getElementById('notificationsToggle');
    if (notificationsToggle) notificationsToggle.checked = localStorage.getItem('notifications') !== 'false';

    if (authToken) {
        setLoggedInUI(true);
        loadUserInfo();
    } else {
        setLoggedInUI(false);
    }
    
    // Wait for Chart.js to load before initializing
    const waitForCharts = setInterval(() => {
        if (window.Chart) {
            clearInterval(waitForCharts);
            initializeCharts();
            loadDashboard();
            if (autoRefreshEnabled) startSystemMonitoring();
        }
    }, 100);

    setupNavigation();
    initializeDrives();
    setTimeout(updateHealthSaver, 2000);
}

// 💾 Load available drives dynamically
async function initializeDrives() {
    const driveSelect = document.getElementById('driveSelect');
    if (!driveSelect) return;

    try {
        const result = await apiCall('/api/drives', { silent: true });
        if (result && result.success && result.drives.length > 0) {
            driveSelect.innerHTML = '';
            result.drives.forEach(drive => {
                const option = document.createElement('option');
                option.value = drive;
                option.textContent = `${drive} Drive`;
                driveSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Failed to initialize drives:', error);
    }
}

// Set UI state based on login
function setLoggedInUI(isLoggedIn) {
    const loginBtn = document.getElementById('loginBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const userInfo = document.getElementById('userInfo');

    if (loginBtn) loginBtn.style.display = isLoggedIn ? 'none' : 'block';
    if (logoutBtn) logoutBtn.style.display = isLoggedIn ? 'block' : 'none';
    if (userInfo) userInfo.style.display = isLoggedIn ? 'block' : 'none';
}

// Hide loading screen safely
function hideLoadingScreen() {
    const loading = document.getElementById('loadingScreen');
    if (loading) {
        setTimeout(() => {
            loading.classList.add('hidden');
            setTimeout(() => {
                if (loading.parentNode) loading.remove();
            }, 500);
        }, 1000);
    }
}

// Check server status
async function checkServerStatus() {
    try {
        const response = await fetch(`${API_BASE}/health`, { cache: "no-store" });
        updateServerStatus(response.ok);
    } catch (error) {
        updateServerStatus(false);
    }
}

function updateServerStatus(online) {
    const indicator = document.getElementById('serverStatus');
    if (indicator) {
        indicator.style.background = online ? '#00ff88' : '#ff0000';
        indicator.title = online ? 'Server Online' : 'Server Offline';
    }
}

// Load user info
async function loadUserInfo() {
    if (!authToken) return;
    try {
        const response = await apiCall('/api/auth/me');
        if (response && response.username) {
            const usernameDisplay = document.getElementById('usernameDisplay');
            if (usernameDisplay) usernameDisplay.textContent = response.username;
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.getAttribute('data-section') || link.getAttribute('href').substring(1);
            showSection(section);
        });
    });
    
    // Auth
    document.getElementById('loginBtn')?.addEventListener('click', showLoginModal);
    document.getElementById('logoutBtn')?.addEventListener('click', logout);
    document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
    document.getElementById('googleLoginBtn')?.addEventListener('click', handleGoogleLogin);
    document.querySelector('.close')?.addEventListener('click', closeLoginModal);
    
    // Dashboard actions
    document.getElementById('boostRamBtn')?.addEventListener('click', boostRAM);
    document.getElementById('cleanJunkBtn')?.addEventListener('click', cleanJunkFiles);
    document.getElementById('optimizeBtn')?.addEventListener('click', autoOptimize);
    document.getElementById('scanSecurityBtn')?.addEventListener('click', () => showSection('security'));
    document.getElementById('refreshDashboard')?.addEventListener('click', () => {
        loadDashboard();
        showToast('Dashboard refreshed', 'success');
    });
    
    // AI Brain
    document.getElementById('predictBtn')?.addEventListener('click', getAIPrediction);
    document.getElementById('autoOptimizeBtn')?.addEventListener('click', triggerAutoOptimize);
    document.getElementById('generateReportBtn')?.addEventListener('click', generatePDFReport);
    
    // Disk Map
    document.getElementById('loadDiskMapBtn')?.addEventListener('click', loadDiskMap);
    document.getElementById('depthSlider')?.addEventListener('input', (e) => {
        document.getElementById('depthValue').textContent = e.target.value;
    });
    
    // Apps
    document.getElementById('refreshAppsBtn')?.addEventListener('click', loadApps);
    document.getElementById('appSearch')?.addEventListener('input', filterApps);
    
    // Security
    document.getElementById('checkFirewallBtn')?.addEventListener('click', checkFirewall);
    document.getElementById('scanPortsBtn')?.addEventListener('click', scanPorts);
    document.getElementById('malwareScanBtn')?.addEventListener('click', runMalwareScan);
    
    // Voice Assistant
    document.getElementById('voiceAssistantBtn')?.addEventListener('click', activateVoiceAssistant);
    
    // Settings
    document.getElementById('autoRefreshToggle')?.addEventListener('change', (e) => {
        autoRefreshEnabled = e.target.checked;
        localStorage.setItem('autoRefresh', autoRefreshEnabled);
        if (autoRefreshEnabled) startSystemMonitoring();
        else stopSystemMonitoring();
    });

    document.getElementById('notificationsToggle')?.addEventListener('change', (e) => {
        localStorage.setItem('notifications', e.target.checked);
    });

    // Notifications Dropdown Toggle
    const notifBell = document.getElementById('notifBell');
    const notifDropdown = document.getElementById('notifDropdown');
    
    notifBell?.addEventListener('click', (e) => {
        e.stopPropagation();
        notifDropdown?.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
        if (!notifDropdown?.contains(e.target) && !notifBell?.contains(e.target)) {
            notifDropdown?.classList.remove('show');
        }
    });

    document.getElementById('clearNotifs')?.addEventListener('click', () => {
        const list = document.getElementById('alertsList');
        if (list) {
            list.innerHTML = `
                <div class="notif-placeholder">
                    <span>🔔</span>
                    <p>No new notifications</p>
                </div>
            `;
        }
        updateNotifBadge(0);
    });

    // Modal close on outside click
    document.getElementById('loginModal')?.addEventListener('click', (e) => {
        if (e.target.id === 'loginModal') closeLoginModal();
    });

    // FAQ Accordion logic
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        item.addEventListener('click', () => {
            const isActive = item.classList.contains('active');
            faqItems.forEach(i => i.classList.remove('active'));
            if (!isActive) item.classList.add('active');
        });
    });
}

function setupNavigation() {
    const currentHash = window.location.hash.substring(1) || 'dashboard';
    showSection(currentHash);
}

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.toggle('active', section.id === sectionId);
    });
    
    document.querySelectorAll('.nav-link').forEach(link => {
        const linkSection = link.getAttribute('data-section') || link.getAttribute('href').substring(1);
        link.classList.toggle('active', linkSection === sectionId);
    });

    // Toggle global footer visibility
    const footer = document.getElementById('mainFooter');
    if (footer) {
        footer.style.display = sectionId === 'dashboard' ? 'block' : 'none';
    }
    
    // Load section data if needed
    if (sectionId === 'dashboard') {
        loadDashboard();
    } else if (sectionId === 'apps' && authToken) {
        loadApps();
    } else if (sectionId === 'security' && authToken) {
        checkFirewall();
    }
}

// Authentication
function showLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) modal.classList.add('show');
}

function closeLoginModal() {
    const modal = document.getElementById('loginModal');
    if (modal) modal.classList.remove('show');
}

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const btn = e.target.querySelector('button[type="submit"]');
    const loader = btn?.querySelector('.btn-loader');
    
    if (loader) loader.style.display = 'block';
    if (btn) btn.disabled = true;
    
    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            showToast('Login successful!', 'success');
            closeLoginModal();
            setLoggedInUI(true);
            loadUserInfo();
            startSystemMonitoring();
        } else {
            showToast('Login failed: ' + (data.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        showToast('Login error: ' + error.message, 'error');
    } finally {
        if (loader) loader.style.display = 'none';
        if (btn) btn.disabled = false;
    }
}

function handleGoogleLogin() {
    window.location.href = `${API_BASE}/api/auth/google`;
}

function logout() {
    authToken = null;
    localStorage.removeItem('authToken');
    setLoggedInUI(false);
    stopSystemMonitoring();
    showToast('Logged out successfully', 'success');
}

// 🧠 2️⃣ API Helper with Silent Mode (replace your apiCall)
async function apiCall(endpoint, options = {}) {
    const headers = { ...(options.headers || {}) };

    if (!(options.body instanceof FormData))
        headers["Content-Type"] = "application/json";

    if (authToken) headers.Authorization = `Bearer ${authToken}`;

    try {
        const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

        if (res.status === 401 && !options.silent) {
            logout();
            return null;
        }

        return await res.json();
    } catch {
        return null;
    }
}

// Toast Notifications
function showToast(message, type = 'info') {
    if (localStorage.getItem('notifications') === 'false') return;
    
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    toast.innerHTML = `
        <span style="font-size: 1.5rem;">${icons[type] || icons.info}</span>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ⚡ 3️⃣ Dashboard Always Works (replace loadDashboard())
async function loadDashboard() {
    const systemInfo = await apiCall("/api/system/info", { silent: true });

    if (!systemInfo) {
        updateServerStatus(false);
        return;
    }

    updateServerStatus(true);

    if (systemInfo.success) updateSystemStats(systemInfo.system);

    if (authToken) {
        const alerts = await apiCall("/api/alerts");
        if (alerts?.success) displayAlerts(alerts);
    }
}

function updateSystemStats(system) {
    if (!system) return;

    // Update CPU
    const cpuPercent = system.cpu_percent || 0;
    const cpuEl = document.getElementById('cpuPercent');
    if (cpuEl) cpuEl.textContent = `${cpuPercent.toFixed(1)}%`;
    const cpuCoresEl = document.getElementById('cpuCores');
    if (cpuCoresEl) cpuCoresEl.textContent = `${system.cpu_count || 0} Cores`;
    updateChart('cpuChart', cpuPercent);
    updateTrend('cpuTrend', cpuPercent);
    
    // Update Memory
    const memoryPercent = system.memory_percent || 0;
    const memEl = document.getElementById('memoryPercent');
    if (memEl) memEl.textContent = `${memoryPercent.toFixed(1)}%`;
    const memDetailsEl = document.getElementById('memoryDetails');
    if (memDetailsEl) memDetailsEl.textContent = 
        `${(system.memory_used_gb || 0).toFixed(1)} GB / ${(system.memory_total_gb || 0).toFixed(1)} GB`;
    updateChart('memoryChart', memoryPercent);
    updateTrend('memoryTrend', memoryPercent);
    
    // Update Disk
    const diskPercent = system.disk_percent || 0;
    const diskEl = document.getElementById('diskPercent');
    if (diskEl) diskEl.textContent = `${diskPercent.toFixed(1)}%`;
    const diskDetailsEl = document.getElementById('diskDetails');
    if (diskDetailsEl) diskDetailsEl.textContent = 
        `${(system.disk_total_gb - system.disk_used_gb || 0).toFixed(1)} GB Free`;
    updateChart('diskChart', diskPercent);
    updateTrend('diskTrend', diskPercent);
    
    // Update Processes
    const processCount = system.process_count || 0;
    const procEl = document.getElementById('processCount');
    if (procEl) procEl.textContent = processCount;
    // Scaled to 500 for better representation on Windows systems
    const processProgress = Math.min(100, (processCount / 500) * 100);
    const procProgEl = document.getElementById('processProgress');
    if (procProgEl) procProgEl.style.width = `${processProgress}%`;
}

function updateTrend(elementId, value) {
    const trend = document.getElementById(elementId);
    if (!trend) return;
    
    const prevValue = parseFloat(trend.dataset.prevValue || value);
    const diff = value - prevValue;
    
    if (diff > 0) {
        trend.textContent = `↑ ${diff.toFixed(1)}%`;
        trend.style.background = 'rgba(255, 0, 0, 0.2)';
        trend.style.color = '#ff6b6b';
    } else if (diff < 0) {
        trend.textContent = `↓ ${Math.abs(diff).toFixed(1)}%`;
        trend.style.background = 'rgba(0, 255, 136, 0.2)';
        trend.style.color = '#00ff88';
    } else {
        trend.textContent = '→ 0%';
        trend.style.background = 'rgba(255, 255, 255, 0.1)';
        trend.style.color = '#b0b0b0';
    }
    
    trend.dataset.prevValue = value;
}

function initializeCharts() {
    const createConfig = (label) => ({
        type: 'line',
        data: {
            labels: Array(25).fill(''),
            datasets: [{
                label: label,
                data: Array(25).fill(0),
                borderColor: '#00ffff',
                backgroundColor: 'rgba(0,255,255,0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 0 },
            plugins: { legend: { display: false } },
            scales: {
                y: { min: 0, max: 100, display: false },
                x: { display: false }
            }
        }
    });

    if (!charts.cpuChart) {
        const cpuCtx = document.getElementById('cpuChart');
        if (cpuCtx) charts.cpuChart = new Chart(cpuCtx, createConfig('CPU'));
    }
    if (!charts.memoryChart) {
        const memCtx = document.getElementById('memoryChart');
        if (memCtx) charts.memoryChart = new Chart(memCtx, createConfig('Memory'));
    }
    if (!charts.diskChart) {
        const diskCtx = document.getElementById('diskChart');
        if (diskCtx) charts.diskChart = new Chart(diskCtx, createConfig('Disk'));
    }
}

function updateChart(chartId, value) {
    const chart = charts[chartId];
    if (!chart) return;

    chart.data.datasets[0].data.push(value);
    chart.data.datasets[0].data.shift();
    chart.update('none');
}

// 🛡 4️⃣ Monitoring Engine Hardened
function startSystemMonitoring() {
    stopSystemMonitoring();

    updateInterval = setInterval(() => {
        if (!document.hidden && autoRefreshEnabled) loadDashboard();
    }, 3000);
}

function stopSystemMonitoring() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

function displayAlerts(alertsData) {
    const alertsList = document.getElementById('alertsList');
    if (!alertsList) return;
    
    const allAlerts = [...(alertsData.stored_alerts || []), ...(alertsData.current_alerts || [])];
    
    if (allAlerts.length === 0) {
        alertsList.innerHTML = `
            <div class="notif-placeholder">
                <span>🔔</span>
                <p>No alerts at this time. System is healthy!</p>
            </div>
        `;
        updateNotifBadge(0);
        return;
    }
    
    alertsList.innerHTML = '';
    allAlerts.forEach(alert => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `notif-item ${alert.type || alert.alert_type || 'info'}`;
        alertDiv.innerHTML = `
            <strong>${alert.title || 'Alert'}</strong>
            <p>${alert.message}</p>
            <small>${new Date(alert.timestamp).toLocaleTimeString()}</small>
        `;
        alertsList.appendChild(alertDiv);
    });

    updateNotifBadge(allAlerts.length);
}

function updateNotifBadge(count) {
    const badge = document.getElementById('notifBadge');
    if (!badge) return;
    
    if (count > 0) {
        badge.textContent = count > 9 ? '9+' : count;
        badge.style.display = 'flex';
    } else {
        badge.style.display = 'none';
    }
}

// System Actions
async function boostRAM() {
    try {
        showToast('Boosting RAM...', 'info');
        const result = await apiCall('/api/boost-ram', { method: 'POST' });
        if (result && result.success) {
            showToast(`RAM Boosted! Freed ${result.freed_percent}% memory`, 'success');
            addLifeBoost(0.1); // ~3 days
            loadDashboard();
        }
    } catch (error) {
        showToast('Error boosting RAM: ' + error.message, 'error');
    }
}

async function cleanJunkFiles() {
    try {
        showToast('Scanning for junk files...', 'info');
        const scanResult = await apiCall('/api/junk-files/scan');
        if (scanResult && scanResult.success) {
            if (confirm(`Found ${scanResult.total_size_mb} MB of junk files. Clean them?`)) {
                showToast('Cleaning junk files...', 'info');
                const cleanResult = await apiCall('/api/junk-files/clean', { method: 'POST' });
                    if (cleanResult && cleanResult.success) {
                        showToast(`Cleaned ${cleanResult.cleaned_files} files, freed ${cleanResult.freed_size_mb} MB`, 'success');
                        addLifeBoost(0.2); // ~6 days
                        loadDashboard();
                    }
            }
        }
    } catch (error) {
        showToast('Error cleaning junk files: ' + error.message, 'error');
    }
}

async function autoOptimize() {
    try {
        showToast('Starting auto-optimization...', 'info');
        const result = await apiCall('/api/ai/auto-optimize', { method: 'POST' });
        if (result && result.success) {
            showToast('Auto-optimization completed!', 'success');
            addLifeBoost(0.4); // ~12 days
            loadDashboard();
        }
    } catch (error) {
        showToast('Error optimizing: ' + error.message, 'error');
    }
}

// AI Brain
async function getAIPrediction() {
    try {
        showToast('Analyzing system health...', 'info');
        const result = await apiCall('/api/ai/predict');
        if (result && result.success) {
            const prediction = result.prediction;
            
            const riskValueEl = document.getElementById('riskValue');
            if (riskValueEl) riskValueEl.textContent = `${(prediction.risk_score * 100).toFixed(0)}%`;
            const riskLevelEl = document.getElementById('riskLevel');
            if (riskLevelEl) riskLevelEl.textContent = prediction.risk_level.toUpperCase();
            const riskExpEl = document.getElementById('riskExplanation');
            if (riskExpEl) riskExpEl.innerHTML = `<p>${prediction.explanation}</p>`;
            
            const riskProgress = document.getElementById('riskProgress');
            if (riskProgress) {
                const circumference = 2 * Math.PI * 90;
                const offset = circumference - (prediction.risk_score * circumference);
                riskProgress.style.strokeDashoffset = offset;
                
                if (prediction.risk_level === 'high') riskProgress.style.stroke = '#ff0000';
                else if (prediction.risk_level === 'medium') riskProgress.style.stroke = '#ffa500';
                else riskProgress.style.stroke = '#00ffff';
            }
            
            const recList = document.getElementById('recommendationsList');
            const recCount = document.getElementById('recCount');
            if (recList) {
                recList.innerHTML = '';
                if (prediction.recommendations && prediction.recommendations.length > 0) {
                    prediction.recommendations.forEach((rec, index) => {
                        const li = document.createElement('div');
                        li.className = 'recommendation-item';
                        li.innerHTML = `<strong>${index + 1}.</strong> ${rec}`;
                        recList.appendChild(li);
                    });
                    if (recCount) recCount.textContent = prediction.recommendations.length;
                } else {
                    recList.innerHTML = '<div class="recommendation-placeholder"><span>💡</span><p>No recommendations</p></div>';
                    if (recCount) recCount.textContent = '0';
                }
            }
            showToast('System health analysis complete', 'success');
        }
    } catch (error) {
        showToast('Error getting prediction: ' + error.message, 'error');
    }
}

async function triggerAutoOptimize() {
    try {
        showToast('Starting AI optimization...', 'info');
        const result = await apiCall('/api/ai/auto-optimize', { method: 'POST' });
        if (result && result.success) {
            showToast('AI optimization completed!', 'success');
            getAIPrediction();
        }
    } catch (error) {
        showToast('Error optimizing: ' + error.message, 'error');
    }
}

async function generatePDFReport() {
    try {
        showToast('Generating PDF report...', 'info');
        const response = await fetch(`${API_BASE}/api/ai/report`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'autosense_report.pdf';
            a.click();
            showToast('PDF report generated!', 'success');
        } else {
            showToast('Error generating report', 'error');
        }
    } catch (error) {
        showToast('Error generating report: ' + error.message, 'error');
    }
}

// Disk Map
async function loadDiskMap() {
    const drive = document.getElementById('driveSelect').value;
    const depth = document.getElementById('depthSlider').value;

    if (!authToken) {
        showToast("Please login to access Disk Map", "error");
        return;
    }

    const container = document.getElementById('treemapContainer');
    const diskInfo = document.getElementById('diskInfo');

    try {
        if (container) {
            container.innerHTML = `
                <div class="treemap-loading">
                    <div class="loading-spinner"></div>
                    <p style="margin-top: 1rem;">Scanning ${drive}... <br> <small style="color: var(--text-muted)">This may take 10-20 seconds for large drives.</small></p>
                </div>
            `;
        }
        
        showToast('Scanning disk...', 'info');
        
        // Use apiCall for consistency and automatic token injection
        const result = await apiCall(`/api/disk-map?drive=${drive}&max_depth=${depth}`, {
            signal: AbortSignal.timeout(60000)
        });

        if (!result) {
            throw new Error("Unable to connect to server");
        }

        if (result.success) {
            // Update Premium Storage Dashboard
            document.getElementById('activeDrive').textContent = result.drive;
            document.getElementById('storageUsedText').textContent = `${formatBytes(result.used_size)} Used`;
            document.getElementById('storageTotalText').textContent = `${formatBytes(result.total_size)} Total`;
            document.getElementById('storageFreeText').textContent = formatBytes(result.free_size);
            
            const usedPercent = (result.used_size / result.total_size) * 100;
            const progressBar = document.getElementById('storageProgressBar');
            if (progressBar) {
                progressBar.style.width = `${usedPercent}%`;
                // Change color based on usage
                if (usedPercent > 90) progressBar.style.background = 'linear-gradient(90deg, #ff4e50, #f9d423)';
                else if (usedPercent > 70) progressBar.style.background = 'linear-gradient(90deg, #f7971e, #ffd200)';
                else progressBar.style.background = 'linear-gradient(90deg, #00d2ff, #3a7bd5)';
            }
            
            if (result.treemap && result.treemap.children && result.treemap.children.length > 0) {
                renderDiskTreemap(result.treemap);
                showToast('Disk map loaded', 'success');
            } else {
                if (container) {
                    container.innerHTML = `<div class="treemap-placeholder"><span>⚠️</span><p>No accessible folders found in ${drive}. <br> <small>Try a different drive or check permissions.</small></p></div>`;
                }
            }
        } else {
            showToast('Error: ' + (result.error || 'Unknown error'), 'error');
            if (container) {
                container.innerHTML = `<div class="treemap-placeholder"><span>❌</span><p>${result.error || 'Failed to load disk map'}</p></div>`;
            }
        }
    } catch (error) {
        console.error("Disk Map Failure:", error);
        if (error.name === 'TimeoutError') {
            showToast('Scan timed out. Try a lower depth.', 'warning');
        } else {
            showToast('Disk map error: ' + error.message, 'error');
        }
        if (container) {
            container.innerHTML = `<div class="treemap-placeholder"><span>❌</span><p>Scan failed: ${error.message}</p></div>`;
        }
    }
}

function renderDiskTreemap(data) {
    const container = document.getElementById('treemapContainer');
    if (!container) return;
    
    container.innerHTML = '';
    const width = Math.max(container.offsetWidth || 0, 800);
    const height = 450;

    try {
        if (data.children) {
            data.children = data.children.filter(c => c.size > 0);
        }

        const root = d3.hierarchy(data)
            .sum(d => Math.max(d.size, 1))
            .sort((a, b) => b.value - a.value);

        d3.treemap()
            .size([width, height])
            .paddingOuter(4)
            .paddingInner(2)
            .round(true)
            (root);

        const svg = d3.select(container)
            .append('svg')
            .attr('viewBox', `0 0 ${width} ${height}`)
            .attr('width', '100%')
            .attr('height', height)
            .style('border-radius', '16px');

        const defs = svg.append('defs');
        
        // Define gradients (optimized)
        const gradients = [
            { id: 'grad-blue', colors: ['#00d2ff', '#3a7bd5'] },
            { id: 'grad-purple', colors: ['#8e2de2', '#4a00e0'] },
            { id: 'grad-teal', colors: ['#00f2fe', '#4facfe'] }
        ];

        gradients.forEach(g => {
            const grad = defs.append('linearGradient').attr('id', g.id).attr('x1', '0%').attr('y1', '0%').attr('x2', '100%').attr('y2', '100%');
            grad.append('stop').attr('offset', '0%').attr('stop-color', g.colors[0]);
            grad.append('stop').attr('offset', '100%').attr('stop-color', g.colors[1]);
        });

        const grads = ['url(#grad-blue)', 'url(#grad-purple)', 'url(#grad-teal)'];
        const tooltip = document.getElementById('treemapTooltip');
        
        let requestId = null;
        let mouseX = 0, mouseY = 0;

        const updateTooltip = () => {
            if (tooltip && tooltip.style.display === 'block') {
                tooltip.style.transform = `translate3d(${mouseX + 20}px, ${mouseY + 20}px, 0)`;
                requestId = requestAnimationFrame(updateTooltip);
            }
        };

        const nodes = svg.selectAll('g')
            .data(root.leaves())
            .enter().append('g')
            .attr('class', 'treemap-node')
            .attr('transform', d => `translate(${d.x0},${d.y0})`);

        nodes.append('rect')
            .attr('width', d => Math.max(0, d.x1 - d.x0))
            .attr('height', d => Math.max(0, d.y1 - d.y0))
            .attr('fill', (d, i) => grads[i % grads.length])
            .attr('rx', 6)
            .attr('ry', 6)
            .style('opacity', 0.8)
            .on('mouseenter', function(event, d) {
                d3.select(this).style('opacity', 1).style('stroke', '#00ffff');
                if (tooltip) {
                    tooltip.innerHTML = `
                        <div style="font-weight: 800; color: #00ffff; font-family: 'Orbitron';">${d.data.name}</div>
                        <div style="font-size: 1.1rem; font-weight: 700;">${formatBytes(d.data.size)}</div>
                    `;
                    tooltip.style.display = 'block';
                    cancelAnimationFrame(requestId);
                    requestId = requestAnimationFrame(updateTooltip);
                }
            })
            .on('mousemove', function(event) {
                mouseX = event.clientX;
                mouseY = event.clientY;
            })
            .on('mouseleave', function() {
                d3.select(this).style('opacity', 0.8).style('stroke', 'rgba(255,255,255,0.1)');
                if (tooltip) {
                    tooltip.style.display = 'none';
                    cancelAnimationFrame(requestId);
                }
            });

        // Visible labels for larger blocks
        nodes.append('text')
            .attr('class', 'treemap-label')
            .attr('x', 8)
            .attr('y', 8)
            .text(d => {
                const w = d.x1 - d.x0;
                const h = d.y1 - d.y0;
                // Only show if block is big enough for text
                return (w > 40 && h > 20) ? d.data.name : '';
            })
            .style('font-size', d => {
                const size = Math.min(14, (d.x1 - d.x0) / 8);
                return Math.max(9, size) + 'px';
            });

    } catch (e) {
        console.error("Treemap Error:", e);
    }
}


function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Apps
async function loadApps() {
    try {
        showToast('Loading applications...', 'info');
        const result = await apiCall('/api/apps');
        if (result && result.success) {
            displayApps(result.apps);
            showToast(`Loaded ${result.count} applications`, 'success');
        }
    } catch (error) {
        showToast('Error loading apps: ' + error.message, 'error');
    }
}

function displayApps(apps) {
    const appsList = document.getElementById('appsList');
    if (!appsList) return;
    
    appsList.innerHTML = '';
    if (apps.length === 0) {
        appsList.innerHTML = '<div class="apps-placeholder"><span>📦</span><p>No applications found</p></div>';
        return;
    }
    
    apps.forEach(app => {
        const appItem = document.createElement('div');
        appItem.className = 'app-item';
        appItem.innerHTML = `
            <div>
                <strong>${app.name}</strong><br>
                <small style="color: var(--text-secondary);">${app.publisher} | ${app.version}</small>
            </div>
            <div>
                <button class="btn-neon" onclick="uninstallApp('${app.name.replace(/'/g, "\\'")}')" style="padding: 0.5rem 1rem; font-size: 0.9rem;">Uninstall</button>
            </div>
        `;
        appsList.appendChild(appItem);
    });
}

function filterApps() {
    const search = document.getElementById('appSearch').value.toLowerCase();
    document.querySelectorAll('.app-item').forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(search) ? 'flex' : 'none';
    });
}

async function uninstallApp(appName) {
    if (confirm(`Are you sure you want to uninstall ${appName}?`)) {
        try {
            showToast('Starting uninstall...', 'info');
            const result = await apiCall(`/api/apps/${encodeURIComponent(appName)}/remove`, { method: 'POST' });
            if (result && result.success) {
                showToast('Uninstall process started', 'success');
                loadApps();
            }
        } catch (error) {
            showToast('Error uninstalling app: ' + error.message, 'error');
        }
    }
}

// Security
async function checkFirewall() {
    try {
        showToast('Checking firewall...', 'info');
        const result = await apiCall('/api/security/firewall');
        if (result && result.success) {
            const statusDiv = document.getElementById('firewallStatus');
            if (statusDiv) {
                statusDiv.innerHTML = `
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">${result.firewall.enabled ? '✅' : '❌'}</div>
                        <strong style="color: ${result.firewall.enabled ? '#00ff88' : '#ff0000'};">
                            ${result.firewall.enabled ? 'ENABLED' : 'DISABLED'}
                        </strong>
                    </div>
                `;
            }
            showToast('Firewall check complete', 'success');
        }
    } catch (error) {
        showToast('Error checking firewall: ' + error.message, 'error');
    }
}

async function scanPorts() {
    try {
        showToast('Scanning ports...', 'info');
        const result = await apiCall('/api/security/ports');
        if (result && result.success) {
            const portsList = document.getElementById('openPortsList');
            if (portsList) {
                portsList.innerHTML = '';
                if (result.open_ports.length === 0) {
                    portsList.innerHTML = '<div class="status-placeholder">No open ports found</div>';
                } else {
                    result.open_ports.slice(0, 20).forEach(port => {
                        const portItem = document.createElement('div');
                        portItem.style.cssText = 'padding: 0.75rem; margin: 0.5rem 0; background: var(--glass-bg); border-radius: 8px;';
                        portItem.innerHTML = `
                            <strong>Port ${port.port}</strong> (${port.protocol})<br>
                            <small style="color: var(--text-secondary);">${port.process ? port.process.name : 'Unknown process'}</small>
                        `;
                        portsList.appendChild(portItem);
                    });
                }
            }
            showToast(`Found ${result.count} open ports`, 'success');
        }
    } catch (error) {
        showToast('Error scanning ports: ' + error.message, 'error');
    }
}

async function runMalwareScan() {
    try {
        showToast('Running malware scan...', 'info');
        const result = await apiCall('/api/security/scan', { method: 'POST' });
        if (result && result.success) {
            const resultsDiv = document.getElementById('malwareScanResults');
            if (resultsDiv) {
                const riskColor = result.risk_level === 'high' ? '#ff0000' : result.risk_level === 'medium' ? '#ffa500' : '#00ff88';
                resultsDiv.innerHTML = `
                    <div style="text-align: center; padding: 1rem;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">${result.risk_level === 'high' ? '🔴' : result.risk_level === 'medium' ? '🟡' : '🟢'}</div>
                        <strong style="color: ${riskColor}; font-size: 1.2rem;">${result.risk_level.toUpperCase()}</strong>
                        <p style="margin-top: 0.5rem; color: var(--text-secondary);">Risk Score: ${(result.risk_score * 100).toFixed(0)}%</p>
                        <p style="color: var(--text-secondary);">Threats: ${result.total_threats}</p>
                        <p style="margin-top: 1rem; font-size: 0.9rem; color: var(--text-muted);">${result.recommendation}</p>
                    </div>
                `;
            }
            showToast('Malware scan complete', 'success');
        }
    } catch (error) {
        showToast('Error running scan: ' + error.message, 'error');
    }
}

// Voice Assistant
function activateVoiceAssistant() {
    const recognition = window.webkitSpeechRecognition || window.SpeechRecognition;
    if (!recognition) {
        showToast('Speech recognition not supported', 'warning');
        return;
    }
    showToast('Voice assistant activated. Say "Hey AutoSense boost system"', 'info');
}

// Health Life Saver Logic
function updateHealthSaver() {
    const cpuEl = document.getElementById('cpuPercent');
    const memEl = document.getElementById('memoryPercent');
    const diskEl = document.getElementById('diskPercent');
    if (!cpuEl || !memEl) return;

    const cpuUsage = parseInt(cpuEl.innerText) || 50;
    const ramUsage = parseInt(memEl.innerText) || 50;
    const diskUsage = parseInt(diskEl?.innerText || '50');
    const diskHealth = 100 - diskUsage;
    
    let baseLife = 5.0; // Baseline 5 years
    
    // Toned down factors (max ~0.5 years total bonus from usage)
    let cpuFactor  = cpuUsage < 30 ? 0.2 : cpuUsage < 60 ? 0.1 : -0.2;
    let ramFactor  = ramUsage < 40 ? 0.15 : ramUsage < 70 ? 0.05 : -0.15;
    let diskFactor = diskHealth > 85 ? 0.15 : diskHealth > 70 ? 0.05 : -0.2;

    let totalLife = baseLife + cpuFactor + ramFactor + diskFactor;
    
    // Add optimization history boost (stored in months, e.g. 0.1 months = ~3 days)
    const savedMonths = parseFloat(localStorage.getItem('lifeSavedMonths') || 0);
    totalLife += (savedMonths / 12);

    const lifeSavedCalculated = Math.max(0, totalLife - baseLife);

    const projLifeEl = document.getElementById('projectedLife');
    const lifeSavedEl = document.getElementById('lifeSaved');
    const healthScoreEl = document.getElementById('currentHealthScore');

    if (projLifeEl) projLifeEl.innerText = totalLife.toFixed(1) + " Years";
    
    if (lifeSavedEl) {
        const totalSavedMonths = lifeSavedCalculated * 12;
        if (totalSavedMonths < 1) {
            // Show days if less than a month
            const days = Math.round(totalSavedMonths * 30.44);
            lifeSavedEl.innerText = "+" + days + " Days";
        } else {
            // Show months with one decimal for precision
            lifeSavedEl.innerText = "+" + totalSavedMonths.toFixed(1) + " Months";
        }
    }
    
    let score = 100 - (cpuUsage * 0.2) - (ramUsage * 0.2);
    score = Math.max(0, Math.min(100, score));
    if (healthScoreEl) healthScoreEl.innerText = Math.round(score) + "%";
}

function addLifeBoost(months) {
    let saved = parseFloat(localStorage.getItem('lifeSavedMonths') || 0);
    saved += months;
    localStorage.setItem('lifeSavedMonths', saved);
    updateHealthSaver();
    
    let displayValue = months < 1 ? Math.round(months * 30.44) + " days" : months + " month(s)";
    showToast(`Device health improved! +${displayValue} added to lifespan via AI optimization.`, 'success');
}

// Make functions globally accessible
window.uninstallApp = uninstallApp;
