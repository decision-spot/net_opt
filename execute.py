"""
Author = Ehsan Khodabandeh
Copyright 2022, Decision Spot, LLC

Assign plants to customers considering a limit on the number of plants to use.
Some plants must be used and some cannot be used.
The solution is driven by weighted distance or transportation cost.
"""
import sys

import pandas as pd
import gurobipy as gp
from gurobipy import GRB

from plots import plot_network
from utils import calculate_distance_haversine, prepare_location_dataframe


def prep_data(file_name):
    input_df_dict = pd.read_excel(file_name, sheet_name=None)
    cust_df = input_df_dict['Customers']
    plant_df = input_df_dict['Plants']
    cust_df.rename(columns={'ID': 'Customer ID', 'Name': 'Customer Name'}, inplace=True)
    plant_df.rename(columns={'ID': 'Plant ID', 'Name': 'Plant Name'}, inplace=True)
    return plant_df, cust_df


def plot_input_map(plant_df, cust_df):
    # Prepare data to plot the input network
    locations = prepare_location_dataframe(plant_df, cust_df)
    plot_network(locations, add_path=False, auto_open_map=False, title='Input Map',
                 open_map_in_cell=open_map_in_cell)


def run_network_optimization(plant_df, cust_df, auto_open_map=True):
    """This is mainly a P-median problem."""
    # region Set Up Data
    dist = get_distance(plant_df, cust_df)
    dist['Cost'] = dist['Distance'].apply(lambda x: max(cost_per_mile * x, min_cost))
    dmd = cust_df.set_index(['Customer ID'])

    # Sets
    plnt = plant_df['Plant ID'].unique()
    cust = cust_df['Customer ID'].unique()
    ij_set = set((i, j) for i in plnt for j in cust)
    must_use_plants = plant_df.loc[plant_df['Must Use'], 'Plant ID'].to_list()
    unavailable_plants = plant_df.loc[~plant_df['Can Use'], 'Plant ID'].to_list()
    # endregion

    # region Optimization Model
    mdl = gp.Model('net_optimization')

    # Variables
    x = mdl.addVars(plnt, vtype=GRB.BINARY, name='x')
    y = mdl.addVars(plnt, cust, vtype=GRB.BINARY, name='y')

    # Constraints
    # 1. Every customer must be assigned to one plant
    # sum_{i} y_{ij} = 1    for all j
    mdl.addConstrs((y.sum('*', j) == 1 for j in cust), 'cust_coverage')

    # 2. We can use maximum P plants
    # sum_{i} x_{i} <= P
    mdl.addConstr(x.sum() <= max_plants, 'max_num_plants')

    # 3. Cant serve a customer from a plant if it's not used
    # y_{ij} <= x_{i}    for all i, j
    mdl.addConstrs((y[i, j] <= x[i] for (i, j) in ij_set), 'rel_x_y')

    # Extra
    # 4. Plants that we must use
    # x_{i} = 1    for all i in F
    mdl.addConstrs((x[i] == 1 for i in must_use_plants), 'must_use')

    # 5. Plants that we cannot use
    # x_{i} = 0    for all i in U
    mdl.addConstrs((x[i] == 0 for i in unavailable_plants), 'cant_use')

    # KPI
    total_weighted_dist = gp.quicksum(dist.loc[i, j]['Distance'] * dmd.loc[j]['Demand'] * y[i, j]
                                      for (i, j) in ij_set)
    # Objective function
    # Case 1: minimize total weighted distance
    objective = total_weighted_dist
    # # Case 2: minimize total transportation cost
    # objective = gp.quicksum((dist.loc[i, j]['Cost'] * y[i, j]) for (i, j) in ij_set)
    mdl.setObjective(objective, GRB.MINIMIZE)
    mdl.setParam(GRB.Param.OutputFlag, 1)  # enables or disables solver output
    # mdl.write(mdl.ModelName + '.lp')  # writing the optimization model to a '.lp' file
    mdl.optimize()
    status = mdl.status
    if status in (GRB.INF_OR_UNBD, GRB.INFEASIBLE, GRB.UNBOUNDED):
        print('The model is either infeasible or unbounded!')
        sys.exit(1)
    elif status == GRB.OPTIMAL:
        print(f'The solution is optimal and the objective value is: {mdl.objVal:,.0f}')
    else:
        print(f'Status is {status}. Investigate!')
        sys.exit(1)
    # endregion

    lanes = generate_outputs(plant_df, cust_df, dist, dmd, total_weighted_dist, x, y)
    # Plot output map
    plot_network(lanes, auto_open_map=auto_open_map, title='Solution Map',
                 open_map_in_cell=open_map_in_cell)


