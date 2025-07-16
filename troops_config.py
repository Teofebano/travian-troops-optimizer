OASIS_DEFENSE = {
    "Rat": (25, 20),
    "Spider": (35, 40),
    "Snake": (40, 60),
    "Bat": (66, 50),
    "Boar": (70, 33),
    "Wolf": (80, 70),
    "Bear": (140, 200),
    "Crocodile": (380, 240),
    "Tiger": (170, 250),
    "Elephant": (440, 520)
}

TROOPS_TABLE = {
    "Teuton": {
        "Clubswinger": {
            "type": "infantry",
            "attack": [
                40.0, 40.6, 41.2, 41.8, 42.5, 43.1, 43.7, 44.4, 45.1, 45.7,
                46.4, 47.1, 47.8, 48.5, 49.3, 50.0, 50.8, 51.5, 52.83, 53.1, 53.9
            ],
            "cost": 250
        },
        "Axeman": {
            "type": "infantry",
            "attack": [
                60.0, 60.9, 61.8, 62.7, 63.7, 64.6, 65.6, 66.6, 67.6, 68.6, 
                69.6, 70.7, 71.7, 72.8, 73.9, 75.0, 76.1, 77.3, 78.4, 79.6, 80.8
            ],
            "cost": 490
        },
        "Teutonic_Knight": {
            "type": "cavalry",
            "attack": [
                150.0, 152.2, 154.5, 156.9, 159.2, 161.6, 164.0, 166.5, 169.0, 171.5, 
                174.1, 176.7, 179.3, 182.0, 184.8, 187.5, 190.3, 193.2, 196.1, 199.0, 202.0
            ],
            "cost": 1525
        }
    },
    "Roman": {
        "Legionnaire": {
            "type": "infantry",
            "attack": [
                40.0, 40.6, 41.2, 41.8, 42.5, 43.1, 43.7, 44.4, 45.1, 45.7, 
                46.4, 47.1, 47.8, 48.5, 49.3, 50.0, 50.8, 51.5, 52.3, 53.1, 53.9
            ],
            "cost": 400
        },
        "Imperian": {
            "type": "infantry",
            "attack": [
                70.0, 71.1, 72.1, 73.2, 74.3, 75.4, 76.5, 77.7, 78.9, 80.0, 
                81.2, 82.5, 83.7, 84.9, 86.2, 87.5, 88.8, 90.2, 91.5, 92.9, 94.3
            ],
            "cost": 600
        },
        "Equites_Imperatoris": {
            "type": "cavalry",
            "attack": [
                120.0, 121.8, 123.6, 125.5, 127.4, 129.3, 131.2, 133.2, 135.2, 137.2, 
                139.3, 141.4, 143.5, 145.6, 147.8, 150.0, 152.3, 154.6, 156.9, 159.2, 161.6
            ],
            "cost": 1410
        },
        "Equites_Caesaris": {
            "type": "cavalry",
            "attack": [
                180.0, 182.7, 185.4, 188.2, 191.0, 193.9, 196.8, 199.8, 202.8, 205.8, 
                208.9, 212.0, 215.2, 218.4, 221.7, 225.0, 228.4, 231.8, 235.3, 238.9, 242.4
            ],
            "cost": 2170
        }
    },
    "Gaul": {
        "Swordman": {
            "type": "infantry",
            "attack": [
                65, 66.0, 67.0, 68.0, 69.0, 70.0, 71.1, 72.1, 73.2, 74.3, 
                75.4, 76.6, 77.7, 78.9, 80.1, 81.3, 82.5, 83.7, 85.0, 87.5
            ],
            "cost": 535
        },
        "Theutates_Thunder": {
            "type": "cavalry",
            "attack": [
                90.0, 91.4, 92.7, 94.1, 95.5, 97.0, 99.9, 101.4, 102.9, 104.4, 
                106.0, 107.6, 109.2, 110.9, 112.5, 114.2, 115.9, 117.7, 119.4, 121.2
            ],
            "cost": 1090
        }
    }
}

def compute_offense_split(tribe: str, troop_levels: dict, troop_counts: dict):
    """
    Parameters:
    - tribe: e.g., "Teuton"
    - troop_levels: dict, e.g., {"Clubswinger": 12, "Teutonic_Knight": 10}
    - troop_counts: dict, e.g., {"Clubswinger": 300, "Teutonic_Knight": 10}

    Returns (infantry_power, cavalry_power, infantry_power_ratio, cavalry_power_ratio, total_power)
    """

    inf_pow, cav_pow = 0.0, 0.0
    inf_pow_ratio, cav_pow_ratio = 0.0, 0.0
    tribe_data = TROOPS_TABLE[tribe]

    for troop, count in troop_counts.items():
        level = troop_levels.get(troop, 1)
        data = tribe_data.get(troop)

        if not data:
            continue

        atk = data["attack"][level - 1]
        if data["type"] == "infantry":
            inf_pow += count * atk
        elif data["type"] == "cavalry":
            cav_pow += count * atk

    total_pow = inf_pow + cav_pow

    if inf_pow != 0:
        inf_pow_ratio = inf_pow/total_pow

    if cav_pow != 0:
        cav_pow_ratio =  cav_pow/total_pow

    return inf_pow, cav_pow, inf_pow_ratio, cav_pow_ratio, total_pow

# # Test, uncommand to test
# levels = {"Clubswinger": 12, "Teutonic_Knight": 10}
# counts = {"Clubswinger": 200, "Teutonic_Knight": 10}

# res = compute_offense_split("Teuton", levels, counts)

# print("Inf:", res[0], "Cav:", res[1], "Ratios:", res[2], res[3], "Total:", res[4])