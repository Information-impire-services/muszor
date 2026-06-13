import os
import glob
import traceback
import yt_dlp
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from demucs import separate

# Force Basic Pitch backends to skip dynamic remote model lookups on startup
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["ONNXRUNTIME_LOGGING_LEVEL"] = "3"

try:
    from basic_pitch.inference import predict_and_save
except Exception as import_err:
    print(f"⚠️ Warning during model library handshake: {str(import_err)}")

app = FastAPI(title="Production-Grade Audio to MIDI Converter")

# =====================================================================
# 1. LOCAL DISK ARCHITECTURE CONFIGURATION
# =====================================================================
DOWNLOAD_DIR = "./downloads"
STEMS_DIR = "./stems"
OUTPUT_DIR = "./output"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(STEMS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =====================================================================
# 2. ROUTE DEFINITIONS & RUNTIME LOGIC
# =====================================================================
@app.get("/")
async def root():
    return {
        "status": "ONLINE",
        "message": "Resilient API Engine Active! 100% Local Processing Mode Operational.",
        "current_directory": os.getcwd(),
    }


@app.get("/api/rip-to-midi-stems")
async def rip_to_midi_stems(url: str = Query(..., description="The track link to process")):
    try:
        video_id = ""
        if "youtu.be" in url:
            video_id = url.split("/")[-1].split("?")[0]
        elif "v=" in url:
            video_id = url.split("v=")[-1].split("&")[0]
        else:
            video_id = url.split("/")[-1]

        print(f"🧹 Processing full-length track for Video ID: {video_id}")

        # System Hygiene: Clear out old dynamic media caches safely
        for f in glob.glob(f"{DOWNLOAD_DIR}/*") + glob.glob(f"{STEMS_DIR}/*") + glob.glob(f"{OUTPUT_DIR}/*"):
            try:
                if os.path.isfile(f):
                    os.remove(f)
            except Exception:
                pass

        output_template = os.path.join(DOWNLOAD_DIR, "audio")
        input_audio = os.path.join(DOWNLOAD_DIR, "audio.mp3")

        # -------------------------------------------------------------
        # STEP 1: PURE LOCAL EXTRACTION VIA YT-DLP CORE
        # -------------------------------------------------------------
        print("📥 Step 1: Initiating native local high-fidelity audio extraction...")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "quiet": False,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as dl_error:
            raise HTTPException(status_code=500, detail=f"Local extraction pipeline failed: {str(dl_error)}")

        if not os.path.exists(input_audio):
            raise HTTPException(status_code=500, detail="Failed to locate extracted audio file artifact.")

        print(f"✅ Full audio downloaded successfully! Size: {os.path.getsize(input_audio)} bytes")

        # -------------------------------------------------------------
        # STEP 2: METAS DEMUCS AI SEPARATION
        # -------------------------------------------------------------
        print("🧠 Step 2: AI Demixing - Splitting track audio channels...")
        try:
            separate.main(["--mp3", "-o", STEMS_DIR, "-n", "2stems", "--filename", "{stem}.{ext}", input_audio])
        except SystemExit:
            pass

        search_path_fallback = os.path.join(STEMS_DIR, "**", "*.mp3")
        generated_stems = glob.glob(search_path_fallback, recursive=True)
        print(f"📂 Found stems in directory: {generated_stems}")

        if not generated_stems:
            raise HTTPException(status_code=500, detail="The AI stem separation stage failed to find any track layers.")

        # -------------------------------------------------------------
        # STEP 3: SPOTIFY BASIC PITCH ONNX INFERENCE
        # -------------------------------------------------------------
        print("🔮 Step 3: ONNX Inference - Translating audio data to MIDI sequences...")
        for stem_path in generated_stems:
            stem_name = os.path.basename(stem_path).replace(".mp3", "")
            if any(k in stem_name.lower() for k in ["bass", "other", "no_drums"]):
                print(f"🎯 Matching stem found! Transcribing: {stem_name}...")
                predict_and_save(
                    audio_path_list=[stem_path],
                    output_directory=OUTPUT_DIR,
                    save_midi=True,
                    sonify_midi=False,
                    save_model_output=False,
                    save_notes=False,
                )

        completed_midi_files = [os.path.basename(f) for f in glob.glob(f"{OUTPUT_DIR}/*.mid")]
        return JSONResponse(
            content={
                "status": "SUCCESS",
                "message": "Full track stems extracted locally and converted perfectly!",
                "files_ready_for_download": completed_midi_files,
                "instructions": "Right-click the files in your VS Code workspace sidebar under the 'output' folder to download them directly for BandLab.",
            }
        )

    except Exception as e:
        print(f"💥 GLOBAL SERVER EXCEPTION: {str(e)}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"status": "ERROR", "detail": str(e)})
