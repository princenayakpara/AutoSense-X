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

    // Modal close on outside click
    document.getElementById('loginModal')?.addEventListener('click', (e) => {
        if (e.target.id === 'loginModal') closeLoginModal();
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
    
    alertsList.innerHTML = '';
    const allAlerts = [...(alertsData.stored_alerts || []), ...(alertsData.current_alerts || [])];
    
    if (allAlerts.length === 0) {
        alertsList.innerHTML = `
            <div class="alert-placeholder">
                <span>🔔</span>
                <p>No alerts at this time. System is healthy!</p>
            </div>
        `;
        return;
    }
    
    allAlerts.forEach(alert => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert ${alert.type || alert.alert_type || 'info'}`;
        alertDiv.innerHTML = `
            <div>
                <strong>${alert.title || 'Alert'}</strong>
                <p>${alert.message}</p>
                <small>${new Date(alert.timestamp).toLocaleTimeString()}</small>
            </div>
        `;
        alertsList.appendChild(alertDiv);
    });
}

// System Actions
async function boostRAM() {
    try {
        showToast('Boosting RAM...', 'info');
        const result = await apiCall('/api/boost-ram', { method: 'POST' });
        if (result && result.success) {
            showToast(`RAM Boosted! Freed ${result.freed_percent}% memory`, 'success');
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
            if (diskInfo) {
                diskInfo.innerHTML = `
                    <strong>${result.drive}</strong> |
                    Total: ${formatBytes(result.total_size)} |
                    Used: ${formatBytes(result.used_size)} |
                    Free: ${formatBytes(result.free_size)}
                `;
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
    
    // Clear previous content
    container.innerHTML = '';
    
    // Robust width calculation
    const width = Math.max(container.offsetWidth || 0, 800);
    const height = 450;

    try {
        if (!window.d3) {
            throw new Error("D3 library not loaded");
        }

        // Filter and sanitize data
        if (data.children) {
            data.children = data.children.filter(c => c.size > 0);
        }

        if (!data.children || data.children.length === 0) {
            container.innerHTML = `<div class="treemap-placeholder"><span>ℹ️</span><p>Storage data is too small to visualize.</p></div>`;
            return;
        }

        const root = d3.hierarchy(data)
            .sum(d => Math.max(d.size, 1)) // Ensure min size of 1 for D3 layout
            .sort((a, b) => b.value - a.value);

        d3.treemap()
            .size([width, height])
            .paddingOuter(4)
            .paddingInner(2)
            (root);

        const svg = d3.select(container)
            .append('svg')
            .attr('viewBox', `0 0 ${width} ${height}`)
            .attr('width', '100%')
            .attr('height', height)
            .style('overflow', 'visible')
            .style('border-radius', '12px');

        const color = d3.scaleOrdinal()
            .range(['#1a1f3d', '#232a5c', '#2c3580', '#3540a4', '#3e4bc8', '#4756ec', '#0066ff', '#0099ff']);

        const leaf = svg.selectAll('g')
            .data(root.leaves())
            .enter().append('g')
            .attr('transform', d => `translate(${d.x0},${d.y0})`);

        leaf.append('rect')
            .attr('width', d => Math.max(0, d.x1 - d.x0))
            .attr('height', d => Math.max(0, d.y1 - d.y0))
            .attr('fill', (d, i) => color(i))
            .attr('stroke', 'rgba(255,255,255,0.1)')
            .on('mouseover', function(event, d) {
                d3.select(this).attr('fill', '#00ffff');
                const tooltip = document.createElement('div');
                tooltip.id = 'treemap-tooltip';
                tooltip.className = 'glass-card';
                tooltip.style.cssText = 'position: fixed; background: rgba(10, 14, 39, 0.95); color: #fff; padding: 10px; border-radius: 8px; pointer-events: none; z-index: 9999; border: 1px solid var(--neon-cyan); box-shadow: 0 0 15px rgba(0, 255, 255, 0.3); font-size: 0.9rem;';
                tooltip.innerHTML = `<strong>${d.data.name}</strong><br>${formatBytes(d.data.size)}`;
                document.body.appendChild(tooltip);
                updateTooltipPos(event);
            })
            .on('mousemove', updateTooltipPos)
            .on('mouseout', function() {
                d3.select(this).attr('fill', (d, i) => color(i));
                const tooltip = document.getElementById('treemap-tooltip');
                if (tooltip) tooltip.remove();
            });

        leaf.append('text')
            .attr('x', 5)
            .attr('y', 20)
            .attr('fill', '#fff')
            .style('font-size', '11px')
            .style('font-weight', '500')
            .style('pointer-events', 'none')
            .text(d => (d.x1 - d.x0 > 60 && d.y1 - d.y0 > 30) ? d.data.name : '');

    } catch (err) {
        console.error("Treemap Render Error:", err);
        // Fallback to a simple list if D3 fails
        const listHtml = data.children ? data.children.slice(0, 10).map(c => `
            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <span>${c.name}</span>
                <span style="color: var(--neon-cyan)">${formatBytes(c.size)}</span>
            </div>
        `).join('') : '<p>No data</p>';
        
        container.innerHTML = `
            <div style="padding: 20px;">
                <h3 style="margin-bottom: 15px; color: var(--neon-cyan);">Top Folders (List Mode)</h3>
                ${listHtml}
                <p style="margin-top: 20px; font-size: 0.8rem; color: var(--text-muted);">Note: Visualization failed to initialize, using list fallback.</p>
            </div>
        `;
    }

    function updateTooltipPos(event) {
        const tooltip = document.getElementById('treemap-tooltip');
        if (tooltip) {
            tooltip.style.left = (event.clientX + 15) + 'px';
            tooltip.style.top = (event.clientY + 15) + 'px';
        }
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

// Make functions globally accessible
window.uninstallApp = uninstallApp;
