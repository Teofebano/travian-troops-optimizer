import streamlit as st
import re

from login import login_required
from troops_config import OASIS_DEFENSE,TROOPS_TABLE
from troops_optimizer import run_simulated_annealing

# Require login
# login_required()

# Main APP
st.title("🏹 Travian Troop Optimizer")

tribe = st.selectbox("Select your tribe", list(TROOPS_TABLE.keys()))

troops = st.multiselect("Select troops", list(TROOPS_TABLE[tribe].keys()))

troop_levels = {}
max_counts = {}

for troop in troops:
    col1, col2 = st.columns(2)
    with col1:
        level = st.number_input(f"{troop} level", min_value=1, max_value=20, value=1)
        troop_levels[troop] = level
    with col2:
        max_count = st.number_input(f"Max {troop} count", min_value=0, max_value=10000, value=1000)
        max_counts[troop] = max_count

st.markdown("---")
st.subheader("⚙️ Coefficients")
col1, col2 = st.columns(2)

with col1:
    army_coeff = st.slider("Army Size Penalty Coefficient", 0.0, 10.0, 5.0, 0.1, format="%.1f")

with col2:
    cav_coeff = st.slider("Cavalry Penalty Coefficient", 0.0, 5.0, 2.5, 0.1, format="%.1f")


st.markdown("---")
st.subheader("🐍 Oasis Troops")
oasis_composition = {}

if 'oasis_composition' not in st.session_state:
    st.session_state.oasis_composition = {animal: 0 for animal in OASIS_DEFENSE}

# Auto Parser
with st.expander("📋 Auto Parse Oasis Animal List (Expand to See)"):
    oasis_text = st.text_area("Paste from in-game oasis message:")
    if st.button("Parse Oasis Animals"):
        for animal in OASIS_DEFENSE:
            st.session_state.oasis_composition[animal] = 0

        for line in oasis_text.splitlines():
            for animal in OASIS_DEFENSE:
                if animal in line:
                    match = re.search(r"\b(\d+)\b", line)
                    if match:
                        st.session_state.oasis_composition[animal] = int(match.group(1))


# Manual Filling
cols = st.columns(len(OASIS_DEFENSE))
for idx, animal in enumerate(OASIS_DEFENSE):
    with cols[idx]:
        st.session_state.oasis_composition[animal] = st.number_input(
            animal,
            min_value=0,
            step=1,
            value=st.session_state.oasis_composition[animal],
            key=f"oasis_{animal}"
        )

oasis_composition = st.session_state.oasis_composition.copy()

if st.button("Run Optimization"):
    result = run_simulated_annealing(
        tribe=tribe,
        troops=troops,
        troop_levels=troop_levels,
        oasis_composition=oasis_composition,
        max_troop_limit=max_counts,
        army_size_penalty_coefficient=army_coeff,
        cavalry_penalty_coefficient=cav_coeff,
        max_iter=100
    )

    st.success("Optimization complete!")
    st.json(result)

