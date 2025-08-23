import matplotlib.pyplot as plt
from typing import List
import numpy as np
import scipy.stats as stats
import scipy.signal as signal


data_file1 = './resultados/teste_dino_ufu_2025-06-23-20:44:08_e36_original_1.csv' # - 204
data_file2 = './resultados/teste_dino_ufu_2025-06-23-20:44:49_e36_original_2.csv' # - 206
data_file3 = './resultados/teste_dino_ufu_2025-06-23-20:21:07 - sem viscosa.csv' # - 215 testes de verdade
data_file4 = './resultados/teste_dino_ufu_2025-08-23-11:58:57.csv' # - 204
data_file5 = './resultados/teste_dino_ufu_2025-08-23-12:09:25.csv' # - 206
data_file6 = './resultados/teste_dino_ufu_2025-08-23-12:00:43.csv' # - 215 testes de verdade

#data_file3 = './resultados/teste_dino_ufu_2025-06-23-20:44:49_e36_original_2.csv' # - 215 testes de verdade

#data_file1 = './resultados/teste_dino_ufu_2025-08-23-12:15:44.csv' # - 204 vvt off
#data_file2 = './resultados/teste_dino_ufu_2025-08-23-12:16:32.csv' # - 206
#data_file3 = './resultados/teste_dino_ufu_2025-08-23-12:17:56.csv' # - 215
#data_file4 = './resultados/teste_dino_ufu_2025-08-23-12:42:35.csv' # - 204 vvt on
#data_file5 = './resultados/teste_dino_ufu_2025-08-23-12:43:42.csv' # - 206
#data_file6= './resultados/teste_dino_ufu_2025-08-23-12:44:27.csv' # - 215


#data_file = './resultados/teste_dino_ufu_2025-06-23-20:06:53e36 4 - com viscosa.csv' #- 204
#data_file = './resultados/teste_dino_ufu_2025-06-23-20:21:07 - sem viscosa.csv' # - 214

#data_file = './resultados/teste_dino_ufu_2025-07-07-17:20:42.csv' # 358,67 rolo rpm constante
#data_file = './resultados/teste_dino_ufu_2025-07-07-17:22:07.csv' # 203,05 rolo rpm constante


atm_dict1 = {
'temp': 20.09, # *C
'pressure': 91.87, # kPa
'humidity': 80.30/100 # %
}
atm_dict2 = {
'temp': 26.70, # *C
'pressure': 92.03, # kPa
'humidity': 36.24/100 # %
}

data_list = [(data_file1,'r',atm_dict1),(data_file2,'r',atm_dict1),(data_file3,'r',atm_dict1),
             (data_file4,'b',atm_dict2),(data_file5,'b',atm_dict2),(data_file6,'b',atm_dict2)]

######## SETTINGS ##########
CORRECTION = True
DISPLAY_TORQUE = True



#m_inercia = 121.107 #kg*m²
m_inercia = 100 #kg*m²
num_dentes = 40
rad_dente = 2*3.1416/num_dentes # quantos radianos entre cada dente

razao_rpms = 5.0185 # 4 e36

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

