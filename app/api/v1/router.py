from fastapi import APIRouter

from app.api.v1.endpoints.agencies import router as agencies_router
from app.api.v1.endpoints.contacts import router as contacts_router


api_router = APIRouter()

api_router.include_router(agencies_router)
api_router.include_router(contacts_router)