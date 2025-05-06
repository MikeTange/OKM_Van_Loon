#!/usr/bin/env python
# coding: utf-8

# # OKM Model #

# ## Set-up ##

# ### Imports ###

<<<<<<< Updated upstream
# In[3]:
=======
# In[371]:
>>>>>>> Stashed changes


import pandas as pd
import numpy as np
import warnings
import openpyxl


# ### Objects ###

<<<<<<< Updated upstream
# In[4]:
=======
# In[372]:
>>>>>>> Stashed changes


class recipe:
    """ a recipe """

    def __init__(self, name : str, id : str, data : pd.DataFrame) -> None:
        """ initialise an instance of recipe"""
        self.name = name
        self.id = id
        self.data = data

    def __str__(self) -> str:
        """ set the string representation of a recipe """
        return f'{self.id} {self.name}'


# ### Functions ###

<<<<<<< Updated upstream
# In[5]:
=======
# In[373]:
>>>>>>> Stashed changes


def rename_nan_columns(df, prefix="col"):
    """
    Rename DataFrame columns whose header could not be inferred, and have 'NaN' as header

    Parameters:
    - df: pandas.DataFrame
    - prefix: prefix to replace NaN column names with

    Returns:
    - DataFrame with renamed columns
    """
    df = df.copy()
    df.columns = [
        f"{prefix}{idx}" if pd.isna(col) else col.strip()
        for idx, col in enumerate(df.columns)]
    return df


def clean_dataframe(df, replace_empty_with_na=True):
    """
    Cleans a DataFrame by:
    - Stripping whitespace from string values
    - Optionally replacing empty strings with pd.NA
    - Converting column types using pandas' best-guess inference

    Parameters:
    - df: pandas.DataFrame
    - replace_empty_with_na: bool, whether to treat empty strings as missing values

    Returns:
    - Cleaned and type-inferred DataFrame
    """
    df = df.copy()

    # Strip whitespace from strings & replace commas with periods as floating points
    df = df.map(lambda x: x.replace(',', '.').strip() if isinstance(x, str) else x)

    # Optionally replace empty strings with pd.NA for better type inference
    if replace_empty_with_na:
        df.replace("", pd.NA, inplace=True)

    # Infer column types
    df = df.convert_dtypes()

    return df


# ## Data preparation ##

# ### Input parameters ###

<<<<<<< Updated upstream
# In[6]:
=======
# In[374]:
>>>>>>> Stashed changes


# BOM
bom_name = "250416 Recepten download NAV 16-4.xlsx"
bom_sheet_name = "Budget"

# Prices & weights
price_weight_name = "Input Price List + Grammage.xlsx"
price_weight_sheet_name = "PriceList"

# Waste
waste_name = "Input Waste Table.xlsx"
waste_sheet_name = 'WASTE'

# Active recipes
active_rec_name = "Input Actieve Recepten Master.xlsx"
active_rec_sheet = "Actief"


# ### Required columns ###
# Price and weight data

<<<<<<< Updated upstream
# In[7]:
=======
# In[375]:
>>>>>>> Stashed changes


req_cols_price_weight = ['INGREDIENT CODE', 'INGREDIENTS', 'KG']


# Waste data

<<<<<<< Updated upstream
# In[8]:
=======
# In[376]:
>>>>>>> Stashed changes


req_cols_waste = ['MEAL CODE', 'INGREDIENT CODE', 'WASTE-NAV', 'WASTE-FIN', 'WASTE-USE']


# Active recipes data

# In[9]:


req_cols_act_rec = ['Artikel']


# ### Data loading & initial validation ###

# #### BOM ####
# 

<<<<<<< Updated upstream
# In[10]:
=======
# In[377]:
>>>>>>> Stashed changes


bom_data_raw = pd.read_excel(bom_name, sheet_name=bom_sheet_name, skiprows=1, header=None, decimal=",")


