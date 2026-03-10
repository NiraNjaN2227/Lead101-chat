from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.api.routes import router as api_router
from app.core.logging_config import setup_logging
from app.core.config import settings
import sentry_sdk
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Setup Logging
setup_logging()

# Setup Sentry (if DSN provided)
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

# Setup Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title=settings.APP_NAME)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include API Routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# Preserve old /chat endpoint for backward compatibility (if frontend calls it directly)
# But ideally frontend should update to /api/v1/chat. 
# We'll forward/wrapper it here to route to the new logic if needed, 
# or just route requests to the same handler logic via include_router(prefix="") 
# if we want to support root /chat. 
# The original main.py had /chat directly on app. 
# Let's add an alias or just include router at root as well for compatibility.
app.include_router(api_router, tags=["chat"]) 
