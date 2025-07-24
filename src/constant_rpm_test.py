import matplotlib.pyplot as plt
from typing import List
import numpy as np
import scipy.stats as stats
import scipy.signal as signal

data_file = './resultados/teste_dino_ufu_2025-07-07-17:20:42.csv' # 358,67 rolo rpm constante
#data_file = './resultados/teste_dino_ufu_2025-07-07-17:22:07.csv' # 203,05 rolo rpm constante

num_dentes = 40
rad_dente = 2*3.1416/num_dentes # quantos radianos entre cada dente

razao_rpms = 5.0185 # 4 e36

# Ler arquivo, separar por vírgula e converter str em int
with open(data_file, 'r') as file:
    data = file.read()
data = data.split(',')
data = [ int(x) for x in data if x ] # diferença de tempo entre cada dente e o anterior em micro segundos
data = np.array(data)

# Data pre-processing
print(len(data))
data=data[340:370]
#data = signal.savgol_filter(data,window_length=1000,polyorder=3)

# Create secondary lists
dt_list = [ dt/1000000 for dt in data] # converte diferença de tempo entre cada dente e o anterior em segundos
w_list = [rad_dente/(dt) for dt in dt_list] # velocidade angular para cada intervalo entre dentes em rad/seg
rpm_list = [w*30/3.1416 for w in w_list]

data = rpm_list

# Função para calcular os parâmetros estatísticos
def calcular_parametros(dados):
    media = np.mean(dados)
    mediana = np.median(dados)
    desvio_padrao = np.std(dados)
    amplitude = np.ptp(dados)
    skewness = stats.skew(dados)
    kurtosis = stats.kurtosis(dados)
    return media, mediana, desvio_padrao, amplitude, skewness, kurtosis

# Cálculo dos parâmetros estatísticos antes do pré-tratamento
media, mediana, desvio_padrao, amplitude, skewness, kurtosis = calcular_parametros(data)

# Exibição dos resultados
print(f"Média: {media}")
print(f"Desvio Padrão: {desvio_padrao}")
print(f"Amplitude: {amplitude}")
print(f"Assimetria (Skewness): {skewness}")
print(f"Achatamento (Kurtosis): {kurtosis}")

# Plot graph
# Create the plot and the first axis
fig, ax1 = plt.subplots()

# Plot first line (left y-axis)
ax1.plot(x, data, 'r-', label='RPM')
ax1.set_ylabel('Rpm', color='r')
ax1.tick_params(axis='y', labelcolor='r')
ax1.grid(True)  # Add grid to left y-axis

# Create a second y-axis sharing the same x-axis
ax2 = ax1.twinx()

# Plot second line (right y-axis)
ax2.plot(x, [media]*len(data), 'b-', label='média')
ax2.tick_params(axis='y', labelcolor='b')

# Add legends
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

# Title and layout
plt.title('rpm do rolo e média')
ax1.set_xlabel('ponto')  # Add x-axis label


fig.tight_layout()
plt.show()