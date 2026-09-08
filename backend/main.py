from settings import settings
from fastapi import FastAPI
from routes.auth import router as AuthRouter
from routes.user import router as UserRouter
from routes.documents import router as DocRouter
from fastapi.middleware.cors import CORSMiddleware
from utilities.exception_handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)

app.include_router(AuthRouter)
app.include_router(UserRouter)
app.include_router(DocRouter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.ANGULAR_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def greet():
    return {
        "success":True,
        "message":"App working correctly!"
    }