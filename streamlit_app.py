import streamlit as st
import math
import numpy as np
import pandas as pd



st.title("Uniswap v3 Impermanent Loss Calculator")

# ======================================================
# ------------------- UNISWAP V3 MATH ------------------
# ======================================================

st.markdown(r"""
# 📘 Uniswap v3 Mathematics: Liquidity, Price, and Token Amounts

### 🔢 **1. The Core Concentrated-Liquidity Invariant**

For a position with liquidity \(L\) active on \([p_{\min}, p_{\max}]\),
the token balances \((x,y)\) at price \(p\) satisfy:

$$
\left( x + \frac{L}{\sqrt{p_{\max}}} \right)
\left( y + L\sqrt{p_{\min}} \right)
= L^{2}.
$$

---

### 🧮 **2. Token Amounts Inside the Active Range**

$$
x(p)=L\left(\frac{1}{\sqrt{p}}-\frac{1}{\sqrt{p_{\max}}}\right),
\qquad
y(p)=L\left(\sqrt{p}-\sqrt{p_{\min}}\right).
$$

As \(p \to p_{\min}\) the position becomes all–x.  
As \(p \to p_{\max}\) the position becomes all–y.

---

### ✏️ **3. Why Square-Root Prices?**

Uniswap v3 liquidity is linear in \(\sqrt{p}\):

$$
\sqrt{p} = \sqrt{\frac{y}{x}}.
$$

This simplifies liquidity math, tick spacing, and fee accounting.

---
""")

# ======================================================
# ---------------- IMPERMANENT LOSS THEORY -------------
# ======================================================

st.markdown(r"""
# 📉 Impermanent Loss

After the price moves from \(p\) to \(p'\), token balances become:

$$
x'(p') = L\left( \frac{1}{\sqrt{\max(p',p_{\min})}} - \frac{1}{\sqrt{p_{\max}}} \right),
$$

$$
y'(p') = L\left( \sqrt{\min(p',p_{\max})} - \sqrt{p_{\min}} \right).
$$

LP value at new price:

$$
V_{\text{LP}}(p') = x'(p') + \frac{1}{p'} y'(p').
$$

HODL value:

$$
V_{\text{HODL}}(p') = x(p)+\frac{1}{p'} y(p).
$$

Impermanent Loss:

$$
\text{IL}(p\rightarrow p') =
\frac{V_{\text{HODL}}(p')-V_{\text{LP}}(p')}{V_{\text{HODL}}(p')}.
$$

""")

# ======================================================
# ------------------- RANGE INPUT UI -------------------
# ======================================================

st.header("Interactive Range-LP Calculator")

st.subheader("1. Position Inputs")

current_price = st.number_input("Current price p (y per x)", min_value=1e-9, value=1.0)
p_min = st.number_input("Lower price bound p_min", min_value=0.0, value=0.8)
p_max = st.number_input("Upper price bound p_max", min_value=0.0, value=1.2)

funding_mode = st.radio(
    "How do you fund the position?",
    ("I only have asset x", "I only have asset y")
)

if funding_mode == "I only have asset x":
    x0 = st.number_input("Amount of token x", min_value=0.0, value=1000.0)
    y0 = None
else:
    y0 = st.number_input("Amount of token y", min_value=0.0, value=1000.0)
    x0 = None

# ======================================================
# ---------------- UTILITY FUNCTIONS -------------------
# ======================================================

def compute_L_from_x(x, p, pmin, pmax):
    denom = 2 * math.sqrt(p) - math.sqrt(pmin) - p / math.sqrt(pmax)
    return float("nan") if denom <= 0 else p * x / denom

def compute_L_from_y(y, p, pmin):
    return y / (math.sqrt(p) - math.sqrt(pmin))

def x_amount(L, p, pmax):
    return L * (1/math.sqrt(p) - 1/math.sqrt(pmax))

def y_amount(L, p, pmin):
    return L * (math.sqrt(p) - math.sqrt(pmin))

def x_amount_future(L, p_prime, pmin, pmax):
    p_eff = max(p_prime, pmin)
    return L * (1/math.sqrt(p_eff) - 1/math.sqrt(pmax))

def y_amount_future(L, p_prime, pmin, pmax):
    p_eff = min(p_prime, pmax)
    return L * (math.sqrt(p_eff) - math.sqrt(pmin))

# ======================================================
# ---------------- LIQUIDITY CALCULATOR ----------------
# ======================================================

st.subheader("2. Liquidity and Token Split")

if st.button("Compute Liquidity and Token Split"):

    # Compute L
    if funding_mode == "I only have asset x":
        L = compute_L_from_x(x0, current_price, p_min, p_max)
    else:
        L = compute_L_from_y(y0, current_price, p_min)

    # Store for IL section
    st.session_state["L"] = L
    st.session_state["p_min"] = p_min
    st.session_state["p_max"] = p_max
    st.session_state["p_initial"] = current_price

    st.success(f"Liquidity L = {L:.6f}")

    # Token composition
    x_pos = x_amount(L, current_price, p_max)
    y_pos = y_amount(L, current_price, p_min)

    st.write(f"**x in position:** {x_pos:.6f}")
    st.write(f"**y in position:** {y_pos:.6f}")
    st.caption("Actual tokens inside the active Uniswap v3 range.")

# ======================================================
# ------------------ IL CALCULATOR ---------------------
# ======================================================

st.header("Impermanent Loss Calculator")

if "L" not in st.session_state:
    st.warning("Please compute liquidity first.")
    st.stop()

L = st.session_state["L"]
p_min = st.session_state["p_min"]
p_max = st.session_state["p_max"]
p_initial = st.session_state["p_initial"]

p_new = st.number_input("New price p'", min_value=1e-9, value=0.7)

# Initial split
x_init = x_amount(L, p_initial, p_max)
y_init = y_amount(L, p_initial, p_min)

# New split
x_new = x_amount_future(L, p_new, p_min, p_max)
y_new = y_amount_future(L, p_new, p_min, p_max)

# Values
V_lp = x_new + y_new / p_new
V_hodl = x_init + y_init / p_new
IL = (V_hodl - V_lp) / V_hodl

st.write(f"**LP value at p' = {p_new}:** {V_lp:.6f}")
st.write(f"**HODL value at p' = {V_hodl:.6f}**")
st.write(f"### ➖ Impermanent Loss: {IL:.4%}")

# ======================================================
# ------------------- IL CURVE PLOT --------------------
# ======================================================

st.subheader("IL Curve")

# ======================================================
# ------------------- IL CURVE PLOT --------------------
# ======================================================


st.subheader("IL Curve Across the Full Range")

# Create a price range slightly outside the LP bounds
p_low = max(1e-12, p_min * 0.9)
p_high = p_max * 1.1

p_vals = np.linspace(p_low, p_high, 400)
IL_vals = []

for pprime in p_vals:
    xp = x_amount_future(L, pprime, p_min, p_max)
    yp = y_amount_future(L, pprime, p_min, p_max)
    Vlp = xp + yp / pprime
    Vhodl = x_init + y_init / pprime
    IL_vals.append((Vhodl - Vlp) / Vhodl)

# Streamlit expects the x-axis as index
df_full = pd.DataFrame({"p'": p_vals, "IL": IL_vals})
df_full = df_full.set_index("p'")

st.line_chart(df_full["IL"])

st.caption(
    "The IL curve spans from slightly below p_min to slightly above p_max. "
    "Flat regions indicate out-of-range behavior where the LP is all-x (left) or all-y (right)."
)
