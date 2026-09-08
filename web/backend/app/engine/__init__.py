from app.core.database import SessionLocal
from app.engine.real_engine import RealThermalMeshEngine

engine: RealThermalMeshEngine = RealThermalMeshEngine(SessionLocal)
