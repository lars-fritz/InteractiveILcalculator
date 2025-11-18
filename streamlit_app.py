import streamlit as st
import math

st.title("Uniswap v3 Impermanent Loss Calculator")


st.markdown("""

# 📘 Uniswap v3 Mathematics: Liquidity, Price, and Token Amounts

### 🔢 **1. The Core Concentrated-Liquidity Invariant**

In Uniswap v3, a position is defined by the liquidity parameter (L) and a price range ([p_{\min}, p_{\max}]).
For any price (p) inside this range, the reserves of token (x) and token (y) in the position satisfy the fundamental invariant:

[
\left( x + \frac{L}{\sqrt{p_{\max}}} \right)
\left( y + L\sqrt{p_{\min}} \right)
= L^{2}.
]

This describes the *geometry* of concentrated liquidity: instead of a constant product (x y = k), Uniswap v3 uses an **affine transformation in square-root price space**, causing the liquidity curve to be shifted and clipped to the active interval.

---

### 🧮 **2. Token Amounts as Explicit Functions of Price**

Solving the invariant for (x) and (y) gives the in-range token amounts:

[
x(p) = L\left( \frac{1}{\sqrt{p}} - \frac{1}{\sqrt{p_{\max}}} \right),
\qquad
y(p) = L\left( \sqrt{p} - \sqrt{p_{\min}} \right).
]

These functions describe the actual composition of the Uniswap v3 position at price (p):

* As (p \to p_{\min}):
  [
  y(p) \to 0, \quad x(p) \to L\left(\frac{1}{\sqrt{p_{\min}}} - \frac{1}{\sqrt{p_{\max}}}\right),
  ]
  the position becomes **all-x**.

* As (p \to p_{\max}):
  [
  x(p) \to 0, \quad y(p) \to L\left(\sqrt{p_{\max}} - \sqrt{p_{\min}}\right),
  ]
  the position becomes **all-y**.

These are precisely the formulas used in your calculator to compute the token split ((x_{\text{pos}}, y_{\text{pos}})) once liquidity (L) is known.

---

### ✏️ **3. Quick Derivation of the Token Amount Formulas**

Start with the standard definitions of token amounts in terms of liquidity:

[
x(p) = \frac{L}{\sqrt{p}} - \frac{L}{\sqrt{p_{\max}}},
\qquad
y(p) = L\sqrt{p} - L\sqrt{p_{\min}}.
]

These follow directly from integrating the “infinitesimal liquidity expression” over the active price interval:

[
dx = \frac{L}{2 p^{3/2}},dp,
\qquad
dy = \frac{L}{2\sqrt{p}},dp.
]

Integrating (dx) from (p) to (p_{\max}) yields (x(p)).
Integrating (dy) from (p_{\min}) to (p) yields (y(p)).

Multiplying the transformed expressions gives the invariant:

[
\left(x + \frac{L}{\sqrt{p_{\max}}}\right)
\left(y + L\sqrt{p_{\min}}\right)
= L^2.
]

---

### 🧠 **4. Why Square-Root Price Appears Everywhere**

Uniswap v3 works naturally in **square-root price** space:

[
\sqrt{p} = \sqrt{\frac{\text{token } y}{\text{token } x}}.
]

This has two important consequences:

1. **Liquidity becomes linear in (\sqrt{p})**
   which greatly simplifies the math.

2. **Fee earnings accumulate linearly across ticks**,
   because ticks are increments in (\sqrt{p}), not in (p).

This is why all Uniswap v3 equations involve terms like:

* (1/\sqrt{p})
* (\sqrt{p_{\min}})
* (\sqrt{p_{\max}})

It also explains the elegance of the token formulas above: they are simply linear functions of (\sqrt{p}).

---

### 📌 **Summary**

For any price (p) inside a Uniswap v3 range:

[
x(p) = L\left(\frac{1}{\sqrt{p}} - \frac{1}{\sqrt{p_{\max}}}\right),
\qquad
y(p) = L\left(\sqrt{p} - \sqrt{p_{\min}}\right),
]

and these satisfy the invariant:

[
\left( x + \frac{L}{\sqrt{p_{\max}}} \right)
\left( y + L\sqrt{p_{\min}} \right)
= L^{2}.
]


""")


