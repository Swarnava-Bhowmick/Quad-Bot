"""
╔══════════════════════════════════════════════════════════════════╗
║   Q4 — GAIT CYCLE CALCULATION                                   ║
║   Quadruped Robot | Industrial Training Program | ROBO AI       ║
║   Run in Jupyter: jupyter notebook  OR  python Q4_...py         ║
╚══════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from scipy.spatial import ConvexHull

plt.rcParams.update({'font.size': 11, 'figure.facecolor': 'white'})

SEP = "=" * 62


# ─────────────────────────────────────────────────────────────────
# CELL 1 — ROBOT DIMENSIONS
# ─────────────────────────────────────────────────────────────────
print(SEP)
print("  CELL 1 — ROBOT DIMENSIONS")
print(SEP)

BODY_L = 300        # mm  body length  (front ↔ rear)
BODY_W = 150        # mm  body width   (left  ↔ right)
BODY_H = 40         # mm  body height
L1     = 100        # mm  thigh  (hip  → knee)
L2     = 100        # mm  shin   (knee → foot)

print(f"  Body          : {BODY_L} × {BODY_W} × {BODY_H} mm")
print(f"  Thigh  L1     : {L1} mm")
print(f"  Shin   L2     : {L2} mm")
print(f"  Max reach     : L1 + L2 = {L1+L2} mm")
print(f"  Min reach     : |L1-L2| = {abs(L1-L2)} mm  (fully folded)")


# ─────────────────────────────────────────────────────────────────
# CELL 2 — STEP 1 : GAIT CYCLE TIME
#
#   Formula:    T  =  stride_length / forward_speed
#   Units  :    T  in seconds,  stride in metres,  speed in m/s
# ─────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  CELL 2 — STEP 1 : GAIT CYCLE TIME")
print(f"  Formula: T = stride_length / speed")
print(SEP)

speed  = 0.30       # m/s   forward walking speed
stride = 0.30       # m     one full stride (one leg completes one step)

T = stride / speed

print(f"\n  stride_length  = {stride} m")
print(f"  forward_speed  = {speed} m/s")
print(f"\n  T = {stride} / {speed}")
print(f"  T = {T:.4f} s          ← gait cycle time")

freq = 1.0 / T
print(f"\n  Stride frequency  f = 1/T = 1/{T} = {freq:.4f} Hz")
print(f"  Verify speed  v = stride × f = {stride} × {freq:.4f} = {stride*freq:.4f} m/s  ✓")


# ─────────────────────────────────────────────────────────────────
# CELL 3 — STEP 2 : STANCE & SWING DURATIONS
#
#   Duty factor β  =  fraction of T the foot is on the ground
#   t_stance = β × T
#   t_swing  = (1 − β) × T
# ─────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  CELL 3 — STEP 2 : STANCE & SWING DURATIONS")
print(f"  Formula: t_stance = β × T  |  t_swing = (1−β) × T")
print(SEP)

beta     = 0.60
t_stance = beta * T
t_swing  = (1 - beta) * T

print(f"\n  Duty factor  β        = {beta}  (60% of cycle on ground)")
print(f"\n  t_stance = {beta} × {T}")
print(f"  t_stance = {t_stance:.4f} s     ← foot on ground")
print(f"\n  t_swing  = (1 − {beta}) × {T}")
print(f"  t_swing  = {1-beta} × {T}")
print(f"  t_swing  = {t_swing:.4f} s     ← foot in air")
print(f"\n  Check: t_stance + t_swing = {t_stance:.4f} + {t_swing:.4f} = {t_stance+t_swing:.4f} s = T ✓")


# ─────────────────────────────────────────────────────────────────
# CELL 4 — STEP 3 : PHASE OFFSETS (TROT GAIT)
#
#   Trot = diagonal pairs move together
#   Diagonal pair 1: LF + RH  (φ = 0)
#   Diagonal pair 2: RF + LH  (φ = 0.5T)
#
#   Leg order:  LF   RF   LH   RH
#   φ (×T):     0   0.5  0.25  0.75
# ─────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  CELL 4 — STEP 3 : PHASE OFFSETS")
print(f"  Gait type: TROT  (diagonal leg pairs move together)")
print(SEP)

leg_names    = ['LF',   'RF',   'LH',   'RH']
phi_fraction = [0.00,   0.50,   0.25,   0.75]        # as fraction of T
phi          = [p * T   for p in phi_fraction]         # in seconds
phi_deg      = [p * 360 for p in phi_fraction]         # in degrees

print(f"\n  {'Leg':<6} {'φ (×T)':<10} {'φ (s)':<10} {'φ (deg)':<10}  Pair")
print(f"  {'-'*52}")
pairs = ['Pair 1 (LF+RH)', 'Pair 2 (RF+LH)', 'Pair 2 (RF+LH)', 'Pair 1 (LF+RH)']
for i in range(4):
    print(f"  {leg_names[i]:<6} {phi_fraction[i]:<10.2f} {phi[i]:<10.4f} {phi_deg[i]:<10.1f}  {pairs[i]}")

print(f"\n  Diagonal Pair 1  →  LF + RH  move SIMULTANEOUSLY  (0° apart)")
print(f"  Diagonal Pair 2  →  RF + LH  move SIMULTANEOUSLY  (180° offset)")
print(f"  Between pairs    →  90° offset  ensures smooth walking")


# ─────────────────────────────────────────────────────────────────
# CELL 5 — STEP 4 : JOINT ANGLE LIMITS
#
#   Hip  joint: rotates in sagittal plane (forward/backward)
#   Knee joint: rotates in sagittal plane (bending only)
# ─────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  CELL 5 — STEP 4 : JOINT ANGLE DEFINITIONS")
print(SEP)

hip_amp   = 20      # deg   hip swings ±20° around neutral
knee_ext  = 25      # deg   knee at stance (slight bend for compliance)
knee_flex = 50      # deg   extra flex added at peak swing
knee_peak = knee_ext + knee_flex

print(f"\n  Hip joint (sagittal, forward/backward rotation)")
print(f"    Max forward  :  +{hip_amp}°")
print(f"    Neutral      :   0°")
print(f"    Max backward :  −{hip_amp}°")
print(f"    Total range  :  {2*hip_amp}°")

print(f"\n  Knee joint (sagittal, bending only — no hyperextension)")
print(f"    Stance angle :   {knee_ext}°  (slight flex for compliance)")
print(f"    Swing peak   :   {knee_peak}°  ({knee_ext}° + {knee_flex}° flex)")
print(f"    Total range  :  {knee_peak - knee_ext}° (during one cycle)")


# ─────────────────────────────────────────────────────────────────
# CELL 6 — STEP 5 : JOINT ANGLE PROFILES
#
#   τ  = normalised time within cycle  [0, 1]
#
#   STANCE  (0 ≤ τ < β):
#     θ_hip(τ)  = hip_amp × (0.5 − τ/β)          [linear sweep]
#     θ_knee(τ) = knee_ext                          [constant]
#
#   SWING   (β ≤ τ ≤ 1):
#     s  = (τ − β) / (1 − β)                       [0 → 1]
#     θ_hip(s)  = −hip_amp/2 + hip_amp × sin(π·s)  [sinusoidal]
#     θ_knee(s) = knee_ext + knee_flex × sin(π·s)  [bell curve]
# ─────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  CELL 6 — STEP 5 : JOINT ANGLE PROFILES")
print(f"  τ = normalised phase [0,1]  |  s = swing progress [0,1]")
print(SEP)

print(f"\n  STANCE PHASE  (0 ≤ τ < {beta})")
print(f"    θ_hip(τ)  = {hip_amp} × (0.5 − τ/{beta})")
print(f"    θ_knee(τ) = {knee_ext}°  (constant)")

print(f"\n    τ=0.0  → θ_hip = {hip_amp}×(0.5−0.0/{beta}) = +{hip_amp*0.5:.2f}°   θ_knee = {knee_ext}°")
tau_mid = beta / 2
print(f"    τ={tau_mid}  → θ_hip = {hip_amp}×(0.5−{tau_mid}/{beta}) = +{hip_amp*(0.5-tau_mid/beta):.2f}°   θ_knee = {knee_ext}°")
print(f"    τ={beta}  → θ_hip = {hip_amp}×(0.5−{beta}/{beta}) = −{hip_amp*0.5:.2f}°   θ_knee = {knee_ext}°")

print(f"\n  SWING PHASE   ({beta} ≤ τ ≤ 1.0)")
print(f"    s  = (τ − {beta}) / {1-beta}")
print(f"    θ_hip(s)  = −{hip_amp/2} + {hip_amp} × sin(π·s)")
print(f"    θ_knee(s) = {knee_ext} + {knee_flex} × sin(π·s)")

print(f"\n    s=0.0  → θ_hip = −{hip_amp/2} + {hip_amp}×sin(0) = −{hip_amp/2:.2f}°   θ_knee = {knee_ext}°")
print(f"    s=0.5  → θ_hip = −{hip_amp/2} + {hip_amp}×sin(π/2) = +{-hip_amp/2+hip_amp:.2f}°   θ_knee = {knee_ext + knee_flex}°  ← peak")
print(f"    s=1.0  → θ_hip = −{hip_amp/2} + {hip_amp}×sin(π)  = −{hip_amp/2:.2f}°   θ_knee = {knee_ext}°")

dt = 0.005
t_arr = np.arange(0, T + dt, dt)
N = len(t_arr)

hip_lf  = np.zeros(N)
knee_lf = np.zeros(N)
for i in range(N):
    tau = (t_arr[i] - phi[0]) % T / T
    if tau < beta:
        hip_lf[i]  = hip_amp * (0.5 - tau / beta)
        knee_lf[i] = knee_ext
    else:
        s = (tau - beta) / (1 - beta)
        hip_lf[i]  = -hip_amp / 2 + hip_amp  * np.sin(np.pi * s)
        knee_lf[i] = knee_ext    + knee_flex  * np.sin(np.pi * s)

print(f"\n  Computed angle profile for LF leg ({N} time steps, dt = {dt} s)")
print(f"  Hip  : min = {hip_lf.min():.2f}°,  max = {hip_lf.max():.2f}°")
print(f"  Knee : min = {knee_lf.min():.2f}°,  max = {knee_lf.max():.2f}°")


# ─────────────────────────────────────────────────────────────────
# CELL 7 — STEP 6 : INVERSE KINEMATICS (CLOSED-FORM)
#
#   Given foot position (x_f, y_f) from hip origin:
#
#   r²  = x_f² + y_f²
#
#   cos(θ_knee) = (r² − L1² − L2²) / (2·L1·L2)
#   θ_knee = arccos(cos(θ_knee))
#
#   θ_hip = arctan2(y_f, x_f)
#         − arctan2(L2·sin(θ_knee),  L1 + L2·cos(θ_knee))
# ─────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  CELL 7 — STEP 6 : INVERSE KINEMATICS")
print(f"  Given foot (x_f, y_f) → compute θ_hip, θ_knee")
print(SEP)

test_cases = [
    (  0, 180, "foot directly below hip (neutral stance)"),
    (-20, 175, "foot slightly forward (mid-stance)"),
    ( 30, 160, "foot forward-lifted (swing)"),
]

for xf, yf, desc in test_cases:
    r_sq  = xf**2 + yf**2
    r     = np.sqrt(r_sq)
    cos_k = (r_sq - L1**2 - L2**2) / (2 * L1 * L2)
    cos_k = np.clip(cos_k, -1, 1)
    theta_k = np.degrees(np.arccos(cos_k))
    theta_h = np.degrees(
        np.arctan2(yf, xf)
        - np.arctan2(L2 * np.sin(np.radians(theta_k)),
                     L1 + L2 * np.cos(np.radians(theta_k)))
    )
    print(f"\n  Case: {desc}")
    print(f"    Foot     (x_f, y_f)  = ({xf}, {yf}) mm")
    print(f"    Reach    r           = √({xf}² + {yf}²) = {r:.2f} mm")
    print(f"    cos(θ_k)             = ({r_sq:.0f} − {L1**2} − {L2**2}) / {2*L1*L2}")
    print(f"                         = {r_sq - L1**2 - L2**2} / {2*L1*L2} = {cos_k:.4f}")
    print(f"    θ_knee               = arccos({cos_k:.4f}) = {theta_k:.2f}°")
    print(f"    θ_hip                = {theta_h:.2f}°")
    reach_check = np.sqrt((L1*np.cos(np.radians(theta_h)) + L2*np.cos(np.radians(theta_h+theta_k)))**2
                         +(L1*np.sin(np.radians(theta_h)) + L2*np.sin(np.radians(theta_h+theta_k)))**2)


# ─────────────────────────────────────────────────────────────────
# CELL 8 — STEP 7 : FOOT TRAJECTORY (FORWARD KINEMATICS)
#
#   Given θ_hip, θ_knee → compute foot position
#   x_knee = L1·sin(θ_hip)
#   y_knee = L1·cos(θ_hip)
#   x_foot = x_knee + L2·sin(θ_hip + θ_knee)
#   y_foot = y_knee + L2·cos(θ_hip + θ_knee)
#   (y positive = downward, matching robot convention)
# ─────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  CELL 8 — STEP 7 : FOOT TRAJECTORY (FORWARD KINEMATICS)")
print(f"  Convention: x = forward,  y = downward (positive)")
print(SEP)

fx_arr = np.zeros(N)
fy_arr = np.zeros(N)
for i in range(N):
    th_h = np.radians(hip_lf[i])
    th_k = np.radians(knee_lf[i])
    kx = L1 * np.sin(th_h)
    ky = L1 * np.cos(th_h)
    fx_arr[i] = kx + L2 * np.sin(th_h + th_k)
    fy_arr[i] = ky + L2 * np.cos(th_h + th_k)

ground_y = L1 + L2
lift_max  = ground_y - fy_arr.min()
x_range   = fx_arr.max() - fx_arr.min()

print(f"\n  Ground level    y = L1+L2 = {L1}+{L2} = {ground_y} mm")
print(f"  Max foot lift   = {lift_max:.2f} mm  (at mid-swing)")
print(f"  Stride length   = {x_range:.2f} mm  (foot X range)")
print(f"  Foot X range    = [{fx_arr.min():.2f},  {fx_arr.max():.2f}] mm")
print(f"  Foot Y range    = [{fy_arr.min():.2f},  {fy_arr.max():.2f}] mm")


# ─────────────────────────────────────────────────────────────────
# CELL 9 — STEP 8 : STABILITY MARGIN
#
#   Support polygon  = convex hull of grounded feet
#   For trot gait (2 feet):  line segment → marginal stability
#   For static stand (4 feet): rectangle → stable
#
#   Stability margin = shortest distance from CoM to polygon edge
# ─────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  CELL 9 — STEP 8 : STABILITY MARGIN")
print(SEP)

half_L = BODY_L / 2
half_W = BODY_W / 2
foot_pos = np.array([
    [ half_L,  half_W],   # LF
    [ half_L, -half_W],   # RF
    [-half_L,  half_W],   # LH
    [-half_L, -half_W],   # RH
])
CoM = np.array([0.0, 0.0])

print(f"\n  Foot positions (body frame, top view):")
for i, name in enumerate(leg_names):
    print(f"    {name}: ({foot_pos[i,0]:.0f}, {foot_pos[i,1]:.0f}) mm")

print(f"\n  CoM position  : ({CoM[0]:.0f}, {CoM[1]:.0f}) mm  [body centre]")

for contact_idx, label in [
    ([0, 3], "Trot Phase A  — LF + RH"),
    ([1, 2], "Trot Phase B  — RF + LH"),
    ([0,1,2,3], "Static stand — all 4 feet"),
]:
    pts = foot_pos[contact_idx]
    if len(pts) >= 3:
        hull = ConvexHull(pts)
        hull_pts = pts[hull.vertices]
        min_dist = float('inf')
        n = len(hull_pts)
        for e in range(n):
            A, B = hull_pts[e], hull_pts[(e+1) % n]
            dist = abs((B[1]-A[1])*CoM[0] - (B[0]-A[0])*CoM[1] + B[0]*A[1] - B[1]*A[0]) / np.linalg.norm(B-A)
            min_dist = min(min_dist, dist)
        stable_str = f"STABLE   (margin = {min_dist:.1f} mm)"
    else:
        min_dist   = 0.0
        stable_str = "MARGINAL (2-foot line → CoM on edge)"
    print(f"\n  {label}")
    print(f"    Stability: {stable_str}")

area_4 = BODY_L * BODY_W
print(f"\n  4-foot support polygon area = {BODY_L} × {BODY_W} = {area_4} mm²  = {area_4/1e6:.4f} m²")


# ─────────────────────────────────────────────────────────────────
# CELL 10 — FULL PARAMETER TABLE
# ─────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  CELL 10 — COMPLETE Q4 PARAMETER TABLE")
print(SEP)

rows = [
    ("Body length",          f"{BODY_L} mm",          "given"),
    ("Body width",           f"{BODY_W} mm",           "given"),
    ("Thigh L1",             f"{L1} mm",              "given"),
    ("Shin  L2",             f"{L2} mm",              "given"),
    ("Forward speed v",      f"{speed} m/s",          "given"),
    ("Stride length",        f"{stride} m",           "given"),
    ("Duty factor β",        f"{beta}",               "given"),
    ("Gait cycle T",         f"{T:.4f} s",            "= stride/v"),
    ("Stride freq f",        f"{freq:.4f} Hz",        "= 1/T"),
    ("Stance duration",      f"{t_stance:.4f} s",     "= β×T"),
    ("Swing  duration",      f"{t_swing:.4f} s",      "= (1−β)×T"),
    ("Phase LF",             f"0.000 s  (0°)",        "reference leg"),
    ("Phase RF",             f"{phi[1]:.3f} s  (180°)","= 0.5T"),
    ("Phase LH",             f"{phi[2]:.3f} s  (90°)", "= 0.25T"),
    ("Phase RH",             f"{phi[3]:.3f} s  (270°)","= 0.75T"),
    ("Hip swing amplitude",  f"±{hip_amp}°",          "sagittal plane"),
    ("Knee at stance",       f"{knee_ext}°",          "slight flex"),
    ("Knee peak (swing)",    f"{knee_peak}°",         "at mid-swing"),
    ("Max foot lift",        f"{lift_max:.2f} mm",    "FK calculation"),
    ("Foot stride range",    f"{x_range:.2f} mm",     "FK calculation"),
]

print(f"\n  {'Parameter':<26} {'Value':<20} {'Notes'}")
print(f"  {'-'*62}")
for name, val, note in rows:
    print(f"  {name:<26} {val:<20} {note}")


# ─────────────────────────────────────────────────────────────────
# CELL 11 — PLOTS
# ─────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  CELL 11 — GENERATING PLOTS")
print(SEP)

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

all_hip  = np.zeros((4, N))
all_knee = np.zeros((4, N))
all_fx   = np.zeros((4, N))
all_fy   = np.zeros((4, N))

for leg in range(4):
    for i in range(N):
        tau = (t_arr[i] - phi[leg]) % T / T
        if tau < beta:
            all_hip[leg, i]  = hip_amp * (0.5 - tau / beta)
            all_knee[leg, i] = knee_ext
        else:
            s = (tau - beta) / (1 - beta)
            all_hip[leg, i]  = -hip_amp / 2 + hip_amp  * np.sin(np.pi * s)
            all_knee[leg, i] = knee_ext    + knee_flex  * np.sin(np.pi * s)
        th_h = np.radians(all_hip[leg, i])
        th_k = np.radians(all_knee[leg, i])
        kx = L1 * np.sin(th_h)
        ky = L1 * np.cos(th_h)
        all_fx[leg, i] = kx + L2 * np.sin(th_h + th_k)
        all_fy[leg, i] = ky + L2 * np.cos(th_h + th_k)

fig = plt.figure(figsize=(16, 14))
fig.suptitle('Q4 — Gait Cycle Calculation: Complete Analysis', fontsize=14, fontweight='bold', y=0.98)
gs  = GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.38)

# --- Plot 1: Hip trajectories ---
ax1 = fig.add_subplot(gs[0, :2])
ax1.axhspan(-35, 35, xmin=0, xmax=t_stance/T, color='#dceeff', alpha=0.5, label='Stance zone')
ax1.axhspan(-35, 35, xmin=t_stance/T, xmax=1, color='#ffeedd', alpha=0.5, label='Swing zone')
ax1.axhline(0, color='gray', lw=0.8, ls='--')
ax1.axvline(t_stance, color='gray', lw=1, ls='--')
for leg in range(4):
    ax1.plot(t_arr, all_hip[leg], lw=2, color=colors[leg], label=leg_names[leg])
ax1.set(xlabel='Time (s)', ylabel='Hip angle (°)', title='Hip joint angles — all 4 legs', ylim=[-32, 32])
ax1.legend(ncol=2, fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.text(t_stance/2, 28, 'STANCE', ha='center', fontsize=9, color='#1555bb')
ax1.text((t_stance+T)/2, 28, 'SWING', ha='center', fontsize=9, color='#bb5511')

# --- Plot 2: Knee trajectories ---
ax2 = fig.add_subplot(gs[1, :2])
ax2.axhspan(0, 90, xmin=0, xmax=t_stance/T, color='#dceeff', alpha=0.5)
ax2.axhspan(0, 90, xmin=t_stance/T, xmax=1, color='#ffeedd', alpha=0.5)
ax2.axvline(t_stance, color='gray', lw=1, ls='--')
for leg in range(4):
    ax2.plot(t_arr, all_knee[leg], lw=2, color=colors[leg], label=leg_names[leg])
ax2.set(xlabel='Time (s)', ylabel='Knee angle (°)', title='Knee joint angles — all 4 legs', ylim=[-2, 82])
ax2.legend(ncol=2, fontsize=9)
ax2.grid(True, alpha=0.3)

# --- Plot 3: Foot trajectories ---
ax3 = fig.add_subplot(gs[2, :2])
ax3.invert_yaxis()
ax3.axhline(ground_y, color='saddlebrown', lw=2, ls='--', label=f'Ground y={ground_y}mm')
for leg in range(4):
    ax3.plot(all_fx[leg], all_fy[leg], lw=2, color=colors[leg], label=leg_names[leg])
    idx_st = np.where(t_arr < t_stance)[0]
    ax3.plot(all_fx[leg, idx_st], all_fy[leg, idx_st], 'o', color=colors[leg], markersize=2)
ax3.set(xlabel='X — forward (mm)', ylabel='Y — downward (mm)',
        title='Foot endpoint trajectories (all 4 legs)')
ax3.legend(ncol=2, fontsize=9)
ax3.grid(True, alpha=0.3)
ax3.set_aspect('equal')

# --- Plot 4: Phase diagram (Gantt-style) ---
ax4 = fig.add_subplot(gs[0, 2])
for i, (leg, p) in enumerate(zip(leg_names, phi)):
    tau_start = p
    tau_end   = p + t_stance
    if tau_end <= T:
        ax4.barh(i, t_stance, left=tau_start, color=colors[i], alpha=0.8, label=leg)
    else:
        ax4.barh(i, T - tau_start, left=tau_start, color=colors[i], alpha=0.8)
        ax4.barh(i, tau_end - T,   left=0,          color=colors[i], alpha=0.8)
    ax4.barh(i, t_swing, left=(tau_start + t_stance) % T, color=colors[i], alpha=0.25)
ax4.set(xlabel='Time (s)', yticks=range(4), yticklabels=leg_names,
        title='Gait diagram\n(solid=stance, light=swing)', xlim=[0, T])
ax4.axvline(t_stance, color='gray', ls='--', lw=0.8)
ax4.grid(True, alpha=0.3, axis='x')

# --- Plot 5: Stability (4-foot) ---
ax5 = fig.add_subplot(gs[1, 2])
hull4 = ConvexHull(foot_pos)
poly  = mpatches.Polygon(foot_pos[hull4.vertices], closed=True,
                          facecolor='#b3e5b3', edgecolor='green', lw=2, alpha=0.6)
ax5.add_patch(poly)
for i in range(4):
    ax5.plot(*foot_pos[i], 'go', ms=14)
    ax5.annotate(leg_names[i], foot_pos[i], textcoords="offset points",
                 xytext=(6, 6), fontsize=9, fontweight='bold')
ax5.plot(*CoM, 'r*', ms=18, label='CoM — STABLE')
bx = half_L * np.array([-1,1,1,-1,-1])
by = half_W * np.array([-1,-1,1,1,-1])
ax5.plot(bx, by, 'b-', lw=1.5, alpha=0.5, label='Body frame')
ax5.set(xlabel='X (mm)', ylabel='Y (mm)', title='4-foot stability\n(static stand)',
        xlim=[-200,200], ylim=[-100,100], aspect='equal')
ax5.legend(fontsize=8)
ax5.grid(True, alpha=0.3)

# --- Plot 6: IK workspace ---
ax6 = fig.add_subplot(gs[2, 2])
t1r = np.linspace(-40,  40, 200) * np.pi/180
t2r = np.linspace( 20,  80, 200) * np.pi/180
T1, T2 = np.meshgrid(t1r, t2r)
Xw = L1*np.cos(T1) + L2*np.cos(T1+T2)
Yw = L1*np.sin(T1) + L2*np.sin(T1+T2)
ax6.scatter(Xw.ravel(), Yw.ravel(), s=1, c='#3399cc', alpha=0.15, label='Workspace')
ax6.plot(0, 0, 'ks', ms=10, label='Hip joint')
for xf, yf, _ in test_cases:
    ax6.plot(xf, yf, 'r^', ms=8)
ax6.set(xlabel='X forward (mm)', ylabel='Y downward (mm)',
        title='2-DOF reachable\nworkspace', aspect='equal')
ax6.legend(fontsize=8); ax6.grid(True, alpha=0.3)

plt.savefig('Q4_Gait_Cycle_Calculation.png', dpi=150, bbox_inches='tight')
print("\n  Saved: Q4_Gait_Cycle_Calculation.png")
plt.show()

print(f"\n{SEP}")
print("  Q4 CALCULATION COMPLETE")
print(SEP)



