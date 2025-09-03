from fastapi import FastAPI
from app.db import SessionLocal, NetFlow, init_db

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"message": "Polygon Net Flow API is running 🚀"}

@app.get("/netflow")
def get_netflow():
    db = SessionLocal()
    result = db.query(NetFlow).order_by(NetFlow.id.desc()).first()
    if result:
        return {
            "exchange": result.exchange,
            "cumulative_inflow": result.cumulative_inflow,
            "cumulative_outflow": result.cumulative_outflow,
            "net_flow": result.net_flow,
            "last_updated": result.last_updated,
        }
    return {"message": "No net flow data available"}
