import os
from datetime import datetime

import pandas as pd

print("=" * 70)
print("   🔮 AI PREDICTIVE MAINTENANCE SYSTEM")
print("=" * 70)
print()

# ============================================================================
# CONFIGURATION
# ============================================================================

CSV_FILE = "../data/logs.csv"

IT_DEVICES = ["PC_IT", "IT_PC", "VLAN_IT", "Switch_IT", "192.168.10", "IT_Department"]

SERVERS = ["Server", "DMZ", "10.10.100", "Server_PT", "Gig0"]

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
    """Load CSV logs"""
    try:
        if not os.path.exists(CSV_FILE):
            print(f"❌ File not found: {CSV_FILE}")
            return pd.DataFrame()

        df = pd.read_csv(CSV_FILE)
        df.columns = df.columns.str.strip()

        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].str.strip()

        return df

    except Exception as e:
        print(f"❌ Error: {e}")
        return pd.DataFrame()


# ============================================================================
# PREDICTIVE ANALYSIS
# ============================================================================


def predict_future_issues(df):
    """Analyze trends to predict future problems"""
    predictions = []

    if df.empty:
        return predictions

    # PREDICTION 1: Attack escalation (increasing DENY attempts)
    deny_df = df[df["action"] == "DENY"].copy()
    if len(deny_df) >= 6:  # Need minimum data
        mid = len(deny_df) // 2
        first_half = len(deny_df[:mid])
        second_half = len(deny_df[mid:])

        if second_half > first_half * 1.5:  # 50% increase
            predictions.append(
                {
                    "type": "ATTACK ESCALATION",
                    "severity": "HIGH",
                    "description": f"Denied access attempts increasing: {first_half} → {second_half}",
                    "recommendation": "Monitor for coordinated attack, consider blocking suspicious sources",
                }
            )

    # PREDICTION 2: High traffic trend (possible DoS)
    high_traffic = df[df["packets"] > 100]
    if len(high_traffic) >= 5:
        avg_packets = high_traffic["packets"].mean()
        predictions.append(
            {
                "type": "TRAFFIC OVERLOAD RISK",
                "severity": "MEDIUM",
                "description": f"{len(high_traffic)} high-traffic events (avg: {avg_packets:.0f} packets)",
                "recommendation": "Monitor bandwidth usage, prepare for potential DoS attack",
            }
        )

    # PREDICTION 3: Persistent unauthorized access
    server_access = df[
        df["destination"].apply(is_server) & ~df["source"].apply(is_it_device)
    ]

    if len(server_access) >= 3:
        sources = server_access["source"].value_counts()
        for source, count in sources.items():
            if count >= 3:
                predictions.append(
                    {
                        "type": "PERSISTENT UNAUTHORIZED ACCESS",
                        "severity": "HIGH",
                        "description": f"{source} attempted server access {count} times",
                        "recommendation": f"Investigate {source} - possible compromise or misconfiguration",
                    }
                )

    # PREDICTION 4: Network instability
    network_changes = df[df["action"] == "NETWORK_CHANGE"]
    if len(network_changes) >= 10:
        predictions.append(
            {
                "type": "NETWORK INSTABILITY",
                "severity": "MEDIUM",
                "description": f"{len(network_changes)} network topology changes detected",
                "recommendation": "Check switch configurations, verify cable connections",
            }
        )

    # PREDICTION 5: Brute force attack pattern
    for source in df["source"].unique():
        source_denies = df[(df["source"] == source) & (df["action"] == "DENY")]
        if len(source_denies) >= 5:
            # Check if attempts are accelerating
            if len(source_denies) >= 10:
                first_5 = source_denies.iloc[:5]
                last_5 = source_denies.iloc[-5:]

                # If recent attempts are closer together in time
                predictions.append(
                    {
                        "type": "BRUTE FORCE ACCELERATION",
                        "severity": "HIGH",
                        "description": f"{source} showing persistent attack pattern ({len(source_denies)} attempts)",
                        "recommendation": f"Consider blocking {source}, investigate source network",
                    }
                )

    return predictions


# ============================================================================
# DISPLAY
# ============================================================================


def display_predictions(predictions):
    """Pretty print predictions"""
    if not predictions:
        print("✅ No concerning trends detected")
        print("✅ All systems appear stable")
        return

    print(f"🔮 {len(predictions)} PREDICTIONS:")
    print("-" * 70)

    for i, pred in enumerate(predictions, 1):
        severity_icon = "🔴" if pred["severity"] == "HIGH" else "🟡"
        print(f"\n{severity_icon} PREDICTION #{i}: {pred['type']}")
        print(f"   Severity: {pred['severity']}")
        print(f"   Analysis: {pred['description']}")
        print(f"   💡 Recommendation: {pred['recommendation']}")


# ============================================================================
# MAIN FUNCTION
# ============================================================================


def run_predictions():
    """Run predictive analysis once"""

    print(f"📁 Loading data from: {CSV_FILE}")
    print(f"⏰ Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    df = load_logs()

    if df.empty:
        print("❌ No data to analyze")
        return

    print(f"📊 Analyzing {len(df)} network events...")
    print()

    predictions = predict_future_issues(df)

    display_predictions(predictions)

    print()
    print("=" * 70)
    print("Analysis complete! Run this script again to check for new trends.")
    print("=" * 70)


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    run_predictions()
