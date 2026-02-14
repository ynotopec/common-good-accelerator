# Architecture Minimale – Accélérateur de Bien Commun
(Spécification de Référence)

## 1. Principe Fondamental
L'optimisation ne naît pas de l'architecture logicielle, mais de la **résistance du réel**.
Pour qu'il y ait direction (amélioration), il faut qu'il y ait contrainte (ancrage).

## 2. Triade Irréductible

1.  **L’État ($S$)**
    La représentation courante du système.

2.  **La Fonction d'Ancrage ($f$)**
    Mesure la divergence entre l'état $S$ et le Bien Commun.
    *Condition critique :* $f$ doit être une **hard constraint** (données, oracle, règles) et non une auto-évaluation.

3.  **L'Opérateur de Mise à jour ($\pi$)**
    L'intelligence qui transforme le signal d'erreur en correction.

## 3. Formalisation

Le système est une fonction récursive dirigée :

[
S_{t+1} = \pi\big(S_t, f(S_t)\big)
]

**Détail du signal $f(S_t)$ :**
Il fournit la **direction** de la correction.
*   *Cas continu :* Gradient mathématique (intensité + vecteur).
*   *Cas discret :* Signal binaire, rapport d'erreur ou score scalaire.

## 4. Invariant de Sécurité

La séparation physique est optionnelle.
La hiérarchie logique est absolue :

> **La fonction d'ancrage $f$ contraint l'opérateur $\pi$.**
> (L'intelligence sert la métrique, elle ne la définit pas.)

---

## Conclusion

Le système minimal est :
**Un état persistant ($S$) piloté par une intelligence ($\pi$) asservie à une réalité mesurable ($f$).**
