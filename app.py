# -*- coding: utf-8 -*-
"""
Applet Streamlit – Exemple 2 (Applications 8, A8.1)
Pré-dimensionnement du renforcement à la flexion d'un tablier continu au moyen du BFUP armé

Lancer localement :  streamlit run app.py
"""
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

import bfup_ex2 as core

st.set_page_config(page_title="BFUP armé – tablier continu | Ex. 2", layout="wide")
D = core.ex2_inputs()

# ----------------------------------------------------------------------------
# Entrées
# ----------------------------------------------------------------------------
with st.sidebar:
    st.header("Données d'entrée")
    st.caption("Valeurs par défaut : énoncé du cours (p. 49-50).")

    st.subheader("Couche de BFUP armé sur appui")
    h_U = st.number_input("h_U [mm]", 30.0, 300.0, D["h_U"], 5.0)
    phi_sU = st.number_input("Ø A_sU [mm]", 8.0, 40.0, D["phi_sU"], 2.0)
    s_sU = st.number_input("Espacement [mm]", 50.0, 300.0, D["s_sU"], 10.0)
    n_layers = st.number_input("Nombre de nappes", 1, 4, int(D["n_layers"]), 1)
    f_Utud = st.number_input("f_Utud – BFUP [MPa]", 0.0, 15.0, D["f_Utud"], 0.5)
    f_sd = st.number_input("f_sd – armature [MPa]", 200.0, 600.0, D["f_sd"], 5.0)

    st.subheader("Section de la poutre sur appui")
    b_part = st.number_input("Largeur participante b_part [m]", 0.5, 6.0, D["b_part"], 0.1)
    h_girder = st.number_input("Hauteur de la poutre [m]", 1.0, 5.0, D["h_girder"], 0.05)
    h_comp = st.number_input("Hauteur comprimée x estimée [m]", 0.2, 3.0, D["h_comp"], 0.05)
    b_web = st.number_input("Largeur comprimée (talon) b_w [m]", 0.2, 2.0, D["b_web"], 0.05)
    stress_block = st.number_input("Bloc de contraintes [-]", 0.5, 1.0, D["stress_block"], 0.05)

    st.subheader("Béton existant")
    f_cd_exam = st.number_input("f_cd (valeur d'examen) [MPa]", 5.0, 60.0, D["f_cd_exam"], 1.0)
    dsig_reserve = st.number_input("Réserve exploitable Δσ [MPa]", 0.0, 30.0, D["dsig_reserve"], 0.5,
                                   help="Part de f_cd non utilisée par le dimensionnement d'origine "
                                        "(cours : 20 MPa actuel vs 12 MPa admis il y a 45 ans).")

    st.subheader("Moments de dimensionnement [kNm]")
    M_sup = st.number_input("M_d sur appui", -50000.0, 0.0, D["M_sup"], 100.0)
    M_span1 = st.number_input("M_d max travée 1", 0.0, 50000.0, D["M_span1"], 100.0)
    M_span2 = st.number_input("M_d max travée 2", 0.0, 50000.0, D["M_span2"], 100.0)
    M_end = st.number_input("M_d appui d'extrémité (schéma)", -50000.0, 0.0, D["M_end"], 100.0)
    deficit_sup = st.slider("Déficit sur appui [%]", 0, 80, int(D["deficit_sup"] * 100)) / 100
    deficit_span = st.slider("Déficit en travée [%]", 0, 80, int(D["deficit_span"] * 100)) / 100
    span_choice = st.selectbox("Travée de référence pour le déficit", core.SPAN_CHOICES)

p = dict(h_U=h_U, phi_sU=phi_sU, s_sU=s_sU, n_layers=n_layers, f_Utud=f_Utud, f_sd=f_sd,
         b_part=b_part, h_girder=h_girder, h_comp=h_comp, b_web=b_web, stress_block=stress_block,
         f_cd_exam=f_cd_exam, dsig_reserve=dsig_reserve, M_sup=M_sup, M_span1=M_span1, M_span2=M_span2,
         M_end=M_end, deficit_sup=deficit_sup, deficit_span=deficit_span, span_choice=span_choice)

r = core.ex2_compute(p)
p = r["p"]
if r["A_U"] <= 0:
    st.error("L'armature occupe plus que la section de la couche de BFUP : vérifier h_U, Ø et l'espacement.")
    st.stop()

