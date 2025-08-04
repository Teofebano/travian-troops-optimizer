from fastapi import FastAPI
from pydantic import BaseModel
from troops_optimizer import run_simulated_annealing
from troops_config import TROOPS_TABLE
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from any origin — for development only!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or replace with specific domain like ["https://ts5.x1.america.travian.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OptimizationRequest(BaseModel):
    tribe: str
    troops: list[str]
    troop_levels: dict[str, int]
    oasis_composition: dict[str, int]
    max_troop_limit: dict[str, int]
    army_coeff: float
    cav_coeff: float

@app.post("/optimize")
def optimize_troops(req: OptimizationRequest):
    result = run_simulated_annealing(
        tribe=req.tribe,
        troops=req.troops,
        troop_levels=req.troop_levels,
        oasis_composition=req.oasis_composition,
        max_troop_limit=req.max_troop_limit,
        army_size_penalty_coefficient=req.army_coeff,
        cavalry_penalty_coefficient=req.cav_coeff,
        max_iter=100
    )
    return result
