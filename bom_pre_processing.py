""" Pre-processing of the BOM (Bill of Materials) data """


from Recipe import *


def split_raw_bom(bom_data_raw : pd.DataFrame) -> list:
    """ 
    Split the raw BOM data into a list of Recipe objects.

    Parameters
    ----------
    bom_data_raw : pd.DataFrame
        the DataFrame containing the raw BOM data

    Returns
    -------
    recipes : list
        list of Recipe objects
    """

    recipes = []

    for i in range(len(bom_data_raw)):
        # a new recipe starts
        if bom_data_raw[4][i] == 'Omschrijving':
            start_idx = i + 1
            recipe_name = bom_data_raw[4][start_idx]
            recipe_id = bom_data_raw[3][start_idx]

            # the recipe ends
            for j in range(i, len(bom_data_raw)):
                if bom_data_raw[3][j] == 'Kostenaandeel voor dit artikel':
                    recipe_bom = bom_data_raw.iloc[(start_idx + 1):j].drop(range(8, 13), axis='columns').reset_index()
                    recipe_bom = recipe_bom.rename(columns={0: "id_nr", 
                                                            1: "nr", 
                                                            2: "Niveau", 
                                                            3: "hf_nr", 
                                                            4: "Omschrijving", 
                                                            5: "Aantal (Basis)", 
                                                            6: "Basiseenheid", 
                                                            7: "Materiaalkosten"})
                    recipe_bom = recipe_bom.astype({"id_nr": str, 
                                                    "nr": int, 
                                                    "Niveau": int, 
                                                    "hf_nr": str, 
                                                    "Omschrijving": str, 
                                                    "Aantal (Basis)": float, 
                                                    "Basiseenheid": str, 
                                                    "Materiaalkosten": float})
                    recipe_bom.insert(loc=2, column="Product Naam", value=[recipe_name for _ in range(len(recipe_bom))])
                    recipes.append(Recipe(name=recipe_name, id=recipe_id, bom=recipe_bom))
                    i += j
                    break
    
    return recipes


def drop_inactive_recipes(recipes : list, 
                          active_recipes : pd.DataFrame, 
                          active_recipes_col : str,
                          active_recipes_id_col : str='Artikel',
                          active_recipes_class : str='Actief') -> list:
    """
    Drop inactive Recipes from the recipes list.

    Parameters
    ----------
    recipes : list
        list of Recipe objects
    active_recipes : pd.DataFrame
        DataFrame containing the active recipe data
    active_recipes_col : str
        the name of the active_recipes column containing the active classification
    active_recipes_id_col : str
        the name of the active_recipes column containing the ids
    active_recipes_class : str
        the classification for an active recipe

    returns
    -------
    act_recipes : list
        list of active Recipe objects
    """

    recipes_temp = []
    for recipe in recipes:
        if str(recipe.id) in np.array(active_recipes[active_recipes[active_recipes_col] == active_recipes_class][active_recipes_id_col]).astype(str):
            recipes_temp.append(recipe)

    act_recipes = recipes_temp

    return act_recipes


def pre_process_bom(bom_data_raw : pd.DataFrame, active_recipes : pd.DataFrame, active_recipes_col : str) -> list:
    """
    Pre-process the raw BOM data.

    Splits the raw BOM data up into Recipe objects, and drops the inactive recipes.

    Parameters
    ----------
    bom_data_raw : pd.DataFrame
        the DataFrame containing the raw BOM data
    active_recipes : pd.DataFrame
        DataFrame containing the active recipe data
    active_recipes_col : str
        the name of the active_recipes column containing the active classification

    Returns
    -------
    recipes : list
        list of active Recipe objects
    """

    all_recipes = split_raw_bom(bom_data_raw)
    recipes = drop_inactive_recipes(all_recipes, active_recipes, active_recipes_col)

    return recipes