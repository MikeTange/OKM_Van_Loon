import pandas as pd
import numpy as np


class Recipe:
    """ a recipe """

    def __init__(self, name : str, id : str, data : pd.DataFrame) -> None:
        """ initialise an instance of recipe"""
        self.name = name
        self.id = id
        self.data = data

    def __str__(self) -> str:
        """ set the string representation of a recipe """
        return f'{self.id} {self.name}'
    

def processing(price_period, act_rec_period, bom_data_raw, price_weight_data, waste_data, active_rec_data):
    # Split data into recipes
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
                    recipes.append(Recipe(name=recipe_name, id=recipe_id, data=recipe_data))
                    i += j
                    break

    # Drop inactive recipes
    recipes_temp = []
    for recipe in recipes:
        if str(recipe.id) in np.array(active_rec_data[active_rec_data[act_rec_period] == 'Actief']['Artikel']).astype(str):
            recipes_temp.append(recipe)

    recipes = recipes_temp

    # Build product master
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

    # Split product data by category
    product_data_ingredient = np.array(product_master[product_master['Categorie'] == 'Ingredient']['Nummer'])
    product_data_packaging = np.array(product_master[product_master['Categorie'] == 'Verpakking']['Nummer'])
    product_data_HF = np.array(product_master[product_master['Categorie'] == 'Halffabrikaat']['Nummer'])


    # Data Validation
    # Ingredients
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

    if (price_weight_data[price_period].dtype == 'O') and (len(ing_error_list) == 0):
        price_weight_data[price_period].astype('float64')

    # Waste
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

    if (waste_data['WASTE-NAV'].dtype == 'O') and (len(waste_error_list) == 0):
        waste_data['WASTE-NAV'].astype('float64')

    if (waste_data['WASTE-FIN'].dtype == 'O') and (len(waste_error_list) == 0):
        waste_data['WASTE-FIN'].astype('float64')

    if (waste_data['WASTE-USE'].dtype == 'O') and (len(waste_error_list) == 0):
        waste_data['WASTE-USE'].astype('float64')

    # User feedback
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


    # Modeling
    # Categories
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

    # New prices
    for recipe in recipes:
        new_prices = []

        for i in range(len(recipe.data)):
            item_id = recipe.data['hf_nr'][i]

            if item_id in product_data_ingredient: # ingredients
                subset_price_df = price_weight_data[price_weight_data['INGREDIENT CODE'] == item_id]
                
                if not len(subset_price_df) == 0:
                    new_price = subset_price_df[price_period].iloc[0]
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

    # Old prices
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
    
    # Weight
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

    # Waste
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

    # Quantities
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

    # Costs - non-HF
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
    
    # Costs - HF
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

    # Deltas
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

    return recipes