<<<<<<< Updated upstream
# In[11]:
=======
# In[378]:
>>>>>>> Stashed changes


print(f'BOM ingelezen: {bom_name} || Tabblad: {bom_sheet_name}')


# #### Prices & weights ####

<<<<<<< Updated upstream
# In[12]:
=======
# In[379]:
>>>>>>> Stashed changes


price_weight_data_raw = pd.read_excel(price_weight_name, sheet_name=price_weight_sheet_name, header=None)

# Drop leading empty rows
price_weight_data_trimmed = price_weight_data_raw.loc[~price_weight_data_raw.isnull().all(axis=1)].reset_index(drop=True)

# Promote the first non-empty row to header
header = price_weight_data_trimmed.iloc[0]
price_weight_data = price_weight_data_trimmed[1:]
price_weight_data.columns = header
price_weight_data = price_weight_data.reset_index(drop=True)

# Rename any columns named: "NaN"
price_weight_data = rename_nan_columns(price_weight_data)

# Check for required columns
if not all(x in price_weight_data.columns for x in req_cols_price_weight):
    print(f'Sommige essentiele kolommen missen in de prijslijst: {set(req_cols_price_weight) - set(price_weight_data.columns)}')

# Clean DataFrame values
price_weight_data = clean_dataframe(price_weight_data).astype({"INGREDIENT CODE": 'string', "INGREDIENTS": 'string'}) # fix incorrect type inferences as strings (universally applicable)


<<<<<<< Updated upstream
# In[13]:
=======
# In[380]:
>>>>>>> Stashed changes


print(f'Prijs en gewicht lijst ingelezen: {price_weight_name} || Tabblad: {price_weight_sheet_name}')


# #### Waste ####

<<<<<<< Updated upstream
# In[14]:
=======
# In[381]:
>>>>>>> Stashed changes


waste_data_raw = pd.read_excel(waste_name, sheet_name=waste_sheet_name, header=None)

# Drop leading empty rows
waste_data_trimmed = waste_data_raw.loc[~waste_data_raw.isnull().all(axis=1)].reset_index(drop=True)

# Promote the first non-empty row to header
header = waste_data_trimmed.iloc[0]
waste_data = waste_data_trimmed[1:]
waste_data.columns = header
df = waste_data.reset_index(drop=True)

# Rename any columns named: "NaN"
waste_data = rename_nan_columns(waste_data)

# Check for required columns
if not all(x in waste_data.columns for x in req_cols_waste):
    print(f'Sommige essentiele kolommen missen in de waste lijst: {set(req_cols_waste) - set(waste_data.columns)}')

# Clean DataFrame values
waste_data = clean_dataframe(waste_data).astype({'MEAL CODE': 'string', 'INGREDIENT CODE': 'string', 'UNITS': 'string'}) # fix incorrect type inferences as strings (universally applicable)


# ##### Add unique id column #####

<<<<<<< Updated upstream
# In[15]:
=======
# In[382]:
>>>>>>> Stashed changes


waste_data['id'] = waste_data[['MEAL CODE', 'INGREDIENT CODE']].agg('_'.join, axis=1).astype('string')


<<<<<<< Updated upstream
# In[16]:
=======
# In[383]:
>>>>>>> Stashed changes


print(f'Waste lijst ingelezen: {waste_name} || Tabblad: {waste_sheet_name}')


# #### Active recipes ####

# In[17]:


warnings.filterwarnings('ignore', category=UserWarning)

active_rec_data_raw = pd.read_excel(active_rec_name, sheet_name=active_rec_sheet, header=None)

# Drop leading empty rows
active_rec_data_trimmed = active_rec_data_raw.loc[~active_rec_data_raw.isnull().all(axis=1)].reset_index(drop=True)

# Promote the first non-empty row to header
header = active_rec_data_trimmed.iloc[0]
active_rec_data = active_rec_data_trimmed[1:]
active_rec_data.columns = header
df = active_rec_data.reset_index(drop=True)

