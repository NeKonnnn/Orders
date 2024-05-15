from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QSizePolicy, QHBoxLayout, QLabel
from PyQt5.QtWidgets import QFileDialog
from main_widget_ui import Ui_mainWidget
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.gridspec as gridspec
from main_widget_ui import Ui_mainWidget, ClickableLabel
import os
import time
from obspy import read
from datetime import datetime
from datetime import timedelta
from copy import deepcopy
from obspy.signal.trigger import classic_sta_lta, trigger_onset
import numpy as np
from scipy.signal import correlate
from scipy.signal import find_peaks
from datetime import timedelta

component_colors = {
    'Z': 'blue',
    'N': 'green',
    'E': 'red'
}

def identify_peaks(correlation, min_peak_height, distance):
    peaks, properties = find_peaks(correlation, height=min_peak_height, distance=distance)
    return peaks

def is_float(element):
    if element is None:
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False
    
def cross_correlate_traces(trace1, trace2):
    correlation = correlate(trace1 - np.mean(trace1), trace2 - np.mean(trace2), mode='full')
    lags = np.arange(-len(trace2) + 1, len(trace1))
    lag = lags[np.argmax(correlation)]
    return lag, correlation


def plot_empty():
    fig, ax = plt.subplots(3, 1)  # Уже создаёт 3 подграфика
    fig.tight_layout()
    return fig, ax

def format_seconds(seconds):
        # timedelta поможет преобразовать секунды в часы, минуты и секунды
        return str(timedelta(seconds=seconds))


