import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class lactate_solver(object):
    def __init__(self, lactate_vector, heartrate_vector ,power_vector):
        self.lactate_vector = lactate_vector
        self.heartrate_vector = heartrate_vector
        self.power_vector = power_vector
        self.solver_methods = {'2and4':self.method_2and4mmol
                               ,'1+2':self.method_1plus2
                               ,'Dmax Mod':self.method_dmaxmod}

    def find_LT_values(self, method_name):
        method_function = self.solver_methods[method_name]
        method_output = method_function()

        method_output_dict = {'LT1_mmol':method_output[0],
                            'LT1_power':method_output[1],
                            'LT1_hr':method_output[2],
                            'LT2_mmol':method_output[3],
                            'LT2_power':method_output[4],
                            'LT2_hr':method_output[5],
                            'LTfit':method_output[6]}

        return method_output_dict

    def method_1plus2(self):
        LTfit = np.poly1d(np.polyfit(x=self.power_vector, y=self.lactate_vector, deg=3))
        x_new = np.linspace(start=self.power_vector.min() ,stop=self.power_vector.max() ,num=200)
        lac_fit = LTfit(x_new)

        # Modeled fit to HR
        HRfit = np.poly1d(np.polyfit(x=self.power_vector, y=self.heartrate_vector, deg=3))
        hr_fit = HRfit(x_new)

        # Find LT1 & LT2
        ## LT1
        LT_1_idx = (lac_fit > (self.lactate_vector.min() + 1)).argmax()
        LT1_mmol = lac_fit[LT_1_idx]
        LT1_power = x_new[LT_1_idx]
        LT1_hr = hr_fit[LT_1_idx]

        ## LT2
        LT_2_idx = (lac_fit > (LT1_mmol + 2)).argmax()
        LT2_mmol = lac_fit[LT_2_idx]
        LT2_power = x_new[LT_2_idx]
        LT2_hr = hr_fit[LT_2_idx]
    
        return LT1_mmol, LT1_power, LT1_hr, LT2_mmol, LT2_power, LT2_hr, LTfit
    
    def method_2and4mmol(self):
        LT1_mmol = LT1_power = LT1_hr = LT2_mmol = LT2_power = LT2_hr = LTfit = 0
        
        return LT1_mmol, LT1_power, LT1_hr, LT2_mmol, LT2_power, LT2_hr, LTfit

    def method_dmaxmod(self, rise_in_lt_over_baseline = 0.4):

        LTfit = np.poly1d(np.polyfit(x=self.power_vector, y=self.lactate_vector, deg=3))
        x_new = np.linspace(start=self.power_vector.min() ,stop=self.power_vector.max() ,num=200)
        lac_fit = LTfit(x_new)

        HRfit = np.poly1d(np.polyfit(x=self.power_vector, y=self.heartrate_vector, deg=3))
        hr_fit = HRfit(x_new)

        max_x = max(self.power_vector)
        min_x = min(self.power_vector)

        roots = np.roots(LTfit - (LTfit(min_x) + rise_in_lt_over_baseline))
        roots = roots[np.logical_and(np.isreal(roots), roots > min_x, roots < max_x)]
        LT1_power = max(roots).real

        v_x = np.poly1d(max_x - LT1_power)
        v_y = np.poly1d(LTfit(max_x) - LTfit(LT1_power))
        u_x = np.poly1d([1, -LT1_power])
        u_y = LTfit - LTfit(LT1_power)
        cross_z = v_x * u_y - v_y * u_x

        LT2_power = np.roots(cross_z.deriv())
        LT2_power = LT2_power[np.logical_and(LT2_power > LT1_power, LT2_power < max_x)]
        LT2_power = LT2_power[0]

        LT1_mmol = LTfit(LT1_power)
        LT2_mmol = LTfit(LT2_power)
        LT1_hr =  HRfit(LT1_power)
        LT2_hr = HRfit(LT2_power)
    
        return LT1_mmol, LT1_power, LT1_hr, LT2_mmol, LT2_power, LT2_hr, LTfit
        
        
    #     return LT1_mmol, LT1_power, LT1_hr, LT2_mmol, LT2_power, LT2_hr, LTfit
    
    def plotter(self, LT1_mmol, LT1_power, LT1_hr, LT2_mmol, LT2_power, LT2_hr, LTfit, save=False):
        x_new = np.linspace(start=self.power_vector.min() ,stop=self.power_vector.max() ,num=200)
        lac_fit = LTfit(x_new)

        fig, ax = plt.subplots(1,1, dpi=200, figsize=(10,6))
        ax.scatter(x=self.power_vector, y=self.lactate_vector, color='blue', label='Lactate Values')
        ax.plot(x_new, lac_fit, color='lightblue', label='Lactate Curve')
        ax1 = ax.twinx()
        ax1.scatter(x=self.power_vector, y=self.heartrate_vector, color='red', label='Heartrate Values')

        ## Reference Lines
        ax.axhline(y=LT1_mmol, ls='--', lw=1, color='black', label='LT1')
        ax.axvline(x=LT1_power, ls='--', lw=1, color='black')
        ax.annotate(xy=(LT1_power + 1,LT1_mmol + 1), text=f'LT1:\n{LT1_mmol:0.2f}mmol/L\n{LT1_power:0.0f}w')
        ax.axhline(y=LT2_mmol, ls=':', lw=1, color='black', label='LT2')
        ax.axvline(x=LT2_power, ls=':', lw=1, color='black')
        ax.annotate(xy=(LT2_power + 1,LT2_mmol + 1), text=f'LT2:\n{LT2_mmol:0.2f}mmol/L\n{LT2_power:0.0f}w')


        ax.set_xlabel('Power')
        ax.set_ylabel('Lactate Concentration (mmol/L)')
        ax1.set_ylabel('Heartrate (bpm)')
        ax.set_ylim(0,self.lactate_vector.max()*1.25)

        fig.legend()
        if save:
            plt.savefig('plot.png') 
        return fig