import os
from telemetry.auto import auto_instrument
from telemetry.hooks import install_async_hooks

auto_instrument("main")          # instrument API + logic
install_async_hooks()            # async visibility
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import os, glob, traceback, yt_dlp

from demucs import separate
from basic_pitch.inference import predict_and_save

from telemetry.context import get_current_context

app = FastAPI(title="Production-Grade Audio to MIDI Converter")

from telemetry.middleware import telemetry_middleware

app.middleware("http")(telemetry_middleware)

@app.get("/")
def root():
    return {"status": "ONLINE"}


@app.get("/api/rip-to-midi-stems")
async def rip_to_midi_stems(url: str = Query(...)):

    ctx = get_current_context()
    ctx.emit("pipeline.start", url=url)

    try:
        ctx.emit("download.start")

        # yt-dlp
        ctx.emit("download.running")
        # (your existing logic unchanged)

        ctx.emit("download.end")

        ctx.emit("demucs.start")
        separate.main([...])
        ctx.emit("demucs.end")

        ctx.emit("midi.start")
        predict_and_save([...])
        ctx.emit("midi.end")

        ctx.emit("pipeline.success")

        return {"status": "ok"}

    except Exception as e:
        ctx.emit("pipeline.error", error=str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

async def telemetry_middleware(request, call_next):

    ctx = ExecutionContext(origin="http")
    current_context.set(ctx)

    ctx.emit("lifecycle.start")
    ctx.emit("http.request", path=str(request.url))

    try:
        response = await call_next(request)

        ctx.emit(
            "http.response",
            status=response.status_code
        )

        return response

    except Exception as e:

        ctx.emit("error", error=str(e))
        raise

    finally:

        ctx.emit("lifecycle.end")

ENABLE_ASYNC_HOOKS = (
    os.getenv("ENABLE_ASYNC_HOOKS", "false").lower()
    == "true"
)

auto_instrument("main")

if ENABLE_ASYNC_HOOKS:
    install_async_hooks()