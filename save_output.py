import pandas as pd


def save_output(recipes, output_path):
    frames = []
    for recipe in recipes:
        frames.append(recipe.data)

    BOM_df = pd.concat(frames)

    # Reorder and drop columns
    BOM_df = BOM_df[['index', 'id_nr', 'Product Naam', 'nr', 'Niveau', 'hf_nr', 'Omschrijving', 'Aantal (Basis)', 'Basiseenheid', 'Materiaalkosten', 'Categorie', 'Nieuwe prijs', 'Oude prijs',
                    'Nieuwe vvp', 'Waste NAV', 'Waste FIN', 'Waste USE', 'Aantal (zonder waste)', 'Aantal (nieuw)', 'Materiaalkosten (nieuw)', 'Delta materiaalkosten', 'Delta Q', 
                    'Delta prijs', 'Delta FIN waste', 'Grammage']]

    # Rename columns
    BOM_df = BOM_df.rename(columns={"index": "Index",
                                    'id_nr': 'Meal ID',
                                    'Product Naam': 'Meal Name',
                                    'nr': 'Volgnummer',
                                    'Niveau': 'Level',
                                    'hf_nr': 'Ingredient ID',
                                    'Omschrijving': 'Ingredient Name',
                                    'Aantal (Basis)': 'Aantal (Basis) (#)',
                                    'Basiseenheid': 'Eenheid (€ / KG-Stuk-Liter-Mtr)',
                                    'Materiaalkosten': 'Materiaalkosten 1.0 (P BOM + Q BOM) (€)',
                                    'Categorie': 'Categorie Master',
                                    'Nieuwe prijs': 'Ingredientprijs p.e. (Actueel) (€)',
                                    'Oude prijs': 'Ingredientprijs p.e. (BOM - Berekend) (€)',
                                    'Nieuwe vvp': 'Materiaalkosten 2.0 (P actueel) (€)',
                                    'Waste NAV': 'Uitval NAV (%)',
                                    'Waste FIN': 'Uitval FIN (%)',
                                    'Waste USE': 'Uitval USE (%)',
                                    'Aantal (zonder waste)': 'Aantal uitval EXL (#)',
                                    'Aantal (nieuw)': 'Aantal uitval USE (#)',
                                    'Materiaalkosten (nieuw)': 'Materiaalkosten 3.0 (P actueel + Q Waste update) (€)',
                                    'Delta materiaalkosten': 'Materiaalkosten (Delta 3.0 vs 1.0) (€)',
                                    'Delta Q': 'Materiaalkosten (Q-effect 3.0 vs 1.0) (€)',
                                    'Delta prijs': 'Materiaalkosten (P-effect 3.0 vs 1.0) (€)',
                                    'Delta FIN waste': 'FIN Waste Impact Waste Update (Delta 3.0 vs 2.0) (€)',
                                    'Grammage': 'Gewicht (kg)'
                                    })
    
    with pd.ExcelWriter(output_path) as writer:
        BOM_df.to_excel(writer, sheet_name="BOM")