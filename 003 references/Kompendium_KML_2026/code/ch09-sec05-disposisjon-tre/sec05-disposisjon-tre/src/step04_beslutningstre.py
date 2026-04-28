"""
Steg 4: Beslutningstre lært fra optimale merkelapper
======================================================
Cut-off-politikken fra steg 3 bruker kun tilstandsscore c. Her lærer vi
et CART-beslutningstre som kan bruke flere features (tilstand, alder,
merke, kosmetisk/funksjonell grad) for å predikere optimal handling.

Treningsetikettene er den handlingen som maksimerer EV for hver enhet
(kolonnen `optimal_action` fra steg 2).
"""

import json
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, plot_tree, export_text

from step01_datainnsamling import BRANDS
from step02_verdimodell import ACTIONS

OUTPUT_DIR = Path(__file__).parent.parent / 'output'

FEATURES = ['condition', 'age_months', 'cosmetic_grade', 'functional_grade'] + \
           [f'brand_{b}' for b in BRANDS]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot-enkode merke og returnere feature-matrisen."""
    X = df[['condition', 'age_months', 'cosmetic_grade', 'functional_grade']].copy()
    for b in BRANDS:
        X[f'brand_{b}'] = (df['brand'] == b).astype(int)
    return X


def train_tree(df: pd.DataFrame, max_depth: int = 4, random_state: int = 42):
    """Tren beslutningstre med begrenset dybde for tolkbarhet."""
    X = build_features(df)
    y = df['optimal_action']
    clf = DecisionTreeClassifier(
        criterion='gini',
        max_depth=max_depth,
        min_samples_leaf=20,
        random_state=random_state,
    )
    clf.fit(X, y)
    return clf, X, y


def plot_tree_diagram(clf, X: pd.DataFrame, output_path: Path) -> None:
    """Render beslutningstreet som diagram."""
    fig, ax = plt.subplots(figsize=(15, 8))

    # Bruk fargepalett som matcher handlinger
    plot_tree(
        clf,
        feature_names=list(X.columns),
        class_names=clf.classes_,
        filled=True,
        rounded=True,
        fontsize=9,
        impurity=False,
        ax=ax,
    )
    ax.set_title('Beslutningstre for disposisjonsvalg',
                 fontsize=13, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 4: BESLUTNINGSTRE (SKLEARN)")
    print(f"{'='*60}")

    df = pd.read_csv(OUTPUT_DIR / 'units_with_values.csv')

    clf, X, y = train_tree(df, max_depth=4)
    accuracy = float(clf.score(X, y))
    print(f"\nTrenings-nøyaktighet: {accuracy:.4f}")
    print(f"Antall løvnoder:      {clf.get_n_leaves()}")
    print(f"Dybde:                {clf.get_depth()}")

    # Feature importance
    importances = dict(zip(X.columns, clf.feature_importances_))
    print("\n--- Feature importance ---")
    for feat, imp in sorted(importances.items(), key=lambda kv: -kv[1]):
        print(f"  {feat:>30s}: {imp:.4f}")

    # Tekstrepresentasjon av treet
    tree_text = export_text(clf, feature_names=list(X.columns))
    print("\n--- Tre (tekst) ---")
    print(tree_text)

    summary = {
        'accuracy': round(accuracy, 4),
        'n_leaves': int(clf.get_n_leaves()),
        'depth': int(clf.get_depth()),
        'feature_importance': {
            feat: round(float(imp), 4) for feat, imp in importances.items()
        },
        'classes': list(clf.classes_),
    }
    with open(OUTPUT_DIR / 'step04_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_DIR / 'tree_text.txt', 'w', encoding='utf-8') as f:
        f.write(tree_text)

    with open(OUTPUT_DIR / 'decision_tree.pkl', 'wb') as f:
        pickle.dump({'clf': clf, 'feature_names': list(X.columns)}, f)

    plot_tree_diagram(clf, X, OUTPUT_DIR / 'disp_tree_diagram.png')


if __name__ == '__main__':
    main()
