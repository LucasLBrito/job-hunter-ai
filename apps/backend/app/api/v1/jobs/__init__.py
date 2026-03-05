from fastapi import APIRouter

from . import crud, search, recommendations, analysis, explore

router = APIRouter()

# Register sub-routers.
# IMPORTANT: Static routes (recommendations, search, analysis, explore) must come BEFORE dynamic path parameter routes (crud)
router.include_router(recommendations.router)
router.include_router(search.router)
router.include_router(analysis.router)
router.include_router(explore.router)
router.include_router(crud.router)