st.markdown(r"""
## 📉 Impermanent Loss From a Price Move

Suppose a Uniswap v3 position is initialized at price \(p\) with liquidity \(L\), active in the range
\([p_{\min}, p_{\max}]\).  
If the price later moves to a new level \(p'\), the number of tokens in the position becomes:

\[
x'(p') = L\left( \frac{1}{\sqrt{\max(p', p_{\min})}} - \frac{1}{\sqrt{p_{\max}}} \right),
\]

\[
y'(p') = L\left( \sqrt{\min(p', p_{\max})} - \sqrt{p_{\min}} \right).
\]

These formulas automatically handle out-of-range situations:

- If \( p' < p_{\min} \): the position becomes **all-x**
- If \( p' > p_{\max} \): the position becomes **all-y**
- If \( p_{\min} < p' < p_{\max} \): the position holds a mixture

---

## 💰 Position Value at the New Price

At price \(p'\), the LP position is worth:

\[
V_{\text{LP}}(p') = x'(p') + \frac{1}{p'}\,y'(p').
\]

For comparison, a passive HODL of the original token mix at initialization price \(p\) is worth:

\[
V_{\text{HODL}}(p') = x(p) + \frac{1}{p'}\,y(p),
\]

where \(x(p)\) and \(y(p)\) are the initial amounts deposited into the position.

---

## 📊 Impermanent Loss

Impermanent Loss is defined as the relative underperformance:

\[
\text{IL}(p \to p') =
\frac{V_{\text{HODL}}(p') - V_{\text{LP}}(p')}{V_{\text{HODL}}(p')}.
\]

This quantity is always \(\le 0\) (LP underperforms HODL), except in fee-generating environments where fee income may offset IL.

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
st.subheader("Interactive IL Calculator")

p_initial = st.number_input("Initial price p", value=1.0, step=0.01)
p_new = st.number_input("New price p'", value=0.7, step=0.01)

# Use your existing L from earlier section (saved as L)
# Or add a manual override:
# L = st.number_input("Liquidity L", value=1000.0)

def x_amount(L, p, pmax):
    return L * (1/math.sqrt(p) - 1/math.sqrt(pmax))

def y_amount(L, p, pmin):
    return L * (math.sqrt(p) - math.sqrt(pmin))

def x_amount_future(L, p_prime, pmin, pmax):
    p_eff = max(p_prime, pmin)   # no y below pmin
    return L * (1/math.sqrt(p_eff) - 1/math.sqrt(pmax))

def y_amount_future(L, p_prime, pmin):
    p_eff = min(p_prime, pmax)   # no x above pmax
    return L * (math.sqrt(p_eff) - math.sqrt(pmin))

# Compute initial token amounts (x,y at p)
x_init = x_amount(L, p_initial, p_max)
y_init = y_amount(L, p_initial, p_min)

# Compute future token amounts (x',y' at p')
x_new = x_amount_future(L, p_new, p_min, p_max)
y_new = y_amount_future(L, p_new, p_min)

# Value of LP and HODL at new price
V_lp = x_new + (1/p_new)*y_new
V_hodl = x_init + (1/p_new)*y_init

IL = (V_hodl - V_lp) / V_hodl

st.write(f"**LP value at p' = {p_new}:** {V_lp:.6f}")
st.write(f"**HODL value at p' = {p_new}:** {V_hodl:.6f}")
st.write(f"### ➖ Impermanent Loss: {IL:.4%}")

# Plot IL curve over a range
import numpy as np
import matplotlib.pyplot as plt

p_vals = np.linspace(0.5 * p_initial, 1.5 * p_initial, 200)
IL_vals = []

for pprime in p_vals:
    xp = x_amount_future(L, pprime, p_min, p_max)
    yp = y_amount_future(L, pprime, p_min)
    Vlp = xp + yp / pprime
    Vhodl = x_init + y_init / pprime
    IL_vals.append((Vhodl - Vlp) / Vhodl)

fig, ax = plt.subplots()
ax.plot(p_vals, IL_vals)
ax.axvline(p_initial, color='gray', linestyle='--', linewidth=1)
ax.set_title("Impermanent Loss Curve")
ax.set_xlabel("Price p'")
ax.set_ylabel("IL")
st.pyplot(fig)
