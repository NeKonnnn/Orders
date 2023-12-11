% Основной код скрипта
Fs = 200e6; % Частота дискретизации
t_linear = 0:1/Fs:2; % Время для линейного ЛЧМ
t_complex = 0:1/Fs:10; % Время для комплексного ЛЧМ
T = 4e-6; % Длительность сигнала
t = 0:1/Fs:T-1/Fs; % Временной вектор
fc = 50e6; % Несущая частота
B = 25e6; % Девиация частоты
SNRs = [10, -1, 10, -5]; % Различные значения ОСШ

% Параметры для функции spectrogram
window = rectwin(length(t)); % Оконная функция
noverlap = 0; % Количество перекрывающихся отсчетов
nfft = length(t); % Количество точек в FFT

% Расчет фрактальной размерности и статистической обработки
fractalDims = zeros(1, length(SNRs));
for i = 1:length(SNRs)
    signal = generateSignal('FM', t, SNRs(i), Fs, fc, B);
    [S, F, T_psd, P] = calculateSpectrogram(signal, Fs);
    
    % Преобразование спектрограммы в двоичное изображение для box-counting
    S_binary = imbinarize(mat2gray(abs(S))); % Бинаризация спектрограммы
    fractalDims(i) = boxCountingDimension(S_binary);
end

% Генерация и визуализация спектрограмм
for i = 1:length(SNRs)
    % Линейный ЛЧМ-сигнал
    y_linear = chirp(t_linear, 0, 1, 250);
    y_linear_noisy = awgn(y_linear, SNRs(i), 'measured');
    
    % Комплексный ЛЧМ-сигнал
    fo = -200;
    f1 = 300;
    y_complex = chirp(t_complex, fo, t_complex(end), f1, 'linear', 0, 'complex');
    y_complex_noisy = awgn(y_complex, SNRs(i), 'measured');

    % Визуализация спектрограмм линейного ЛЧМ
    figure;
    pspectrum(y_linear_noisy, Fs, 'spectrogram', 'TimeResolution', 0.1, 'OverlapPercent', 99, 'Leakage', 0.85);
    title(['Спектрограмма линейного ЛЧМ, ОСШ = ', num2str(SNRs(i)), ' дБ']);

    % Визуализация спектрограмм комплексного ЛЧМ
    figure;
    pspectrum(y_complex_noisy, Fs, 'spectrogram', 'TimeResolution', 0.2, 'OverlapPercent', 99, 'Leakage', 0.85);
    title(['Спектрограмма комплексного ЛЧМ, ОСШ = ', num2str(SNRs(i)), ' дБ']);
end

% Расчет фрактальной размерности и статистической обработки
fractalDims = zeros(1, length(SNRs));
probDensities = zeros(length(SNRs), 100);
D_values = zeros(length(SNRs), 100);

for i = 1:length(SNRs)
    signal = generateSignal('FM', t, SNRs(i), Fs, fc, B);
    [S, F, T, P] = calculateSpectrogram(signal, Fs);
    fractalDims(i) = fractalDimension(S, F, T);
    [D_values(i, :), probDensities(i, :)] = statisticalAnalysis(signal);
end

% Визуализация результатов
% Визуализация фрактальной размерности от ОСШ
figure;
plot(SNRs, fractalDims, 'o-');
xlabel('ОСШ, дБ');
ylabel('Фрактальная размерность, D');
title('Зависимость фрактальной размерности от ОСШ');

% Визуализация статистической обработки
figure;
for i = 1:length(SNRs)
    plot(D_values(i, :), probDensities(i, :));
    hold on;
end
xlabel('Фрактальная размерность, D');
ylabel('Плотность вероятности');
title('Распределение фрактальной размерности для ФМ сигналов');
legend(strcat('ОСШ = ', string(SNRs), ' дБ'), 'Location', 'best');
hold off;

% Параметры для анализа Неймана-Пирсона
Pfa = 0.01; % Вероятность ложной тревоги
threshold = qfuncinv(Pfa); % Пороговое значение (исходя из Q-функции)

% Оценка вероятности обнаружения
Pd = zeros(1, length(SNRs)); % Вероятность обнаружения для разных ОСШ

