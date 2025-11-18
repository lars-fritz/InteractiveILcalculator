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

These describe exactly how a v3 position holds x/y inside the active range.

---
""")

# ======================================================
# ------------- FUNDING INPUTS + RANGE -----------------
# ======================================================

st.header("Interactive Range-LP Calculator")

st.subheader("1. Position Inputs")

p = st.number_input("Current price p (y per x)", min_value=1e-12, value=1.0)
p_min = st.number_input("Lower price bound p_min", min_value=0.0, value=0.8)
p_max = st.number_input("Upper price bound p_max", min_value=0.0, value=1.2)

funding_mode = st.radio(
    "How do you fund the position?",
    ("I only have asset x", "I only have asset y")
)

if funding_mode == "I only have asset x":
    x0 = st.number_input("Amount of token x", min_value=0.0, value=1000.0)
    y0 = 0.0
else:
    y0 = st.number_input("Amount of token y", min_value=0.0, value=1000.0)
    x0 = 0.0


# ======================================================
# ---------------- UTILITY FUNCTIONS -------------------
# ======================================================

def compute_L_from_x(x, p, pmin, pmax):
    """Liquidity from x only."""
    denom = 2 * math.sqrt(p) - math.sqrt(pmin) - p / math.sqrt(pmax)
    if denom <= 0:
        return float("nan")
    return p * x / denom

def x_amount(L, p, pmax):
    return L * (1/math.sqrt(p) - 1/math.sqrt(pmax))

def y_amount(L, p, pmin):
    return L * (math.sqrt(p) - math.sqrt(pmin))

def x_amount_future(L, p_prime, pmin, pmax):
    """Respect boundary: below p_min → all x."""
    p_eff = max(p_prime, pmin)
    return L * (1/math.sqrt(p_eff) - 1/math.sqrt(pmax))

def y_amount_future(L, p_prime, pmin, pmax):
    """Respect boundary: above p_max → all y."""
    p_eff = min(p_prime, pmax)
    return L * (math.sqrt(p_eff) - math.sqrt(pmin))


# ======================================================
# -------------- LIQUIDITY + TOKEN SPLIT ---------------
# ======================================================

st.subheader("2. Liquidity and Token Split")

if p_min >= p_max or p <= 0:
    st.error("Require 0 < p_min < p_max and current price p > 0.")
    st.stop()

# Convert y → x if user funds only with y
if funding_mode == "I only have asset x":
    x_fund = x0
else:
    x_fund = y0 / p  # convert y to x

if x_fund <= 0:
    st.warning("Provide a positive funding amount.")
    st.stop()

# Compute liquidity
L = compute_L_from_x(x_fund, p, p_min, p_max)

if math.isnan(L):
    st.error("Liquidity L became NaN. Check the range and price.")
    st.stop()

st.success(f"Liquidity L = {L:.6f}")

# Compute token split in position
x_pos = x_amount(L, p, p_max)
y_pos = y_amount(L, p, p_min)

st.write(f"**x in position:** {x_pos:.6f}")
st.write(f"**y in position:** {y_pos:.6f}")
st.caption("Tokens currently inside the active Uniswap v3 liquidity range.")


# ======================================================
# ------------------- IL AT A POINT --------------------
# ======================================================

st.header("Impermanent Loss Calculator")

p_new = st.number_input("New price p' for point IL", min_value=1e-12, value=0.7)

# Initial token mix
x_init = x_amount(L, p, p_max)
y_init = y_amount(L, p, p_min)

# New token mix at p'
x_new = x_amount_future(L, p_new, p_min, p_max)
y_new = y_amount_future(L, p_new, p_min, p_max)

# Position values
V_lp = x_new + y_new / p_new
V_hodl = x_init + y_init / p_new
IL_point = (V_hodl - V_lp) / V_hodl

st.write(f"**LP value at p' = {p_new}:** {V_lp:.6f}")
st.write(f"**HODL value at p' = {V_hodl:.6f}**")
st.write(f"### ➖ Point IL: {IL_point:.4%}")


# ======================================================
# ---------------- IL CURVE FULL RANGE -----------------
# ======================================================

st.subheader("IL Curve Across Full Active & Out-of-Range")

# Slight padding
p_low = max(1e-12, p_min * 0.9)
p_high = p_max * 1.1

p_vals = np.linspace(p_low, p_high, 500)
IL_vals = []

for pprime in p_vals:
    xp = x_amount_future(L, pprime, p_min, p_max)
    yp = y_amount_future(L, pprime, p_min, p_max)

    Vlp = xp + yp / pprime
    Vhodl = x_init + y_init / pprime

    if Vhodl == 0:
        IL_vals.append(np.nan)
    else:
        IL_vals.append((Vhodl - Vlp) / Vhodl)

df_curve = pd.DataFrame({"p_prime": p_vals, "IL": IL_vals}).dropna()
df_curve = df_curve.set_index("p_prime")

st.line_chart(df_curve["IL"])
st.caption(
    "IL curve from slightly below p_min to above p_max. "
    "Left region = all-x. Right region = all-y. Middle = mixed in-range liquidity."
)
