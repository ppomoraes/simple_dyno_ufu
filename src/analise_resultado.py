import matplotlib.pyplot as plt
from typing import List
import numpy as np
import scipy.stats as stats
import scipy.signal as signal

data_file = './resultados/teste_dino_ufu_2025-06-23-20:44:08_e36_original_1.csv' # - 204
data_file = './resultados/teste_dino_ufu_2025-06-23-20:44:49_e36_original_2.csv' # - 206
data_file = './resultados/teste_dino_ufu_2025-06-23-20:45:31_e36_original_3.csv' # - 215
#data_file = './resultados/teste_dino_ufu_2025-06-23-20:06:53e36 4 - com viscosa.csv' #- 204
#data_file = './resultados/teste_dino_ufu_2025-06-23-20:21:07 - sem viscosa.csv' # - 214

data_file = './resultados/teste_dino_ufu_2025-07-07-17:20:42.csv' # 358,67 rolo rpm constante
data_file = './resultados/teste_dino_ufu_2025-07-07-17:22:07.csv' # 203,05 rolo rpm constante

#m_inercia = 121.107 #kg*m²
m_inercia = 105 #kg*m²
num_dentes = 40
rad_dente = 2*3.1416/num_dentes # quantos radianos entre cada dente

razao_rpms = 5.0185 # 4 e36

temp = 20.09 # *C
pressure = 91.87 # kPa
humidity = 80.30 # %

def moving_average(values: List[int], window_size: int = 40) -> List[float]:
    if len(values) < window_size:
        raise ValueError(f"List must have at least {window_size} elements.")

    averages = []
    for i in range(len(values) - window_size + 1):
        window = values[i:i + window_size]
        avg = sum(window) / window_size
        averages.append(avg)

    return averages

def chauvenet(data):
    mean = np.mean(data)        #calcula a media
    std_dev = np.std(data)      #calcula o desvio
    N = len(data)               #calcula o tamanho da amostra
    criterion = 1.0 / (2 * N)   #calcula o criterio de chauvenet: 1/2N
    
    deviations = np.abs(data - mean) / std_dev  #desv absoluto em termos do nro de stddv
    #calcula a prob p cada desvio usando a sf (fc sobrevivencia) = (1 - CDF)
    #e multiplica por 2 para ter a prob de estar fora da região aceitavel em ambos lados da dist
    probs = stats.norm.sf(deviations) * 2       
    
    #aplica o filtro na amostra, selecionando os que não são outliers
    naoexclui = probs >= criterion
    return data[naoexclui]

# Ler arquivo, separar por vírgula e converter str em int
with open(data_file, 'r') as file:
    data = file.read()
data = data.split(',')
data = [ int(x) for x in data if x ] # diferença de tempo entre cada dente e o anterior em micro segundos
data = np.array(data)

# Data pre-processing
print(len(data))
data = chauvenet(data)
print(len(data))
#data=data[100:-200]
data=data[340:370]
#data = moving_average(data,20) # Fazer média móvel de 40 itens
#data = signal.savgol_filter(data,window_length=1000,polyorder=3)
x=[n for n in range(len(data))]
c = np.polyfit(x,data,15)
y = np.polyval(c,x)
#data = y

# Create secondary lists
dt_list = [ dt/1000000 for dt in data] # converte diferença de tempo entre cada dente e o anterior em segundos
w_list = [rad_dente/(dt) for dt in dt_list] # velocidade angular para cada intervalo entre dentes em rad/seg
rpm_list = [w*30*razao_rpms/3.1416 for w in w_list]