class MyMplCanvas(FigureCanvas):
    def __init__(self, fig, parent=None):
        self.fig = fig
        super(MyMplCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

class MainWidget(QWidget, Ui_mainWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.fig, self.ax = plot_empty()
        self.companovka = QHBoxLayout(self.mpl_widget)
        self.canvas = MyMplCanvas(self.fig, self)
        self.companovka.addWidget(self.canvas)
        self.canvas.hide()
        self.station_combo_box.hide()
        self.logo_label = ClickableLabel(self)
        self.logo_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.logo_label.setPixmap(QPixmap("drag_and_drop.png"))
        self.companovka.addWidget(self.logo_label)
        self.setAcceptDrops(True)
        self.station_combo_box.currentTextChanged.connect(self.plot_selected)
        self.filename = None
        self.st = None
        self.filtered_st = None
        self.EnterPushButton.clicked.connect(self.apply_settings)
        self.hideShowPushButton.clicked.connect(self.toggle_settings)
        self.logo_label.clicked.connect(self.open_file_dialog)
        self.toggle_settings()
        
        self.analyzeButton.clicked.connect(self.analyze_and_cross_correlate_wave_arrivals)
        self.crossCorrelateButton.clicked.connect(self.perform_cross_correlation)
    
    def analyze_and_cross_correlate_wave_arrivals(self):
        self.analyze_wave_arrivals()
        self.perform_cross_correlation()

    def find_p_s_wave_arrivals(self, station):
        try:
            traces = self.filtered_st.select(station=station)
            p_wave_arrival = None
            s_wave_arrival = None

            start_time = time.time()  # Начало измерения времени

            for trace in traces:
                trace_start_time = trace.stats.starttime
                sampling_rate = trace.stats.sampling_rate
                cft = classic_sta_lta(trace.data, int(1 * sampling_rate), int(4 * sampling_rate))
                threshold_crossings = np.where(cft > 1.0)[0]

                if len(threshold_crossings) > 0:
                    if p_wave_arrival is None or threshold_crossings[0] < (p_wave_arrival - trace_start_time) * sampling_rate:
                        p_wave_arrival = trace_start_time + (threshold_crossings[0] / sampling_rate)
                    for crossing in threshold_crossings[1:]:
                        potential_s_wave = trace_start_time + (crossing / sampling_rate)
                        if potential_s_wave > p_wave_arrival:
                            s_wave_arrival = potential_s_wave
                            break

            detection_duration = time.time() - start_time  # Конец измерения времени
            detection_duration_str = str(timedelta(seconds=detection_duration))

            # Преобразование в строки для вывода
            if p_wave_arrival is not None:
                p_wave_arrival_str = p_wave_arrival.strftime('%Y-%m-%d %H:%M:%S.%f')
            else:
                p_wave_arrival_str = None

            if s_wave_arrival is not None:
                s_wave_arrival_str = s_wave_arrival.strftime('%Y-%m-%d %H:%M:%S.%f')
            else:
                s_wave_arrival_str = None

            if p_wave_arrival and s_wave_arrival:
                print(f"Станция {station}: P-волна прибыла в {p_wave_arrival_str}, S-волна прибыла в {s_wave_arrival_str}, обнаружены за {detection_duration_str}")
            elif p_wave_arrival:
                print(f"Станция {station}: Только P-волна прибыла в {p_wave_arrival_str}, обнаружены за {detection_duration_str}")
            else:
                print(f"Станция {station}: Волн не обнаружено, анализ занял {detection_duration_str}")

            return p_wave_arrival_str, s_wave_arrival_str, detection_duration_str

        except Exception as e:
            print(f"Ошибка при определении прихода волн: {e}")
            return None, None, None

    def report_wave_arrivals(self):
        stations = set([tr.stats.station for tr in self.filtered_st])
        for station in stations:
            p_wave, s_wave, detection_duration = self.find_p_s_wave_arrivals(station)
            if p_wave and s_wave:
                print(f"Станция {station}: P-волна прибыла в {p_wave}, S-волна прибыла в {s_wave}, обнаружены за {detection_duration}")
            elif p_wave:
                print(f"Станция {station}: Только P-волна прибыла в {p_wave}, обнаружены за {detection_duration}")
            else:
                print(f"Станция {station}: Волн не обнаружено, анализ занял {detection_duration}")

    def analyze_sensor_components(self, sensor):
        components = ['HHZ', 'HHN', 'HHE']
        # Сформируем все возможные пары компонентов
        component_pairs = [(components[i], components[j]) for i in range(len(components)) for j in range(i + 1, len(components))]
        correlations = {}
        
        # Фильтруем компоненты, которые доступны на станции
        available_components = [comp for comp in components if len(self.filtered_st.select(station=sensor, component=comp)) > 0]
        available_pairs = [pair for pair in component_pairs if pair[0] in available_components and pair[1] in available_components]
        
        for comp1, comp2 in available_pairs:
            traces1 = self.filtered_st.select(station=sensor, component=comp1)
            traces2 = self.filtered_st.select(station=sensor, component=comp2)
            
            if len(traces1) == 0 or len(traces2) == 0:
                continue  # Пропускаем пару, если данные отсутствуют

            trace1 = traces1[0]
            trace2 = traces2[0]
            lag, _ = cross_correlate_traces(trace1.data, trace2.data)
            correlations[f"{comp1}-{comp2}"] = lag

        # Анализируем корреляции для определения времени прихода волны
        lags = list(correlations.values())
        if len(lags) < len(available_pairs):
            print(f"Недостаточно данных для полного анализа на станции {sensor}.")
            return False

        return len(set(lags)) <= 2  # True если два или три сдвига совпадают
    
    def analyze_wave_arrivals(self):
        if self.filtered_st is None or len(self.filtered_st) < 2:
            print("Недостаточно данных для анализа.")
            return

        stations = set([tr.stats.station for tr in self.filtered_st])
        arrival_times = {}

        for station in stations:
            result = self.analyze_sensor_components(station)
            arrival_times[station] = "Время прихода волны подтверждено" if result else "Время прихода волны не подтверждено"

        for station, result in arrival_times.items():
            print(f"{station}: {result}")

        self.report_wave_arrivals()  # Убедитесь, что этот вызов здесь присутствует

    def perform_cross_correlation(self):
        if self.filtered_st is None or len(self.filtered_st) < 3:
            print("Недостаточно данных для анализа.")
            return

        components = ['Z', 'N', 'E']
        correlations = {}
        component_colors = {
            'ZN': 'blue',
            'ZE': 'green',
            'NE': 'red'
        }
        max_correlation_values = []

        for i in range(len(components)):
            for j in range(i + 1, len(components)):
                trace1 = self.filtered_st.select(component=components[i])[0]
                trace2 = self.filtered_st.select(component=components[j])[0]
                lag, correlation = cross_correlate_traces(trace1.data, trace2.data)
                key = components[i] + components[j]
                max_correlation = np.max(correlation)
                correlations[key] = (lag, correlation, max_correlation)
                max_correlation_values.append(max_correlation)

        # Устанавливаем динамический порог как 50% от максимальной найденной корреляции
        dynamic_threshold = 0. * max(max_correlation_values)

        print("Корреляции между компонентами:")
        for key, (lag, correlation, max_correlation) in correlations.items():
            print(f"{key}: Lag = {lag}, Max correlation = {max_correlation}")
            # Находим пики, используя динамический порог и минимальное расстояние между пиками
            peaks = identify_peaks(correlation, min_peak_height=dynamic_threshold, distance=1000)  # Примерное расстояние
            # print(f"Peaks for {key}: {peaks}")

        self.ax[0].clear()
        for i, (key, (lag, correlation, _)) in enumerate(correlations.items()):
            if i < len(self.ax):
                color = component_colors.get(key, 'black')
                self.ax[i].plot(np.arange(-len(trace2.data) + 1, len(trace1.data)), correlation, color=color)
                self.ax[i].axvline(len(trace1.data) - 1 + lag, color='orange', linestyle='--')
                self.ax[i].set_title(f"Кросс-корреляция компонент {key}")

        self.canvas.draw()

        # Обновление графика
        self.ax[0].clear()
        for i, (key, value) in enumerate(correlations.items()):
            if i < len(self.ax):
                color = component_colors.get(key, 'black')  # Получаем цвет из словаря
                self.ax[i].plot(correlation, color=color)
                self.ax[i].axvline(len(trace1.data) - 1 + lag, color='orange', linestyle='--')
                self.ax[i].set_title(f"Кросс-корреляция компонент {key}")
                # self.ax[i].legend([key])

        self.canvas.draw()

    def dropEvent(self, event):
        self.load_new_file(event.mimeData().text())
        event.accept()

    def high_show_settings(self):
        if self.hideShowPushButton.text() == '>':
            self.widget.hide()
            self.hideShowPushButton.setText('<')
        else:
            self.widget.show()
            self.hideShowPushButton.setText('>')

    def toggle_settings(self):
        if self.hideShowPushButton.text() == '>':
            self.widget.hide()
            self.hideShowPushButton.setText('<')
        else:
            self.widget.show()
            self.hideShowPushButton.setText('>')

    def setup_new_file_loading(self):
        # Добавление кнопки загрузки нового файла, если она ещё не добавлена
        self.newFileButton = QtWidgets.QPushButton("Загрузить новый файл", self)
        self.newFileButton.clicked.connect(self.open_file_dialog)
        self.verticalLayout.addWidget(self.newFileButton)

    def open_file_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "MiniSEED Files (*.mseed);;All Files (*)")
        if filename:
            self.clear_previous_data()  # Метод для очистки данных
            self.load_new_file(filename)

    def clear_previous_data(self):
        # Очистка данных и графиков
        self.filtered_st = None
        self.station_combo_box.clear()
        for ax in self.ax:
            ax.clear()
        self.canvas.draw()

    def load_new_file(self, filename):
        if os.path.splitext(filename)[1] == '.mseed':
            try:
                # Очистка предыдущих данных и графиков
                self.station_combo_box.clear()
                self.fig.clear()  # Очистка фигуры matplotlib
                self.fig, self.ax = plot_empty()  # Создание новых пустых графиков
                self.canvas = MyMplCanvas(self.fig, self)  # Пересоздание холста с новыми графиками
                self.companovka.addWidget(self.canvas)  # Добавление нового холста в компоновку

                # Загрузка нового файла
                self.filename = filename.replace('file:///', '')
                self.st = read(self.filename)
                self.filtered_st = deepcopy(self.st)
                stations = set([tr.stats.station for tr in self.st])

                # Обновление интерфейса
                self.station_combo_box.addItems(sorted(stations))
                self.station_combo_box.show()
                self.canvas.show()
                self.logo_label.hide()  # Скрытие лейбла с логотипом

                print("Файл успешно загружен. Выберите станцию для анализа.")
            except Exception as e:
                print(f"Ошибка при загрузке файла: {e}")
                self.logo_label.show()  # Показать логотип, если загрузка файла не удалась
        else:
            print("Выбран файл неподдерживаемого формата.")

    def plot_selected(self):
        if not self.station_combo_box.currentText():
            return
        self.logo_label.hide()
        self.canvas.show()
        records = [rec for rec in self.filtered_st if rec.stats["station"] == self.station_combo_box.currentText()]
        for i, rec in enumerate(records):
            self.ax[i].clear()
            color = component_colors.get(rec.stats['channel'][-1], 'black')  # Используем последний символ канала для определения компонента
            self.ax[i].plot(rec.data, label=rec.stats['channel'], lw=1, color=color)
            self.ax[i].set_xlim(0, len(rec.data))
            self.fig.suptitle(self.filename.split('/')[-1])
        self.canvas.draw()

    def apply_settings(self):
        if self.filtered_st is None:
            return
        self.filtered_st = deepcopy(self.st)
        try:
            if self.detrendCheckBox.isChecked():
                self.filtered_st.detrend(type='demean')
            if self.highPassCheckBox.isChecked() and is_float(self.highPassLineEdit.text()):
                self.filtered_st.filter('highpass', freq=float(self.highPassLineEdit.text()))
            if self.bandPassCheckBox.isChecked() and is_float(self.bandPassStartLineEdit.text()) and is_float(self.bandPassEndLineEdit.text()):
                self.filtered_st.filter('bandpass', freqmin=float(self.bandPassStartLineEdit.text()), freqmax=float(self.bandPassEndLineEdit.text()))
        except Exception as e:
            print(f"Ошибка при применении фильтров: {e}")
        self.plot_selected()

    def apply_filters(self):
        self.filtered_st = deepcopy(self.st)
        try:
            if self.detrendCheckBox.checkState():
                self.filtered_st.detrend()
            if self.highPassCheckBox.checkState():
                if is_float(self.highPassLineEdit.text()):
                    self.filtered_st.filter('highpass', freq=float(self.highPassLineEdit.text()))
                else:
                    print('В поле фильтра высоких частот не число!')
            if self.bandPassCheckBox.checkState():
                if is_float(self.bandPassStartLineEdit.text()) and is_float(self.bandPassEndLineEdit.text()):
                    self.filtered_st.filter('bandpass', freqmin=float(self.bandPassStartLineEdit.text()),
                                            freqmax=float(self.bandPassEndLineEdit.text()))
                else:
                    print('В полях полосового фильтра не число!')
        except Exception as e:
            print(e)

    def find_events(self):
        try:
            if self.ltaStaCheckBox.checkState():
                if is_float(self.staLineEdit.text()) and is_float(self.ltaLineEdit.text()):
                    records = []
                    for rec in self.filtered_st:
                        if rec.stats["station"] == self.station_combo_box.currentText():
                            records.append(rec)
                    for i, rec in enumerate(records):
                        record = rec
                        trace = record.data
                        cft = classic_sta_lta(trace, int(float(self.staLineEdit.text()) * record.stats.sampling_rate),
                                              int(float(self.ltaLineEdit.text()) * record.stats.sampling_rate))
                        self.ax[i].clear()
                        self.ax[i].plot(cft)
                        peak = np.argmax(cft)
                        self.ax[i].axvline(peak, color="red")
                    self.canvas.draw()
        except Exception as e:
            print(e)