from math import radians, cos, sin, sqrt, atan2
from pathlib import Path

import pandas as pd


def load_raw_data(input_dir='', selected_sheets=None, get_single_file=True):
    assert (isinstance(selected_sheets, (str, list))
            or not selected_sheets), 'selected_sheets should be str, list, or None'
    if not isinstance(input_dir, Path):
        input_dir = Path(input_dir)
    assert input_dir.is_dir(), f'{input_dir} is not a valid directory'
    _dir = get_file_directory(input_dir)
    _input_files = _dir.glob('*.xlsx')
    if get_single_file:
        # We only have or care about the top excel file in the directory
        _input_files = next(_input_files)  # glob returns a generator and we're interested in the first file.
        if not _input_files:
            raise ValueError('Invalid file path! No Excel file was found!')
        input_df_dict = read_excel(_input_files, selected_sheets=selected_sheets)
    else:
        input_df_dict = read_excel_files(_input_files, selected_sheets)
    return input_df_dict


def get_file_directory(file):
    try:
        return Path(__file__).parents[0] / file
    except NameError:
        return Path().resolve() / file


def read_excel_files(input_files, selected_sheets=None):
    input_df_dict = {}
    for _file in input_files:
        file_name = Path(_file).stem
        df_dict = read_excel(_file, file_name, selected_sheets)
        if (isinstance(df_dict, pd.DataFrame) and not df_dict.empty) or df_dict:
            input_df_dict[file_name] = df_dict
    return input_df_dict


def read_excel(input_file, file_name='', selected_sheets=None):
    excel_file = pd.ExcelFile(input_file)
    sheets = selected_sheets or excel_file.sheet_names
    try:
        input_df_dict = pd.read_excel(excel_file, sheets)
    except Exception as e:  # xlrd.XLRDError or ValueError
        file_name = file_name or input_file
        print(f'WARNING: {file_name} is missing some sheets! {e}')
        input_df_dict = {}
    return input_df_dict


def calculate_distance_haversine(lat1, lon1, lat2, lon2, road_factor=1, units='miles'):
    """Compute great circle distance between two points

    Args:
        lat1 (float): lat coordinate of the first location in decimal degrees
        lon1 (float): lon coordinate of the first location in decimal degrees
        lat2 (float): lat coordinate of the second location in decimal degrees
        lon2 (float): lon coordinate of the second location in decimal degrees
        road_factor (float): multiply distance to account for road (default = 1)
        units (str): units for distance. It must be either miles or kilometers. Defaults to 'miles'
    Returns
        float: distance between points
    """
    # set radius of earth
    u = units.lower()
    r = 3958.756  # default is in miles
    if u in {'miles', 'mile', 'm'}:
        r = 3958.756  # another alternative 6376.4999975644832 km (3962.173405788 mile)
    elif u in {'kilometers', 'kilometer', 'km'}:
        r = 6371.00
    else:
        print(f"'km' or 'miles' are options. {units} is passed. 'miles' is used by default.")

    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = [radians(x) for x in [lat1, lon1, lat2, lon2]]
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    # asin and atan2 give the same result. Putting it here in case you had seen that version
    # c = 2 * asin(sqrt(a))
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c * road_factor


def prepare_location_dataframe(plants, customers):
    """Return a dataframe with the proper attributes needed for the plot."""
    origin_df = plants[['Plant Name', 'Latitude', 'Longitude']].copy()
    origin_df.rename(columns={'Plant Name': 'Origin', 'Latitude': 'Origin Lat',
                              'Longitude': 'Origin Lon'}, inplace=True)
    dest_df = customers[['Customer Name', 'Latitude', 'Longitude']].copy()
    dest_df.rename(columns={'Customer Name': 'Destination', 'Latitude': 'Dest Lat',
                            'Longitude': 'Dest Lon'}, inplace=True)
    df = pd.concat([origin_df, dest_df], sort=False, axis=1)
    return df
