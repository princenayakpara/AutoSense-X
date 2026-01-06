
import os

css_path = r'c:\Users\prince_nayakpara\Desktop\Autosense-X\AutoSense-X\AutoSense-X\frontend\styles.css'
new_css_content = """
/* ============================================
   DEMO SCENE ANIMATIONS
   ============================================ */
.demo-scene {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
    overflow: hidden;
    background: #0a0e27;
}

/* --- SCENE 1: AI BRAIN --- */
.scene-ai-brain {
    background: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #0a0e27 80%);
}

.ai-node {
    position: absolute;
    width: 15px;
    height: 15px;
    background: var(--neon-cyan);
    border-radius: 50%;
    box-shadow: 0 0 20px var(--neon-cyan);
    animation: nodePulse 2s infinite ease-in-out;
}

.node-1 { top: 30%; left: 30%; animation-delay: 0s; }
.node-2 { top: 60%; left: 70%; animation-delay: 0.5s; width: 20px; height: 20px; }
.node-3 { top: 70%; left: 20%; animation-delay: 1s; }

.ai-connection {
    position: absolute;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--neon-cyan), transparent);
    animation: connectPulse 3s infinite linear;
    transform-origin: left center;
}

.conn-1 { top: 30%; left: 30%; width: 45%; transform: rotate(20deg); animation-delay: 0.2s; }
.conn-2 { top: 60%; left: 70%; width: 50%; transform: rotate(-170deg); animation-delay: 0.7s; }
.conn-3 { top: 70%; left: 20%; width: 60%; transform: rotate(-40deg); animation-delay: 1.2s; }

.ai-pulse-ring {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 300px;
    height: 300px;
    border: 2px solid rgba(0, 255, 255, 0.1);
    border-radius: 50%;
    animation: ringExpand 4s infinite linear;
}

@keyframes nodePulse {
    0%, 100% { transform: scale(1); opacity: 0.8; }
    50% { transform: scale(1.5); opacity: 1; box-shadow: 0 0 40px var(--neon-cyan); }
}

@keyframes connectPulse {
    0% { opacity: 0; transform: scaleX(0); }
    50% { opacity: 1; transform: scaleX(1); }
    100% { opacity: 0; transform: scaleX(0) translateX(50px); }
}

@keyframes ringExpand {
    0% { width: 0; height: 0; opacity: 1; }
    100% { width: 800px; height: 800px; opacity: 0; }
}

/* --- SCENE 2: RAM BOOST --- */
.scene-ram-boost {
    background: linear-gradient(135deg, #16213e 0%, #000 100%);
    display: flex;
    justify-content: center;
    align-items: center;
}

.boost-rocket {
    font-size: 100px;
    position: relative;
    z-index: 2;
    filter: drop-shadow(0 0 20px rgba(255, 100, 0, 0.6));
    animation: rocketShake 0.1s infinite;
}

.boost-circle {
    position: absolute;
    width: 200px;
    height: 200px;
    border: 10px solid rgba(255, 255, 255, 0.1);
    border-top-color: var(--neon-green);
    border-radius: 50%;
    animation: spinBoost 1s infinite linear;
}

.boost-speed-lines {
    position: absolute;
    width: 100%;
    height: 100%;
    background: repeating-linear-gradient(
        0deg,
        transparent 0,
        transparent 50px,
        rgba(255, 255, 255, 0.05) 50px,
        rgba(255, 255, 255, 0.05) 100px
    );
    animation: speedLines 0.5s infinite linear;
}

.boost-particle {
    position: absolute;
    width: 4px;
    height: 4px;
    background: #fff;
    border-radius: 50%;
    animation: particleFly 1s infinite linear;
}

.p1 { top: 20%; left: 0; animation-duration: 0.8s; }
.p2 { top: 80%; left: 20%; animation-duration: 1.2s; }
.p3 { top: 50%; left: -10%; animation-duration: 0.6s; }

@keyframes rocketShake {
    0%, 100% { transform: translateY(0) rotate(45deg); }
    50% { transform: translateY(2px) rotate(45deg); }
}

@keyframes spinBoost {
    to { transform: rotate(360deg); }
}

@keyframes speedLines {
    from { background-position: 0 0; }
    to { background-position: 0 200px; }
}

@keyframes particleFly {
    from { transform: translateX(-100px); opacity: 0; }
    50% { opacity: 1; }
    to { transform: translateX(120vw); opacity: 0; }
}

/* --- SCENE 3: DISK MAP --- */
.scene-disk-map {
    background: #1a1a2e;
    perspective: 1000px;
}

.disk-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 1fr);
    gap: 10px;
    width: 60%;
    height: 60%;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotateX(20deg);
}

.disk-block {
    background: rgba(0, 255, 255, 0.2);
    border: 1px solid var(--neon-cyan);
    transition: all 0.5s ease;
}

.disk-block:hover { background: var(--neon-cyan); }
.b1 { animation: blockPulse 3s infinite alternate; }
.b2 { animation: blockPulse 4s infinite alternate-reverse; background: rgba(255, 0, 255, 0.2); border-color: var(--neon-pink); }
.b3 { animation: blockPulse 2.5s infinite alternate; background: rgba(0, 255, 100, 0.2); border-color: var(--neon-green); }
.b4 { animation: blockPulse 3.5s infinite alternate-reverse; }

.disk-scanner-line {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 5px;
    background: var(--neon-cyan);
    box-shadow: 0 0 20px var(--neon-cyan);
    animation: scanDisk 3s infinite ease-in-out;
}

@keyframes blockPulse {
    0% { transform: scale(1); opacity: 0.5; }
    100% { transform: scale(0.95); opacity: 1; }
}

@keyframes scanDisk {
    0% { top: 0; opacity: 0; }
    20% { opacity: 1; }
    80% { opacity: 1; }
    100% { top: 100%; opacity: 0; }
}

/* --- SCENE 4: SECURITY --- */
.scene-security {
    background: radial-gradient(circle at 60% 40%, #001f3f 0%, #000 100%);
    display: flex;
    justify-content: center;
    align-items: center;
}

.radar-circle {
    position: absolute;
    border: 1px solid var(--neon-green);
    border-radius: 50%;
    box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
}

.c1 { width: 300px; height: 300px; opacity: 0.3; }
.c2 { width: 500px; height: 500px; opacity: 0.1; }

.radar-scanner {
    position: absolute;
    width: 300px;
    height: 300px;
    background: conic-gradient(from 0deg, transparent 80%, rgba(0, 255, 0, 0.5));
    border-radius: 50%;
    animation: radarSpin 4s infinite linear;
}

.radar-shield {
    font-size: 80px;
    position: relative;
    z-index: 2;
    filter: drop-shadow(0 0 20px var(--neon-green));
    animation: shieldBreath 2s infinite ease-in-out;
}

.radar-dot {
    position: absolute;
    width: 8px;
    height: 8px;
    background: red;
    border-radius: 50%;
    opacity: 0;
    animation: dotBlink 4s infinite;
}

.d1 { top: 35%; left: 60%; animation-delay: 1s; }
.d2 { top: 65%; left: 40%; animation-delay: 2.5s; }

@keyframes radarSpin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@keyframes shieldBreath {
    0%, 100% { transform: scale(1); filter: drop-shadow(0 0 20px var(--neon-green)); }
    50% { transform: scale(1.1); filter: drop-shadow(0 0 40px var(--neon-green)); }
}

@keyframes dotBlink {
    0% { opacity: 0; }
    20% { opacity: 1; transform: scale(1.5); }
    40% { opacity: 0; }
}
"""

try:
    with open(css_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    # Keep lines up to 3107 (0-indexed 3106)
    valid_lines = lines[:3148]
    
    with open(css_path, 'w', encoding='utf-8') as f:
        f.writelines(valid_lines)
        f.write(new_css_content)
        
    print("Successfully repaired styles.css")

except Exception as e:
    print(f"Error: {e}")
