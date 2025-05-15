""" Data validation 

Data validation is two-fold:
    1. All ingredients should have a new price
    2. All level 1 items should have waste percentages

Data validation will optionally also produce an output Excel file containing all data validation fails.
"""

from openpyxl.worksheet.table import Table, TableStyleInfo
from typing import Callable
import pandas as pd
import numpy as np
import warnings


def check_ingr_prices(ingredients : np.array,
                      price_data : pd.DataFrame,
                      prices_col : str,
                      price_data_id_col : str='INGREDIENT CODE',
                      update_callback : Callable=None) -> dict:
    """
    Check if all item classified as ingredients have a new price.

    Parameters
    ----------
    ingredients : np.array
        NumPy array containing the item ids of the ingredients
    price_data : pd.DataFrame
        DataFrame containing the price data
    prices_col : str
        the name of the price_data column containing the new prices
    price_data_id_column : str
        the name of the price_data column containing the item ids
    update_callback : Callable
        the update_callback function to use to pass feedback to the user

    Returns
    -------
    fails : dict
        dictionary of all items which failed the ingredient validation
    """
    
    fails = {}

    for ing in ingredients:
        subset = price_data[price_data[price_data_id_col] == ing].reset_index()

        if len(subset) == 1:
            try:
                price = float(subset[prices_col].iloc[0])
            except (ValueError, TypeError):
                if update_callback:
                    update_callback(f'Kan de prijs voor ingredient {ing} niet lezen. Prijs: "{subset[prices_col][0]}"')
                warnings.warn(f'Kan de prijs voor ingredient {ing} niet lezen. Prijs: "{subset[prices_col][0]}"')
                fails[ing] = [f'Kan de prijs niet lezen. Prijs: "{subset[prices_col][0]}"',
                              'ingredient validation'] # add as validation type
        
        elif len(subset) == 0:
            if update_callback:
                    update_callback(f'Ingredient {ing} komt niet voor in de prijslijst')
            warnings.warn(f'Ingredient {ing} komt niet voor in de prijslijst')
            fails[ing] = [f'Ingredient komt niet voor in de prijslijst',
                           'ingredient validation'] # add as validation type

        else:
            if update_callback:
                    update_callback(f'Ingredient {ing} komt meermaals voor in de prijslijst. Indexen: {subset["index"]}')
            warnings.warn(f'Ingredient {ing} komt meermaals voor in de prijslijst. Indexen: {subset["index"]}')
            fails[ing] = [f'Ingredient komt meermaals voor in de prijslijst. Indexen: {subset["index"]}',
                          'ingredient validation'] # add as validation type

    return fails


def check_wastes(recipes : list,
                 packagings : np.array,
                 waste_data : pd.DataFrame,
                 waste_data_id_col : str='id',
                 waste_data_nav_col : str='WASTE-NAV',
                 waste_data_fin_col : str='WASTE-FIN',
                 waste_data_use_col : str='WASTE-USE',
                 id_column : str='hf_nr',
                 level_column : str='Niveau',
                 update_callback : Callable=None) -> dict:
    """
    Check if all level 1 items have waste percentages.

    Parameters
    ----------
    recipes : list
        list of Recipe objects
    packagings : np.array
        the ids of the packaging items
    waste_data : pd.DataFrame
        DataFrame containing the waste data
    waste_data_id_col : str
        the name of the waste_data column containing the ids (Recipe id + item id)
    waste_data_nav_col : str
        the name of the waste_data column containing the NAV wastes
    waste_data_fin_col : str
        the name of the waste_data column containing the FIN wastes
    waste_data_use_col : str
        the name of the waste_data column containing the USE wastes
    id_column : str
        the name of the Recipe.bom column containing the item ids
    level_column : str
        the name of the Recipe.bom column containing the levels
    update_callback : Callable
        the update_callback function to use to pass feedback to the user

    Returns
    -------
    fails : dict
        dictionary of all items which failed the waste validation
    """

    fails = {}

    for recipe in recipes:
        for i in range(len(recipe.bom)):
            item_id = recipe.bom[id_column][i]
            waste_id = f'{recipe.id}_{item_id}'

            if recipe.bom[level_column][i] == 1:
                if not item_id in packagings: # ignore packagings
                    subset = waste_data[waste_data[waste_data_id_col] == waste_id]

                    if len(subset) == 1:
                        nav = subset[waste_data_nav_col].iloc[0]
                        fin = subset[waste_data_fin_col].iloc[0]
                        use = subset[waste_data_use_col].iloc[0]
                        try:
                            waste = float(nav) + float(fin) + float(use)
                        except (ValueError, TypeError):
                            if update_callback:
                                update_callback(f'Kan de waste voor level 1 item: "{item_id}", voor maaltijd: "{recipe.id}" niet lezen. \
Waste-nav: "{nav}", Waste-fin: "{fin}", Waste-use: "{use}"')
                            warnings.warn(f'Kan de waste voor level 1 item: "{item_id}", voor maaltijd: "{recipe.id}" niet lezen. \
Waste-nav: "{nav}", Waste-fin: "{fin}", Waste-use: "{use}"')
                            fails[waste_id] = [f'Kan de waste voor level 1 item: "{item_id}", voor maaltijd: "{recipe.id}" niet lezen. \
Waste-nav: "{nav}", Waste-fin: "{fin}", Waste-use: "{use}"', 
                                                'waste validation'] # add as validation type

                    elif len(subset) == 0:
                        if update_callback:
                                update_callback(f'Level 1 item: "{item_id}", voor maaltijd: "{recipe.id}" komt niet voor in de waste lijst')
                        warnings.warn(f'Level 1 item: "{item_id}", voor maaltijd: "{recipe.id}" komt niet voor in de waste lijst')
                        fails[waste_id] = [f'Level 1 item: "{item_id}", voor maaltijd: "{recipe.id}" komt niet voor in de waste lijst',
                                           'waste validation'] # add as validation type

                    else:
                        if update_callback:
                                update_callback(f'Level 1 item: "{item_id}", voor maaltijd: "{recipe.id}" komt meermaals voor in de waste lijst')
                        warnings.warn(f'Level 1 item: "{item_id}", voor maaltijd: "{recipe.id}" komt meermaals voor in de waste lijst')
                        fails[waste_id] = [f'Level 1 item: "{item_id}", voor maaltijd: "{recipe.id}" komt meermaals voor in de waste lijst', 
                                           'waste validation'] # add as validation type
    
    return fails


