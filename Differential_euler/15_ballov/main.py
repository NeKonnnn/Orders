from scipy.integrate import odeint
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.layers import Dense, Input, Concatenate
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from functions import *

# Параметры экспериментов
experiment_params = [
(-2, 1, 3, -4), # Эксперимент 1
(-1, 2, -3, 4), # Эксперимент 2
(0.5, -1.5, 2, -2.5), # Эксперимент 3
(1, -1, 1.5, -1.5), # Эксперимент 4
(-2.5, 2.5, -0.5, 0.5), # Эксперимент 5
(2, -2, 3, -3), # Эксперимент 6
(-1.5, 1, 2.5, -2), # Эксперимент 7
(1.5, -1, -2, 2), # Эксперимент 8
(-3, 3, -1, 1), # Эксперимент 9
(2.5, -2.5, 0.5, -0.5) # Эксперимент 10
]

time_points = np.linspace(0, 5, 100)

# Переменные для хранения результатов
solutions = []
predicted_solutions = []
mse_values = []
max_derivatives = []

for i, params in enumerate(experiment_params, start=1):
    solution, predicted_solution, mse = conduct_experiment(*params, experiment_id=i, time_points=time_points)
    
    # Добавление результатов в массивы
    mse_values.append(mse)

    # Вычисление максимального значения производной для текущего решения
    dy1_dt = np.gradient(solution[:, 0], time_points)
    dy2_dt = np.gradient(solution[:, 1], time_points)
    max_derivative = max(np.max(np.abs(dy1_dt)), np.max(np.abs(dy2_dt)))
    max_derivatives.append(max_derivative)

print("Длина max_derivatives:", len(max_derivatives))
print("Длина mse_values:", len(mse_values))

# Визуализация зависимости погрешности от максимального значения производной
plt.figure(figsize=(10, 6))
plt.scatter(max_derivatives, mse_values, color='blue')
plt.xlabel('Максимальное значение производной')
plt.ylabel('MSE')
plt.title('Зависимость MSE от максимума производной на отрезке')
plt.grid(True)
plt.show()