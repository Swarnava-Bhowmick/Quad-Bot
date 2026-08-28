# CAD/CAM Quadruped Robot

**A ground-up robotics project: mechanical design, CAD assembly, gait kinematics, and stability analysis for a 4-legged walking robot.**

This repository documents the complete design and analysis of a simplified quadruped robot — from a rectangular body frame and four 2-DOF legs, through trot-gait trajectory generation in MATLAB/Python, to a formal static-stability check. It was built as the final project of the **ROBO AI Industrial Training Program on Robotics and AI**.

> Every design decision here — link lengths, joint limits, gait timing — is backed by a kinematic or mechanical calculation, not just picked by eye. If you're learning legged robotics, this is meant to be read start to finish as a worked example.

---

## What's Inside

- A 3D-printable/machinable **CAD assembly** (FreeCAD, STEP export) of a 4-legged robot
- Closed-form **inverse and forward kinematics** for a 2-link leg
- A full **trot-gait trajectory generator** (MATLAB + Python) with phase offsets for all four legs
- A **support-polygon stability analysis** comparing static standing vs. trotting
- An honest look at the **design's limitations** and how a real product (like Spot or MIT Cheetah) solves them

## Quick Facts

| | |
|---|---|
| **Legs** | 4, each with 2 DOF (hip + knee) |
| **Body size** | 200 × 100 × 40 mm |
| **Leg reach** | 200 mm (100 mm thigh + 100 mm shin) |
| **Gait** | Trot, duty factor β = 0.60, cycle time T = 1.0 s |
| **Walking speed** | 0.30 m/s |
| **Static stability margin** | 75 mm (standing) / 0 mm (trotting — expected for trot) |
| **CAD tool** | FreeCAD 0.21 (Assembly 4) |
| **Analysis tools** | MATLAB R2023b, Python 3.11 (NumPy, Matplotlib, SciPy) |

---

## 1. Mechanical Design

The robot is a rigid rectangular chassis with four identical leg assemblies bolted to its corners. Each leg is an open kinematic chain — **Body → Hip → Thigh → Knee → Shin → Foot** — moving entirely in one vertical plane (sagittal plane), which keeps the kinematics simple while still producing a walking gait.

**Why these choices?**
- A rectangular body is the simplest shape that gives four clean mounting corners while keeping mass low.
- Equal link lengths (thigh = shin = 100 mm) simplify the inverse-kinematics math and give a symmetric workspace.
- All four legs are identical parts, instanced four times — one part to design, one part to debug.

### Body Frame

| Parameter | Value | Notes |
|---|---|---|
| Length (X) | 200 mm | Hip-to-hip distance, walking direction |
| Width (Y) | 100 mm | Hip-to-hip distance, lateral |
| Height (Z) | 40 mm | Chassis thickness |
| Corner chamfer | 4 mm | All vertical edges |
| Mounting holes | Ø6 mm × 4 | One per leg, at each corner |

### Leg Links

| Part | Dimensions | Holes | Role |
|---|---|---|---|
| Thigh (Link 1) | 100 × 12 × 10 mm | Ø6 mm at hip + knee ends | Connects body to knee joint |
| Shin (Link 2) | 100 × 12 × 10 mm | Ø6 mm at knee end | Connects knee to foot (flat contact) |

### Hip Positions (body frame)

| Leg | X (mm) | Y (mm) |
|---|---|---|
| Left Front (LF) | +95 | +45 |
| Right Front (RF) | +95 | −45 |
| Left Hind (LH) | −95 | +45 |
| Right Hind (RH) | −95 | −45 |

---

## 2. CAD Assembly

Modelled in **FreeCAD 0.21**: parts in Part Design, assembly in **Assembly 4** using LCS-to-LCS (Local Coordinate System) attachment — no separate constraint solver, just parametric snapping.

- `Body.FCStd` — chamfered body with 4 mounting holes *(×1)*
- `Thigh.FCStd` — upper leg link, hip + knee holes *(×4)*
- `Shin.FCStd` — lower leg link, knee hole, flat foot *(×4)*
- `Assembly.FCStd` — all 9 parts combined, exported as STEP (AP214) for simulation

Each thigh's hip LCS snaps to the body; each shin's knee LCS snaps to the matching thigh — so building the full 9-part assembly is a repeatable, parametric process rather than manual positioning.

---

## 3. Joints & Motion Limits

Both the hip and knee are **single-axis revolute joints**, rotating about the **Y-axis (lateral)** so the leg swings forward/backward in the sagittal plane — the natural motion axis for a walking leg, and the same convention used in biological quadruped anatomy.

| Joint | Full Range | Used During Gait | Why |
|---|---|---|---|
| **Hip** | −30° to +30° | ±10° (33% of range) | ±30° gives enough stride without the thigh hitting the body; front/rear legs stay clear even at max swing |
| **Knee** | +10° to +90° | 25° to 75° (63% of range) | A 10° minimum avoids a fully-straight "singular" leg (bad for inverse kinematics); 90° gives clearance to lift the foot during swing |

At maximum extension the foot sits **141 mm** from the hip — clear of both the ground plane and the body, confirming the design has no self-collision within its intended range of motion.

---

## 4. Gait Cycle — How the Robot Walks

The robot uses a **trot gait**: diagonal leg pairs (LF+RH and RF+LH) move together, alternating which pair is on the ground. This is the same gait horses and dogs use at moderate speed, and it's a good balance of speed and simplicity for a legged robot.

**Timing**, derived from stride length and walking speed:

