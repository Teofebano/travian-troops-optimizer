from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from troops_optimizer import run_simulated_annealing
from troops_config import TROOPS_TABLE
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

@app.post("/api/v1/optimize")
def optimize_troops(req: OptimizationRequest):
    if req.tribe not in TROOPS_TABLE:
        raise HTTPException(status_code=400, detail=f"Unknown tribe: {req.tribe}")

    tribe_data = TROOPS_TABLE[req.tribe]

    if not req.troops:
        raise HTTPException(status_code=400, detail="troops list must not be empty")

    for troop in req.troops:
        if troop not in tribe_data:
            raise HTTPException(status_code=400, detail=f"Unknown troop '{troop}' for tribe '{req.tribe}'")

        level = req.troop_levels.get(troop, 1)
        max_level = len(tribe_data[troop]["attack"])
        if level < 1 or level > max_level:
            raise HTTPException(
                status_code=400,
                detail=f"Level {level} for '{troop}' is out of range [1, {max_level}]"
            )

        if troop not in req.max_troop_limit:
            raise HTTPException(status_code=400, detail=f"max_troop_limit missing entry for '{troop}'")

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