# Rename any columns named: "NaN"
active_rec_data = rename_nan_columns(active_rec_data)

# Check for required columns
if not all(x in active_rec_data.columns for x in req_cols_act_rec):
    print(f'Sommige essentiele kolommen missen in de actieve recepten master: {set(req_cols_act_rec) - set(active_rec_data.columns)}')

# Clean DataFrame values
active_rec_data = clean_dataframe(active_rec_data)


# In[18]:


print(f'Actieve recepten lijst ingelezen: {active_rec_name} || Tabblad: {active_rec_sheet}')


# ## User input ##
# Get user input on what to do exactly.

# ### Prices ###

# In[19]:


# price_period = input(f'In welke van de volgende kolommen staan de nieuwe prijzen?\n{[x for x in price_weight_data.columns]}')
price_period = 'PRICE Q2'


# ### Active recipes ###

# In[20]:


act_rec_period = '2025 Q2'


# ### Data cleaning ###

# #### BOM ####

# ##### Split data into recipes #####

<<<<<<< Updated upstream
# In[21]:
=======
# In[384]:
>>>>>>> Stashed changes


recipes = []

for i in range(len(bom_data_raw)):
    # a new recipe starts
    if bom_data_raw[4][i] == 'Omschrijving':
        start_idx = i + 1
        recipe_name = bom_data_raw[4][i + 1]
        recipe_id = bom_data_raw[3][i + 1]

        # the recipe ends
        for j in range(i, len(bom_data_raw)):
            if bom_data_raw[3][j] == 'Kostenaandeel voor dit artikel':
                end_idx = j
                recipe_data = bom_data_raw.iloc[(i + 2):j].drop(range(8, 13), axis='columns').reset_index()
                recipe_data = recipe_data.rename(columns={0: "id_nr", 1: "nr", 2: "Niveau", 3: "hf_nr", 4: "Omschrijving", 5: "Aantal (Basis)", 6: "Basiseenheid", 7: "Materiaalkosten"})
                recipe_data = recipe_data.astype({"id_nr": str, "nr": int, "Niveau": int, "hf_nr": str, "Omschrijving": str, "Aantal (Basis)": float, "Basiseenheid": str, "Materiaalkosten": float})
                recipe_data.insert(loc=2, column="Product Naam", value=[recipe_name for i in range(len(recipe_data))])
                recipes.append(recipe(name=recipe_name, id=recipe_id, data=recipe_data))
                i += j
                break


# ##### Drop inactive recipes #####

# In[22]:


recipes_temp = []
for recipe in recipes:
    if str(recipe.id) in np.array(active_rec_data[active_rec_data[act_rec_period] == 'Actief']['Artikel']).astype(str):
        recipes_temp.append(recipe)

recipes = recipes_temp


# ### Product master ###
# Create a product master based on the information in the BOM:
# - If an item starts with '3' --> **packaging**, else
# - If an item has a child --> **HF**, else
# - Item --> **ingredient**

<<<<<<< Updated upstream
# In[23]:
=======
# In[385]:
>>>>>>> Stashed changes


product_master_dict = {}

for recipe in recipes:
    for i in range(len(recipe.data)):
        item_id = recipe.data['hf_nr'][i]

        if not item_id in product_master_dict.keys():
            if item_id.startswith('3'):
                classification = 'Verpakking'
            elif not i + 1 == len(recipe.data):
                if recipe.data['Niveau'][i + 1] > recipe.data['Niveau'][i]:
                    classification = 'Halffabrikaat'
                else:
                    classification = 'Ingredient'
            else:
                classification = 'Ingredient'
        
            product_master_dict[item_id] = [item_id, classification]

product_master = pd.DataFrame.from_dict(product_master_dict, orient='index', columns=['Nummer', 'Categorie']).reset_index(drop=True)


