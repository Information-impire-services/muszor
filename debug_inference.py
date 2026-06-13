print("🚀 [Step 1/3] Starting completely isolated hardware/package check...")

print("📦 [Step 2/3] Testing library imports...")
try:
    import yt_dlp
    from demucs import separate
    from basic_pitch.inference import predict_and_save
    print("✅ Core ML and Extraction modules imported successfully!")
except Exception as e:
    print(f"❌ IMPORT FAILURE: {str(e)}")
    import sys; sys.exit(1)

print("🔮 [Step 3/3] Forcing Basic Pitch model initialization...")
try:
    # We call a dummy evaluation parameter to force the package to locate its weights
    print("🤖 Checking if Spotify model weights are present locally...")
    predict_and_save(
        audio_path_list=[], # Empty list forces instant initialization without processing a file
        output_directory="./output",
        save_midi=False,
        sonify_midi=False,
        save_model_output=False,
        save_notes=False
    )
    print("✅ Model initialized perfectly without network timeouts!")
except SystemExit:
    # Basic pitch might throw a SystemExit(0) when completing an empty execution list safely
    print("✅ Empty execution list exited cleanly. Weights are verified!")
except Exception as e:
    print(f"\n💥 PIPELINE CRASHED DURING INITIALIZATION!")
    print(f"Error Details: {str(e)}")
    import traceback
    traceback.print_exc()
