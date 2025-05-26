""" Creation and splitting of the product master """


import pandas as pd
import numpy as np


def create_product_master(recipes : list, 
                          id_column : str='hf_nr', 
                          level_column : str='Niveau',
                          out_col_name_id : str='Nummer',
                          out_col_name_class : str='Categorie') -> pd.DataFrame:
    """
    Create a product master out of a list of Recipes.

    The logic being applied to determine a classification is the following:
    - If an item starts with '3' --> packaging ('Verpakking'), else
    - If an item has a child --> HF ('Halffabrikaat'), else
    - Item --> ingredient ('Ingredient')

    Parameters
    ----------
    recipes : list
        list of Recipe objects
    id_column : str
        the name of the Recipe.bom column containing the item ids
    level_column : str
        the name of the Recipe.bom column containing the levels
    out_col_name_id : str
        the name of the output product_master column containing the ids
    out_col_name_class : str
        the name of the output product_master column containing the classifications

    Returns
    -------
    product_master : pd.DataFrame
        DataFrame containing the product master
    """

    product_master_dict = {}

    for recipe in recipes:
        for i in range(len(recipe.bom)):
            item_id = recipe.bom[id_column][i]

            if not item_id in product_master_dict.keys():
                if item_id.startswith('3'):
                    classification = 'Verpakking'
                elif not i + 1 == len(recipe.bom):
                    if recipe.bom[level_column][i + 1] > recipe.bom[level_column][i]:
                        classification = 'Halffabrikaat'
                    else:
                        classification = 'Ingredient'
                else:
                    classification = 'Ingredient'
            
                product_master_dict[item_id] = [item_id, classification]

    product_master = pd.DataFrame.from_dict(product_master_dict, orient='index', columns=[out_col_name_id, out_col_name_class]).reset_index(drop=True)

    return product_master


def split_product_master(product_master : pd.DataFrame,
                         cat_name : str,
                         cat_column : str='Categorie',
                         id_column : str='Nummer') -> np.array:
    """
    Split the product_master data into a NumPy array containing the ids of only 1 category.

    NumPy arrays containing just the category ids are used for faster checking against

    Parameters
    ----------
    product_master : pd.DataFrame
        DataFrame containing the product master
    cat_name : str
        the name of the specific category to look for
    cat_column : str
        the name of the product_master column containing the categories
    id_column : str
        the name of the product_master column containing the ids

    Returns
    -------
    split_array : np.array
        NumPy array containing the ids of 1 category
    """

    split_array = np.array(product_master[product_master[cat_column] == cat_name][id_column])

    return split_array


def process_product_master(recipes : list, 
                           categories : list=['Ingredient', 'Verpakking', 'Halffabrikaat']) -> tuple:
    """
    Fully process the product master. from creation to splitting.

    First create the product master using a list of Recipes (see create_product_master() for details on how).
    Then split the product master into a tuple of NumPy arrays for each category (see split_product_master()).

    Parameters
    ----------
    recipes : list
        list of Recipe objects
    categories : list
        list containing the categories to split the product_master into

    Returns
    -------
    split_data : tuple
        tuple containing a NumPy array of ids per category
    """

    product_master = create_product_master(recipes)

    split_data = []
    for cat in categories:
        split_data.append(split_product_master(product_master, cat))
    
    split_data = tuple(split_data)

    return split_data
