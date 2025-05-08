""" The Recipe class and it's associated methods """


import pandas as pd
import numpy as np


class MissingRequirementError(Exception):
    """ error to to raise for missing required columns for a method"""
    pass


class Recipe:
    """ 
    A Recipe 
    
    Attributes
    ----------
    name : str
        the name of the Recipe
    id : str
        the id of the Recipe
    bom : pd.DataFrame
        the BOM (Bill Of Materials) of the Recipe

    Methods
    --------
    add_categories()
        Classify each item in the BOM to a category, and add this to the Recipe BOM.
    add_new_prices()
        Determine a new price for each item in the BOM, and add this to the Recipe BOM.
    add_old_prices()
        Calculate the old price for each item in the BOM, and add this to the Recipe BOM.
    add_weights()
        Calculate the weight in kilos for all items whose unit is not already kilos, and add this to the Recipe BOM.
    add_wastes()
        Determine the wastes (NAV, FIN, USE) for each item in the BOM, and add this to the Recipe BOM.
    add_quantities()
        Calculate the new quantities for each item in the BOM based on its waste, and add this to the Recipe BOM.
    add_costs()
        Calculate the new costs for each item in the BOM based on its new prices and quantities, and add this to the Recipe BOM.
    """


    def __init__(self, name : str, id : str, bom : pd.DataFrame) -> None:
        """ 
        Initialise an instance of Recipe.
        
        Parameters
        ----------
        name : str
            the name of the Recipe
        id : str
            the id of the Recipe
        bom : pd.DataFrame
            the BOM (Bill Of Materials) of the Recipe
        """

        self.name = name
        self.id = id
        self.bom = bom


    def __str__(self) -> str:
        """ set the string representation of a Recipe """
        return f'{self.id} {self.name}'
    

    def add_categories(self, ingredients : np.array, HFs : np.array, packagings : np.array, id_column : str='hf_nr', out_col_name : str='Categorie') -> None:
        """ 
        Classify each item in the BOM to a category, and add this to the Recipe BOM.
        
        Parameters
        ----------
        ingredients : np.array
            the item ids which are to be classified as an 'Ingredient'
        HFs : np.array
            the item ids which are to be classified as a 'Halffabrikaat'
        packagings : np.array
            the item ids which are to be classified as a 'Verpakking'
        id_column : str
            the name of the self.bom column containing the item ids
        out_col_name : str
            the name of the newly added column
        """

        categories = []

        for i in range(len(self.bom)):
            item_id = self.bom[id_column][i]

            if item_id in ingredients:
                categories.append('Ingredient')

            elif item_id in HFs:
                categories.append('Halffabrikaat')

            elif item_id in packagings:
                categories.append('Verpakking')
            
            else:
                categories.append('Ongeclassificeerd')
        
        self.bom[out_col_name] = categories


    def add_new_prices(self, 
                       ingredients : np.array, 
                       HFs : np.array, 
                       packagings : np.array, 
                       price_data : pd.DataFrame,
                       prices_col : str,
                       price_data_id_col : str,
                       id_column : str='hf_nr', 
                       out_col_name : str='Nieuwe Prijs') -> None:
        """
        Determine a new price for each item in the BOM, and add this to the Recipe BOM.

        Ingredients should have a new price specified in price_data.
        HFs don't have prices (only costs). They are set to np.nan rather than None, 
            so numpy will interpret them as empty values for later calculations.
        Packagings are set to have a new price of 0.

        Parameters
        ----------
        ingredients : np.array
            the ids of the ingredient items
        HFs : np.array
            the ids of the HF (halffabrikaat) items
        packagings : np.array
            the ids of the packaging items
        price_data : pd.DataFrame
            DataFrame containing the price data
        prices_col : str
            the name of the price_data column containing the new prices
        price_data_id_col : str
            the name of the price_data column containing the item ids
        id_column : str
            the name of the Recipe.bom column containing the item ids
        out_col_name : str
            the name of the newly added column
        """

        new_prices = []

        for i in range(len(self.bom)):
            item_id = self.bom[id_column][i]

            if item_id in ingredients:
                subset_price_df = price_data[price_data[price_data_id_col] == item_id]
                
                if not len(subset_price_df) == 0:
                    new_price = subset_price_df[prices_col].iloc[0]
                else:
                    new_price = 'Geen nieuwe prijs'
            
            elif item_id in packagings:
                new_price = 0

            elif item_id in HFs:
                new_price = np.nan
            
            else: # unclassified items
                new_price = 'Geen nieuwe prijs'
        
            new_prices.append(new_price)
            
        self.bom[out_col_name] = new_prices


    def add_old_prices(self, 
                       ingredients : np.array, 
                       HFs : np.array, 
                       packagings : np.array, 
                       costs_col : str='Materiaalkosten',
                       quantities_col : str='Aantal (Basis)',
                       id_column : str='hf_nr', 
                       out_col_name : str='Oude Prijs') -> None:
        """
        Calculate the old price for each item in the BOM, and add this to the Recipe BOM.

        Only ingredients (and unclassified items) have a calculated old price. 
        HFs are left blank, and packagings are set to 0.

        Parameters
        ----------
        ingredients : np.array
            the ids of the ingredient items
        HFs : np.array
            the ids of the HF (halffabrikaat) items
        packagings : np.array
            the ids of the packaging items
        costs_col : str
            the name of the Recipe.bom column containing the old costs
        quantities_col : str
            the name of the Recipe.bom column containing the old quantities
        id_column : str
            the name of the Recipe.bom column containing the item ids
        out_col_name : str
            the name of the newly added column
        """

        old_prices = []

        for i in range(len(self.bom)):
            item_id = self.bom[id_column][i]

            if item_id in ingredients:
                old_price = self.bom[costs_col][i] / self.bom[quantities_col][i]
            
            elif item_id in packagings:
                old_price = 0

            elif item_id in HFs:
                old_price = None

            else: # unclassified
                old_price = self.bom[costs_col][i] / self.bom[quantities_col][i]
        
            old_prices.append(old_price)
            
        self.bom[out_col_name] = old_prices


    def add_weights(self, 
                    packagings : np.array, 
                    weight_data : pd.DataFrame,
                    price_data_id_col : str='INGREDIENT CODE',
                    unit_column : str='Basiseenheid',
                    quantities_column : str='Aantal (Basis)',
                    id_column : str='hf_nr', 
                    out_col_name : str='Grammage') -> None:
        """
        Calculate the weight in kilos for all items whose unit is not already kilos, and add this to the Recipe BOM.

        Packagings are set to have a weight of 0. 
        The weights of all other items are either converted to kilos or copied if already in kilos.

        Parameters
        ----------
        packagings : np.array
            the ids of the packaging items
        weight_data : pd.DataFrame
            DataFrame containing the weight data
        price_data_id_col : str
            the name of the weight_data column containing the item ids
        unit_column : str
            the name of the Recipe.bom column containing the units
        quantities_column : str
            the name of the Recipe.bom column containing the old quantities
        id_column : str
            the name of the Recipe.bom column containing the item ids
        out_col_name : str
            the name of the newly added column
        """

        weights = []

        for i in range(len(self.bom)):
            item_id = self.bom[id_column][i]

            if item_id in packagings: # packaging to 0
                weight = 0.0

            elif not self.bom[unit_column][i] == 'KG':

                subset_weight_data = weight_data[weight_data[price_data_id_col] == item_id]

                if len(subset_weight_data) == 0: # no info about this item
                    weight = 'Geen conversie info'
                
                elif len(subset_weight_data) == 1: # new info about this item
                    weight = subset_weight_data['KG'].iloc[0] * self.bom[quantities_column][i]

                else:
                    weight = 'Dubbele conversie info'
            
            else:
                weight = self.bom[quantities_column][i]

            weights.append(weight)

        self.bom[out_col_name] = weights


    def add_wastes(self, 
                   HFs : np.array,
                   waste_data : pd.DataFrame,
                   waste_data_id_col : str='id',
                   waste_data_nav_col : str='WASTE-NAV',
                   waste_data_fin_col : str='WASTE-FIN',
                   waste_data_use_col : str='WASTE-USE',
                   level_column : str='Niveau',
                   id_column : str='hf_nr', 
                   out_col_name_nav : str='Waste NAV',
                   out_col_name_fin : str='Waste FIN',
                   out_col_name_use : str='Waste USE') -> None:
        """
        Determine the wastes (NAV, FIN, USE) for each item in the BOM, and add this to the Recipe BOM.

        Waste is determined at the highest level (level 1). 
        Lower level items inherit their waste from the level 1 item they are a part of.
        If no waste is determined at level 1, it is assumed to be 0.

        Parameters
        ----------
        HFs : np.array
            the ids of the HF (halffabrikaat) items
        waste_data : pd.Dataframe
            DataFrame containing the waste data
        waste_data_id_col : str
            the name of the waste_data column containing the ids (Recipe id + item id)
        waste_data_nav_col : str
            the name of the waste_data column containing the NAV wastes
        waste_data_fin_col : str
            the name of the waste_data column containing the FIN wastes
        waste_data_use_col : str
            the name of the waste_data column containing the USE wastes
        level_column : str
            the name of the Recipe.bom column containing the levels
        id_column : str
            the name of the Recipe.bom column containing the item ids
        out_col_name_nav : str
            the name of the newly added column for NAV waste
        out_col_name_fin : str
            the name of the newly added column for FIN waste
        out_col_name_use : str
            the name of the newly added column for USE waste
        """

        waste_nav_col = []
        waste_fin_col = []
        waste_use_col = []

        for i in range(len(self.bom)):
            item_id = self.bom[id_column][i]

            if self.bom[level_column][i] == 1: # waste is only determined at level 1
                subset_waste_data = waste_data[waste_data[waste_data_id_col] == f'{self.id}_{item_id}']

                if len(subset_waste_data) == 0:
                    waste_nav = 0
                    waste_fin = 0
                    waste_use = 0

                elif len(subset_waste_data) == 1:
                    waste_nav = subset_waste_data[waste_data_nav_col].iloc[0]
                    waste_fin = subset_waste_data[waste_data_fin_col].iloc[0]
                    waste_use = subset_waste_data[waste_data_use_col].iloc[0]

                else:
                    waste_nav = 'Dubbele waste info'
                    waste_fin = 'Dubbele waste info'
                    waste_use = 'Dubbele waste info'
            
            else:
                for j in range(i, -1, -1): # loop backwards to find the closest level 1 item
                    if self.bom[level_column].iloc[j] == 1:

                        if self.bom[id_column].iloc[j] in HFs:
                            parent_hf_id = self.bom[id_column].iloc[j]
                            subset_waste_data_parent = waste_data[waste_data[waste_data_id_col] == f'{self.id}_{parent_hf_id}']

                            if len(subset_waste_data_parent) == 0:
                                waste_nav = 0
                                waste_fin = 0
                                waste_use = 0

                            elif len(subset_waste_data_parent) == 1:
                                waste_nav = subset_waste_data_parent[waste_data_nav_col].iloc[0]
                                waste_fin = subset_waste_data_parent[waste_data_fin_col].iloc[0]
                                waste_use = subset_waste_data_parent[waste_data_use_col].iloc[0]

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

        self.bom[out_col_name_nav] = waste_nav_col
        self.bom[out_col_name_fin] = waste_fin_col
        self.bom[out_col_name_use] = waste_use_col


    def add_quantities(self,
                       quantities_column : str='Aantal (Basis)',
                       waste_nav_column : str='Waste NAV',
                       waste_use_column : str='Waste USE',
                       out_col_name_q : str='Aantal (nieuw)',
                       out_col_name_q_no_waste : str='Aantal (zonder waste)') -> None:
        """
        Calculate the new quantities for each item in the BOM based on its waste, and add this to the Recipe BOM.

        CAUTION:
            This method requires the add_wastes() method to have ran previously.
        
        Parameters
        ----------
        quantities_column : str
            the name of the Recipe.bom column containing the old quantities
        waste_nav_column : str
            the name of the Recipe.bom column containing the NAV wastes
        waste_use_column : str
            the name of the Recipe.bom column containing the USE wastes
        out_col_name_q : str
            the name of the newly added column for the new quantities
        out_col_name_q_no_waste : str
            the name of the newly added column for the new quantities disregarding waste

        Raises
        ------
        MissingRequirementError
            if required columns are missing from the Recipe BOM
        """
        
        # Checking requirements
        requirements = {'Waste NAV', 'Waste USE'}
        req_test = requirements.difference(set(self.bom.columns))
        if len(req_test) > 0:
            raise MissingRequirementError(f'missing one or more required column(s): {req_test}. Run add_wastes() before attempting to run add_quantities()')

        q_no_waste_col = []
        q_new_col = []

        for i in range(len(self.bom)):
            
            try:
                q_no_waste = self.bom[quantities_column][i] / (1 + self.bom[waste_nav_column][i])
            except TypeError:
                q_no_waste = 'Kan niet berekenen'

            try:
                q_new = q_no_waste * (1 + self.bom[waste_use_column][i])
            except TypeError:
                q_new = 'Kan niet berekenen'

            q_no_waste_col.append(q_no_waste)
            q_new_col.append(q_new)

        self.bom[out_col_name_q_no_waste] = q_no_waste_col
        self.bom[out_col_name_q] = q_new_col


    def add_costs(self,
                  ingredients : np.array,
                  HFs : np.array,
                  packagings : np.array,
                  new_price_column : str='Nieuwe prijs',
                  quantities_old_column : str='Aantal (Basis)',
                  quantities_new_column : str='Aantal (nieuw)',
                  level_column : str='Niveau',
                  id_column : str='hf_nr', 
                  out_col_name_newp_oldq : str='Nieuwe vvp',
                  out_col_name_newp_newq : str='Materiaalkosten (nieuw)') -> None:
        """
        Calculate the new costs fo each item in the BOM based on its new prices and quantities, 
            and add this to the Recipe BOM.

        This method does two passes over the BOM. Costs for non-HF (halffabrikaat) items are determined on the first pass. 
        On the second pass the costs for HF items are determined by summing the costs of all underlying (lower level) non-HF items; 
            these are then inserted into the DataFrame at the appropriate positions.

        CAUTION:
            This method requires the add_new_prices() and add_quantities() methods to have ran previously.

        Parameters
        ----------
        ingredients : np.array
            the ids of the ingredient items
        HFs : np.array
            the ids of the HF (halffabrikaat) items
        packagings : np.array
            the ids of the packaging items
        new_price_column : str
            the name of the Recipe.bom column containing the new prices
        quantities_old_column : str
            the name of the Recipe.bom column containing the old quantities
        quantities_new_column : str
            the name of the Recipe.bom column containing the new quantities
        level_column : str
            the name of the Recipe.bom column containing the levels
        id_column : str
            the name of the Recipe.bom column containing the item ids
        out_col_name_newp_oldq : str
            the name of the newly added column for the costs of the new price * old quantity
        out_col_name_newp_newq : str
            the name of the newly added column for the costs of the new price * new quantity

        Raises
        ------
        MissingRequirementError
            if required columns are missing from the Recipe BOM
        """

        # Checking requirements
        requirements = {'Nieuwe prijs', 'Aantal (nieuw)'}
        req_test = requirements.difference(set(self.bom.columns))
        if len(req_test) > 0:
            raise MissingRequirementError(f'missing one or more required column(s): {req_test}. Run add_new_prices() and add_quantities() \
                                          before attempting to run add_costs()')

        # Costs - non-HF
        newp_oldq_col = []
        newp_newq_col = []

        for i in range(len(self.bom)):
            item_id = self.bom[id_column][i]

            if (item_id in ingredients) or (item_id in packagings):
                try:
                    newp_oldq = self.bom[new_price_column][i] * self.bom[quantities_old_column][i]
                    newp_newq = self.bom[new_price_column][i] * self.bom[quantities_new_column][i]
                
                except TypeError: # could use the old price here as well
                    newp_oldq = 'Kan niet berekenen'
                    newp_newq = 'Kan niet berekenen'
            
            elif item_id in HFs:
                newp_oldq = None
                newp_newq = None
            
            else:
                newp_oldq = 'Ongeclassificeerd item'
                newp_newq = 'Ongeclassificeerd item'

            newp_oldq_col.append(newp_oldq)
            newp_newq_col.append(newp_newq)

        self.bom[out_col_name_newp_oldq] = newp_oldq_col
        self.bom[out_col_name_newp_newq] = newp_newq_col
    
        # Costs - HF
        for i in range(len(self.bom)):
            item_id = self.bom[id_column][i]

            if item_id in HFs:

                hf_newp_oldq = 0.0
                hf_newp_newq = 0.0

                hf_level = self.bom[level_column][i]
                for j in range(i + 1, len(self.bom)):
                    if self.bom[level_column][j] > hf_level:

                        try:
                            if not np.isnan(self.bom[out_col_name_newp_oldq][j]):
                                hf_newp_oldq += self.bom[out_col_name_newp_oldq][j]
                        except:
                            pass
                        
                        try:
                            if not np.isnan(self.bom[out_col_name_newp_newq][j]):
                                hf_newp_newq += self.bom[out_col_name_newp_newq][j]
                        except:
                            pass
                        
                    else:
                        break
            
                self.bom.at[i, out_col_name_newp_oldq] = hf_newp_oldq
                self.bom.at[i, out_col_name_newp_newq] = hf_newp_newq


    def add_deltas(self,
                   new_price_column : str='Nieuwe prijs',
                   old_price_column : str='Oude prijs',
                   quantities_old_column : str='Aantal (Basis)',
                   quantities_new_column : str='Aantal (nieuw)',
                   old_costs_column : str='Materiaalkosten',
                   new_costs_column : str='Materiaalkosten (nieuw)',
                   new_cost_oldq_column : str='Nieuwe vvp',
                   out_col_name_delta_q : str='Delta Q',
                   out_col_name_delta_p : str='Delta prijs',
                   out_col_name_delta_cost : str='Delta materiaalkosten',
                   out_col_name_delta_waste : str='Delta FIN waste') -> None:
        """
        Calculate the deltas (Q, P, cost, waste) for each item in the BOM, and add these to the Recipe BOM.

        CAUTION:
            This method requires the add_old_prices() and add_costs() methods to have ran previously.

        Parameters
        ----------
        new_price_column : str
            the name of the Recipe.bom column containing the new prices
        old_price_column : str
            the name of the Recipe.bom column containing the old prices
        quantities_old_column : str
            the name of the Recipe.bom column containing the old quantities
        quantities_new_column : str
            the name of the Recipe.bom column containing the new quantities
        old_costs_column : str
            the name of the Recipe.bom column containing the old costs
        new_costs_column : str
            the name of the Recipe.bom column containing the new costs
        new_cost_oldq_column : str
            the name of the Recipe.bom column containing the new costs of the old quantities
        out_col_name_delta_q : str
            the name for the newly added column for delta Q (quantity)
        out_col_name_delta_p : str
            the name for the newly added column for delta P (price)
        out_col_name_delta_cost : str
            the name for the newly added column for delta cost
        out_col_name_delta_waste : str
            the name for the newly added column for delta waste

        Raises
        ------
        MissingRequirementError
            if required columns are missing from the Recipe BOM
        """

        # Checking requirements
        requirements = {'Nieuwe prijs', 'Oude prijs', 'Aantal (nieuw)', 'Materiaalkosten (nieuw)', 'Nieuwe vvp'}
        req_test = requirements.difference(set(self.bom.columns))
        if len(req_test) > 0:
            raise MissingRequirementError(f'missing one or more required column(s): {req_test}. Run add_new_prices() and add_quantities() \
                                          before attempting to run add_costs()')

        delta_q_col = []
        delta_p_col = []
        delta_cost_col = []
        fin_waste_impact_col = []

        for i in range(len(self.bom)):

            try:
                delta_q = (self.bom[quantities_new_column][i] - self.bom[quantities_old_column][i]) * self.bom[old_price_column][i]
            except TypeError:
                delta_q = 'Kan niet berekenen'
            
            try:
                delta_p = (self.bom[new_price_column][i] - self.bom[old_price_column][i]) * self.bom[quantities_new_column][i]
            except TypeError:            
                delta_p = 'Kan niet berekenen'
            
            try:                  
                delta_cost = self.bom[new_costs_column][i] - self.bom[old_costs_column][i]
            except TypeError:
                delta_cost = 'Kan niet berekenen'
            
            try:
                fin_waste_impact = self.bom[new_costs_column][i] - self.bom[new_cost_oldq_column][i]
            except TypeError:
                fin_waste_impact = 'Kan niet berekenen'

            delta_q_col.append(delta_q)
            delta_p_col.append(delta_p)
            delta_cost_col.append(delta_cost)
            fin_waste_impact_col.append(fin_waste_impact)
        
        self.bom[out_col_name_delta_q] = delta_q_col
        self.bom[out_col_name_delta_p] = delta_p_col
        self.bom[out_col_name_delta_cost] = delta_cost_col
        self.bom[out_col_name_delta_waste] = fin_waste_impact_col