import pandas as pd


def save_output(recipes : list,
                output_path : str,
                output_file_sheet_name : str='BOM',
                out_col_order : list=['index', 
                                      'id_nr', 
                                      'Product Naam', 
                                      'nr', 
                                      'Niveau', 
                                      'hf_nr', 
                                      'Omschrijving', 
                                      'Aantal (Basis)', 
                                      'Basiseenheid', 
                                      'Materiaalkosten', 
                                      'Categorie', 
                                      'Nieuwe prijs', 
                                      'Oude prijs',
                                      'Nieuwe vvp', 
                                      'Waste NAV', 
                                      'Waste FIN', 
                                      'Waste USE', 
                                      'Aantal (zonder waste)', 
                                      'Aantal (nieuw)', 
                                      'Materiaalkosten (nieuw)', 
                                      'Delta materiaalkosten', 
                                      'Delta Q', 
                                      'Delta prijs', 
                                      'Delta FIN waste', 
                                      'Grammage'],
                out_col_renames : dict={"index": "Index",
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
                                        'Grammage': 'Gewicht (kg)'}) -> None:
    """
    Save the output to Excel by combining all the Recipes together, and renaming / dropping columns

    Parameters
    ----------
    recipes : list
        list of Recipe objects
    output_path : str
        the path of the output Excel file including the name
    output_file_sheet_name : str
        the name of the output Excel file sheet name
    out_col_order : list
        list of the order in which columns are to appear in the output file. 
        Leaving (or commenting) a column out will drop it
    out_col_renames : dict
        dictionary renaming the columns
    """

    frames = []
    for recipe in recipes:
        frames.append(recipe.bom)

    df = pd.concat(frames)

    # Reorder and drop columns
    df = df[out_col_order]

    # Rename columns
    df = df.rename(columns=out_col_renames)
    
    with pd.ExcelWriter(output_path) as writer:
        df.to_excel(writer, sheet_name=output_file_sheet_name)