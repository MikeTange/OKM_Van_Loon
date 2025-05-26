""" Set the parameters surrounding the OKM processing app """

### INPUT PARAMETERS ###
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


### REQUIREMENTS ###
# Input files
req_cols_price_weight = ['INGREDIENT CODE', 'INGREDIENTS', 'KG'] # prices & weights
req_cols_waste = ['MEAL CODE', 'INGREDIENT CODE', 'WASTE-NAV', 'WASTE-FIN', 'WASTE-USE'] # waste
req_cols_act_rec = ['Artikel'] # active recipes
