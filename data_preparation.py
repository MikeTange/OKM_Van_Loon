import pandas as pd
import numpy as np


def rename_nan_columns(df : pd.DataFrame, prefix : str="col"):
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


def clean_dataframe(df : pd.DataFrame, replace_empty_with_na : bool=True):
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
    df = df.applymap(lambda x: x.replace(',', '.').strip() if isinstance(x, str) else x)

    # Optionally replace empty strings with pd.NA for better type inference
    if replace_empty_with_na:
        df.replace("", pd.NA, inplace=True)

    # Infer column types
    df = df.convert_dtypes()

    return df


def load_price_data(file_path : str, sheet_name : str, req_cols : list) -> pd.DataFrame:
    price_weight_data_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

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
    if not all(x in price_weight_data.columns for x in req_cols):
        print(f'Sommige essentiele kolommen missen in de prijslijst: {set(req_cols) - set(price_weight_data.columns)}')

    # Clean DataFrame values
    price_weight_data = clean_dataframe(price_weight_data).astype({"INGREDIENT CODE": 'string', "INGREDIENTS": 'string'}) # fix incorrect type inferences as strings (universally applicable)

    return price_weight_data


def load_waste_data(file_path : str, sheet_name : str, req_cols : list) -> pd.DataFrame:
    waste_data_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

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
    if not all(x in waste_data.columns for x in req_cols):
        print(f'Sommige essentiele kolommen missen in de waste lijst: {set(req_cols) - set(waste_data.columns)}')

    # Clean DataFrame values
    waste_data = clean_dataframe(waste_data).astype({'MEAL CODE': 'string', 'INGREDIENT CODE': 'string', 'UNITS': 'string'}) # fix incorrect type inferences as strings (universally applicable)

    # Add unique id column
    waste_data['id'] = waste_data[['MEAL CODE', 'INGREDIENT CODE']].agg('_'.join, axis=1).astype('string')

    return waste_data


def load_active_rec_data(file_path : str, sheet_name : str, req_cols : list) -> pd.DataFrame:
    active_rec_data_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

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
    if not all(x in active_rec_data.columns for x in req_cols):
        print(f'Sommige essentiele kolommen missen in de actieve recepten master: {set(req_cols) - set(active_rec_data.columns)}')

    # Clean DataFrame values
    active_rec_data = clean_dataframe(active_rec_data)

    return active_rec_data