# ##### Split product data by categorie #####
# Store the ids ('hf_nr') in NumPy arrays for easy and fast checking against later.

<<<<<<< Updated upstream
# In[24]:
=======
# In[386]:
>>>>>>> Stashed changes


product_data_ingredient = np.array(product_master[product_master['Categorie'] == 'Ingredient']['Nummer'])
product_data_packaging = np.array(product_master[product_master['Categorie'] == 'Verpakking']['Nummer'])
product_data_HF = np.array(product_master[product_master['Categorie'] == 'Halffabrikaat']['Nummer'])


<<<<<<< Updated upstream
=======
# ## User input ##
# Get user input on what to do exactly.

# In[387]:


# price_period = input(f'In welke van de volgende kolommen staan de nieuwe prijzen?\n{[x for x in price_weight_data.columns]}')
price_period = 'PRICE Q2'


>>>>>>> Stashed changes
# ## Data validation ##
# Validating the correctness of the input data.

# ### Ingredients ###
# 
# Check if all ingredients have a new price.

<<<<<<< Updated upstream
# In[25]:
=======
# In[388]:
>>>>>>> Stashed changes


ing_error_list = []

for ing in product_data_ingredient:
    subset = price_weight_data[price_weight_data['INGREDIENT CODE'] == ing].reset_index()

    if len(subset) == 1:
        try:
            price = float(subset[price_period].iloc[0])
        except ValueError:
            ing_error_list.append(f'Kan de prijs voor ingredient: "{ing}" niet lezen. Prijs: "{subset[price_period][0]}"')
    
    elif len(subset) == 0:
        ing_error_list.append(f'Ingredient "{ing}" komt niet voor in de prijslijst')

    else:
        ing_error_list.append(f'Ingredient "{ing}" komt meermaals voor in de prijslijst. Indexen: {subset["index"]}')


# In case of no errors, force cast data type for price_period if it's not already correct.

<<<<<<< Updated upstream
# In[26]:
=======
# In[389]:
>>>>>>> Stashed changes


if (price_weight_data[price_period].dtype == 'O') and (len(ing_error_list) == 0):
    price_weight_data[price_period].astype('float64')


# ### Waste ###
# Check if all items at level 1 have waste percentages.

<<<<<<< Updated upstream
# In[27]:
=======
# In[390]:
>>>>>>> Stashed changes


waste_error_list = []

for recipe in recipes:
    for i in range(len(recipe.data)):
        item_id = recipe.data['hf_nr'][i]
        waste_id = f'{recipe.id}_{item_id}'

        if recipe.data['Niveau'][i] == 1:
            if not item_id in product_data_packaging: # ignore packaging
                subset = waste_data[waste_data['id'] == waste_id]

                if len(subset) == 1:
                    nav = subset['WASTE-NAV'].iloc[0]
                    fin = subset['WASTE-FIN'].iloc[0]
                    use = subset['WASTE-USE'].iloc[0]
                    try:
                        waste = float(nav) + float(fin) + float(use)
                    except ValueError:
                        waste_error_list.append(f'Kan de waste voor level 1 item: "{item_id}", voor maaltijd: "{recipe.id}" niet lezen. Waste-nav: "{nav}", Waste-fin: "{fin}", Waste-use: "{use}"')

                elif len(subset) == 0:
                    waste_error_list.append(f'Level 1 item: "{item_id}", voor maaltijd: "{recipe.id}" komt niet voor in de waste lijst')

                else:
                    waste_error_list.append(f'Level 1 item: "{item_id}", voor maaltijd: "{recipe.id}" komt meermaals voor in de waste lijst')


# In case of no errors, force cast data types for waste columns if they're not already correct.

<<<<<<< Updated upstream
# In[28]:
=======
# In[391]:
>>>>>>> Stashed changes


if (waste_data['WASTE-NAV'].dtype == 'O') and (len(waste_error_list) == 0):
    waste_data['WASTE-NAV'].astype('float64')

