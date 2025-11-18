import streamlit as st
import math
import numpy as np
import pandas as pd

st.title("Uniswap v3 Impermanent Loss Calculator")

# ======================================================
# ------------------- UNISWAP V3 TEXT ------------------
# ======================================================

st.markdown(r"""
# 📘 Uniswap v3 Mathematics: Liquidity, Price, and Token Amounts

### 🔢 **1. Core Concentrated-Liquidity Invariant**

A Uniswap v3 LP position with liquidity \(L\) active over the price range  
\([p_{\min}, p_{\max}]\) satisfies the invariant

$$
\left( x + \frac{L}{\sqrt{p_{\max}}} \right)
\left( y + L\sqrt{p_{\min}} \right)
= L^{2}.
$$

This replaces the Uniswap v2 invariant \(xy=k\), and is derived from integrating
the infinitesimal liquidity curve which is **linear in \(\sqrt{p}\)**.

---

### 🧮 **2. Token Amounts Inside the Active Range**

When the *current* price is \(p\), the tokens held inside the position are:

$$
x(p)=L\!\left(\frac{1}{\sqrt{p}}-\frac{1}{\sqrt{p_{\max}}}\right), \qquad
y(p)=L\!\left(\sqrt{p}-\sqrt{p_{\min}}\right).
$$

Interpretation:

- As \(p \to p_{\min}\): position becomes **all-x**
- As \(p \to p_{\max}\): position becomes **all-y**
- For \(p_{\min} < p < p_{\max}\): position holds a **dynamic mix** of x/y

---

### ✏️ **3. Why Square-Root Prices?**

Uniswap v3 uses prices in **square root space**:

$$
\sqrt{p} = \sqrt{\frac{y}{x}}.
$$

This has two benefits:

1. Liquidity is *linear* in \(\sqrt{p}\)  
2. Fee growth is *linear* in tick index → simpler accounting

This is why all formulas involve \(\sqrt{p}\), \(1/\sqrt{p}\), etc.

---

""")

# ======================================================
# ------------------ IL THEORY TEXT --------------------
# ======================================================

st.markdown(r"""
# 📉 Impermanent Loss Fundamentals

Assume the position was initialized at price \(p\) with liquidity \(L\).

If price later moves to \(p'\), the token balances become:

$$
x'(p') = L\!\left(\frac{1}{\sqrt{\max(p',p_{\min})}} - 
                 \frac{1}{\sqrt{p_{\max}}}\right),
$$

$$
y'(p') = L\!\left(\sqrt{\min(p',p_{\max})} - \sqrt{p_{\min}}\right).
$$

This automatically produces:

- left plateau (all-x) when \(p' < p_{\min}\)
- right plateau (all-y) when \(p' > p_{\max}\)
- middle mixed zone when \(p_{\min} < p' < p_{\max}\)

---

### 💰 Position Value at New Price

LP value at price \(p'\):

$$
V_{\mathrm{LP}}(p') = x'(p') + \frac{1}{p'}y'(p').
$$

HODL value:

$$
V_{\mathrm{HODL}}(p') = x(p) + \frac{1}{p'}\,y(p).
$$

---

### 📊 Impermanent Loss

$$
\mathrm{IL}(p\!\to\!p') =
\frac{V_{\mathrm{HODL}}(p') - V_{\mathrm{LP}}(p')}{V_{\mathrm{HODL}}(p')}.
$$

(Always \(\le 0\) before fees.)
""")

# ======================================================
# -------------- INPUTS FOR LP POSITION ----------------
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
    denom = 2 * math.sqrt(p) - math.sqrt(pmin) - p / math.sqrt(pmax)
    if denom <= 0:
        return float("nan")
    return p * x / denom

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
# ------------------ LIQUIDITY BLOCK -------------------
# ======================================================

st.subheader("2. Liquidity and Token Split")

if p_min >= p_max or p <= 0:
    st.error("Require 0 < p_min < p_max and p > 0.")
    st.stop()

# Funding conversion: only-y → convert to x
if funding_mode == "I only have asset x":
    x_fund = x0
else:
    x_fund = y0 / p

if x_fund <= 0:
    st.warning("Provide a positive funding amount.")
    st.stop()

# Compute L
L = compute_L_from_x(x_fund, p, p_min, p_max)

if math.isnan(L):
    st.error("Liquidity L became NaN. Check range and price.")
    st.stop()

st.success(f"Liquidity L = {L:.6f}")

# Token composition at current price
x_pos = x_amount(L, p, p_max)
y_pos = y_amount(L, p, p_min)

st.write(f"**x in position:** {x_pos:.6f}")
st.write(f"**y in position:** {y_pos:.6f}")

st.caption("Exact tokens currently deposited in the active Uniswap v3 range.")

# For IL use:
p_initial = p
x_init = x_pos
y_init = y_pos

# ======================================================
# ---------------- IL AT A PARTICULAR p' ---------------
# ======================================================

st.header("Impermanent Loss at a Specific New Price")

p_new = st.number_input("New price p' for point IL estimate", min_value=1e-12, value=0.7)

x_new = x_amount_future(L, p_new, p_min, p_max)
y_new = y_amount_future(L, p_new, p_min, p_max)

V_lp = x_new + y_new / p_new
V_hodl = x_init + y_init / p_new
IL_point = (V_hodl - V_lp) / V_hodl

st.write(f"**LP value at p' = {p_new}:** {V_lp:.6f}")
st.write(f"**HODL value at p' = {V_hodl:.6f}**")
st.write(f"### ➖ Point Impermanent Loss: {IL_point:.4%}")

# ======================================================
# ------------------- FULL IL CURVE --------------------
# ======================================================

st.header("IL Curve Across Full Range (p' vs IL)")

p_low = max(1e-12, p_min * 0.9)
p_high = p_max * 1.1

p_vals = np.linspace(p_low, p_high, 600)
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
    "Full IL curve from slightly below p_min to slightly above p_max.\n"
    "Left plateau = all-x region. Right plateau = all-y region."
)
