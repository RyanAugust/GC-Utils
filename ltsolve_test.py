import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from lactate_solver import lactate_solver

# read in lactate values
df = pd.read_excel("C:\\Users\\ryand\\Downloads\\Athlete_Examples.xlsx",sheet_name="RyanDryer")
# df = pd.read_excel("C:\\Users\\ryand\\Downloads\\Athlete_Examples.xlsx",sheet_name="Example")
pwr = df['power'].to_numpy()
lct = df['lactate'].to_numpy()
hr = df['heartrate'].to_numpy()


example = lactate_solver(lactate_vector=lct, heartrate_vector=hr, power_vector=pwr)
LT_output = example.find_LT_values(method_name='1+2')
print(LT_output)
example.plotter(save=True, **LT_output)