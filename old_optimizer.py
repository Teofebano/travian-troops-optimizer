from scipy.optimize import dual_annealing

# Troops Stats
TROOPS = {
    "CS": {
        # "attack": 48.5, #Edinburgh
        "attack": 50, #Glasgow
        "is_cavalry": False,
        "cost": 95 + 75 + 40 + 40
    },
    "TK": {
        # "attack": 179.3, #Edinburgh
        "attack": 171.5, #Glasgow
        "is_cavalry": True,
        "cost": 450 + 515 + 480 + 80
    }
}

# Oasis Troops
OASIS_TROOPS = {
    "rat": 8,
    "spider": 5,
    "snake": 0,
    "bat": 0,
    "boar": 0,
    "wolf": 0,
    "bear": 0,
    "crocodile": 0,
    "tiger": 0,
    "elephant": 0
}

# Oasis 
ANIMAL_DEF = {
    "rat": (25, 20),
    "spider": (35, 40),
    "snake": (40, 60),
    "bat": (66, 50),
    "boar": (70, 33),
    "wolf": (80, 70),
    "bear": (140, 200),
    "crocodile": (380, 240),
    "tiger": (170, 250),
    "elephant": (440, 500)
}

# Bound
MAX_CS = 500
MAX_TK = 20
ARMY_SIZE_COEFFICIENT = 3
CAVALRY_COEFFICIENT = 0.5

# Compute Defense
def compute_defense(oasis_troops):
    d_inf, d_cav = 0, 0
    for animal, count in oasis_troops.items():
        inf, cav = ANIMAL_DEF.get(animal, (0, 0))
        d_inf += count * inf
        d_cav += count * cav
    return d_inf, d_cav

D_INF, D_CAV = compute_defense(OASIS_TROOPS)

# Loss Function
def count_percentage_loss_percentage(cs,tk):
    cs, tk = int(round(cs)), int(round(tk))
    
    if cs < 1 or tk < 0 or cs > MAX_CS or tk > MAX_TK:
        return float("inf")

    atk_inf = TROOPS["CS"]["attack"]
    atk_cav = TROOPS["TK"]["attack"]

    offense = cs * atk_inf + tk * atk_cav
    if offense == 0:
        return float("inf")

    # Calculate loss percentage
    ratio_inf = (cs * atk_inf) / offense
    ratio_cav = (tk * atk_cav) / offense
    defense = ratio_inf * D_INF + ratio_cav * D_CAV
    print(offense)
    print(defense)
    return 100 * (defense / offense) ** 1.5

def count_troops_loss(loss_percent,cs,tk):
    lost_cs = round(cs * loss_percent / 100)
    lost_tk = round(tk * loss_percent / 100)

    return lost_cs,lost_tk

def count_loss_cost(lost_cs,lost_tk):
    cost_cs = TROOPS["CS"]["cost"]
    cost_tk = TROOPS["TK"]["cost"]

    return lost_cs * cost_cs + lost_tk * cost_tk

def loss(v):
    cs, tk = int(round(v[0])), int(round(v[1]))
    loss_percent = count_percentage_loss_percentage(cs,tk)

    lost_cs, lost_tk = count_troops_loss(loss_percent,cs,tk)

    # Cost of lost troops
    lost_cost = count_loss_cost(lost_cs,lost_tk)

    # Total troops sent (you can also use cost here instead of count)
    sent_penalty = cs + CAVALRY_COEFFICIENT * tk

    # Combined cost
    return 1 * lost_cost + ARMY_SIZE_COEFFICIENT * sent_penalty

# Simulated Annealing
bounds = [(0, MAX_CS), (0, MAX_TK)]

result = dual_annealing(
    func=loss,
    bounds=bounds,
    maxiter=10,
    seed=42,
)

# --- Interpret Result ---
print(result)
optimal_cs = int(round(result.x[0]))
optimal_tk = int(round(result.x[1]))
final_loss = count_percentage_loss_percentage(optimal_cs,optimal_tk)
lost_cs,lost_tk = count_troops_loss(final_loss,optimal_cs,optimal_tk)
total_cost = count_loss_cost(lost_cs,lost_tk)

# --- Output ---
print(" Optimal Troop Composition:")
print(f"  - Clubswingers (CS): {optimal_cs}")
print(f"  - Teutonic Knights (TK): {optimal_tk}")
print(f"  - Estimated Loss (% casualties): {final_loss:.2f}")
print(f"  - Total Troops Loss : {lost_cs, lost_tk}")
print(f"  - Total Cost : {total_cost}")
print(f"  - Function Evaluations: {result.nfev}")
