#!/usr/bin/env python
# coding: utf-8

# # OKM Model #

# ## Set-up ##

# ### Imports ###

# In[100]:


import pandas as pd
import numpy as np


# ### Objects ###

# In[101]:


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


# ## Data preparation ##

# ### Data loading ###

# #### BOM ####
# 

# In[102]:


bom_data_raw = pd.read_excel("250410 Recepten download NAV 10-4.xlsx", skiprows=1, header=None, decimal=",")


# #### Prices & weights ####

# In[103]:


price_weight_data = pd.read_excel("Input Price List + Grammage.xlsx", sheet_name="PriceList", header=0).astype({'INGREDIENT CODE': 'string'})


# #### Waste ####

# In[104]:


waste_data = pd.read_excel("Input Waste Table.xlsx", sheet_name='WASTE', header=0).astype({'MEAL CODE': "string", 'INGREDIENT CODE': 'string'})


# ##### Add unique id column #####

# In[105]:


waste_data['id'] = waste_data[['MEAL CODE', 'INGREDIENT CODE']].agg('_'.join, axis=1).astype('string')


# #### Product master ####

# In[106]:


product_data = pd.read_excel("Input Productmaster.xlsx", sheet_name='Product')


# ##### Active recipes #####

# In[107]:


active_rec_data = pd.read_excel("Input Productmaster.xlsx", sheet_name='Actief')


# In[108]:


active_recipes = [str(x) for x in active_rec_data[active_rec_data['Actief'] == 'Ja']['Artikel']]


# ##### Split product data by categorie #####
# Store the ids ('hf_nr') in NumPy arrays for easy and fast checking against later.

# In[109]:


product_data_ingredient = np.array(product_data[product_data['Categorie'] == 'Ingredient']['Nummer'])
product_data_packaging = np.array(product_data[product_data['Categorie'] == 'Verpakking']['Nummer'])
product_data_HF = np.array(product_data[product_data['Categorie'] == 'Halffabrikaat']['Nummer'])
product_data_gas = np.array(product_data[product_data['Categorie'] == 'Gas']['Nummer'])


# ### Data cleaning ###

# #### BOM ####

# ##### Split data into recipes #####

# In[110]:


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
# Keep this separate for now in case it has to be removed later.

# In[111]:


# recipes_temp = []
# for recipe in recipes:
#     if str(recipe.id) in active_recipes:
#         recipes_temp.append(recipe)

# recipes = recipes_temp 


# ## Modeling ##

# ### Add categories ###

# In[112]:


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

        elif item_id in product_data_gas:
            categories.append('Gas')

        else:
            categories.append('Ongeclassificeerd')

    recipe.data['Categorie'] = categories


# ### New prices ###
# From price list for ingredients & gas; 0 for packaging; and empty for HFs.

# In[113]:


for recipe in recipes:
    new_prices = []

    for i in range(len(recipe.data)):
        item_id = recipe.data['hf_nr'][i]

        if (item_id in product_data_ingredient) or (item_id in product_data_gas): # ingredients & gas
            subset_price_df = price_weight_data[price_weight_data['INGREDIENT CODE'] == item_id]
            new_price = subset_price_df['PRICE Q1'].iloc[0]

        elif item_id in product_data_packaging: # packaging
            new_price = 0

        elif item_id in product_data_HF: # HFs
            new_price = None

        else: # unclassified
            new_price = 'Geen nieuwe prijs'

        new_prices.append(new_price)

    recipe.data['Nieuwe prijs'] = new_prices


# ### Old prices ###
# Old costs / old quantity for ingredients & gas; 0 for packaging; and empty for HFs.

# In[114]:


for recipe in recipes:
    old_prices = []

    for i in range(len(recipe.data)):
        item_id = recipe.data['hf_nr'][i]

        if (item_id in product_data_ingredient) or (item_id in product_data_gas): # ingredients & gas
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
# Convert items not in kg. Items already in kg stay the same.

# In[115]:


for recipe in recipes:
    weights = []

    for i in range(len(recipe.data)):
        if not recipe.data['Basiseenheid'][i] == 'KG':

            item_id = recipe.data['hf_nr'][i]

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

# In[116]:


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
                        subset_waste_data_parent = waste_data[waste_data['id'] == f'{recipe.id}_{recipe.data['hf_nr'].iloc[j]}']

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

# In[117]:


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

# In[118]:


for recipe in recipes:
    newp_oldq_col = []
    newp_newq_col = []

    for i in range(len(recipe.data)):
        item_id = recipe.data['hf_nr'][i]

        if (item_id in product_data_ingredient) or (item_id in product_data_packaging) or (item_id in product_data_gas):
            try:
                newp_oldq = recipe.data['Nieuwe prijs'][i] * recipe.data['Aantal (Basis)'][i]
                newp_newq = recipe.data['Nieuwe prijs'][i] * recipe.data['Aantal (nieuw)'][i]

            except TypeError: # TODO - could use the old price here as well
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

# In[119]:


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

# In[120]:


for recipe in recipes:
    delta_q_col = []
    delta_p_col = []
    delta_cost_col = []

    for i in range(len(recipe.data)):

        try:
            delta_q = (recipe.data['Aantal (nieuw)'][i] - recipe.data['Aantal (Basis)'][i]) * recipe.data['Oude prijs'][i]
            delta_p = (recipe.data['Nieuwe prijs'][i] - recipe.data['Oude prijs'][i]) * recipe.data['Aantal (Basis)'][i]
            delta_cost = recipe.data['Materiaalkosten (nieuw)'][i] - recipe.data['Materiaalkosten'][i]

        except TypeError:
            delta_q = 'Kan niet berekenen'
            delta_p = 'Kan niet berekenen'
            delta_cost = 'Kan niet berekenen'

        delta_q_col.append(delta_q)
        delta_p_col.append(delta_p)
        delta_cost_col.append(delta_cost)

    recipe.data['Delta Q'] = delta_q_col
    recipe.data['Delta prijs'] = delta_p_col
    recipe.data['Delta materiaalkosten'] = delta_cost_col


# ## Output Excel file ##

# ### BOM ###

# In[121]:


frames = []
for recipe in recipes:
    frames.append(recipe.data)

BOM_df = pd.concat(frames)


# ### Save to Excel ###

# In[122]:


with pd.ExcelWriter("Output v4 (inclusief inactief).xlsx") as writer:
    BOM_df.to_excel(writer, sheet_name="BOM")

