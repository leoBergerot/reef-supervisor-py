from .root import router as root_router
from .users import router as user_router
from .parameters import router as parameter_router
from .preferences import router as preference_router
from .tank import router as tank_router
from .measures import router as measure_router

__all__ = ["root_router", "user_router", "parameter_router", "preference_router", "tank_router", "measure_router"]
