import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# read in lactate values
df = pd.read_excel("C:\\Users\\ryand\\Downloads\\Athlete_Examples.xlsx",sheet_name="RyanDryer")
# df = pd.read_excel("C:\\Users\\ryand\\Downloads\\Athlete_Examples.xlsx",sheet_name="Example")
pwr = df['power'].to_numpy()
lct = df['lactate'].to_numpy()
hr = df['heartrate'].to_numpy()

p3 = np.poly1d(np.polyfit(x=pwr, y=lct, deg=3))

x_new = np.linspace(start=pwr.min() ,stop=pwr.max() ,num=200)
lac_fit = p3(x_new)

# Find LT1 & LT2
## LT1
LT_1_idx = (lac_fit > (lct.min() + 1)).argmax()
print(LT_1_idx)
LT_1 = lac_fit[LT_1_idx]
LT_1_p = x_new[LT_1_idx]

## LT2
LT_2_2mmol_idx = (lac_fit > (LT_1 + 2)).argmax()
LT_2 = lac_fit[LT_2_2mmol_idx]
LT_2_p = x_new[LT_2_2mmol_idx]

fig, ax = plt.subplots(1,1, dpi=200, figsize=(10,6))
ax.scatter(x=pwr, y=lct, color='blue', label='Lactate Values')
ax.plot(x_new, lac_fit, color='lightblue', label='Lactate Curve')
ax1 = ax.twinx()
ax1.scatter(x=pwr, y=hr, color='red', label='Heartrate Values')

## Reference Lines
ax.axhline(y=LT_1, ls='--', lw=1, color='black', label='LT1')
ax.axvline(x=LT_1_p, ls='--', lw=1, color='black')
ax.annotate(xy=(LT_1_p + 1,LT_1 + 1), text=f'LT1:\n{LT_1:0.2f}mmol/L\n{LT_1_p:0.0f}w')
ax.axhline(y=LT_2, ls=':', lw=1, color='black', label='LT2')
ax.axvline(x=LT_2_p, ls=':', lw=1, color='black')
ax.annotate(xy=(LT_2_p + 1,LT_2 + 1), text=f'LT2:\n{LT_2:0.2f}mmol/L\n{LT_2_p:0.0f}w')


ax.set_xlabel('Power')
ax.set_ylabel('Lactate Concentration (mmol/L)')
ax1.set_ylabel('Heartrate (bpm)')
ax.set_ylim(0,lct.max()*1.25)


fig.legend()

plt.savefig('plot.png') 