if (waste_data['WASTE-FIN'].dtype == 'O') and (len(waste_error_list) == 0):
    waste_data['WASTE-FIN'].astype('float64')

if (waste_data['WASTE-USE'].dtype == 'O') and (len(waste_error_list) == 0):
    waste_data['WASTE-USE'].astype('float64')


# ### Errors feedback ###
# Give feedback to the user about data validation errors.

<<<<<<< Updated upstream
# In[29]:
=======
# In[392]:
>>>>>>> Stashed changes


if (len(ing_error_list) == 0) and (len(waste_error_list)) == 0:
    print('Data validatie succesvol! Geen errors gevonden')

else:
    print('-' * 80)
    print('-' * 80)
    print('Data validatie problemen gevonden:')
    print('-' * 80)
    print('-' * 80)
    
    with pd.ExcelWriter("errors.xlsx") as writer:
        pd.DataFrame(ing_error_list, columns=['errors']).to_excel(writer, sheet_name="Ingredienten errors")
        pd.DataFrame(waste_error_list, columns=['errors']).to_excel(writer, sheet_name="Waste errors")

    if len(ing_error_list) != 0:
        print('Ingredienten errors:')
        print('-' * 80)
        for error in ing_error_list:
            print(error)
    
    if len(waste_error_list) != 0:
        print('-' * 80)
        print('Waste errors:')
        print('-' * 80)
        for error in waste_error_list:
            print(error)
    
    print('-' * 80)
    print('-' * 80)
    print('Output error file opgeslagen: errors.xlsx')
    print('-' * 80)
    print('-' * 80)


# ## Modeling ##

<<<<<<< Updated upstream
# In[30]:
=======
# In[393]:
>>>>>>> Stashed changes


print('Starten met modeleren')


# ### Add categories ###

<<<<<<< Updated upstream
# In[31]:
=======
# In[394]:
>>>>>>> Stashed changes


for recipe in recipes:
    categories = []

    for i in range(len(recipe.data)):
        item_id = recipe.data['hf_nr'][i]

        if item_id in product_data_ingredient:
            categories.append('Ingredient')

        elif item_id in product_data_HF:
            categories.append('Halffabrikaat')

        elif item_id in product_data_packaging:
            categories.append('Verpakking')
        
        else:
            categories.append('Ongeclassificeerd')
    
    recipe.data['Categorie'] = categories


# ### New prices ###
# From price list for ingredients & gas; 0 for packaging; and empty for HFs.

<<<<<<< Updated upstream
# In[32]:
=======
# In[395]:
>>>>>>> Stashed changes


for recipe in recipes:
    new_prices = []

    for i in range(len(recipe.data)):
        item_id = recipe.data['hf_nr'][i]

        if item_id in product_data_ingredient: # ingredients
            subset_price_df = price_weight_data[price_weight_data['INGREDIENT CODE'] == item_id]
            
            if not len(subset_price_df) == 0:
                new_price = subset_price_df['PRICE Q2'].iloc[0]
            else:
                new_price = 'Geen nieuwe prijs'
        
        elif item_id in product_data_packaging: # packaging
            new_price = 0

        elif item_id in product_data_HF: # HFs
            new_price = np.nan
        
        else: # unclassified
            new_price = 'Geen nieuwe prijs'
    
        new_prices.append(new_price)
        
    recipe.data['Nieuwe prijs'] = new_prices


# ### Old prices ###
# Old costs / old quantity for ingredients & gas; 0 for packaging; and empty for HFs.

<<<<<<< Updated upstream
# In[33]:
=======
# In[396]:
>>>>>>> Stashed changes


warnings.filterwarnings('ignore', category=RuntimeWarning)