def output_validation_fails(fails : pd.DataFrame,
                            output_path : str='Data Validation.xlsx',
                            output_file_sheet_name : str='Data Validation Fails',
                            update_callback : Callable=None,
                            xl_tbl_name : str='Errors') -> None:
    """ 
    Generate an output Excel file containing data validation fails.

    Parameters
    ----------
    fails : pd.DataFrame
        DataFrame containing the validation fails
    output_path : str
        the path of the output Excel file including the name
    output_file_sheet_name : str
        the name of the output Excel file sheet name
    update_callback : Callable
        the update_callback function to use to pass feedback to the user
    xl_tbl_name : str
        the name of the Excel Table the data will be outputted to
    """

    fails = fails.reset_index(names='ID')

    with pd.ExcelWriter(output_path) as writer:
        fails.to_excel(writer, sheet_name=output_file_sheet_name, index=False)

        # Create an Excel Table
        worksheet = writer.sheets[output_file_sheet_name]

        num_rows, num_cols = fails.shape
        last_col_letter = chr(ord('A') + num_cols - 1)  # Assumes <= 26 columns
        table_range = f"A1:{last_col_letter}{num_rows + 1}"

        table = Table(displayName=xl_tbl_name, ref=table_range)

        style = TableStyleInfo(
            name="TableStyleMedium9", showFirstColumn=False,
            showLastColumn=False, showRowStripes=True, showColumnStripes=False
        )
        table.tableStyleInfo = style

        worksheet.add_table(table)


        if update_callback:
            update_callback(f'{len(fails)} data validation issues encountered. Output file saved: {output_path}')


def validate_data(ingredients : np.array,
                  price_data : pd.DataFrame,
                  prices_col : str,
                  recipes : list,
                  packagings : np.array,
                  waste_data : pd.DataFrame,
                  waste_data_nav_col : str='WASTE-NAV',
                  waste_data_fin_col : str='WASTE-FIN',
                  waste_data_use_col : str='WASTE-USE',
                  update_callback : Callable=None) -> None:
    """
    Run the full data validation.

    Parameters
    ----------
    ingredients : np.array
        NumPy array containing the item ids of the ingredients
    price_data : pd.DataFrame
        DataFrame containing the price data
    prices_col : str
        the name of the price_data column containing the new prices
    recipes : list
        list of Recipe objects
    packagings : np.array
        the ids of the packaging items
    waste_data : pd.DataFrame
        DataFrame containing the waste data
    update_callback : Callable
        the update_callback function to use to pass feedback to the user
    """

    ingredient_fails = check_ingr_prices(ingredients, price_data, prices_col, update_callback=update_callback)

    # Fix any data casting errors that may slipped through
    # Difficult to catch these before this point, but not ideal currently...
    if (price_data[prices_col].dtype == 'O') and (len(ingredient_fails) == 0):
        price_data[prices_col].astype('float64') # TODO - test whether this actually works or if it needs to be move out of this function

    waste_fails = check_wastes(recipes, packagings, waste_data, update_callback=update_callback)

    # Fix any data casting errors that may slipped through
    # Difficult to catch these before this point, but not ideal currently...
    if (waste_data[waste_data_nav_col].dtype == 'O') and (len(waste_fails) == 0):
        waste_data[waste_data_nav_col].astype('float64')

    if (waste_data[waste_data_fin_col].dtype == 'O') and (len(waste_fails) == 0):
        waste_data[waste_data_fin_col].astype('float64')

    if (waste_data[waste_data_use_col].dtype == 'O') and (len(waste_fails) == 0):
        waste_data[waste_data_use_col].astype('float64')

    fails_dict = ingredient_fails | waste_fails # combine the fails dictionaries

    if fails_dict:
        fails_df = pd.DataFrame.from_dict(fails_dict, orient='index', columns=['error', 'type'])
        output_validation_fails(fails_df, update_callback=update_callback)
