"""Usage: python3 prep_data.py OUT_DIR STICKER_DIR
Prepare REPORT_DATA (geometry + placeholder BEMT loads) and embedded cat stickers."""
import json, base64, io, math
import numpy as np
from PIL import Image

import sys
OUT = (sys.argv[1] if len(sys.argv) > 1 else '.') + '/'
A = (sys.argv[2] if len(sys.argv) > 2 else './stickers') + '/'

# ---------------- geometry: Harrington Rotor 1 (NACA TN 2318) ----------------
R = 12.5            # ft
Nb = 2
c_tip = 0.375       # ft (published, r/R = 1)
taper = 0.35        # tip/root (published)
c_root = c_tip / taper
r0 = 0.10           # root cutout r/R (assumed)
h = 0.093 * 2 * R   # rotor spacing ft (published 9.3% D)
Vtip = 469.0        # ft/s (analysis condition)
a_sound = 1116.4
Omega = Vtip / R
rpm = Omega * 60 / (2 * math.pi)

N = 60
r = np.linspace(r0, 1.0, N)
c = c_root + (c_tip - c_root) * (r - r0) / (1 - r0)
# nonlinear thickness taper 31% -> 12% (shape approximated; replace with deck values)
tc = 0.12 + 0.19 * ((1 - r) / (1 - r0)) ** 1.6
sigma_r = Nb * c / (math.pi * R)
rr = np.linspace(0, 1, 2001)
cc = np.where(rr >= r0, c_root + (c_tip - c_root) * (rr - r0) / (1 - r0), 0)
sigma_tw = Nb * 3 * np.trapezoid(cc * rr**2, rr) / (math.pi * R)

# ---------------- placeholder loads: simple coaxial BEMT ----------------
CLA = 5.73
def cd_of(alpha, tcv):
    return 0.0080 + 0.02 * (tcv - 0.12) + 0.40 * alpha**2

def bemt(theta, lam_c):
    lam = np.full(N, 0.04)
    F = np.ones(N)
    for _ in range(200):
        k = sigma_r * CLA / (16 * F) - lam_c / 2
        lam_new = np.sqrt(k**2 + sigma_r * CLA * theta * r / (8 * F)) - k
        phi = np.maximum(lam_new / r, 1e-6)
        f = Nb / 2 * (1 - r) / (r * phi)
        F_new = (2 / math.pi) * np.arccos(np.clip(np.exp(-f), 0, 1))
        F_new = np.maximum(F_new, 1e-3)
        if np.max(np.abs(lam_new - lam)) < 1e-9:
            lam, F = lam_new, F_new
            break
        lam, F = 0.5 * lam + 0.5 * lam_new, F_new
    alpha = theta - lam / r
    cl = CLA * alpha
    dCT = 0.5 * sigma_r * cl * r**2            # dCT/d(r/R)
    dCPi = lam * dCT                           # induced
    dCP0 = 0.5 * sigma_r * cd_of(alpha, tc) * r**3
    dCP = dCPi + dCP0
    return dict(lam=lam, dCT=dCT, dCP=dCP, alpha=alpha, cl=cl,
                CT=np.trapezoid(dCT, r), CP=np.trapezoid(dCP, r))

rc = 0.82  # contracted upper-wake radius at lower rotor plane (assumed)
def lower(theta, lam_u_mean):
    lam_c = (lam_u_mean / rc**2) * 0.5 * (1 - np.tanh((r - rc) / 0.025))  # smoothed slipstream edge
    out = bemt(theta, lam_c)
    out['lam_total'] = out['lam'] + lam_c
    return out

theta_u = math.radians(10.0)
U = bemt(theta_u, np.zeros(N))
lam_u_mean = U['CT'] and np.trapezoid(U['lam'] * 2 * r, r) / np.trapezoid(2 * r, r)
# torque balance: find lower collective with CP_l == CP_u (bisection)
lo, hi = math.radians(5), math.radians(18)
for _ in range(80):
    mid = 0.5 * (lo + hi)
    if lower(mid, lam_u_mean)['CP'] < U['CP']:
        lo = mid
    else:
        hi = mid