| Parameter | Formula | Value |
|---|---|---|
| Gait cycle time (T) | stride length ÷ speed | 1.000 s |
| Stance duration | β × T | 0.600 s (foot on ground) |
| Swing duration | (1 − β) × T | 0.400 s (foot in the air) |
| Max foot lift | forward kinematics | 92.8 mm |
| Stride range | forward kinematics | 108.5 mm |

**Phase offsets** stagger each leg relative to the reference (LF) leg, so the four feet don't all move at once:

- **LF** — 0% of cycle (reference leg)
- **LH** — 25% of cycle
- **RF** — 50% of cycle (opposite diagonal to LF)
- **RH** — 75% of cycle

**How each joint moves within its own cycle:**
- *Hip, stance phase:* sweeps linearly from +10° to −10° — this is what pushes the body forward while the foot stays planted.
- *Hip, swing phase:* a smooth half-sine from −10° back to +10°, carrying the foot forward through the air.
- *Knee, stance phase:* held at a constant 25° — a slight bend for compliance and to avoid a locked-straight leg.
- *Knee, swing phase:* a bell-curve up to 75° and back to 25°, lifting the foot clear of the ground mid-swing.

The half-sine/bell-curve shapes aren't arbitrary — they guarantee **zero velocity at the start and end of each phase**, which is what makes the motion smooth instead of jerky.

---

## 5. Kinematics

**Inverse kinematics** — given a target foot position `(x, y)` relative to the hip, solve for joint angles using the standard closed-form 2R solution:

```
r²            = x² + y²
cos(θ_knee)   = (r² − L1² − L2²) / (2·L1·L2)
θ_knee        = arccos(cos(θ_knee))
θ_hip         = atan2(y, x) − atan2(L2·sin(θ_knee), L1 + L2·cos(θ_knee))
```

**Forward kinematics** — given joint angles, find where the foot ends up:

```
x_knee = L1 · sin(θ_hip)
y_knee = L1 · cos(θ_hip)
x_foot = x_knee + L2 · sin(θ_hip + θ_knee)
y_foot = y_knee + L2 · cos(θ_hip + θ_knee)
```

These two functions are the backbone of everything else in this repo: the trajectory generator uses forward kinematics to predict foot paths, and inverse kinematics would be used to command the robot to a specific foot placement.

---

## 6. Motion Validation

Before trusting the gait math, it was checked against six concrete pass/fail criteria:

- **Smooth foot trajectory** — the foot traces a clean elliptical arc with no discontinuities ✅
- **No ground penetration** — foot depth never exceeds the 200 mm ground plane ✅
- **No body–leg collision** — verified geometrically at maximum hip/knee extension ✅
- **Continuous joint velocities** — no sudden torque spikes in the angle-vs-time derivative ✅
- **Phase-correct foot timing** — diagonal pairs land and lift in sync, as the gait design intends ✅
- **Symmetric leg motion** — all four legs produce identical angle profiles, just time-shifted ✅

Validation was done two ways: a **MATLAB 3D stick-figure animation** (runs on base MATLAB or GNU Octave, no toolboxes needed) and a **9-panel validation plot** covering joint angles, foot paths, the gait contact diagram, and the stability polygon in one figure. The STEP assembly was also optionally run through **SimScale** for a browser-based rigid-body motion check with collision detection.

---

## 7. Stability Analysis

A legged robot is **statically stable** if the ground-projected Centre of Mass (CoM) falls inside the polygon formed by its grounded feet — the classic *support polygon* test.

| Situation | Feet Down | Support Shape | CoM Position | Margin | Verdict |
|---|---|---|---|---|---|
| Standing still | All 4 | 300 × 150 mm rectangle | Dead centre | **75 mm** | **Stable** |
| Trotting — Phase A | LF + RH | Diagonal line | Exactly on the line | 0 mm | Marginal |
| Trotting — Phase B | RF + LH | Diagonal line | Exactly on the line | 0 mm | Marginal |

A 0 mm margin while trotting sounds alarming, but it's expected — a symmetric two-point trot always has a zero-area support "polygon" (it's just a line). Real trotting robots don't rely on static balance during the trot phase; they rely on **momentum and fast leg exchange**, the same way a jogging human doesn't statically balance on one foot. Two easy ways to add a real margin if needed:
- Bias the CoM 5–10 mm forward, so it sits just off the diagonal line
- Switch to a **crawl gait** (3 feet always down) for low-speed, fully-static walking

---

## 8. Known Limitations

Being upfront about what this design *doesn't* do well — and how production quadrupeds solve it:

| Limitation | Why It Matters | How Real Robots Fix It |
|---|---|---|
| **2 DOF per leg only** | No sideways stepping, no tight turns, no adapting to uneven ground | Add a 3rd hip joint (abduction/adduction) — used on Boston Dynamics Spot, MIT Cheetah |
| **0 mm trot stability margin** | No tolerance for an off-centre payload or a sideways push while trotting | Use a crawl gait at low speed, or shift the CoM slightly forward |
| **Rigid-body assumption** | Foot impacts transmit full force straight to the servos and links | Add passive springs/dampers in the shin, soft foot pads |
| **Open-loop trajectories** | A slip or delayed foot contact throws off the whole timed sequence | Add an IMU, foot-contact sensors, and closed-loop PID/MPC control |

---

## Tools Used

| Tool | Purpose |
|---|---|
| **FreeCAD 0.21** | 3D CAD modelling, assembly, STEP export |
| **MATLAB R2023b** | Gait calculation, trajectory plotting, 3D animation |
| **Python 3.11** (NumPy, Matplotlib, SciPy) | Cross-check of MATLAB results, plotting |

---

## Author

**Swarnava Bhowmick**
ROBO AI — Industrial Training Program on Robotics and AI (10-Day Program)
