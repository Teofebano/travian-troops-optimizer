from scipy.optimize import dual_annealing
from troops_config import OASIS_DEFENSE, TROOPS_TABLE, compute_offense_split

def compute_oasis_defense(oasis_composition):
    """
    Computes oasis power

    Parameters:
    - oasis_composition: dict of animal name to count, e.g., {"Rat": 12, "Spider": 10}

    Returns (total_def_infantry, total_def_cavalry)
    """

    inf_def, cav_def = 0, 0
    for animal, count in oasis_composition.items():
        if animal not in OASIS_DEFENSE:
            continue

        i_d, c_d = OASIS_DEFENSE[animal]
        inf_def += i_d * count
        cav_def += c_d * count

    return inf_def, cav_def

def count_loss_percentage(tribe: str,
                          troop_counts: dict,
                          troop_levels: dict,
                          oasis_composition: dict) -> int:
    """
    Computes rounded-down loss percentage for given army vs oasis.

    Parameters:
    - tribe: e.g., "Teuton"
    - troop_counts: dict, e.g., {"Clubswinger": 300, "Teutonic_Knight": 10}
    - troop_levels: dict, e.g., {"Clubswinger": 12, "Teutonic_Knight": 10}
    - oasis_composition: dict of animal name to count, e.g., {"Rat": 12, "Spider": 10}

    Returns:
    - Integer loss percentage (rounded down), or float("inf") if invalid
    """
    # 1. Compute offense power
    inf_pow, cav_pow, inf_pow_ratio, cav_pow_ratio, total_pow = compute_offense_split(
        tribe, troop_levels, troop_counts
    )

    if total_pow == 0:
        return float("inf")

    # 2. Compute oasis defense
    inf_def, cav_def = compute_oasis_defense(oasis_composition)

    # 3. Defense against offense ratio
    effective_defense = inf_def * inf_pow_ratio + cav_def * cav_pow_ratio

    # 4. Compute and return floored loss %
    loss_percent = 100 * (effective_defense / total_pow) ** 1.5

    return loss_percent

def loss_function(tribe: str,
                  troop_counts: dict,
                  troop_levels: dict,
                  oasis_composition: dict,
                  army_size_penalty_coefficient: float = 5.0,
                  cavalry_penalty_coefficient: float = 2.5,
                  max_troop_limit: dict = None):
    """
    Loss function to minimize.

    Parameters:
    - tribe: e.g., "Teuton"
    - troop_counts: dict, e.g., {"Clubswinger": 300, "Teutonic_Knight": 10}
    - troop_levels: dict of levels
    - oasis_composition: dict of animal name to count, e.g., {"Rat": 12, "Spider": 10}
    - army_size_penalty_coefficient: penalty per army size
    - cavalry_penalty_coefficient: penalty per cavalry unit
    - max_troop_limit: optional upper bound for each troop

    Returns:
    - total cost (resource loss + send penalty)
    """

    if max_troop_limit:
        for troop, count in troop_counts.items():
            if count > max_troop_limit.get(troop, float("inf")):
                return float("inf") # Punish infinitely

    if sum(troop_counts.values()) == 0:
        return float("inf") # Punish infinitely

    # Step 1: Loss %
    loss_percent = count_loss_percentage(tribe, troop_counts, troop_levels, oasis_composition)

    # Step 2: Penalty from loss troops cost
    loss_cost_penalty = 0
    for troop, count in troop_counts.items():
        troop_loss = round(count * loss_percent / 100)
        loss_cost_penalty += troop_loss * TROOPS_TABLE[tribe][troop]["cost"]

    # Step 3: Penalty from army count
    army_size_penalty = 0
    for troop, count in troop_counts.items():
        troop_type = TROOPS_TABLE[tribe][troop]["type"]
        if troop_type == "infantry":
            army_size_penalty += count
        elif troop_type == "cavalry":
            army_size_penalty += count * cavalry_penalty_coefficient
    
    army_size_penalty *= army_size_penalty_coefficient

    return loss_cost_penalty + army_size_penalty

def loss_function_vectorized(x, tribe, troops, troop_levels, oasis_composition,
                             army_size_penalty_coefficient, cavalry_penalty_coefficient, max_troop_limit):
    """
    Vectorized loss function for Simulated Annealing
    """

    troop_counts = {troop: int(round(x[i])) for i, troop in enumerate(troops)}
    return loss_function(
        tribe=tribe,
        troop_counts=troop_counts,
        troop_levels=troop_levels,
        oasis_composition=oasis_composition,
        army_size_penalty_coefficient=army_size_penalty_coefficient,
        cavalry_penalty_coefficient=cavalry_penalty_coefficient,
        max_troop_limit=max_troop_limit
    )

def run_simulated_annealing(tribe: str,
                            troops: list,
                            troop_levels: dict,
                            oasis_composition: dict,
                            max_troop_limit: dict,
                            army_size_penalty_coefficient: float = 3.0,
                            cavalry_penalty_coefficient: float = 10.0,
                            max_iter: int = 100,
                            seed: int = 42):
    """
    Simulated Annealing
    """

    # Step 1: Define bounds for each troop
    bounds = [(0, max_troop_limit[troop]) for troop in troops]

    # Step 2: Run optimizer
    result = dual_annealing(
        lambda x: loss_function_vectorized(
            x,
            tribe,
            troops,
            troop_levels,
            oasis_composition,
            army_size_penalty_coefficient,
            cavalry_penalty_coefficient,
            max_troop_limit
        ),
        bounds=bounds,
        maxiter=max_iter,
        seed=seed
    )

    # Step 3: Decode result
    best_counts = {troops[i]: int(round(result.x[i])) for i in range(len(troops))}
    best_score = result.fun
    loss_percent = count_loss_percentage(tribe, best_counts, troop_levels, oasis_composition)

    # Step 4: Calculate troop loss and cost
    troop_losses = {}
    total_loss_cost = 0
    for troop, count in best_counts.items():
        troop_loss = round(count * loss_percent // 100)
        troop_losses[troop] = troop_loss
        cost_per_unit = TROOPS_TABLE[tribe][troop]["cost"]
        total_loss_cost += troop_loss * cost_per_unit

    return {
        "best_counts": best_counts,
        "objective_score": best_score,
        "loss_percent": loss_percent,
        "troop_losses": troop_losses,
        "total_loss_cost": total_loss_cost
    }

# # Testing
# if __name__ == "__main__":
#     # Example inputs
#     tribe = "Teuton"
#     troops = ["Clubswinger", "Teutonic_Knight"]
#     troop_levels = {
#         "Clubswinger": 13,
#         "Teutonic_Knight": 12
#     }
#     max_troop_limit = {
#         "Clubswinger": 500,
#         "Teutonic_Knight": 20
#     }
#     oasis_composition = {
#         "Rat": 22,
#         "Spider": 0,
#         "Snake": 0,
#         "Bat": 0,
#         "Boar": 0,
#         "Wolf": 0,
#         "Bear": 0,
#         "Crocodile": 0,
#         "Tiger": 0,
#         "Elephant": 0
#     }

#     result = run_simulated_annealing(
#         tribe=tribe,
#         troops=troops,
#         troop_levels=troop_levels,
#         oasis_composition=oasis_composition,
#         max_troop_limit=max_troop_limit
#     )

#     print("✅ Best Troop Composition:", result["best_counts"])
#     print("📉 Loss Percent:", result["loss_percent"], "%")
#     print("💀 Troop Losses:", result["troop_losses"])
#     print("💸 Total Resource Lost:", result["total_loss_cost"])
#     print("🧮 Objective Score:", result["objective_score"])
