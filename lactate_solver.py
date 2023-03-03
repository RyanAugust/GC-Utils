import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# read in lactate values
df = pd.read_csv("C:\\Users\\ryand\\Downloads\\Athlete_Example.csv")
pwr = df['power'].to_numpy()
lct = df['lactate'].to_numpy()
hr = df['heartrate'].to_numpy()

p3 = np.poly1d(np.polyfit(x=pwr, y=lct, deg=3))

x_new = np.linspace(start=pwr.min() ,stop=pwr.max() ,num=200)
lac_fit = p3(x_new)

fig, ax = plt.subplots(1,1, dpi=200, figsize=(10,6))
ax.scatter(x=pwr, y=lct, color='blue', label='Lactate Values')
ax.plot(x_new, lac_fit, color='lightblue', label='Lactate Curve')
ax1 =ax.twinx()
ax1.scatter(x=pwr, y=hr, color='red', label='Heartrate Values')

## Reference Lines
ax.axhline(y=2, ls='--', lw=1, color='black', label='2mmol/L Lactate')
ax.axhline(y=4, ls=':', lw=1, color='black', label='4mmol/L Lactate')

ax.set_xlabel('Power')
ax.set_ylabel('Lactate Concentration (mmol/L)')
ax1.set_ylabel('Heartrate (bpm)')

fig.legend()

plt.savefig('plot.png')