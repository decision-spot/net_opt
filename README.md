# Network Optimization
A two-echelon network optimization model with a given set of plants and customers.

## Problem
The goal of this model is to consider adding a few warehouses to reduce transportation cost and provide better services to the customers.

- We consider the plant locations as potential warehouse locations.
- There is a limit on the number of warehouses that we can have.
- Some plant locations must be used and some cannot be used.

Having these conditions, find out the best allocation of warehouses to customers.

Two different objective functions can be used:
- Minimizing total weighted distance
- Minimizing total transportation cost

## Repo Guide
- You can find all you need in the [network_optimization](network_optimization.ipynb) notebook.
- The python files (`plots.py` and `utils.py`) are helper functions.
- The notebook has a few parameters that one can change to see their effects; such as
maximum number of warehouses (or plant locations) and values used for cost.
- The `execute.py` file is similar to what you find in the notebook and it's added here
for those who wish to have all the code in a `.py` file rather than a notebook. 
That means, you can ignore the notebook and use this file as your starting point, 
running it in your favorite IDE or using command line. 
- A sample of data to run the model is given in [Sample Data.xlsx](Sample%20Data.xlsx).
A smaller version of that file is given in [Small Sample Data.xlsx](Small%20Sample%20Data.xlsx)
for those without access to Gurobi license 
(check out [License Requirement](#license-requirement) section for more info about the license).
Note that the column names in this file should be respected as they are used in the code.
- The main packages you need are `pandas`, `plotly`, and `gurobipy`. 
Although a full list of packages can be found in the [requirements.txt](requirements.txt) 
for those who wish to create an identical virtual environment (Python 3.9) to run the code.  
- An input map of the locations and an output map of the final assignment will be plotted.
By default, they are saved in your directory as html files.
- This repo was part of a workshop at 2022 Open Data Science Conference (ODSC) in Boston, where
we introduced data scientists to mathematical optimization and the reasons they should know about it.
You can find the pdf of those slides in [odsc22_presentation](odsc22_presentation.pdf). 

## Google Colab
If you like to access the notebook in Google Colab, click on 
[this link](https://colab.research.google.com/github/decision-spot/net_opt/blob/main/network_optimization.ipynb).
When you open the notebook, there will be further instructions under "For Google Colab Only" section.

Note that you must sign in with a Google account to be able to run the code in Colab.

### What is Google Colab?
Google Colab is a free, online Jupyter Notebook environment that allows you to 
write and execute Python code through your browser.
If you're curious to know the steps needed for loading a repo in Google Colab from scratch, here they are:
- Go to https://colab.research.google.com/ (you must sign in with your Google account).
- Click on the GitHub tab, and in the search box, enter this repo's URL (https://github.com/decision-spot/net_opt).
- You should see the `network_optimization.ipynb`. Click it and it opens in a new tab.

## License Requirement
The problem is modeled using Gurobi Python API. So, a Gurobi license is required to run this model.
If you don't have a license, you can request a free commercial evaluation license 
or a free academic license [here](https://www.gurobi.com/downloads/).
A smaller dataset is provided ([Small Sample Data.xlsx](Small%20Sample%20Data.xlsx))
that can be used to run the model with gurobi restricted license (available via 
`pip install gurobi` as shown in the notebook).