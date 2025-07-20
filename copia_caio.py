import matplotlib.pyplot as plt
from typing import List
import numpy as np
import scipy.stats as stats
import pandas as pd

data_file = './resultados/teste_dino_ufu_2025-04-17-16:48:53.csv'
m_inercia = 36.2 #kg*m²
num_dentes = 40
rad_dente = 2*3.1416/num_dentes # quantos radianos entre cada dente

razao_rpms = 6.479500000000001 # 3 pajero
temp = 29.14 #*C
pressure = 91.64 #kPa
humidity = 56.62 #%

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
# Converter todos os elementos em int se esse elemento não for vazio
data = [ int(x) for x in data if x ] # diferença de tempo entre cada dente e o anterior em micro segundos
data = np.array(data)


data=data[100:-50]
data = chauvenet(data)

#x=[n for n in range(len(data))]
#c = np.polyfit(x,data,15)
#y = np.polyval(c,x)
#data = y

dt_list = [ dt/1000000 for dt in data] # converte diferença de tempo entre cada dente e o anterior em segundos
w_list = [rad_dente/(dt) for dt in dt_list] # velocidade angular para cada intervalo entre dentes em rad/seg
rpm_list = [int(w*30*razao_rpms/3.1416) for w in w_list]

intervalo = 200
histerese = 450
temp = 40
pressure = 91 #kPa
humidity = 0.5 #%

dados_brutos = {'dt': dt_list,
     'rad_s': w_list,
     'rpm': rpm_list
    }

results = {'rpm':[],'potencia':[]}

for x in range(rpm_list[0], max(rpm_list) + 1, intervalo):
    janela = dados_brutos[(dados_brutos['rpm'] > x - histerese) & (dados_brutos['rpm'] < x + histerese)]

    if len(janela) > 2:
        w0 = janela.iloc[0]['rad_s']
        w1 = janela.iloc[-1]['rad_s']
        w_med = (w0 + w1) / 2

        dt = sum(janela.iloc[0:]['dt'])

        rpm_avg = (janela.iloc[0]['rpm'] + janela.iloc[-1]['rpm']) / 2

        # Inertial power
        potencia = (m_inercia / 2) * (w1 ** 2 - w0 ** 2) / dt

        # Linear velocity
        #velocidade = w_med * d_rolo * 1.8  # m/s

        # Viscous loss
        #potencia_vis = coef_visc * (w_med ** 3)
        potencia_vis = 0

        # Mass factor - can be adjusted
        f_mass = 1.0

        # Total power + correction
        potencia_total = (potencia + potencia_vis) * f_mass
        #potencia_corr = (1.176 * ca - 0.176) * potencia_total

        # Torque (Nm)
        torque = potencia_total / (rpm_avg * np.pi / 30)

        # Power in HP
        potencia_hp = potencia_total / 746

        results['rpm'].append(rpm_avg)
        results['potencia'].append(potencia_hp)


print(max(results['potencia']))
print(max(results['rpm']))


# Line plot
plt.plot(results['rpm'],results['potencia'], color='red', linewidth=2)

# Labels and title
plt.xlabel('rpm')
plt.ylabel('potencia')
plt.title('Potencia do caio versão python')
plt.legend()
plt.grid(True)

# Display plot
plt.show()

'''

def calcula_potencia_inercial2(dados_brutos: pd.DataFrame, intervalo: int, histerese: int,
                                temperatura: float, pressao: float, UR: float, rpm_inicial: int,
                                m_inercia: float, coef_visc: float, d_rolo: float) -> pd.DataFrame:
    """
    dados_brutos: DataFrame with columns [timestamp, rad/s, RPM]
    intervalo: Step RPM
    histerese: Half-width RPM window
    temperatura: Celsius
    pressao: Ambient pressure (kPa)
    UR: Relative humidity (0-1)
    rpm_inicial: Starting RPM
    m_inercia: Inertia constant (kg·m²)
    coef_visc: Viscous coefficient
    d_rolo: Roller diameter (m)
    """

    dados = []
    rpm_max = dados_brutos['RPM'].max()
    cont_id = 0

    # Correção de pressão - SAE J1349
    es = (610.78 * np.exp((17.3 * temperatura) / (237.3 + temperatura))) / 1000
    ea = UR * es
    pressao_corr = pressao - ea
    ca = (99 / pressao_corr) * np.sqrt((temperatura + 273) / 298)

    for x in range(rpm_inicial, int(rpm_max) + 1, intervalo):
        janela = dados_brutos[(dados_brutos['RPM'] > x - histerese) & (dados_brutos['RPM'] < x + histerese)]

        if len(janela) > 2:
            w0 = janela.iloc[0]['rad_s']
            w1 = janela.iloc[-1]['rad_s']
            w_med = (w0 + w1) / 2

            t0 = janela.iloc[0]['timestamp']
            t1 = janela.iloc[-1]['timestamp']
            dt = (t1 - t0) / 100000  # convert from 10µs to seconds

            rpm_avg = (janela.iloc[0]['RPM'] + janela.iloc[-1]['RPM']) / 2

            # Inertial power
            potencia = (m_inercia / 2) * (w1 ** 2 - w0 ** 2) / dt

            # Linear velocity
            velocidade = w_med * d_rolo * 1.8  # m/s

            # Viscous loss
            potencia_vis = coef_visc * (w_med ** 3)

            # Mass factor - can be adjusted
            f_mass = 1.0

            # Total power + correction
            potencia_total = (potencia + potencia_vis) * f_mass
            potencia_corr = (1.176 * ca - 0.176) * potencia_total

            # Torque (Nm)
            torque = potencia_corr / (rpm_avg * np.pi / 30)

            # Power in HP
            potencia_hp = potencia_corr / 746

'''