from fastapi import APIRouter

from app.api.v1.endpoints.agencies import router as agencies_router
from app.api.v1.endpoints.contacts import router as contacts_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.faqs import router as faqs_router
from app.api.v1.endpoints.fees import router as fees_router
from app.api.v1.endpoints.locations import router as locations_router
from app.api.v1.endpoints.requirements import router as requirements_router
from app.api.v1.endpoints.services import router as services_router


api_router = APIRouter()

api_router.include_router(agencies_router)
api_router.include_router(contacts_router)
api_router.include_router(services_router)
api_router.include_router(locations_router)
api_router.include_router(requirements_router)
api_router.include_router(fees_router)
api_router.include_router(faqs_router)
api_router.include_router(documents_router)