for recipe in recipes:
    old_prices = []

    for i in range(len(recipe.data)):
        item_id = recipe.data['hf_nr'][i]

        if item_id in product_data_ingredient: # ingredients
            old_price = recipe.data['Materiaalkosten'][i] / recipe.data['Aantal (Basis)'][i]
        
        elif item_id in product_data_packaging: # packaging
            old_price = 0

        elif item_id in product_data_HF: # HFs
            old_price = None

        else: # unclassified
            old_price = recipe.data['Materiaalkosten'][i] / recipe.data['Aantal (Basis)'][i]
    
        old_prices.append(old_price)
        
    recipe.data['Oude prijs'] = old_prices


# ### Weight in kg ###
# Convert items not in kg. Items already in kg stay the same. Packaging goes to 0, regardless of the unit.

<<<<<<< Updated upstream
# In[34]:
=======
# In[397]:
>>>>>>> Stashed changes


for recipe in recipes:
    weights = []

    for i in range(len(recipe.data)):
        item_id = recipe.data['hf_nr'][i]

        if item_id in product_data_packaging: # packaging to 0
            weight = 0.0

        elif not recipe.data['Basiseenheid'][i] == 'KG':

            subset_weight_data = price_weight_data[price_weight_data['INGREDIENT CODE'] == item_id]

            if len(subset_weight_data) == 0: # no info about this item
                weight = 'Geen conversie info'
            
            elif len(subset_weight_data) == 1: # new info about this item
                weight = subset_weight_data['KG'].iloc[0] * recipe.data['Aantal (Basis)'][i]

            else:
                weight = 'Dubbele conversie info'
        
        else:
            weight = recipe.data['Aantal (Basis)'][i]

        weights.append(weight)

    recipe.data['Grammage'] = weights


# ### Waste ###
# For items at level 1: find the waste in the waste data. For all other items, find the parent item at level 1, and take the waste from there.

<<<<<<< Updated upstream
# In[35]:
=======
# In[398]:
>>>>>>> Stashed changes


for recipe in recipes:
    waste_nav_col = []
    waste_fin_col = []
    waste_use_col = []

    for i in range(len(recipe.data)):
        item_id = recipe.data['hf_nr'][i]

        if recipe.data['Niveau'][i] == 1: # waste is only determined at level 1
            subset_waste_data = waste_data[waste_data['id'] == f'{recipe.id}_{item_id}']

            if len(subset_waste_data) == 0:
                # waste_nav = 'Geen waste info'
                # waste_fin = 'Geen waste info'
                # waste_use = 'Geen waste info'

                waste_nav = 0
                waste_fin = 0
                waste_use = 0

            elif len(subset_waste_data) == 1:
                waste_nav = subset_waste_data['WASTE-NAV'].iloc[0]
                waste_fin = subset_waste_data['WASTE-FIN'].iloc[0]
                waste_use = subset_waste_data['WASTE-USE'].iloc[0]

            else:
                waste_nav = 'Dubbele waste info'
                waste_fin = 'Dubbele waste info'
                waste_use = 'Dubbele waste info'
        
        else:
            for j in range(i, -1, -1): # loop backwards to find the closest level 1 item
                if recipe.data['Niveau'].iloc[j] == 1:

                    if recipe.data['hf_nr'].iloc[j] in product_data_HF:
                        parent_hf_id = recipe.data["hf_nr"].iloc[j]
                        subset_waste_data_parent = waste_data[waste_data['id'] == f'{recipe.id}_{parent_hf_id}']

                        if len(subset_waste_data_parent) == 0:
                            # waste_nav = 'Geen waste info'
                            # waste_fin = 'Geen waste info'
                            # waste_use = 'Geen waste info'

                            waste_nav = 0
                            waste_fin = 0
                            waste_use = 0

                        elif len(subset_waste_data_parent) == 1:
                            waste_nav = subset_waste_data_parent['WASTE-NAV'].iloc[0]
                            waste_fin = subset_waste_data_parent['WASTE-FIN'].iloc[0]
                            waste_use = subset_waste_data_parent['WASTE-USE'].iloc[0]

                        else:
                            waste_nav = 'Dubbele waste info'
                            waste_fin = 'Dubbele waste info'
                            waste_use = 'Dubbele waste info'

                    else:
                        waste_nav = 'Geen bijbehorend HF'
                        waste_fin = 'Geen bijbehorend HF'
                        waste_use = 'Geen bijbehorend HF'
                    
                    break

        waste_nav_col.append(waste_nav)
        waste_fin_col.append(waste_fin)
        waste_use_col.append(waste_use)

    recipe.data['Waste NAV'] = waste_nav_col
    recipe.data['Waste FIN'] = waste_fin_col
    recipe.data['Waste USE'] = waste_use_col