for i = 1:length(SNRs)
    signal = generateSignal('FM', t, SNRs(i), Fs, fc, B);
    energy = sum(abs(signal).^2) / length(signal); % Энергия сигнала
    detectionMetric = energy / threshold; % Метрика обнаружения

    if detectionMetric > threshold
        Pd(i) = 1; % Сигнал обнаружен
    else
        Pd(i) = 0; % Сигнал не обнаружен
    end
end

% Визуализация результатов критерия Неймана-Пирсона
figure;
plot(SNRs, Pd, 'o-');
xlabel('ОСШ, дБ');
ylabel('Вероятность обнаружения, Pd');
title('Вероятность обнаружения сигнала по критерию Неймана-Пирсона');

% Теперь все определения функций

% Функция для генерации различных типов сигналов: ФМ, ЛЧМ, Костас
function signal = generateSignal(type, t, SNR, Fs, fc, B)
    switch type
        case 'FM'
            signal = fmmod(randn(size(t)), fc, Fs, B);
        case 'Chirp'
            f0 = 0;
            f1 = Fs/2;
            signal = chirp(t, f0, t(end), f1, 'linear');
        case 'Costas'
            signal = generateCostas(t, SNR, Fs);
    end
    signal = awgn(signal, SNR, 'measured');
end

% Функция для генерации сигнала Костаса
function signal = generateCostas(t, SNR, Fs)
    freqs = [100, 200, 300, 400];
    N = length(freqs);
    signalLength = length(t);
    signal = zeros(1, signalLength);

    for i = 1:N
        startIndex = floor((i - 1) * signalLength / N) + 1;
        endIndex = floor(i * signalLength / N);
        signal(startIndex:endIndex) = cos(2 * pi * freqs(i) * t(startIndex:endIndex));
    end

    signal = awgn(signal, SNR, 'measured');
end

% Функция для расчета спектрограммы сигнала
function [S, F, T, P] = calculateSpectrogram(signal, Fs)
    window = rectwin(length(signal));
    noverlap = 0;
    nfft = length(signal);
    [S, F, T, P] = spectrogram(signal, window, noverlap, nfft, Fs, 'yaxis');
end

% Функция для расчета фрактальной размерности сигнала
function D = fractalDimension(S, F, T)
    N = length(S);
    e = linspace(min(min(abs(S))), max(max(abs(S))), 100);
    Ns = arrayfun(@(x) sum(abs(S(:)) > x), e);
    D = polyfit(log(e), log(Ns), 1);
    D = D(1); % Фрактальная размерность
end

% Функция для статистической обработки сигнала
function [D, probDensity] = statisticalAnalysis(signal)
    pd = makedist('Normal', 'mu', mean(signal), 'sigma', std(signal));
    D = linspace(min(signal), max(signal), 100);
    probDensity = pdf(pd, D);
end

% Функция для визуализации критерия обнаружения
function plotDetectionCriterion(SNRs, Pfa, signal, Fs)
    threshold = qfuncinv(Pfa);
    figure;
    hold on;
    for i = 1:length(SNRs)
        signal = generateSignal('FM', t, SNRs(i), Fs, fc, B);
        energy = sum(abs(signal).^2) / length(signal);
        detectionMetric = energy / threshold;
        if detectionMetric > threshold
            plot(SNRs(i), detectionMetric, 'go');
        else
            plot(SNRs(i), detectionMetric, 'ro');
        end
    end
    plot(xlim, [threshold threshold], 'b--');
    hold off;
    xlabel('ОСШ, дБ');
    ylabel('Метрика обнаружения');
    title('Критерий обнаружения Неймана-Пирсона');
    legend('Обнаружено', 'Не обнаружено', 'Порог');
end

function D_bc = boxCountingDimension(S_binary)
    Ns = [];
    sizes = 2.^(0:-1:-10); % Размеры коробок для исследования

    for boxSize = sizes
        boxSizeRounded = max(1, round(boxSize)); % Округляем до ближайшего целого и гарантируем, что не меньше 1
        fun = @(block_struct) any(block_struct.data(:));
        count = sum(blockproc(S_binary, [boxSizeRounded boxSizeRounded], fun));
        Ns = [Ns, count];
    end

    logSizes = log(1./sizes);
    logNs = log(Ns);
    D_bc = polyfit(logSizes, logNs, 1);
    D_bc = D_bc(1); % Фрактальная размерность
end