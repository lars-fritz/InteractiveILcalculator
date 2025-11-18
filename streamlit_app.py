import streamlit as st
import math

st.title("Uniswap v3 Impermanent Loss Calculator")

# --- SECTION 1: Placeholder for Uniswap v3 Math ---
st.header("Uniswap v3 Math (Placeholder)")
st.markdown("""
Below is a **fully polished, drop-in Streamlit Markdown block** containing:

* ✔ The invariant
* ✔ Token formulas
* ✔ A clean intuitive explanation
* ✔ A short derivation of the formulas
* ✔ A short explanation of why Uniswap v3 uses **square-root price**

All formulas are written in **pure Markdown + LaTeX**, which Streamlit renders natively with `st.markdown(..., unsafe_allow_html=True)`.

You can paste this entire block directly into your app.

---

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

This is all you need for liquidity computation and token-split calculation in your IL tool.

---

If you'd like, I can also prepare:

* The **L-from-x** and **L-from-y** formulas as part of this section
* A visual illustration (ASCII or SVG) of how tokens convert as price moves
* An optional section on **ticks** and how prices map to tick indices

Just say the word.

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