# ### Quantities ###
# Calculate the quantities based on the known waste data.

<<<<<<< Updated upstream
# In[36]:
=======
# In[399]:
>>>>>>> Stashed changes


for recipe in recipes:
    q_no_waste_col = []
    q_new_col = []

    for i in range(len(recipe.data)):
        
        try:
            q_no_waste = recipe.data['Aantal (Basis)'][i] / (1 + recipe.data['Waste NAV'][i])
        except TypeError:
            q_no_waste = 'Kan niet berekenen'

        try:
            q_new = q_no_waste * (1 + recipe.data['Waste USE'][i])
        except TypeError:
            q_new = 'Kan niet berekenen'

        q_no_waste_col.append(q_no_waste)
        q_new_col.append(q_new)

    recipe.data['Aantal (zonder waste)'] = q_no_waste_col
    recipe.data['Aantal (nieuw)'] = q_new_col


# ### Costs ###
# Several costs are calculated: 
# - new p * old q ("vvp")
# - new p * new q ("materiaalkosten")
# 
# Costs are first calculated for the non-HF items, based on row-level info. Afterwards the HF item costs are calculated and inserted based on hierarchical info.

# #### Non-HF costs ####

<<<<<<< Updated upstream
# In[37]:
=======
# In[400]:
>>>>>>> Stashed changes


for recipe in recipes:
    newp_oldq_col = []
    newp_newq_col = []

    for i in range(len(recipe.data)):
        item_id = recipe.data['hf_nr'][i]

        if (item_id in product_data_ingredient) or (item_id in product_data_packaging):
            try:
                newp_oldq = recipe.data['Nieuwe prijs'][i] * recipe.data['Aantal (Basis)'][i]
                newp_newq = recipe.data['Nieuwe prijs'][i] * recipe.data['Aantal (nieuw)'][i]
            
            except TypeError: # could use the old price here as well
                newp_oldq = 'Kan niet berekenen'
                newp_newq = 'Kan niet berekenen'
        
        elif item_id in product_data_HF:
            newp_oldq = None
            newp_newq = None
        
        else:
            newp_oldq = 'Ongeclassificeerd item'
            newp_newq = 'Ongeclassificeerd item'

        newp_oldq_col.append(newp_oldq)
        newp_newq_col.append(newp_newq)

    recipe.data['Nieuwe vvp'] = newp_oldq_col
    recipe.data['Materiaalkosten (nieuw)'] = newp_newq_col


# #### HF costs ####
# For an HF the costs are determined based on the costs of the individual ingredients which make up the HF.

<<<<<<< Updated upstream
# In[38]:
=======
# In[401]:
>>>>>>> Stashed changes


