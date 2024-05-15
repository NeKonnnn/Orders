import numpy as np
from scipy.integrate import odeint
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from functions import *

# Входные данные
display_points = 20

# Эксперимент 1
time_series = np.linspace(0, 2.5, 4, endpoint=True)  
parameters = [-2, 8]  
simulate_and_fit(time_series, parameters, display_points, 1)

# Эксперимент 2
time_series = np.linspace(0, 8, 8, endpoint=True)  
simulate_and_fit(time_series, parameters, display_points, 2)

# Эксперимент 3
time_series = np.linspace(0, 12, 60, endpoint=True)  
simulate_and_fit(time_series, parameters, display_points, 3)

# Эксперимент 4
time_series = np.linspace(0, 3, 5, endpoint=True)  
parameters = [3, -2]  
simulate_and_fit(time_series, parameters, display_points, 4)

# Эксперимент 5
time_series = np.linspace(0, 2.5, 15, endpoint=True)  
simulate_and_fit(time_series, parameters, display_points, 5)

# Эксперимент 6
time_series = np.linspace(0, 1.5, 30, endpoint=True)  
simulate_and_fit(time_series, parameters, display_points, 6)

# Эксперимент 7
time_series = np.linspace(0, 3, 6, endpoint=True)  
parameters = [4.5, 150]  
simulate_and_fit(time_series, parameters, display_points, 7)

# Эксперимент 8
time_series = np.linspace(0, 2.5, 20, endpoint=True)  
simulate_and_fit(time_series, parameters, display_points, 8)

# Эксперимент 9
time_series = np.linspace(0, 3, 75, endpoint=True) 
simulate_and_fit(time_series, parameters, display_points, 9)

#Эксперимент 10 
time_series = np.linspace(0, 4, 40, endpoint=True)
parameters = [6, -100]
simulate_and_fit(time_series, parameters, display_points, 10)