# ----------------------------------------------------------------------------
# En-tête et indicateurs
# ----------------------------------------------------------------------------
st.title("Renforcement à la flexion d'un tablier continu – BFUP armé sur appui")
st.markdown("Pré-dimensionnement par redistribution plastique des moments · "
            "*Cours « Structures existantes : chapitres choisis », Applications 8 / A8.1, p. 49-52*")

c1, c2, c3, c4 = st.columns(4)
c1.metric("F_RUd – force du tirant BFUP", f"{r['F_RUd']:.2f} MN",
          f"armature : {r['F_s']/(r['F_s']+r['F_U'])*100:.0f} %", delta_color="off", delta_arrow="off")
c2.metric("ΔM_RUd (100 %)", f"{r['dM']:.1f} MNm", f"y_U = {r['y_U']:.2f} m", delta_color="off", delta_arrow="off")
c3.metric("Exploitation du tirant", f"{r['util']*100:.0f} %",
          f"Δσ_cd = {r['dsig']:.1f} / réserve {p['dsig_reserve']:g} MPa",
          delta_color="normal" if r["util"] >= 1 else "off", delta_arrow="off")
c4.metric("ΔM_RUd,eff vs ΔM_requis", f"{r['dM_eff']:.2f} MNm",
          f"requis {r['dM_req']:.2f} MNm – {'OK' if r['ok'] else 'NON'}",
          delta_color="normal" if r["ok"] else "inverse", delta_arrow="off")

if r["x_over_h"] >= 0.5:
    st.warning(f"x/h = {r['x_over_h']:.2f} ≥ 0.5 : ductilité insuffisante pour admettre la redistribution "
               "plastique des moments.")
if r["util"] < 1:
    st.info(f"La zone comprimée limite le tirant à {r['util']*100:.0f} % de sa capacité "
            f"(Δσ_cd = {r['dsig']:.1f} MPa > réserve {p['dsig_reserve']:g} MPa).")


def fmt_table(df, fmts):
    out = df.copy().astype(object)
    for c, f in fmts.items():
        out[c] = [("" if (v is None or (isinstance(v, float) and np.isnan(v))) else f.format(round(v, 6) + 0.0))
                  for v in df[c]]
    return out


def show(fig, name):
    st.pyplot(fig, width="stretch")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    st.download_button("Télécharger la figure (PNG)", buf.getvalue(), file_name=name, mime="image/png", key=name)


GE = lambda ok: r"\geq" if ok else "<"
CMP_SIG = ">" if r["dsig"] > p["dsig_reserve"] else r"\leq"

tab1, tab2, tab3, tab4 = st.tabs(["1) Augmentation ΔM_RUd", "2) Redistribution plastique",
                                  "Étude paramétrique", "3) Discussion et notes"])

