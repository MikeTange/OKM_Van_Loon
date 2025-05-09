""" Processing the OKM data """


from Recipe import *


def process_recipes(recipes : list,
                    ingredients : np.array, 
                    HFs : np.array, 
                    packagings : np.array,
                    price_data : pd.DataFrame,
                    prices_col : str,
                    price_data_id_col : str,
                    weight_data : pd.DataFrame,
                    waste_data : pd.DataFrame) -> list[Recipe]:
    """ 
    Process all Recipes in the recipes list

    Parameters
    ----------
    recipes : list
        list of Recipe objects to process
    ingredients : np.array
        the item ids which are to be classified as an 'Ingredient'
    HFs : np.array
        the item ids which are to be classified as a 'Halffabrikaat'
    packagings : np.array
        the item ids which are to be classified as a 'Verpakking'
    price_data : pd.DataFrame
        DataFrame containing the price data
    prices_col : str
        the name of the price_data column containing the new prices
    price_data_id_col : str
        the name of the price_data column containing the item ids
    weight_data : pd.DataFrame
        DataFrame containing the weight data
    waste_data : pd.Dataframe
        DataFrame containing the waste data
        
    Returns
    -------
    recipes : list[Recipe]
        list of processed Recipe objects
    """

    for recipe in recipes:
        recipe.process(ingredients, HFs, packagings, price_data, prices_col, price_data_id_col, weight_data, waste_data)

    return recipes