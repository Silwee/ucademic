from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from auth.views import auth_router
from courses.views import courses_router
# from data.engine import create_db_and_tables
from user.views import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_pagination(app)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(courses_router)