# ----------------------------------------------------------------------------
with tab1:
    fig, ax = plt.subplots(1, 2, figsize=(15, 5), gridspec_kw=dict(width_ratios=[1.1, 1], wspace=0.15))
    core.draw_layer(ax[0], r)
    core.draw_tie_model(ax[1], r)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.03)
    show(fig, "ex2_tirant.png")
    left, right = st.columns([1, 1.15])
    with left:
        st.markdown("**Force de traction du tirant en BFUP armé (valeur de dimensionnement)**")
        df = pd.DataFrame([["A_sU · f_sd", r["A_sU"], p["f_sd"], r["F_s"], r["F_s"] * p["b_part"] / 1e3],
                           ["A_U · f_Utud", r["A_U"], p["f_Utud"], r["F_U"], r["F_U"] * p["b_part"] / 1e3],
                           ["Σ = F_RUd", np.nan, np.nan, r["F_s"] + r["F_U"], r["F_RUd"]]],
                          columns=["", "A [mm²/m]", "f [MPa]", "F [kN/m]", f"F × {p['b_part']:g} m [MN]"])
        st.dataframe(fmt_table(df, {"A [mm²/m]": "{:.0f}", "f [MPa]": "{:.1f}", "F [kN/m]": "{:.0f}",
                                    f"F × {p['b_part']:g} m [MN]": "{:.2f}"}), hide_index=True, width="stretch")
        st.caption(f"ρ_s,U = A_sU/A_U = {r['A_sU']:.0f}/{r['A_U']:.0f} = {r['rho']*100:.1f} %. "
                   f"La contribution du BFUP ({r['F_U']/(r['F_s']+r['F_U'])*100:.0f} %) reste limitée à l'ELU.")
    with right:
        st.latex(rf"F_{{RUd}} = b_{{part}}\,(A_{{sU}} f_{{sd}} + A_U f_{{Utud}}) = {p['b_part']:g}\,"
                 rf"({r['F_s']:.0f} + {r['F_U']:.0f})\ \mathrm{{kN}} = {r['F_RUd']:.2f}\ \mathrm{{MN}}")
        st.latex(rf"y_U = h - \tfrac{{x}}{{2}} - \tfrac{{h_U}}{{2}} = {p['h_girder']:g} - {p['h_comp']/2:g} - "
                 rf"{p['h_U']/2000:.2f} = {r['y_U']:.2f}\ \mathrm{{m}}")
        st.latex(rf"\Delta M_{{RUd}} = y_U\,F_{{RUd}} = {r['y_U']:.2f}\cdot{r['F_RUd']:.2f} = {r['dM']:.1f}\ \mathrm{{MNm}}")
        st.latex(rf"\Delta\sigma_{{cd}} = \frac{{F_{{RUd}}}}{{A_{{cc}}}} = \frac{{{r['F_RUd']:.2f}}}"
                 rf"{{{p['b_web']:g}\cdot{p['stress_block']*p['h_comp']:.2f}}} = {r['dsig']:.1f}\ \mathrm{{MPa}}"
                 rf"\ {CMP_SIG}\ {p['dsig_reserve']:g}\ \mathrm{{MPa}}")
        st.latex(rf"\Rightarrow\ \text{{exploitation}} = {min(1, p['dsig_reserve']/r['dsig'])*100:.0f}\,\%"
                 rf"\ \Rightarrow\ \Delta M_{{RUd,eff}} = {r['dM_eff']:.2f}\ \mathrm{{MNm}}")

# ----------------------------------------------------------------------------
with tab2:
    fig, ax = plt.subplots(1, 2, figsize=(15, 5), gridspec_kw=dict(width_ratios=[2.2, 1], wspace=0.25))
    core.draw_moments(ax[0], r)
    core.draw_balance(ax[1], r)
    fig.subplots_adjust(left=0.07, right=0.98, top=0.9, bottom=0.12)
    show(fig, "ex2_redistribution.png")
    st.markdown("L'augmentation en travée par la couche mince (45 mm) est négligée ; avec une redistribution "
                "plastique des moments de la travée vers l'appui, le renforcement sur appui doit reprendre "
                "la totalité des déficits.")
    st.latex(rf"\Delta M_{{requis}} = {p['deficit_sup']*100:.0f}\,\%\cdot{abs(p['M_sup'])/1e3:.2f} + "
             rf"{p['deficit_span']*100:.0f}\,\%\cdot{r['M_span']/1e3:.2f} = {r['d_sup']:.2f} + {r['d_span']:.2f}"
             rf" = {r['dM_req']:.2f}\ \mathrm{{MNm}}")
    st.latex(rf"\Delta M_{{RUd,eff}} = {r['dM_eff']:.2f}\ {GE(r['ok'])}\ \Delta M_{{requis}} = {r['dM_req']:.2f}"
             rf"\ \mathrm{{MNm}}")
    (st.success if r["ok"] else st.error)(
        "Le renforcement sur appui reprend la totalité des déficits (sous réserve d'une ductilité suffisante)."
        if r["ok"] else "Le renforcement sur appui ne suffit pas à reprendre les déficits.")

