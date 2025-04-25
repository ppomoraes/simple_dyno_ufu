import matplotlib.pyplot as plt
from typing import List
import numpy as np
import scipy.stats as stats

data_file = './resultados/teste_dino_ufu_2025-04-17-16:48:53.csv'
m_inercia = 36.2
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
data = chauvenet(data)
data = moving_average(data,200) # Fazer média móvel de 40 itens

dt_list = [ dt/1000000 for dt in data] # converte diferença de tempo entre cada dente e o anterior em segundos
w_list = [rad_dente/(dt) for dt in dt_list] # velocidade angular para cada intervalo entre dentes em rad/seg
rpm_list = [w*30*razao_rpms/3.1416 for w in w_list]

#               rpm,potencia
potencia_list = [[],[]] # em Watts
for idx in range(1,len(dt_list)):
    dt_med = ((dt_list[idx]+dt_list[idx-1])/2) # dt médio entre esse ponto e o anterior
    potencia_list[0].append((rpm_list[idx]+rpm_list[idx-1])/2) #append rpm media
    potencia_list[1].append((m_inercia / 2) * ((w_list[idx]**2) - (w_list[idx-1]**2)) / dt_med)

potencia_list[1] = [pot/746 for pot in potencia_list[1]] # converter de Watt para Cavalo
#rpm_list = rpm_list[1:] #remove first element to match potencia_list

clean_rpm = []
clean_pot = []
for i in range(len(potencia_list[1])):
    if potencia_list[1][i]>0:
        clean_pot.append(potencia_list[1][i])
        clean_rpm.append(potencia_list[0][i])

clean_pot=moving_average(clean_pot,200)
clean_rpm=moving_average(clean_rpm,200)
print(max(clean_pot))
print(max(clean_rpm))

# Line plot
plt.plot(clean_rpm,clean_pot, color='red', linewidth=2)

# Labels and title
plt.xlabel('RPM motor')
plt.ylabel('Potência')
plt.title('sem tratamento')
plt.legend()
plt.grid(True)

# Display plot
plt.show()


'''Temperature = 29.23 *C
16:31:28.769 -> Pressure = 91.65 kPa
16:31:28.769 -> Humidity = 57.57 %


Temperature = 29.14 *C
16:50:06.779 -> Pressure = 91.64 kPa
16:50:06.779 -> Humidity = 56.62 %'''