# BFUP armé – tablier continu : applet de l'exemple 2 (A8.1)

Applet Streamlit qui reproduit l'application 8 / A8.1 (p. 49-52) du cours « Structures existantes : chapitres choisis » : pré-dimensionnement du renforcement à la flexion d'un tablier continu (viaduc, 15 travées) au moyen d'une couche épaisse de BFUP armé sur appui intermédiaire.

- **1) Augmentation ΔM_RUd** : force du tirant F_RUd = b_part (A_sU f_sd + A_U f_Utud), bras de levier y_U, ΔM_RUd, contrainte de compression supplémentaire Δσ_cd dans le béton et taux d'exploitation du tirant limité par la réserve de résistance du béton.
- **2) Redistribution plastique** : diagramme des moments (schéma à partir des valeurs clés), déficits sur appui et en travée, comparaison ΔM_RUd,eff ≥ ΔM_requis.
- **Étude paramétrique** : ΔM_RUd, ΔM_RUd,eff, ΔM_requis et exploitation en fonction de h_U, de l'armature, de b_w, de la réserve Δσ, de x ou de b_part, avec export CSV.
- **3) Discussion** : largeur comprimée nécessaire pour exploiter 100 % du tirant, contrôle de ductilité x/h < 0.5, pistes d'amélioration, hypothèses et écarts relevés dans le corrigé.

Toutes les entrées sont modifiables dans la barre latérale ; les valeurs par défaut sont celles de l'énoncé.

## Lancer localement

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Déployer sur Streamlit Community Cloud

1. Pousser ce dossier dans un dépôt GitHub.
2. Sur [share.streamlit.io](https://share.streamlit.io) : **Create app**, puis indiquer l'URL du fichier, au format
   `https://github.com/<utilisateur>/<depot>/blob/main/app.py`.
3. **Deploy**. L'applet est redéployée à chaque `git push`.

## Structure

| Fichier | Rôle |
|---|---|
| `app.py` | Interface Streamlit |
| `bfup_ex2.py` | Calculs et fonctions de tracé ; utilisable seul dans Spyder (`python bfup_ex2.py`) |
| `test_app.py` | Tests : valeurs du corrigé et exécution de l'applet (`pytest`) |
| `requirements.txt` | Dépendances |
| `.streamlit/config.toml` | Thème |

## Écarts relevés dans le corrigé du cours

- Bras de levier : le texte donne 1.84 m puis calcule avec 1.83 m ; ΔM_RUd = 12.6 MNm dans les deux cas.
- 68 % × 12.6 = 8.6 MNm (valeurs arrondies) contre 8.48 MNm sans arrondi ; la conclusion ne change pas.
- Le déficit en travée (3.19 MNm) est calculé sur la travée 2 (15 936.73 kNm) ; l'option « Travée de référence » permet d'utiliser la travée 1 (3.24 MNm).

Unités : entrées en mm, m, MPa, kNm ; résultats en kN/m, MN, MNm.