# ----------------------------------------------------------------------------
with tab3:
    PARAMS = {
        "h_U – épaisseur BFUP [mm]": ("h_U", 40.0, 250.0),
        "Ø A_sU [mm]": ("phi_sU", 10.0, 32.0),
        "Espacement A_sU [mm]": ("s_sU", 60.0, 250.0),
        "b_w – largeur comprimée [m]": ("b_web", 0.3, 1.5),
        "Réserve Δσ du béton [MPa]": ("dsig_reserve", 2.0, 20.0),
        "Hauteur comprimée x [m]": ("h_comp", 0.5, 1.8),
        "b_part – largeur participante [m]": ("b_part", 1.0, 4.0),
    }
    a, b = st.columns([1, 2.2])
    with a:
        lab = st.selectbox("Paramètre", list(PARAMS))
        key, lo, hi = PARAMS[lab]
        rng = st.slider("Plage", lo, hi, (lo, hi))
    vals = np.linspace(rng[0], rng[1], 41)
    rows = []
    for v in vals:
        q = dict(p)
        q[key] = v
        rr = core.ex2_compute(q)
        rows.append((v, rr["dM"], rr["dM_eff"], rr["dM_req"], rr["util"]) if rr["A_U"] > 0
                    else (v, np.nan, np.nan, np.nan, np.nan))
    o = np.array(rows, dtype=float)
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.plot(o[:, 0], o[:, 1], color="#92c5de", label="ΔM_RUd (100 %)")
    ax.plot(o[:, 0], o[:, 2], color=core.C_TENS, lw=2, label="ΔM_RUd,eff")
    ax.plot(o[:, 0], o[:, 3], color=core.C_COMP, ls="--", label="ΔM_requis")
    ax.axvline(p[key], color="0.6", ls=":", lw=0.9)
    ax.set_xlabel(lab)
    ax.set_ylabel("[MNm]")
    ax2 = ax.twinx()
    ax2.plot(o[:, 0], o[:, 4] * 100, color="0.45", lw=0.9, ls="-.", label="exploitation [%]")
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("exploitation du tirant [%]", color="0.45")
    ax2.spines["right"].set_visible(True)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=8, ncol=2, loc="upper left")
    fig.tight_layout()
    with b:
        st.pyplot(fig, width="stretch")
    plt.close(fig)
    st.caption("Tant que l'exploitation est < 100 %, augmenter l'armature ou h_U n'augmente pas ΔM_RUd,eff : "
               "c'est la zone comprimée qui gouverne.")
    st.download_button("Télécharger les résultats (CSV)",
                       pd.DataFrame(o, columns=[key, "dM_RUd", "dM_RUd_eff", "dM_requis", "exploitation"]).to_csv(index=False),
                       file_name=f"ex2_parametrique_{key}.csv", mime="text/csv")

# ----------------------------------------------------------------------------
with tab4:
    st.markdown("**Indicateurs pour la discussion (point 3)**")
    i1, i2, i3 = st.columns(3)
    i1.metric("b_w requis pour exploiter 100 % du tirant", f"{r['b_web_full']:.2f} m",
              f"actuel {p['b_web']:g} m", delta_color="off", delta_arrow="off")
    i2.metric("Force de tirant nécessaire", f"{r['F_req']:.2f} MN",
              f"mobilisable {min(r['F_RUd'], r['F_RUd_useful']):.2f} MN", delta_color="off", delta_arrow="off")
    i3.metric("Ductilité : x / h", f"{r['x_over_h']:.2f}", "< 0.50 requis",
              delta_color="normal" if r["x_over_h"] < 0.5 else "inverse", delta_arrow="off")
    st.markdown(f"""
**Pistes d'amélioration (cours)**
- Sur appui : agrandir la zone comprimée (épaissir le talon de la poutre au moyen du BFUP) ou augmenter
  l'armature passive de la couche de BFUP — cette dernière n'est utile que si l'exploitation atteint 100 %.
- En travée : lamelles en fibres de carbone collées sous le talon tendu.
- La couche de 120 mm est surdimensionnée pour la flexion seule ; elle est aussi choisie pour l'effort
  tranchant (A8.2).

**Hypothèses du modèle**
- La couche de BFUP armé agit comme tirant additionnel entièrement plastifié (f_sd pour l'armature, f_Utud pour
  le BFUP) sur la largeur participante b_part.
- Bras de levier y_U = h − x/2 − h_U/2, avec x estimée ; aucune analyse en section n'est faite (pré-dimensionnement).
- La compression supplémentaire est reprise par le béton existant sur b_w × (bloc × x), dans la limite de la
  réserve Δσ entre f_cd actuel et la valeur admise à l'origine.
- Le diagramme des moments est un schéma reconstruit à partir des valeurs clés du cours (paraboles par travée).

**Écarts relevés dans le corrigé du cours**
- Bras de levier : le texte donne 1.84 m puis calcule avec 1.83 m ; ΔM_RUd = 12.6 MNm dans les deux cas.
- 68 % × 12.6 = 8.6 MNm (corrigé, arrondis) contre {r['dM_eff']:.2f} MNm sans arrondi ; la conclusion ne change pas.
- Le déficit en travée (3.19 MNm) est calculé sur la travée 2 (15 936.73 kNm) ; avec la travée 1 il vaut
  {p['deficit_span']*p['M_span1']/1e3:.2f} MNm (option « Travée de référence »).
""")
