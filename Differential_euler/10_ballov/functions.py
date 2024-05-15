import numpy as np
from scipy.integrate import odeint
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def calculate_performance_metric(real_params, estimated_params):
    """
    Вычисляет метрику производительности для оценки качества подгонки.

    :param real_params: Истинные параметры модели.
    :param estimated_params: Оцененные параметры модели.
    :return: Значение метрики R квадрат.
    """
    average_value = np.mean(0.5 * (real_params + estimated_params))
    numerator = sum((real_params - estimated_params) ** 2)
    denominator = sum((real_params - average_value) ** 2)
    return 1 - numerator / denominator


def model_equation(y, t, coefficient1, coefficient2):
    """
    Определяет линейное дифференциальное уравнение.

    :param y: Значение функции в данный момент времени.
    :param t: Текущее время.
    :param coefficient1: Первый коэффициент уравнения.
    :param coefficient2: Второй коэффициент уравнения.
    :return: Производная функции по времени.
    """
    dydt = coefficient1 * y + coefficient2
    return dydt


def optimize_parameters(time_points, coefficient1, coefficient2):
    """
    Подгоняет параметры дифференциального уравнения к данным.

    :param time_points: Массив временных точек для подгонки.
    :param coefficient1: Начальное предположение для первого коэффициента.
    :param coefficient2: Начальное предположение для второго коэффициента.
    :return: Оптимизированные значения коэффициентов.
    """
    fitted_solution = odeint(model_equation, y0=1.0, t=time_points, args=(coefficient1, coefficient2))
    return fitted_solution.flatten()


def simulate_and_fit(time_series, actual_parameters, number_of_display_points, experiment_id):
    """
    Симулирует данные, выполняет оптимизацию параметров и отображает результаты.

    :param time_series: Временные точки для симуляции данных.
    :param actual_parameters: Истинные параметры модели.
    :param number_of_display_points: Количество точек для отображения на графике.
    :param experiment_id: Идентификатор эксперимента для вывода результатов.
    """
    # Симуляция данных с учетом шума
    np.random.seed(42)
    simulated_solution= odeint(model_equation, y0=1.0, t=time_series, args=tuple(actual_parameters)).flatten()
    noise = np.random.normal(0, np.abs(simulated_solution * 1.02 - simulated_solution), len(time_series))
    noisy_data = simulated_solution + noise
    # Начальное предположение для оптимизации
    initial_estimate = [1.0, 1.0]

    # Оптимизация параметров с шумом и без
    optimized_params_noisy, _ = curve_fit(optimize_parameters, time_series, noisy_data, p0=initial_estimate)
    optimized_params_clean, _ = curve_fit(optimize_parameters, time_series, simulated_solution, p0=initial_estimate)

    # Вывод результатов
    print(f"Эксперимент {experiment_id}:")
    print("Истинные параметры:", actual_parameters)
    print("Оптимизированные параметры (с шумом):", optimized_params_noisy)
    print("Оптимизированные параметры (без шума):", optimized_params_clean)
    performance_metric = calculate_performance_metric(actual_parameters, optimized_params_noisy)
    print("Метрика R^2:", performance_metric)

    # Визуализация результатов
    extended_time_series = np.linspace(time_series[0], time_series[-1], number_of_display_points)
    simulated_clean = odeint(model_equation, y0=1.0, t=extended_time_series, args=tuple(optimized_params_clean)).flatten()
    simulated_true = odeint(model_equation, y0=1.0, t=extended_time_series, args=tuple(actual_parameters)).flatten()

    plt.figure(figsize=(8, 6))
    plt.scatter(time_series, noisy_data, label='Симулированные данные с шумом')
    plt.scatter(time_series, simulated_solution, label='Входные данные', color='orange')
    plt.plot(extended_time_series, simulated_clean, label='Оптимизированные данные', color='red')
    plt.plot(extended_time_series, simulated_true, label='Истинные данные', color='green')
    plt.xlabel('Время')
    plt.ylabel('Значения')
    plt.title(f"Результаты эксперимента {experiment_id}")
    plt.legend()
    plt.show()