for recipe in recipes:
    for i in range(len(recipe.data)):
        item_id = recipe.data['hf_nr'][i]

        if item_id in product_data_HF:

            hf_newp_oldq = 0.0
            hf_newp_newq = 0.0
            hf_oldp_oldq = 0.0

            hf_level = recipe.data['Niveau'][i]
            for j in range(i + 1, len(recipe.data)):
                if recipe.data['Niveau'][j] > hf_level:

                    try:
                        if not np.isnan(recipe.data['Nieuwe vvp'][j]):
                            hf_newp_oldq += recipe.data['Nieuwe vvp'][j]
                    except:
                        pass
                    
                    try:
                        if not np.isnan(recipe.data['Materiaalkosten (nieuw)'][j]):
                            hf_newp_newq += recipe.data['Materiaalkosten (nieuw)'][j]
                    except:
                        pass
                    
                    try:
                        if not np.isnan(recipe.data['Materiaalkosten'][j]):
                            if not recipe.data['hf_nr'][j] in product_data_HF:
                                hf_oldp_oldq += recipe.data['Materiaalkosten'][j]
                    except:
                        pass
                    
                else:
                    break
        
            recipe.data.at[i, 'Nieuwe vvp'] = hf_newp_oldq
            recipe.data.at[i, 'Materiaalkosten (nieuw)'] = hf_newp_newq
            recipe.data.at[i, 'Materiaalkosten HF (berekend)'] = hf_oldp_oldq


# ### Deltas ###

<<<<<<< Updated upstream
# In[39]:
=======
# In[402]:
>>>>>>> Stashed changes


for recipe in recipes:
    delta_q_col = []
    delta_p_col = []
    delta_cost_col = []
    fin_waste_impact_col = []

    for i in range(len(recipe.data)):

        try:
            delta_q = (recipe.data['Aantal (nieuw)'][i] - recipe.data['Aantal (Basis)'][i]) * recipe.data['Oude prijs'][i]
        except TypeError:
            delta_q = 'Kan niet berekenen'
        
        try:
            delta_p = (recipe.data['Nieuwe prijs'][i] - recipe.data['Oude prijs'][i]) * recipe.data['Aantal (nieuw)'][i]
        except TypeError as e:            
            delta_p = 'Kan niet berekenen'
        
        try:                  
            delta_cost = recipe.data['Materiaalkosten (nieuw)'][i] - recipe.data['Materiaalkosten'][i]
        except TypeError:
            delta_cost = 'Kan niet berekenen'
        
        try:
            fin_waste_impact = recipe.data['Materiaalkosten (nieuw)'][i] - recipe.data['Nieuwe vvp'][i]
        except TypeError:
            fin_waste_impact = 'Kan niet berekenen'

        delta_q_col.append(delta_q)
        delta_p_col.append(delta_p)
        delta_cost_col.append(delta_cost)
        fin_waste_impact_col.append(fin_waste_impact)
    
    recipe.data['Delta Q'] = delta_q_col
    recipe.data['Delta prijs'] = delta_p_col
    recipe.data['Delta materiaalkosten'] = delta_cost_col
    recipe.data['Delta FIN waste'] = fin_waste_impact_col


<<<<<<< Updated upstream
# In[40]:
=======
# In[403]:
>>>>>>> Stashed changes


print('Klaar met modeleren')


# ## Output Excel file ##

<<<<<<< Updated upstream
# In[41]:
=======
# In[404]:
>>>>>>> Stashed changes


print('Output file maken')


# ### BOM ###

<<<<<<< Updated upstream
# In[42]:
=======
# In[405]:
>>>>>>> Stashed changes


frames = []
for recipe in recipes:
    frames.append(recipe.data)

BOM_df = pd.concat(frames)


# ### Excel file formatting ###
# Change column order and names. Drop a few columns.

<<<<<<< Updated upstream
# In[43]:
=======
# In[406]:
>>>>>>> Stashed changes


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


# ### Save to Excel ###

<<<<<<< Updated upstream
# In[44]:
=======
# In[407]:
>>>>>>> Stashed changes


with pd.ExcelWriter(f"Output v7 - {price_period[-2:]}.xlsx") as writer:
    BOM_df.to_excel(writer, sheet_name="BOM")


# In[370]:


input('Script is klaar! \n\n Je kan dit venster sluiten')

