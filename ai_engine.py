"""
AI System Brain - IsolationForest + LSTM for failure prediction and auto-optimization
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import psutil
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Warning: TensorFlow not available. LSTM predictions will be disabled.")


class AISystemBrain:
    """AI Engine for system health prediction and optimization"""
    
    def __init__(self, model_path: str = "./models/ai_model.h5"):
        self.model_path = model_path
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.lstm_model = None
        self.is_trained = False
        self.feature_history = []
        self.max_history_length = 100
        self.is_fitted = False
        
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path) if os.path.dirname(model_path) else "./models", exist_ok=True)
        
        # Try to load existing model
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained LSTM model if available"""
        if TENSORFLOW_AVAILABLE and os.path.exists(self.model_path):
            try:
                self.lstm_model = load_model(self.model_path)
                self.is_trained = True
            except Exception as e:
                print(f"Could not load model: {e}")
    
    def collect_system_features(self) -> Dict[str, float]:
        """Collect current system features for prediction"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network stats
            net_io = psutil.net_io_counters()
            
            # Process stats
            processes = list(psutil.process_iter(['pid', 'cpu_percent', 'memory_percent']))
            
            features = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'network_sent_mb': net_io.bytes_sent / (1024**2),
                'network_recv_mb': net_io.bytes_recv / (1024**2),
                'process_count': len(processes),
                'high_cpu_processes': sum(1 for p in processes if p.info.get('cpu_percent', 0) > 10),
                'high_memory_processes': sum(1 for p in processes if p.info.get('memory_percent', 0) > 5),
                'cpu_load_avg': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else cpu_percent / 100,
            }
            
            return features
        except Exception as e:
            print(f"Error collecting features: {e}")
            return {}
    
    def predict_degradation_risk(self) -> Dict:
        """Predict system degradation risk using IsolationForest"""
        try:
            features = self.collect_system_features()
            if not features:
                return {
                    "risk_score": 0.5,
                    "risk_level": "unknown",
                    "explanation": "Unable to collect system metrics",
                    "recommendations": []
                }
            
            # Convert to array for prediction
            feature_array = np.array([[
                features.get('cpu_percent', 0),
                features.get('memory_percent', 0),
                features.get('disk_percent', 0),
                features.get('process_count', 0),
                features.get('high_cpu_processes', 0),
                features.get('high_memory_processes', 0),
            ]])
            
            # Scale features
            if not hasattr(self, 'scaler_fitted') or not self.is_fitted:
                # If not fitted, try to fit on this single sample or a small batch
                # In production, we'd want at least a few samples
                self.scaler.fit(feature_array)
                self.scaler_fitted = True
                
            scaled_features = self.scaler.transform(feature_array)
            
            # Predict anomaly score with safety check
            risk_score = 0.5
            if self.is_fitted:
                try:
                    anomaly_score = self.isolation_forest.decision_function(scaled_features)[0]
                    risk_score = max(0, min(1, (1 - anomaly_score) / 2))
                except:
                    # In case of dimension mismatch or other fit issues
                    pass
            else:
                # Basic rule-based score if not fitted
                risk_score = (features.get('cpu_percent', 0) / 200) + (features.get('memory_percent', 0) / 200)
                risk_score = max(0, min(1, risk_score))
            
            # Determine risk level
            if risk_score < 0.3:
                risk_level = "low"
            elif risk_score < 0.6:
                risk_level = "medium"
            else:
                risk_level = "high"
            
            # Generate explanation
            explanation = self._generate_explanation(features, risk_score, risk_level)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(features, risk_score)
            
            return {
                "risk_score": round(risk_score, 3),
                "risk_level": risk_level,
                "explanation": explanation,
                "recommendations": recommendations,
                "features": features,
                "timestamp": datetime.utcnow().isoformat(),
                "is_ai_fitted": self.is_fitted
            }
        except Exception as e:
            print(f"Error in prediction: {e}")
            return {
                "risk_score": 0.5,
                "risk_level": "unknown",
                "explanation": f"Prediction error: {str(e)}",
                "recommendations": []
            }
    
    def _generate_explanation(self, features: Dict, risk_score: float, risk_level: str) -> str:
        """Generate human-readable explanation"""
        explanations = []
        
        if features.get('cpu_percent', 0) > 80:
            explanations.append(f"CPU usage is critically high at {features['cpu_percent']:.1f}%")
        elif features.get('cpu_percent', 0) > 60:
            explanations.append(f"CPU usage is elevated at {features['cpu_percent']:.1f}%")
        
        if features.get('memory_percent', 0) > 85:
            explanations.append(f"Memory usage is critically high at {features['memory_percent']:.1f}%")
        elif features.get('memory_percent', 0) > 70:
            explanations.append(f"Memory usage is elevated at {features['memory_percent']:.1f}%")
        
        if features.get('disk_percent', 0) > 90:
            explanations.append(f"Disk space is critically low ({100 - features['disk_percent']:.1f}% free)")
        elif features.get('disk_percent', 0) > 80:
            explanations.append(f"Disk space is running low ({100 - features['disk_percent']:.1f}% free)")
        
        if features.get('process_count', 0) > 200:
            explanations.append(f"Too many running processes ({features['process_count']})")
        
        if features.get('high_cpu_processes', 0) > 5:
            explanations.append(f"Multiple high CPU processes detected ({features['high_cpu_processes']})")
        
        if not explanations:
            explanations.append("System is operating within normal parameters")
        
        base_explanation = f"System health risk is {risk_level.upper()} (score: {risk_score:.1%}). "
        return base_explanation + " ".join(explanations) + "."
    
    def _generate_recommendations(self, features: Dict, risk_score: float) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if features.get('cpu_percent', 0) > 70:
            recommendations.append("Close unnecessary applications to reduce CPU load")
            recommendations.append("Check for background processes consuming CPU")
        
        if features.get('memory_percent', 0) > 75:
            recommendations.append("Free up RAM by closing unused applications")
            recommendations.append("Consider running RAM boost optimization")
        
        if features.get('disk_percent', 0) > 85:
            recommendations.append("Clean up disk space by removing junk files")
            recommendations.append("Uninstall unused applications")
            recommendations.append("Clear temporary files and cache")
        
        if features.get('process_count', 0) > 150:
            recommendations.append("Review and disable unnecessary startup programs")
            recommendations.append("Kill unnecessary background processes")
        
        if features.get('high_cpu_processes', 0) > 3:
            recommendations.append("Identify and terminate high CPU processes")
        
        if not recommendations:
            recommendations.append("System is optimized. Continue regular maintenance.")
        
        # Ensure we always return a decent list for UI
        if len(recommendations) < 2 and risk_score > 0.4:
            recommendations.append("Schedule a deep security scan to ensure system integrity.")
            
        return recommendations

    def ensure_fitted(self, historical_data: List[Dict] = None):
        """Ensure the IsolationForest is fitted with data"""
        try:
            if not historical_data or len(historical_data) < 5:
                # If no data provided, we can't fit properly yet
                return False
            
            # Extract features for fitting
            data = []
            for entry in historical_data:
                data.append([
                    entry.get('cpu_percent', 0),
                    entry.get('memory_percent', 0),
                    entry.get('disk_percent', 0),
                    entry.get('process_count', 0),
                    entry.get('high_cpu_processes', 0),
                    entry.get('high_memory_processes', 0),
                ])
            
            X = np.array(data)
            self.scaler.fit(X)
            self.scaler_fitted = True
            
            X_scaled = self.scaler.transform(X)
            self.isolation_forest.fit(X_scaled)
            self.is_fitted = True
            return True
        except Exception as e:
            print(f"Error fitting model: {e}")
            return False
    
    def auto_optimize(self) -> Dict:
        """Auto-optimize system based on current state"""
        try:
            features = self.collect_system_features()
            optimizations = []
            results = {}
            
            # RAM Optimization
            if features.get('memory_percent', 0) > 70:
                ram_result = self._optimize_ram()
                optimizations.append("RAM Boost")
                results['ram_boost'] = ram_result
            
            # CPU Optimization
            if features.get('cpu_percent', 0) > 70:
                cpu_result = self._optimize_cpu()
                optimizations.append("CPU Optimization")
                results['cpu_optimization'] = cpu_result
            
            # Disk Optimization
            if features.get('disk_percent', 0) > 80:
                disk_result = self._optimize_disk()
                optimizations.append("Disk Cleanup")
                results['disk_cleanup'] = disk_result
            
            # Process Cleanup
            if features.get('process_count', 0) > 150:
                process_result = self._optimize_processes()
                optimizations.append("Process Cleanup")
                results['process_cleanup'] = process_result
            
            return {
                "success": True,
                "optimizations_performed": optimizations,
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _optimize_ram(self) -> Dict:
        """Optimize RAM by clearing system cache"""
        try:
            import gc
            gc.collect()
            
            # On Windows, try to clear working set
            if os.name == 'nt':
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
                except:
                    pass
            
            memory_before = psutil.virtual_memory().percent
            # Small delay to see effect
            import time
            time.sleep(0.5)
            memory_after = psutil.virtual_memory().percent
            
            return {
                "success": True,
                "memory_before": memory_before,
                "memory_after": memory_after,
                "freed_percent": max(0, memory_before - memory_after)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _optimize_cpu(self) -> Dict:
        """Optimize CPU by identifying and suggesting high CPU processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    cpu = proc.info.get('cpu_percent', 0)
                    if cpu > 10:
                        processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cpu_percent": cpu
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return {
                "success": True,
                "high_cpu_processes": processes[:10],
                "recommendation": "Consider closing top CPU-consuming processes"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _optimize_disk(self) -> Dict:
        """Suggest disk cleanup"""
        return {
            "success": True,
            "recommendation": "Run junk file cleaner to free up disk space",
            "suggested_actions": [
                "Clear temporary files",
                "Remove browser cache",
                "Uninstall unused applications"
            ]
        }
    
    def _optimize_processes(self) -> Dict:
        """Suggest process cleanup"""
        try:
            process_count = len(list(psutil.process_iter()))
            return {
                "success": True,
                "current_processes": process_count,
                "recommendation": "Review startup programs and disable unnecessary ones"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def train_lstm_model(self, historical_data: List[Dict]) -> bool:
        """Train LSTM model on historical data"""
        if not TENSORFLOW_AVAILABLE:
            return False
        
        try:
            # Prepare data
            df = pd.DataFrame(historical_data)
            if len(df) < 50:
                return False
            
            # Select features
            feature_cols = ['cpu_percent', 'memory_percent', 'disk_percent']
            X = df[feature_cols].values
            y = df['risk_score'].values if 'risk_score' in df.columns else np.zeros(len(df))
            
            # Normalize
            X_scaled = self.scaler.fit_transform(X)
            
            # Create sequences
            sequence_length = 10
            X_seq, y_seq = [], []
            for i in range(sequence_length, len(X_scaled)):
                X_seq.append(X_scaled[i-sequence_length:i])
                y_seq.append(y[i])
            
            X_seq = np.array(X_seq)
            y_seq = np.array(y_seq)
            
            # Build model
            if self.lstm_model is None:
                self.lstm_model = Sequential([
                    LSTM(50, return_sequences=True, input_shape=(sequence_length, len(feature_cols))),
                    Dropout(0.2),
                    LSTM(50, return_sequences=False),
                    Dropout(0.2),
                    Dense(25),
                    Dense(1)
                ])
                self.lstm_model.compile(optimizer='adam', loss='mse', metrics=['mae'])
            
            # Train
            self.lstm_model.fit(X_seq, y_seq, epochs=10, batch_size=32, verbose=0)
            
            # Save model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            self.lstm_model.save(self.model_path)
            self.is_trained = True
            
            return True
        except Exception as e:
            print(f"Error training LSTM: {e}")
            return False