def get_distance(orig_df, dest_df):
    df = orig_df.merge(dest_df, how='cross').set_index(['Plant ID', 'Customer ID'])
    df['Distance'] = df.apply(lambda r: calculate_distance_haversine(
        r['Latitude_x'], r['Longitude_x'], r['Latitude_y'], r['Longitude_y']), axis=1)
    return df


def generate_outputs(plant_df, cust_df, dist, dmd, total_weighted_dist, x, y):
    # region Post Process
    print('=' * 40)
    assigned_list = [k for k, v in y.items() if v.x > 0.5]
    assigned_df = pd.DataFrame(assigned_list, columns=['Plant ID', 'Customer ID'])
    _opt_plants = [plant_df.loc[plant_df['Plant ID'] == k, 'City'].iloc[0]
                   for k, v in x.items() if v.x > 0.5]
    print(f'Selected plants are in: {", ".join(str(_) for _ in _opt_plants)}')
    adf = pd.merge(assigned_df, dmd[['Demand']], how='inner',
                   left_on='Customer ID', right_index=True)
    adf = pd.merge(adf.set_index(['Plant ID', 'Customer ID']), dist[['Distance']],
                   how='inner', left_index=True, right_index=True).reset_index()
    adf['Within400'] = [True if x <= 400 else False for x in adf['Distance']]
    adf['Within800'] = [True if x <= 800 else False for x in adf['Distance']]
    adf['Within1200'] = [True if x <= 1200 else False for x in adf['Distance']]
    total_dmd = adf['Demand'].sum()
    weighted_avg_dist = total_weighted_dist.getValue() / total_dmd
    print(f'Weighted Average Distance: {weighted_avg_dist:,.1f}')
    pct_dmd_within400 = adf.loc[adf['Within400'], 'Demand'].sum() / total_dmd
    pct_dmd_within800 = adf.loc[adf['Within800'], 'Demand'].sum() / total_dmd
    pct_dmd_within1200 = adf.loc[adf['Within1200'], 'Demand'].sum() / total_dmd
    print(f'Total demand: {total_dmd:,.0f}')
    print(f'Percentages of demand within 400 miles of a plant: {pct_dmd_within400 * 100:,.2f}%')
    print(f'Percentages of demand within 800 miles of a plant: {pct_dmd_within800 * 100:,.2f}%')
    print(f'Percentages of demand within 1200 miles of a plant: {pct_dmd_within1200 * 100:,.2f}%')
    print('=' * 40)
    # Create the set of lanes
    lanes = pd.merge(assigned_df, dmd[['Demand']], how='inner',
                     left_on='Customer ID', right_index=True)
    lanes['Lane'] = lanes['Plant ID'].map(str) + '-' + lanes['Customer ID'].map(str)
    lanes = lanes[['Plant ID', 'Customer ID', 'Demand', 'Lane']].merge(
        cust_df[['Customer ID', 'Customer Name', 'Latitude', 'Longitude']], on='Customer ID')
    lanes.rename(columns={'Latitude': 'Dest Lat', 'Longitude': 'Dest Lon'}, inplace=True)
    lanes = lanes.merge(plant_df[['Plant ID', 'Plant Name', 'Latitude', 'Longitude']], on='Plant ID')
    lanes.rename(columns={'Latitude': 'Origin Lat', 'Longitude': 'Origin Lon',
                          'Plant Name': 'Origin', 'Customer Name': 'Destination'}, inplace=True)
    lanes = lanes[['Lane', 'Origin', 'Destination', 'Demand', 'Plant ID',
                   'Origin Lat', 'Origin Lon', 'Customer ID', 'Dest Lat', 'Dest Lon']].drop_duplicates()
    # endregion
    return lanes


if __name__ == '__main__':
    # ================== Set up data ==================
    # Params
    max_plants = 3
    cost_per_mile = 2
    min_cost = 450
    open_map_in_cell = False  # This is for Jupyter Notebook. The map is saved in an HTML file anyway
    auto_open_map = True  # Whether to open the output map automatically in the browser.
    file_name = 'Sample Data.xlsx'  # Two choices: 'Sample Data.xlsx' and 'Small Sample Data.xlsx'
    plant_df, cust_df = prep_data(file_name)
    plot_input_map(plant_df, cust_df)
    run_network_optimization(plant_df, cust_df, auto_open_map)