def potencia_list_from_datafile(data_file:str,atm_dict:dict):
    # Ler arquivo, separar por vírgula e converter str em int
    with open(data_file, 'r') as file:
        data = file.read()
    data = data.split(',')
    data = [ int(x) for x in data if x ] # diferença de tempo entre cada dente e o anterior em micro segundos

    dt_list = data
    # Delete every data point that is not just before the delay or one of its multiples so it mimicks the better solution
    aq_delay = 25000 # 25 ms
    dt_timestamp_list = []
    filtered_dt_list = []
    timestamp_sum = 0
    last_timestamp = 0

    for i in range(len(dt_list)):
        last_timestamp=timestamp_sum
        timestamp_sum+=dt_list[i]
        if int(last_timestamp/aq_delay)!=int(timestamp_sum/aq_delay):
            dt_timestamp_list.append((dt_list[i-1],last_timestamp))
            filtered_dt_list.append(dt_list[i-1])

    data = np.array(filtered_dt_list)

    # Data pre-processing
    print(len(data))
    data = chauvenet(data)
    print(len(data))
    data = signal.savgol_filter(data,window_length=65,polyorder=3,mode='nearest')
    #data=data[:-20]
    x=[n for n in range(len(data))]
    c = np.polyfit(x,data,10)
    y = np.polyval(c,x)
    #data = y

    # Create secondary lists
    dt_list = [ dt/1000000 for dt in data] # converte diferença de tempo entre cada dente e o anterior em segundos
    w_list = [rad_dente/(dt) for dt in dt_list] # velocidade angular para cada intervalo entre dentes em rad/seg
    rpm_list = [w*30*razao_rpms/3.1416 for w in w_list]

    # Correção de pressão - SAE J1349
    es = (610.78 * np.exp((17.3 * atm_dict['temp']) / (237.3 + atm_dict['temp']))/1000)
    ea = atm_dict['humidity'] * es
    pressao_corr = atm_dict['pressure'] - ea
    ca = (99 / pressao_corr) * np.sqrt((atm_dict['temp'] + 273) / 298)

    # Cálculos de potência
    #            rpm,potencia,torque
    potencia_list = [[],[],[]] # em Watts
    for idx in range(1,len(dt_list)):
        dt_med = aq_delay/1000000 # (dt_timestamp_list[idx][1]-dt_timestamp_list[idx-1][1])/1000000
        w_med = ((w_list[idx]+w_list[idx-1])/2)
        potencia_list[0].append((rpm_list[idx]+rpm_list[idx-1])/2) #append rpm media
        Potencia_Vis = 0#0.0004 * (w_med** 3)
        potencia_inercial = (m_inercia / 2) * ((w_list[idx]**2) - (w_list[idx-1]**2)) / dt_med
        potencia_total = potencia_inercial+Potencia_Vis

        if CORRECTION:
            # Correção de pressão - SAE J1349
            potencia_total = (1.176 * ca - 0.176) * potencia_total

        potencia_list[1].append(potencia_total)
        potencia_list[2].append(potencia_total/(w_med*razao_rpms))

    potencia_list = [signal.savgol_filter(potencia_list[0],window_length=95,polyorder=1,mode='mirror'),
                    signal.savgol_filter(potencia_list[1],window_length=95,polyorder=1,mode='mirror'),
                    signal.savgol_filter(potencia_list[2],window_length=95,polyorder=1,mode='mirror')]

    potencia_list[1] = [pot/735.5 for pot in potencia_list[1]] # converter de Watt para Cavalo
    #potencia_list[1] = [pot/250 for pot in potencia_list[1]] # converter de Watt para pompeu

    potencia_list[0] = list(potencia_list[0])
    potencia_list[1] = list(potencia_list[1])
    potencia_list[2] = list(potencia_list[2])
    
    return potencia_list

'''
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
'''
'''
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


## plot power and torque curves
# Line plot
plt.plot(potencia_list[0],potencia_list[1], color='red', linewidth=2)
    print(dt_med)
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
'''



# Plot final graph
# Create the plot and the first axis
fig, ax1 = plt.subplots()


for data_file in data_list:
    potencia_list = potencia_list_from_datafile(data_file[0],data_file[2])

# --- Plot three Power curves (left y-axis) ---
# Each plot uses a different line style to be visible
    if data_file[1] == 'r':
        ax1.plot(potencia_list[0], potencia_list[1], data_file[1]+'-', label='Motronic')   # Solid line
    else:
        ax1.plot(potencia_list[0], potencia_list[1], data_file[1]+'-', label='Speeduino')   # Solid line


    ax1.set_ylabel('Potência (cv)', color='r')
    ax1.tick_params(axis='y', labelcolor='r')
    ax1.grid(True)
    ax1.set_ylim(0, 200)
    ax1.set_xlim(1500, 7200)

    if DISPLAY_TORQUE:
        # Create a second y-axis sharing the same x-axis
        ax2 = ax1.twinx()

        # --- Plot three Torque curves (right y-axis) ---
        # Each plot uses a different line style to be visible
        if data_file[1] == 'r':
            ax2.plot(potencia_list[0], potencia_list[2], data_file[1]+'--', label='Motronic')   # Solid line
        else:
            ax2.plot(potencia_list[0], potencia_list[2], data_file[1]+'--', label='Speeduino')   # Solid line

        ax2.set_ylabel('Torque (nm)', color='b')
        ax2.tick_params(axis='y', labelcolor='b')
        ax2.set_ylim(80, 280)

        # Add legends
        # This part automatically gathers all lines from both axes
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 +labels_2, loc='upper left')

    else:
        # Add legends
        # This part automatically gathers all lines from both axes
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        ax1.legend(lines_1, labels_1, loc='upper left')

# Title and layout
plt.title('Potência e Torque, e36 Pompeu Speeduino test.')
ax1.set_xlabel('rpm')

fig.tight_layout()
plt.show()