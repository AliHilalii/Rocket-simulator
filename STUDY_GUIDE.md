# Rocket Simulator — Full Study Guide (Phases 1-8)

This is the consolidated reference for everything the project uses so far:
every physics formula, which course covers it, and where to study it. Go
through this fully before treating the project as "understood" — being able
to explain any row below, unprompted, is the actual goal.

(Note on the Terminale spé physique-chimie mappings: based on the reformed
French Bac program as I understand it — worth double-checking against your
own textbook's table of contents, since it can vary slightly by year/teacher.)

## Phase 1 — Vertical Launch

| Concept | Formula | AP course | Terminale spé connection | Study resource |
|---|---|---|---|---|
| Gravity vs. altitude | `g = g0(R/(R+h))^2` | AP Physics 1 — Gravitation | Direct match: "Mouvement et interactions" (satellites, gravitational field) | Khan Academy "Gravitation"; Flipping Physics |
| Exponential atmosphere (superseded in Phase 3) | `rho = rho0*e^(-h/H)` | Not core AP | Not covered | — |
| Drag force | `F_d = 1/2 rho v|v| Cd A` | Not core AP | Direct match: "chute avec frottement fluide" | Professor Dave Explains — air resistance |
| Thrust (simplified) | Newton's 3rd Law / momentum | AP Physics 1 — Momentum | Direct match: "propulsion par réaction" | Khan Academy — Momentum & Impulse |
| Newton's 2nd Law | `F=ma` | AP Physics 1 — Dynamics | Core of "Mouvement et interactions" | Khan Academy AP Physics 1 |
| Euler integration | Numerical ODE solving | AP Physics C / Calculus | **Direct match — explicitly required**: "méthode d'Euler" | Your textbook's numerical resolution chapter |

## Phase 2 — Real Motor Thrust Curves

| Concept | Formula | AP course | Terminale spé connection | Study resource |
|---|---|---|---|---|
| Total impulse | `J = ∫F dt` (trapezoidal rule) | AP Physics 1 — Impulse-Momentum Theorem | Reinforces momentum unit | Khan Academy — Momentum & Impulse |
| Thrust-curve interpolation | Linear interpolation (`np.interp`) | Not AP; AP Precalculus territory | — | Self-taught / numerical methods intro |
| Impulse-based mass depletion | Ties propellant burn rate to delivered impulse | Foundation of the Tsiolkovsky rocket equation (beyond AP1/2) | — | Search "Tsiolkovsky rocket equation derivation" if curious |

## Phase 3 — Real Atmosphere Model

| Concept | Formula | AP course | Terminale spé connection | Study resource |
|---|---|---|---|---|
| Hydrostatic equilibrium | `dP = -rho*g*dh` | AP Physics 2 — Fluids | Pressure concepts touched in general physique-chimie | Khan Academy — Fluids (pressure & depth) |
| Ideal gas law | `P = rho*R*T / M` | AP Physics 2 — Thermodynamics | Covered under "Constitution et transformations de la matière" (loi des gaz parfaits) | Khan Academy — Ideal gas law |
| Layered atmosphere (troposphere/stratosphere, temperature lapse rate) | Piecewise `T(h)`, `P(h)` | Not standard AP; real ICAO/NASA Standard Atmosphere model | Not covered — this is genuinely beyond the curriculum | NASA/ICAO "International Standard Atmosphere" (search term) |

## Phase 4 — Full 3D Flight + RK4

| Concept | Formula | AP course | Terminale spé connection | Study resource |
|---|---|---|---|---|
| Vectors (position, velocity, force in 3D) | — | AP Physics 1 — vectors are foundational from day one | Vectors ("vecteurs") are explicitly taught for forces/velocity | Khan Academy — Vectors intro |
| Launch angle decomposition | `sin`/`cos` components | Not physics — trigonometry | Standard lycée trigonometry | Any trig refresher |
| Relative velocity (wind) | `v_rel = v - v_wind` (Galilean relativity) | AP Physics 1 — relative motion | Direct match: "référentiels" (frames of reference) | Khan Academy — relative motion |
| RK4 integration | 4th-order Runge-Kutta ODE solver | AP Physics C / numerical methods | Beyond Terminale spé (which requires Euler, not RK4) — a genuine step ahead | Search "Runge-Kutta 4th order method explained" |

## Phase 5 — Stability (Barrowman Method)

| Concept | Formula | AP course | Terminale spé connection | Study resource |
|---|---|---|---|---|
| Torque / center of pressure vs. center of gravity | Restoring torque when CP is aft of CG | AP Physics 1 — Torque & Rotational Motion | Direct match: "moment d'une force" | Khan Academy — Torque |
| Barrowman CP equations (nose + fin normal-force coefficients) | Semi-empirical aerospace formulas | Not in any AP course | Not in any French curriculum — genuinely original aerospace-engineering content | Apogee Rockets' technical publications; OpenRocket technical documentation (both free online) |

## Phase 6 — Parachute Recovery

| Concept | Formula | AP course | Terminale spé connection | Study resource |
|---|---|---|---|---|
| Terminal velocity under a larger Cd·A | Same drag equation, applied post-apogee | AP Physics 1 — Dynamics (equilibrium) | Reinforces "chute avec frottement" | Same as Phase 1 drag resources |
| Apogee detection | Peak-finding (altitude stops increasing) | Not physics — algorithm/logic | — | — |
| Sizing a parachute for a target descent rate | Engineering design, not a "law" | N/A | N/A | This is applied engineering — worth describing as such in your write-up |

## Phase 7 — Monte Carlo Dispersion Analysis

| Concept | Formula | AP course | Terminale spé connection | Study resource |
|---|---|---|---|---|
| Randomized trials (wind speed/direction, launch angle) | Normal & uniform distributions | Not AP1/2 — this is statistics | Probabilités is covered generally, but not applied to simulation like this | Khan Academy — Normal distributions |
| Aggregating results (mean, std dev, percentile) | Basic descriptive statistics | Not AP1/2 physics; AP Statistics | General stats — mean/std dev are pre-Terminale concepts, applying them to engineering risk is the new part | Khan Academy — Statistics: mean, standard deviation |
| Why coarser timestep is safe during descent | Numerical methods — accuracy vs. speed tradeoff | Not physics | Reinforces the same numerical-method thinking as Euler's method, applied practically | — |

## Phase 8 — 3D Rocket Animation

| Concept | Formula | AP course | Terminale spé connection | Study resource |
|---|---|---|---|---|
| Rotation matrix aligning one vector to another (Rodrigues' formula) | `R = I + [v]_x + [v]_x^2 (1-c)/s^2` | Not AP1/2 — linear algebra | Not in French lycée curriculum — genuinely college-level (linear algebra) content | Search "Rodrigues rotation formula derivation" if curious; otherwise just understand the *goal* (rotate object A to point along vector B) |
| Orientation from velocity direction (tangent to trajectory) | Direction ≈ (position change) / (time change), i.e. central-difference approximation of a derivative | Same numerical-derivative idea as Euler's method | Reinforces "vitesse = variation de position" | — |
| 3D mesh construction (cones, cylinders, boxes combined) | Geometry, not physics | N/A | N/A | PyVista's own documentation/examples |

## Priority order if you're short on time

1. **Newton's 2nd Law + drag + terminal velocity** (Phases 1, 6) — the absolute core, and the most direct Terminale spé match.
2. **Momentum/Impulse** (Phase 2) — second most AP-relevant concept.
3. **Euler's method, then RK4** (Phases 1, 4) — understand Euler fully first (it's required for your class), then RK4 as "the more accurate version of the same idea."
4. **Torque/static margin** (Phase 5) — quick, high-value, direct curriculum match.
5. **Atmosphere model, vectors, relative velocity** (Phases 3, 4) — good depth, lower urgency.
6. **Monte Carlo / basic statistics** (Phase 7) — valuable for your write-up's engineering narrative.
7. **Barrowman equations specifically, rotation matrices** (Phases 5, 8) — genuinely original/advanced content; understand the *concept* deeply, memorizing exact formulas is optional if time-constrained.
