import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt

st.title("Uniswap v3 Impermanent Loss Calculator")

# =========================================
# ----------- UNISWAP V3 MATH -------------
# =========================================

st.markdown(r"""
# 📘 Uniswap v3 Mathematics: Liquidity, Price, and Token Amounts

### 🔢 **1. The Core Concentrated-Liquidity Invariant**

For a Uniswap v3 position with liquidity \(L\) and active range \([p_{\min}, p_{\max}]\),
the token balances \((x,y)\) at price \(p\) satisfy:

$$
\left( x + \frac{L}{\sqrt{p_{\max}}} \right)
\left( y + L\sqrt{p_{\min}} \right)
= L^{2}.
$$

---

### 🧮 **2. Token Amounts as Explicit Functions of Price**

The in-range token balances are:

$$
x(p)=L\left(\frac{1}{\sqrt{p}}-\frac{1}{\sqrt{p_{\max}}}\right),
\qquad
y(p)=L\left(\sqrt{p}-\sqrt{p_{\min}}\right).
$$

As \(p \to p_{\min}\):

$$
y(p)\to0,\qquad 
x(p)\to L\left(\frac{1}{\sqrt{p_{\min}}}-\frac{1}{\sqrt{p_{\max}}}\right).
$$

As \(p \to p_{\max}\):

$$
x(p)\to0,\qquad 
y(p)\to L\left(\sqrt{p_{\max}}-\sqrt{p_{\min}}\right).
$$

---

### ✏️ **3. Derivation Sketch**

Integrating the infinitesimal liquidity relations

$$
dx = \frac{L}{2 p^{3/2}}\, dp,
\qquad
dy = \frac{L}{2\sqrt{p}}\, dp,
$$

yields the formulas above and the invariant.

---

### 🧠 **4. Why Square-Root Price?**

Uniswap v3 is linear in \(\sqrt{p}\):

$$
\sqrt{p}=\sqrt{\frac{y}{x}}.
$$

This simplifies liquidity, ticks, fee accumulation, and explains
why all v3 formulas involve square-root terms.

---
""")

# =========================================
# ----------- IMPERMANENT LOSS -----------
# =========================================

st.markdown(r"""
# 📉 Impermanent Loss From a Price Move

If a position initialized at price \(p\) with liquidity \(L\) later moves to \(p'\), 
the token balances become:

$$
x'(p') = L\left( \frac{1}{\sqrt{\max(p',p_{\min})}} - \frac{1}{\sqrt{p_{\max}}} \right),
$$

$$
y'(p') = L\left( \sqrt{\min(p',p_{\max})} - \sqrt{p_{\min}} \right).
$$

Position value at new price:

$$
V_{\text{LP}}(p') = x'(p') + \frac{1}{p'}y'(p').
$$

HODL value:

$$
V_{\text{HODL}}(p') = x(p)+\frac{1}{p'}y(p).
$$

Impermanent Loss:

$$
\text{IL}(p\to p') =
\frac{V_{\text{HODL}}(p')-V_{\text{LP}}(p')}{V_{\text{HODL}}(p')}.
$$
""")

# =========================================
# ----------- INTERACTIVE CALC -----------
# =========================================

st.header("Interactive Range-LP Calculator")

st.subheader("1. Position Inputs")

current_price = st.number_input(
    "Current price p (y per x)",
    min_value=0.0000001,
    value=1.0,
    step=0.01
)

p_min = st.number_input("Lower price bound p_min", min_value=0.0, value=0.8, step=0.01)
p_max = st.number_input("Upper price bound p_max", min_value=0.0, value=1.2, step=0.01)

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


# ========= Utility functions =========

def compute_L_from_x(x, p, pmin, pmax):
    denom = 2 * math.sqrt(p) - math.sqrt(pmin) - p / math.sqrt(pmax)
    if denom <= 0:
        return float("nan")
    return p * x / denom

def compute_L_from_y(y, p, pmin):
    return y / (math.sqrt(p) - math.sqrt(pmin))

def x_amount(L, p, pmax):
    return L * (1/math.sqrt(p) - 1/math.sqrt(pmax))

def y_amount(L, p, pmin):
    return L * (math.sqrt(p) - math.sqrt(pmin))

def x_amount_future(L, p_prime, pmin, pmax):
    p_eff = max(p_prime, pmin)
    return L * (1/math.sqrt(p_eff) - 1/math.sqrt(pmax))

def y_amount_future(L, p_prime, pmin):
    p_eff = min(p_prime, pmax)
    return L * (math.sqrt(p_eff) - math.sqrt(pmin))


# ========= Compute Liquidity =========

st.subheader("2. Liquidity and Token Split")

if st.button("Compute Liquidity and Token Split"):

    if funding_mode == "I only have asset x":
        L = compute_L_from_x(x0, current_price, p_min, p_max)
    else:
        L = compute_L_from_y(y0, current_price, p_min)

    st.session_state["L"] = L
    st.session_state["p_min"] = p_min
    st.session_state["p_max"] = p_max
    st.session_state["p_initial"] = current_price

    st.success(f"Liquidity L = {L:.6f}")

    x_pos = x_amount(L, current_price, p_max)
    y_pos = y_amount(L, current_price, p_min)

    st.write(f"**x in position:** {x_pos:.6f}")
    st.write(f"**y in position:** {y_pos:.6f}")

    st.caption("These are the tokens inside the active Uniswap v3 range.")


# =====================================
# ----------- IL CALCULATOR -----------
# =====================================

st.header("Impermanent Loss Calculator")

if "L" not in st.session_state:
    st.warning("Please compute liquidity above first.")
    st.stop()

L = st.session_state["L"]
p_min = st.session_state["p_min"]
p_max = st.session_state["p_max"]
p_initial = st.session_state["p_initial"]

p_new = st.number_input("New price p'", value=0.7, step=0.01)

# Initial and new composition
x_init = x_amount(L, p_initial, p_max)
y_init = y_amount(L, p_initial, p_min)

x_new = x_amount_future(L, p_new, p_min, p_max)
y_new = y_amount_future(L, p_new, p_min)

V_lp = x_new + y_new/p_new
V_hodl = x_init + y_init/p_new

IL_val = (V_hodl - V_lp) / V_hodl

st.write(f"**LP value at p' = {p_new}:** {V_lp:.6f}")
st.write(f"**HODL value at p' = {p_new}:** {V_hodl:.6f}")
st.write(f"### ➖ Impermanent Loss: {IL_val:.4%}")

# ----- IL curve -----

p_vals = np.linspace(0.5*p_initial, 1.5*p_initial, 200)
IL_vals = []

for pprime in p_vals:
    xp = x_amount_future(L, pprime, p_min, p_max)
    yp = y_amount_future(L, pprime, p_min)
    Vlp = xp + yp/pprime
    Vhodl = x_init + y_init/pprime
    IL_vals.append((Vhodl - Vlp) / Vhodl)

fig, ax = plt.subplots()
ax.plot(p_vals, IL_vals)
ax.axvline(p_initial, color='gray', linestyle='--', linewidth=1)
ax.set_title("Impermanent Loss Curve")
ax.set_xlabel("Price p'")
ax.set_ylabel("IL")
st.pyplot(fig)

