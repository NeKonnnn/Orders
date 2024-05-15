from scipy.integrate import odeint
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.layers import Dense, Input, Concatenate
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

# Определение системы дифференциальных уравнений
def system(y, t, a, b, c, d):
    y1, y2 = y
    dy1_dt = a * y1 + b * y2
    dy2_dt = c * y1 + d * y2
    return [dy1_dt, dy2_dt]

# Функция для расчета MSE
def calculate_mse(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)

# Определение модели NeuralODE для системы уравнений
def build_neural_ode_model_system():
    input_y = Input(shape=(2,))
    input_t = Input(shape=(1,))
    combined_input = Concatenate()([input_y, input_t])
    x = Dense(units=64, activation='relu')(combined_input)
    x = Dense(units=64, activation='relu')(x)
    x = Dense(units=64, activation='relu')(x)
    output_dy = Dense(units=2)(x)  # Предсказание производных dy1_dt и dy2_dt
    model = Model(inputs=[input_y, input_t], outputs=output_dy)
    return model

neural_ode_model_system = build_neural_ode_model_system()
neural_ode_model_system.compile(optimizer='adam', loss='mse')

# Функция для проведения одного эксперимента
def conduct_experiment(a, b, c, d, experiment_id, time_points):
    # Начальные условия для всех экспериментов
    y0 = [1.0, 2.0]

    # Решение системы уравнений и добавление шума к данным
    solution = odeint(system, y0, time_points, args=(a, b, c, d))
    noise = np.random.normal(0, 0.5, solution.shape)
    noisy_data = solution + noise

    # Подготовка данных для обучения
    X_train = [noisy_data, time_points.reshape(-1, 1)]
    y_train = solution

    # Обучение модели
    neural_ode_model_system.fit(X_train, y_train, epochs=200, verbose=1)

    # Предсказание производных
    predicted_derivatives = neural_ode_model_system.predict(X_train)

    # Вывод результатов
    print(f"Эксперимент {experiment_id}:")
    print("Истинные параметры:", [a, b, c, d])
    
    # Визуализация
    plt.figure(figsize=(10, 8))

    # Подграфик для y1
    plt.subplot(2, 1, 1)
    plt.scatter(time_points, noisy_data[:, 0], label='Симулированные данные y1 с шумом', color='blue')
    plt.scatter(time_points, solution[:, 0], label='Входные данные y1', color='orange')
    plt.plot(time_points, solution[:, 0], label='Истинные данные y1', color='green')
    plt.plot(time_points, predicted_derivatives[:, 0], label='Предсказанные данные y1', color='red')
    plt.xlabel('Время')
    plt.ylabel('y1')
    plt.title(f"Результаты эксперимента {experiment_id} для y1")
    plt.legend()

    # Подграфик для y2
    plt.subplot(2, 1, 2)
    plt.scatter(time_points, noisy_data[:, 1], label='Симулированные данные y2 с шумом', color='blue')
    plt.scatter(time_points, solution[:, 1], label='Входные данные y2', color='orange')
    plt.plot(time_points, solution[:, 1], label='Истинные данные y2', color='green')
    plt.plot(time_points, predicted_derivatives[:, 1], label='Предсказанные данные y2', color='red')
    plt.xlabel('Время')
    plt.ylabel('y2')
    plt.title(f"Результаты эксперимента {experiment_id} для y2")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Расчёт MSE для предсказанных производных
    mse = calculate_mse(solution, predicted_derivatives)
    print("MSE:", mse)

    return solution, predicted_derivatives, mse
