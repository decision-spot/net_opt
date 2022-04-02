"""Script to create Hub & Spoke plots.
Obtained and modified the code of:
https://github.com/ekhoda/plotly_hub_and_spoke
"""
import plotly.graph_objects as go


def plot_network(data, add_path=True, auto_open_map=False, title='', open_map_in_cell=False):
    """Plot a hub-and-spoke network."""
    # Prepare the data
    df_dict = create_location_dataframe(data)
    locations = set_locations_map(df_dict)
    lat_range, lon_range = get_lat_lon_range(df_dict)
    scope = get_scope(lat_range, lon_range)

    fig = go.Figure()
    # Specify the layout attributes
    title = title or f'{scope.upper()} Network'
    layout = dict(title=title,
                  showlegend=True,
                  geo=dict(
                      scope=scope,
                      showland=True,
                      # # if you want to zoom only on the area with lat/lon rather than the whole scope
                      # lataxis=dict(range=lat_range),
                      # lonaxis=dict(range=lon_range),
                      landcolor='rgb(243, 243, 243)',
                      countrycolor='rgb(204, 204, 204)'))
    fig.update_layout(layout)

    # Add locations
    for d in locations:
        fig.add_trace(d)

    # Add paths
    if add_path:
        for i, row in data.iterrows():
            fig.add_trace(go.Scattergeo(
                lon=[row['Origin Lon'], row['Dest Lon']],
                lat=[row['Origin Lat'], row['Dest Lat']],
                mode='lines',
                line=dict(width=2, color='green'),
                opacity=0.8,
                showlegend=False,
            ))

    if open_map_in_cell:
        fig.show()  # to show it in Jupyter notebook
    # Save the map as an HTML in the current directory and whether to automatically open it or not
    fig.write_html(file=f'{title}.html', auto_open=auto_open_map)


def create_location_dataframe(data):
    """Return a dataframe with the proper attributes needed for the plot."""
    origin_df = data[['Origin', 'Origin Lat', 'Origin Lon']].drop_duplicates()
    origin_df['text'] = origin_df['Origin']
    origin_df['size'] = 20
    origin_df['color'] = 'blue'
    origin_df['shape'] = 'triangle-up'
    origin_df['name'] = origin_df['Origin']
    origin_df.rename(columns={'Origin Lat': 'lat', 'Origin Lon': 'lon'}, inplace=True)

    dest_df = data[['Destination', 'Dest Lat', 'Dest Lon']].drop_duplicates()
    dest_df['text'] = dest_df['Destination']
    dest_df['size'] = 8
    dest_df['color'] = 'orange'
    dest_df['shape'] = 'circle'
    dest_df['name'] = dest_df['Destination']
    dest_df.rename(columns={'Dest Lat': 'lat', 'Dest Lon': 'lon'}, inplace=True)
    # we'll concat origin_df with dest_df
    origin_df.drop('Origin', axis=1, inplace=True)
    dest_df.drop('Destination', axis=1, inplace=True)

    df_dict = {'Plant': origin_df, 'Customer': dest_df}
    return df_dict


def set_locations_map(df_dict):
    """Create a list of dictionaries that hold location attributes needed for the plot."""
    locations = []
    for name, df in df_dict.items():
        try:
            locations.append(
                dict(type='scattergeo',
                     lon=df['lon'],
                     lat=df['lat'],
                     text=df['text'],
                     name=name,
                     marker=dict(size=df['size'],
                                 symbol=df['shape'],
                                 color=df['color'],
                                 line=dict(width=3, color='rgba(68, 68, 68, 0)'))))
        except KeyError:
            pass
    return locations


def get_lat_lon_range(df_dict):
    """Return the range of lat and lon in the data."""
    min_lat = +90
    max_lat = -90
    min_lon = +180
    max_lon = -180
    for df in df_dict.values():
        try:
            df_lat_min = df['lat'].min()
            df_lat_max = df['lat'].max()
            df_lon_min = df['lon'].min()
            df_lon_max = df['lon'].max()
            if df_lat_min < min_lat:
                min_lat = df_lat_min
            if df_lat_max > max_lat:
                max_lat = df_lat_max
            if df_lon_min < min_lon:
                min_lon = df_lon_min
            if df_lon_max > max_lon:
                max_lon = df_lon_max
        except KeyError:
            pass
    return [min_lat, max_lat], [min_lon, max_lon]


def get_scope(lat_range, lon_range):
    """Assign the proper scope based on range of data's lat/lon.

    The geographic scope in Plotly can be one of:
    "world" | "usa" | "europe" | "asia" | "africa" | "north america" | "south america".
    (source: https://plot.ly/python/reference/#layout-geo-scope)

    We're interested in USA, North America, South America, and Europe.
    """
    us_lat_rng = [24, 55]
    us_lon_rng = [-127, -50]
    na_lat_rng = [15, 85]
    na_lon_rng = [-170, -50]
    eu_lat_rng = [30, 80]
    eu_lon_rng = [-20, 70]
    sa_lat_rng = [-60, 12]
    sa_lon_rng = [-81, -34]

    if (lat_range[0] >= us_lat_rng[0] and lat_range[1] <= us_lat_rng[1]
            and lon_range[0] >= us_lon_rng[0] and lon_range[1] <= us_lon_rng[1]):
        scope = 'usa'
    elif (lat_range[0] >= na_lat_rng[0] and lat_range[1] <= na_lat_rng[1]
          and lon_range[0] >= na_lon_rng[0] and lon_range[1] <= na_lon_rng[1]):
        scope = 'north america'
    elif (lat_range[0] >= eu_lat_rng[0] and lat_range[1] <= eu_lat_rng[1]
          and lon_range[0] >= eu_lon_rng[0] and lon_range[1] <= eu_lon_rng[1]):
        scope = 'europe'
    elif (lat_range[0] >= sa_lat_rng[0] and lat_range[1] <= sa_lat_rng[1]
          and lon_range[0] >= sa_lon_rng[0] and lon_range[1] <= sa_lon_rng[1]):
        scope = 'south america'
    else:  # can add asia and africa
        scope = 'world'  # default
    return scope
