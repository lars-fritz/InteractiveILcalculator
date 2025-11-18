import streamlit as st
import math

st.title("Uniswap v3 Impermanent Loss Calculator")

# --- SECTION 1: Placeholder for Uniswap v3 Math ---
st.header("Uniswap v3 Math (Placeholder)")
st.markdown("""
This section will contain the general mathematical discussion of concentrated liquidity,
ticks, price ranges, and the mapping between liquidity L and token amounts x,y.
(You will paste your text here later.)
""")

# --- SECTION 2: Placeholder for IL Discussion ---
st.header("Impermanent Loss (Placeholder)")
st.markdown("""
Here we will describe impermanent loss, how to derive it from Uniswap v3 maths,
and how it depends on price movements inside and outside the range.
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
        "I already have both assets x and y",
        "I only have asset x",
        "I only have asset y"
    )
)

# Amount inputs
if funding_mode == "I already have both assets x and y":
    x0 = st.number_input("Amount of token x", min_value=0.0, value=1000.0)
    y0 = st.number_input("Amount of token y", min_value=0.0, value=1000.0)

elif funding_mode == "I only have asset x":
    x0 = st.number_input("Amount of token x", min_value=0.0, value=1000.0)
    y0 = None

else:
    y0 = st.number_input("Amount of token y", min_value=0.0, value=1000.0)
    x0 = None

# --- Computation of L ---
def compute_L_from_x(x, p, pmin, pmax):
    denom = 2*math.sqrt(p) - math.sqrt(pmin) - p/math.sqrt(pmax)
    if denom <= 0:
        return float("nan")
    return p*x/denom

st.subheader("2. Liquidity Calculation")

if st.button("Compute Liquidity"):

    if funding_mode == "I already have both assets x and y":
        L = compute_L_from_x(x0, current_price, p_min, p_max)

        st.success(f"Liquidity L = {L:.6f}")

    elif funding_mode == "I only have asset x":
        # Direct L-from-x approach
        L = compute_L_from_x(x0, current_price, p_min, p_max)
        st.info("Assuming you convert x into required y at current price p.")
        st.success(f"Liquidity L = {L:.6f}")

    elif funding_mode == "I only have asset y":
        # Solve using the y-based formula
        sqrtp = math.sqrt(current_price)
        L = y0 / (sqrtp - math.sqrt(p_min))
        st.info("Assuming you convert y into required x at current price p.")
        st.success(f"Liquidity L = {L:.6f}")
