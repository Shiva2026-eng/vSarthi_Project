from fastapi import FastAPI
from routes.auth import router as AuthRouter
from routes.user import router as UserRouter
from routes.documents import router as DocRouter
from dotenv import load_dotenv
load_dotenv()
app=FastAPI()
app.include_router(AuthRouter)
app.include_router(UserRouter)
app.include_router(DocRouter)
@app.get("/")
def greet():
    return {
        "success":True,
        "message":"App working correctly!"
    }
    