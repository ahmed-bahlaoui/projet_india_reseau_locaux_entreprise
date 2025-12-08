import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
import time
import os

print("="*70)
print("   🤖 AI NETWORK ANOMALY DETECTION SYSTEM")
print("="*70)
print()

# ============================================================================
# CONFIGURATION
# ============================================================================

CSV_FILE = "../data/logs.csv"
CHECK_INTERVAL = 5  # seconds

# Define which devices can access servers
IT_DEVICES = [
    "PC_IT", "IT_PC", "VLAN_IT", "Switch_IT", 
    "192.168.10", "IT_Department"
]

SERVERS = [
    "Server", "DMZ", "10.10.100",
    "Server_PT", "Gig0"
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_it_device(device_name):
    """Check if device is from IT department"""
    device_name = str(device_name).strip()
    return any(it_keyword in device_name for it_keyword in IT_DEVICES)

def is_server(device_name):
    """Check if device is a server"""
    device_name = str(device_name).strip()
    return any(server_keyword in device_name for server_keyword in SERVERS)

def load_logs():
    """Load CSV logs with error handling"""
    try:
        if not os.path.exists(CSV_FILE):
            print(f"⚠️  Warning: {CSV_FILE} not found.")
            return pd.DataFrame()
        
        df = pd.read_csv(CSV_FILE)
        df.columns = df.columns.str.strip()
        
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.strip()
        
        return df
    
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return pd.DataFrame()

# ============================================================================
# ANOMALY DETECTION - RULE-BASED
# ============================================================================

def detect_rule_based_anomalies(df):
    """Detect anomalies using business rules"""
    anomalies = []
    
    if df.empty:
        return anomalies
    
    for idx, row in df.iterrows():
        source = str(row['source'])
        destination = str(row['destination'])
        action = str(row['action'])
        packets = int(row['packets']) if pd.notna(row['packets']) else 0
        timestamp = row['timestamp']
        
        # ANOMALY 1: Non-IT device accessing servers ⚠️ PRIMARY RULE
        if is_server(destination) and not is_it_device(source):
            anomalies.append({
                'timestamp': timestamp,
                'type': 'UNAUTHORIZED SERVER ACCESS',
                'source': source,
                'destination': destination,
                'action': action,
                'severity': 'HIGH',
                'description': f"{source} (non-IT) attempted to access {destination}"
            })
        
        # ANOMALY 2: Traffic loop
        elif source == destination:
            anomalies.append({
                'timestamp': timestamp,
                'type': 'TRAFFIC LOOP',
                'source': source,
                'destination': destination,
                'action': action,
                'severity': 'MEDIUM',
                'description': f"Traffic loop detected on {source}"
            })
        
        # ANOMALY 3: High packet count
        elif packets > 500:
            anomalies.append({
                'timestamp': timestamp,
                'type': 'HIGH TRAFFIC VOLUME',
                'source': source,
                'destination': destination,
                'action': action,
                'severity': 'MEDIUM',
                'description': f"Unusually high traffic: {packets} packets from {source}"
            })
    
    # ANOMALY 4: Brute force (repeated DENY)
    deny_counts = df[df['action'] == 'DENY'].groupby('source').size()
    for source, count in deny_counts.items():
        if count >= 5:
            anomalies.append({
                'timestamp': 'Multiple events',
                'type': 'BRUTE FORCE ATTACK',
                'source': source,
                'destination': 'Multiple targets',
                'action': 'DENY',
                'severity': 'HIGH',
                'description': f"{source} had {count} denied access attempts"
            })
    
    return anomalies

# ============================================================================
# ANOMALY DETECTION - AI/ML BASED
# ============================================================================

def train_ai_model(df):
    """Train Isolation Forest for anomaly detection"""
    if len(df) < 10:
        return None, None, None, None
    
    try:
        le_source = LabelEncoder()
        le_dest = LabelEncoder()
        le_action = LabelEncoder()
        
        sources = df['source'].fillna('Unknown').astype(str)
        destinations = df['destination'].fillna('Unknown').astype(str)
        actions = df['action'].fillna('Unknown').astype(str)
        
        source_encoded = le_source.fit_transform(sources)
        dest_encoded = le_dest.fit_transform(destinations)
        action_encoded = le_action.fit_transform(actions)
        packets = df['packets'].fillna(0).astype(float)
        
        X = np.column_stack([
            source_encoded,
            dest_encoded,
            action_encoded,
            packets
        ])
        
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X)
        
        return model, le_source, le_dest, le_action
    
    except Exception as e:
        return None, None, None, None

