import streamlit as st
import math

st.title("Uniswap v3 Impermanent Loss Calculator")

# --- SECTION 1: Placeholder for Uniswap v3 Math ---
st.header("Uniswap v3 Math (Placeholder)")
st.markdown("""
(You will paste your explanatory text here later.)
""")

# --- SECTION 2: Placeholder for IL Discussion ---
st.header("Impermanent Loss (Placeholder)")
st.markdown("""
IL derivation and discussion will go here.
""")

# --- SECTION 3: Interactive Calculator ---
st.header("Interactive IL Calculator")

st.subheader("1. Position Inputs")

current_price = st.number_input(
    "Current price p (value of token y in units of token x)",
    min_value=0.0000001,
    value=1.0,
    step=0.01
)

p_min = st.number_input("Lower price bound p_min", min_value=0.0, value=0.8, step=0.01)
p_max = st.number_input("Upper price bound p_max", min_value=0.0, value=1.2, step=0.01)

funding_mode = st.radio(
    "How do you fund the position?",
    (
        "I only have asset x",
        "I only have asset y"
    )
)

# Amount inputs
if funding_mode == "I only have asset x":
    x0 = st.number_input("Amount of token x", min_value=0.0, value=1000.0)
    y0 = None

else:
    y0 = st.number_input("Amount of token y", min_value=0.0, value=1000.0)
    x0 = None


# --- Utility functions ---
def compute_L_from_x(x, p, pmin, pmax):
    denom = 2*math.sqrt(p) - math.sqrt(pmin) - p/math.sqrt(pmax)
    if denom <= 0:
        return float("nan")
    return p * x / denom

def compute_L_from_y(y, p, pmin):
    # Derived directly from y = L (sqrt(p) - sqrt(pmin))
    return y / (math.sqrt(p) - math.sqrt(pmin))

def compute_xpos(L, p, pmax):
    return L * (1/math.sqrt(p) - 1/math.sqrt(pmax))

def compute_ypos(L, p, pmin):
    return L * (math.sqrt(p) - math.sqrt(pmin))


# --- Computation ---
st.subheader("2. Liquidity and Position Composition")

if st.button("Compute Liquidity and Token Split"):

    if funding_mode == "I only have asset x":
        L = compute_L_from_x(x0, current_price, p_min, p_max)

    elif funding_mode == "I only have asset y":
        L = compute_L_from_y(y0, current_price, p_min)

    st.success(f"Liquidity L = {L:.6f}")

    # Compute tokens in the position
    x_pos = compute_xpos(L, current_price, p_max)
    y_pos = compute_ypos(L, current_price, p_min)

    st.subheader("Current Token Composition in the Position")
    st.write(f"**x in position:**  {x_pos:.6f}")
    st.write(f"**y in position:**  {y_pos:.6f}")

    st.markdown("---")
    st.caption("These are the actual tokens currently deposited inside the active Uniswap v3 position.")
