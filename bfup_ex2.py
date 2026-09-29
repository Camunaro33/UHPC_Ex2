# -*- coding: utf-8 -*-
"""
bfup_ex2.py – noyau de calcul et de tracé de l'exemple 2 (Applications 8, A8.1)
Pré-dimensionnement du renforcement à la flexion d'un tablier continu au moyen du BFUP armé
(couche épaisse sur appui intermédiaire, redistribution plastique des moments).

Cours « Structures existantes : chapitres choisis », p. 49-52.
Unités : entrées en mm, m, MPa, kNm ; résultats en kN/m, MN, MNm.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

B = 1000.0  # largeur de référence [mm]
C_CONC, C_UHPC, C_STEEL, C_COMP, C_TENS, C_NA = "0.85", "0.55", "k", "#b2182b", "#2166ac", "#d6604d"

plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "axes.titleweight": "bold",
                     "axes.spines.top": False, "axes.spines.right": False})

SPAN_CHOICES = ("travée 2 (corrigé)", "travée 1", "max des deux travées")


def ex2_inputs():
    return dict(
        h_U=120.0, phi_sU=20.0, s_sU=100.0, n_layers=2,
        f_Utud=6.0, E_U=45000.0, eps_Utu=2.0, f_sd=435.0, E_s=205000.0,
        b_part=2.0,                  # largeur participante [m] par poutre
        h_girder=2.5, h_comp=1.2,    # hauteur totale [m], hauteur comprimée estimée [m]
        b_web=0.6, stress_block=0.8,  # largeur comprimée [m], bloc de contraintes [-]
        f_cd_exam=20.0, dsig_reserve=8.0,  # [MPa] valeur d'examen, réserve exploitable
        M_sup=-8971.95, M_span1=16183.68, M_span2=15936.73, M_end=-7532.4,  # [kNm]
        M_min1=6507.95, M_min2=3728.26,
        deficit_sup=0.30, deficit_span=0.20,
        span_choice=SPAN_CHOICES[0],
    )


def bar_area(phi, s):
    return np.pi * phi**2 / 4.0 * B / s


def ex2_compute(p=None):
    p = ex2_inputs() if p is None else {**ex2_inputs(), **p}
    A_sU = p["n_layers"] * bar_area(p["phi_sU"], p["s_sU"])
    A_U = B * p["h_U"] - A_sU
    rho = A_sU / A_U
    F_s = A_sU * p["f_sd"] / 1e3                     # kN/m
    F_U = A_U * p["f_Utud"] / 1e3                    # kN/m
    F_RUd = p["b_part"] * (F_s + F_U) / 1e3          # MN
    y_U = p["h_girder"] - p["h_comp"] / 2 - p["h_U"] / 2 / 1000
    dM = y_U * F_RUd                                 # MNm
    A_cc = p["b_web"] * p["stress_block"] * p["h_comp"]
    dsig = F_RUd / A_cc                              # MPa
    util = min(1.0, p["dsig_reserve"] / dsig)
    dM_eff = util * dM
    M_span = {"travée 1": p["M_span1"], "max des deux travées": max(p["M_span1"], p["M_span2"])}.get(
        p["span_choice"], p["M_span2"])
    d_sup = p["deficit_sup"] * abs(p["M_sup"]) / 1e3
    d_span = p["deficit_span"] * M_span / 1e3
    dM_req = d_sup + d_span
    # pistes d'amélioration (discussion, point 3)
    b_web_full = F_RUd / (p["dsig_reserve"] * p["stress_block"] * p["h_comp"])   # largeur pour exploiter 100 %
    F_RUd_useful = p["dsig_reserve"] * A_cc                                        # MN mobilisables
    F_req = dM_req / y_U                                                            # MN requis
    return dict(p=p, A_sU=A_sU, A_U=A_U, rho=rho, F_s=F_s, F_U=F_U, F_RUd=F_RUd, y_U=y_U, dM=dM,
                A_cc=A_cc, dsig=dsig, util=util, dM_eff=dM_eff, M_span=M_span, d_sup=d_sup,
                d_span=d_span, dM_req=dM_req, ok=dM_eff >= dM_req, b_web_full=b_web_full,
                F_RUd_useful=F_RUd_useful, F_req=F_req, x_over_h=p["h_comp"] / p["h_girder"])


def _bisect(f, a, b, tol=1e-7, nmax=300):
    fa = f(a)
    for _ in range(nmax):
        m = 0.5 * (a + b)
        fm = f(m)
        if abs(b - a) < tol:
            break
        if fa * fm <= 0:
            b = m
        else:
            a, fa = m, fm
    return 0.5 * (a + b)


def parabola_span(Ma, Mb, Mpeak, n=200):
    """Parabole entre moments d'extrémité Ma, Mb dont l'extremum (positif) vaut Mpeak (schéma)."""
    xi = np.linspace(0, 1, n)
    f = lambda M0: (Ma * (1 - xi) + Mb * xi + 4 * M0 * xi * (1 - xi)).max() - Mpeak
    M0 = _bisect(f, 0, 5 * (abs(Mpeak) + abs(Ma) + abs(Mb)))
    return xi, Ma * (1 - xi) + Mb * xi + 4 * M0 * xi * (1 - xi)


# ----------------------------------------------------------------------------
# Tracés
# ----------------------------------------------------------------------------
def draw_layer(ax, r):
    p = r["p"]
    w, hU, n = 1000.0, p["h_U"], int(p["n_layers"])
    ax.add_patch(Rectangle((0, -40), w, 40, fc=C_CONC, ec="k", hatch="///", lw=0.6))
    ax.add_patch(Rectangle((0, 0), w, hU, fc=C_UHPC, ec="k", lw=0.8))
    levels = [hU / 2] if n == 1 else list(np.linspace(0.62, 0.38, n) * hU)
    ms = max(3, min(8, p["phi_sU"] / 3))
    for i, lvl in enumerate(levels):
        xs = np.arange(p["s_sU"] / 2 + (i % 2) * p["s_sU"] / 2, w, p["s_sU"])
        ax.plot(xs, [lvl] * len(xs), "o", color=C_STEEL, ms=ms)
    ax.annotate("", (-40, 0), (-40, hU), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(-60, hU / 2, f"h_U =\n{hU:.0f} mm", ha="right", va="center", fontsize=8)
    ax.text(w / 2, hU + 20, f"Ø{p['phi_sU']:.0f} @ {p['s_sU']:.0f} mm, {n} nappe{'s' if n > 1 else ''} → "
            f"A_sU = {r['A_sU']:.0f} mm²/m  (ρ = {r['rho']*100:.1f} %)", ha="center")
    ax.text(w / 2, -70, "béton existant", ha="center", va="top", fontsize=8)
    ax.set_xlim(-280, w + 50)
    ax.set_ylim(-160, hU + 90)
    ax.axis("off")
    ax.set_title("Couche de BFUP armé sur appui (1 m)")


def draw_tie_model(ax, r):
    p = r["p"]
    H, bw = p["h_girder"], p["b_web"]
    hb = min(0.4, 0.3 * H)
    ax.add_patch(Polygon([(-1.0, H), (1.0, H), (1.0, H - 0.2), (0.1, H - 0.2), (0.1, hb), (bw / 2, hb),
                          (bw / 2, 0), (-bw / 2, 0), (-bw / 2, hb), (-0.1, hb), (-0.1, H - 0.2), (-1.0, H - 0.2)],
                         fc=C_CONC, ec="k", lw=0.8))
    ax.add_patch(Rectangle((-1.0, H), 2.0, max(0.05, p["h_U"] / 1000), fc=C_UHPC, ec="k"))
    ax.add_patch(Rectangle((-bw / 2, 0), bw, p["stress_block"] * p["h_comp"], fc=C_COMP, alpha=0.35, ec="none"))
    ax.axhline(p["h_comp"], color=C_NA, ls="--", lw=0.8)
    ax.text(1.05, p["h_comp"], f"x ≈ {p['h_comp']:g} m", color=C_NA, va="center", fontsize=8)
    ax.annotate("", (0.75, H + 0.06), (0.75, p["h_comp"] / 2), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(0.8, (H + p["h_comp"] / 2) / 2, f"y_U = {r['y_U']:.2f} m", fontsize=8)
    ax.annotate("", (-1.45, H + 0.06), (-1.0, H + 0.06), arrowprops=dict(arrowstyle="-|>", color=C_TENS, lw=2))
    ax.text(-1.45, H + 0.2, f"F_RUd = {r['F_RUd']:.2f} MN", color=C_TENS, fontsize=8)
    ax.annotate("", (-bw / 2 - 0.45, 0.48 * hb / 0.4), (-bw / 2, 0.48 * hb / 0.4),
                arrowprops=dict(arrowstyle="<|-", color=C_COMP, lw=2))
    ax.text(-1.55, 0.62, f"Δσ_cd = {r['dsig']:.1f} MPa\nsur A_cc = {r['A_cc']:.2f} m²",
            color=C_COMP, fontsize=8)
    ax.set_xlim(-1.6, 1.7)
    ax.set_ylim(-0.1, H + 0.45)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"Modèle de section sur appui (b_part = {p['b_part']:g} m)")


def draw_moments(ax, r):
    p = r["p"]
    x1, m1 = parabola_span(0.0, p["M_sup"], p["M_span1"])
    x2, m2 = parabola_span(p["M_sup"], p["M_end"], p["M_span2"])
    X, M = np.r_[x1, 1 + x2], np.r_[m1, m2]
    ax.fill_between(X, 0, M, color=C_COMP, alpha=0.15)
    ax.plot(X, M, color=C_COMP)
    ax.axhline(0, color="k", lw=0.6)
    for xx, mm in ((x1[np.argmax(m1)], p["M_span1"]), (1.0, p["M_sup"]),
                   (1 + x2[np.argmax(m2)], p["M_span2"]), (2.0, p["M_end"])):
        ax.plot(xx, mm, "o", color=C_COMP, ms=4)
        ax.text(xx, mm, f"  {mm:.2f}", fontsize=8, va="bottom" if mm > 0 else "top")
    MR_sup0 = (1 - p["deficit_sup"]) * p["M_sup"]
    MR_span0 = (1 - p["deficit_span"]) * r["M_span"]
    MR_sup1 = MR_sup0 - r["dM_eff"] * 1e3
    ax.hlines(MR_sup0, 0.8, 1.2, color="0.4", ls="--")
    ax.text(1.21, MR_sup0, f"M_Rd,0 appui ≈ {MR_sup0:.0f}", fontsize=7.5, va="center")
    ax.hlines(MR_span0, 1.3, 1.7, color="0.4", ls="--")
    ax.text(1.71, MR_span0, f"M_Rd,0 travée ≈ {MR_span0:.0f}", fontsize=7.5, va="center")
    ax.hlines(MR_sup1, 0.8, 1.2, color=C_TENS, lw=1.5)
    ax.text(1.21, MR_sup1, f"M_Rd,1 appui renforcé ≈ {MR_sup1:.0f}", fontsize=7.5, va="center", color=C_TENS)
    ax.invert_yaxis()  # moments positifs vers le bas (convention du cours)
    ax.set_xticks([0, 1, 2], ["appui", "appui interm.", "appui"])
    ax.set_ylabel("M_d [kNm]")
    ax.set_title("Moments de dimensionnement (schéma à partir des valeurs clés)")
    ax.text(0.01, 0.02, f"enveloppe inférieure (cours) : {p['M_min1']:.2f} / {p['M_min2']:.2f} kNm",
            transform=ax.transAxes, fontsize=7.5)


def draw_balance(ax, r):
    lab = ["déficit\nappui", "déficit\ntravée", "ΔM\nrequis", "ΔM_RUd\n(100 %)", f"ΔM_RUd\n({r['util']*100:.0f} %)"]
    val = [r["d_sup"], r["d_span"], r["dM_req"], r["dM"], r["dM_eff"]]
    b = ax.bar(lab, val, color=["0.75", "0.75", C_COMP, "#92c5de", C_TENS], width=0.6)
    ax.bar_label(b, fmt="%.2f", fontsize=8)
    ax.set_ylabel("[MNm]")
    ax.set_title("Demande vs apport du renforcement")


def figure(r):
    fig = plt.figure(figsize=(17, 9.5))
    gs = fig.add_gridspec(2, 4, height_ratios=[1.1, 1], hspace=0.3, wspace=0.28,
                          left=0.05, right=0.98, top=0.94, bottom=0.07)
    draw_layer(fig.add_subplot(gs[0, 0]), r)
    draw_tie_model(fig.add_subplot(gs[0, 1]), r)
    draw_moments(fig.add_subplot(gs[0, 2:]), r)
    draw_balance(fig.add_subplot(gs[1, 3]), r)
    return fig


if __name__ == "__main__":
    r = ex2_compute()
    print(f"F_RUd = {r['F_RUd']:.2f} MN ; ΔM_RUd = {r['dM']:.1f} MNm ; Δσ_cd = {r['dsig']:.1f} MPa ; "
          f"exploitation {r['util']*100:.0f} % ; ΔM_eff = {r['dM_eff']:.2f} vs ΔM_req = {r['dM_req']:.2f} MNm")
    figure(r)
    plt.show()