# Cálculos de potência
#            rpm,potencia,torque
potencia_list = [[],[],[]] # em Watts
for idx in range(1,len(dt_list)):
    dt_med = ((dt_list[idx]+dt_list[idx-1])/2) # dt médio entre esse ponto e o anterior
    w_med = ((w_list[idx]+w_list[idx-1])/2)
    potencia_list[0].append((rpm_list[idx]+rpm_list[idx-1])/2) #append rpm media
    Potencia_Vis = 0#0.0004 * (w_med** 3)
    potencia_inercial = (m_inercia / 2) * ((w_list[idx]**2) - (w_list[idx-1]**2)) / dt_med
    potencia_total = potencia_inercial+Potencia_Vis
    potencia_list[1].append(potencia_total)
    potencia_list[2].append(potencia_total/(w_med*razao_rpms))

#potencia_list = [signal.savgol_filter(potencia_list[0],window_length=1000,polyorder=3),
 #               signal.savgol_filter(potencia_list[1],window_length=1000,polyorder=3),
  #             signal.savgol_filter(potencia_list[2],window_length=1000,polyorder=3)]

potencia_list[1] = [pot/735.5 for pot in potencia_list[1]] # converter de Watt para Cavalo

potencia_list[0] = list(potencia_list[0])
potencia_list[1] = list(potencia_list[1])
potencia_list[2] = list(potencia_list[2])

# cálculo dos máximos:
max_rpm = max(potencia_list[0])
max_pot = max(potencia_list[1])
max_pot_rpm = potencia_list[0][potencia_list[1].index(max_pot)]
max_torque = max(potencia_list[2])
max_torque_rpm = potencia_list[0][potencia_list[2].index(max_torque)]

# print results
print('#'*50)
print('Máxima rpm atingida:',int(max_rpm),'\n')
print(f'Máxima potência gerada: {int(max_pot)} cavalos, a {int(max_pot_rpm)} rpm.\n')
print(f'Máximo torque gerado: {int(max_torque)} nm, a {int(max_torque_rpm)} rpm.\n')
print('#'*50)


# Line plot of dt
plt.plot(x,data, color='red', linewidth=2)

# Labels and title
plt.xlabel('ponto')
plt.ylabel('dt')
plt.title('')
plt.legend()
plt.grid(True)

# Display plot
plt.show()
'''
## plot power and torque curves
# Line plot
plt.plot(potencia_list[0],potencia_list[1], color='red', linewidth=2)

# y axis limit
plt.ylim(0, max(potencia_list[1])*1.15)

# Labels and title
plt.xlabel('rpm')
plt.ylabel('potencia')
plt.title('Potencia do polyfit')
plt.legend()
plt.grid(True)

# Display plot
plt.show()


# Plot final graph
# Create the plot and the first axis
fig, ax1 = plt.subplots()

# Plot first line (left y-axis)
ax1.plot(potencia_list[0], potencia_list[1], 'r-', label='Potência')
ax1.set_ylabel('Potência (cv)', color='r')
ax1.tick_params(axis='y', labelcolor='r')
ax1.grid(True)  # Add grid to left y-axis
ax1.set_ylim(0, max(potencia_list[1])*1.15)  # Custom y-limits for left axis

# Create a second y-axis sharing the same x-axis
ax2 = ax1.twinx()

# Plot second line (right y-axis)
ax2.plot(potencia_list[0], potencia_list[2], 'b-', label='Torque')
ax2.set_ylabel('Torque (nm)', color='b')
ax2.tick_params(axis='y', labelcolor='b')
ax2.set_ylim(0, max(potencia_list[2])*1.15)  # Custom y-limits for left axis

# Add legends
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

# Title and layout
plt.title('Potência e Torque, e36 Pompeu')
ax1.set_xlabel('rpm')  # Add x-axis label

# Annotate max values at bottom-left
textstr = f"Máxima potência gerada: {int(max_pot)} cv, a {int(max_pot_rpm)} rpm.\n Máximo torque gerado: {int(max_torque)} nm, a {int(max_torque_rpm)} rpm."
bbox_props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax1.text(0.02, 0.02, textstr, transform=ax1.transAxes, fontsize=10,
         verticalalignment='bottom', bbox=bbox_props)

fig.tight_layout()
plt.show()
'''