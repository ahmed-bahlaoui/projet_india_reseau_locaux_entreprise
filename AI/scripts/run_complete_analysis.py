import os

print("=" * 70)
print("   🤖 COMPLETE NETWORK AI ANALYSIS")
print("=" * 70)
print()

print("This will run:")
print("1. Anomaly Detection (continuous monitoring)")
print("2. Predictive Analysis (on-demand)")
print()

choice = input("Run both? (y/n): ").lower()

if choice == "y":
    # Run predictions first (one-time)
    print("\n🔮 STEP 1: Running Predictive Analysis...")
    print("=" * 70)
    os.system("python predictive_maintenance.py")

    print("\n\n")
    input("Press Enter to start continuous anomaly monitoring...")
    print("\n")

    # Then start continuous monitoring
    print("🔍 STEP 2: Starting Continuous Anomaly Detection...")
    print("=" * 70)
    os.system("python anomaly_detection.py")
else:
    print("\nRun scripts individually:")
    print("  python anomaly_detection.py       (for continuous monitoring)")
    print("  python predictive_maintenance.py  (for one-time prediction)")