theta_l = 0.5 * (lo + hi)
L = lower(theta_l, lam_u_mean)

CT = U['CT'] + L['CT']; CP = U['CP'] + L['CP']
FM = CT**1.5 / (math.sqrt(2) * CP)

def rnd(a, n=6):
    return [round(float(x), n) for x in a]

# airfoil sections (NACA 00xx) at stations, in ft for chordwise plot
def naca00(t, n=61):
    x = (1 - np.cos(np.linspace(0, math.pi, n))) / 2
    yt = 5 * t * (0.2969*np.sqrt(x) - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1036*x**4)
    return x, yt
sections = []
for rs in [0.25, 0.50, 0.75, 1.00]:
    cs = c_root + (c_tip - c_root) * (rs - r0) / (1 - r0)
    ts = 0.12 + 0.19 * ((1 - rs) / (1 - r0)) ** 1.6
    x, yt = naca00(ts)
    xs = np.concatenate([x, x[::-1]]) * cs
    ys = np.concatenate([yt, -yt[::-1]]) * cs
    sections.append(dict(r=rs, chord=round(cs, 4), tc=round(ts, 4), x=rnd(xs, 4), y=rnd(ys, 4)))

data = dict(
    meta=dict(title='Harrington Coaxial Rotor 1', subtitle='RCAS rotor report · hover, torque-balanced',
              loads_source='Simple coaxial BEMT estimate (placeholder: replace with RCAS output)',
              loads_is_placeholder=True),
    geometry=dict(R_ft=R, blades_per_rotor=Nb, c_root_ft=round(c_root, 4), c_tip_ft=c_tip, taper=taper,
                  root_cutout=r0, spacing_ft=round(h, 3), spacing_over_D=0.093, twist_deg=0.0,
                  tc_root=0.31, tc_tip=0.12, solidity_published=0.027, solidity_tw=round(float(sigma_tw), 4),
                  Vtip_fps=Vtip, rpm=round(rpm, 1), Mtip=round(Vtip / a_sound, 3),
                  upper_rotation='CCW', pitch_axis_xc=0.25),
    span=dict(r=rnd(r, 4), chord_ft=rnd(c, 4), tc=rnd(tc, 4)),
    sections=sections,
    loads=dict(r=rnd(r, 4),
               upper=dict(theta_deg=round(math.degrees(theta_u), 2), CT=round(U['CT'], 6), CP=round(U['CP'], 7),
                          dCT=rnd(U['dCT']), lam=rnd(U['lam'])),
               lower=dict(theta_deg=round(math.degrees(theta_l), 2), CT=round(L['CT'], 6), CP=round(L['CP'], 7),
                          dCT=rnd(L['dCT']), lam=rnd(L['lam_total'])),
               total=dict(CT=round(CT, 6), CP=round(CP, 7), FM=round(FM, 3)),
               wake_radius=rc),
)
json.dump(data, open(OUT + 'report_data.json', 'w'), separators=(',', ':'))
print('sigma_tw', sigma_tw, 'rpm', rpm)
print('upper', math.degrees(theta_u), U['CT'], U['CP'])
print('lower', math.degrees(theta_l), L['CT'], L['CP'])
print('total CT', CT, 'CP', CP, 'FM', FM, 'Tu/Tl', U['CT'] / L['CT'])

# ---------------- cats ----------------
cats = {f'cat{n:02d}': f'cat{n:02d}.png' for n in range(1, 15)}  # stickers/cat01.png ... cat14.png, numbered in original attachment order
out = {}; total = 0
for k, f in cats.items():
    p = A + f
    im = Image.open(p).convert('RGBA')
    im.thumbnail((320, 320), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'WEBP', quality=82, method=6)
    s = base64.b64encode(b.getvalue()).decode()
    out[k] = dict(src='data:image/webp;base64,' + s, w=im.width, h=im.height)
    total += len(s)
json.dump(out, open(OUT + 'cats.json', 'w'), separators=(',', ':'))
print('cat base64 bytes', total)
