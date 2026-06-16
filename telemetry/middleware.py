from telemetry.context import ExecutionContext, current_context


async def telemetry_middleware(request, call_next):
    ctx = ExecutionContext(origin="http")
    current_context.set(ctx)

    ctx.emit("http.request", path=str(request.url))

    try:
        response = await call_next(request)
        ctx.emit("http.response", status=response.status_code)
        return response

    except Exception as e:
        ctx.emit("error", error=str(e))
        raise

    finally:
        ctx.emit("lifecycle.end")