def detect_ai_anomalies(df, model, le_source, le_dest, le_action):
    """Use AI to detect statistical anomalies"""
    anomalies = []
    
    if model is None or df.empty:
        return anomalies
    
    try:
        sources = df['source'].fillna('Unknown').astype(str)
        destinations = df['destination'].fillna('Unknown').astype(str)
        actions = df['action'].fillna('Unknown').astype(str)
        packets = df['packets'].fillna(0).astype(float)
        
        source_encoded = []
        dest_encoded = []
        action_encoded = []
        
        for i in range(len(df)):
            try:
                source_encoded.append(le_source.transform([sources.iloc[i]])[0])
            except:
                source_encoded.append(-1)
            
            try:
                dest_encoded.append(le_dest.transform([destinations.iloc[i]])[0])
            except:
                dest_encoded.append(-1)
            
            try:
                action_encoded.append(le_action.transform([actions.iloc[i]])[0])
            except:
                action_encoded.append(-1)
        
        X = np.column_stack([
            source_encoded,
            dest_encoded,
            action_encoded,
            packets
        ])
        
        predictions = model.predict(X)
        
        for idx, pred in enumerate(predictions):
            if pred == -1:
                row = df.iloc[idx]
                anomalies.append({
                    'timestamp': row['timestamp'],
                    'type': 'AI STATISTICAL ANOMALY',
                    'source': row['source'],
                    'destination': row['destination'],
                    'action': row['action'],
                    'severity': 'MEDIUM',
                    'description': f"AI detected unusual pattern: {row['source']} → {row['destination']}"
                })
        
        return anomalies
    
    except Exception as e:
        return []

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_anomalies(anomalies):
    """Pretty print detected anomalies"""
    if not anomalies:
        print("✅ Everything OK - No anomalies detected")
        return
    
    print(f"⚠️  {len(anomalies)} ANOMALIES DETECTED:")
    print("-" * 70)
    
    for i, anom in enumerate(anomalies, 1):
        severity_icon = "🔴" if anom['severity'] == 'HIGH' else "🟡"
        print(f"\n{severity_icon} ANOMALY #{i}: {anom['type']}")
        print(f"   Time: {anom['timestamp']}")
        print(f"   Source: {anom['source']}")
        print(f"   Destination: {anom['destination']}")
        print(f"   Severity: {anom['severity']}")
        print(f"   Description: {anom['description']}")

# ============================================================================
# MAIN MONITORING LOOP
# ============================================================================

def monitor_network():
    """Main monitoring function - runs continuously every 5 seconds"""
    
    print(f"🔍 Starting anomaly detection...")
    print(f"📁 Watching file: {CSV_FILE}")
    print(f"⏱️  Check interval: {CHECK_INTERVAL} seconds")
    print(f"🛡️  IT Devices: {', '.join(IT_DEVICES[:3])}...")
    print(f"🖥️  Protected Servers: {', '.join(SERVERS[:3])}...")
    print()
    print("="*70)
    print()
    
    previous_row_count = 0
    
    while True:
        try:
            df = load_logs()
            
            if df.empty:
                print("⚠️  No data in CSV. Waiting...")
                time.sleep(CHECK_INTERVAL)
                continue
            
            current_row_count = len(df)
            
            # Only analyze if new data added
            if current_row_count > previous_row_count:
                print(f"📊 Analyzing {current_row_count} events (new: {current_row_count - previous_row_count})")
                print(f"⏰ Check time: {datetime.now().strftime('%H:%M:%S')}")
                print()
                
                # Train AI
                print("🤖 Training AI model...")
                model, le_source, le_dest, le_action = train_ai_model(df)
                if model:
                    print("✅ AI model ready")
                else:
                    print("⚠️  Need more data for AI (minimum 10 events)")
                print()
                
                # Detect anomalies
                rule_anomalies = detect_rule_based_anomalies(df)
                ai_anomalies = detect_ai_anomalies(df, model, le_source, le_dest, le_action)
                
                all_anomalies = rule_anomalies + ai_anomalies
                
                # Display
                display_anomalies(all_anomalies)
                
                print()
                print("="*70)
                print()
                
                previous_row_count = current_row_count
            else:
                print(f"⏳ No new events... (checked at {datetime.now().strftime('%H:%M:%S')})")
            
            time.sleep(CHECK_INTERVAL)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            break
        
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(CHECK_INTERVAL)

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    monitor_network()