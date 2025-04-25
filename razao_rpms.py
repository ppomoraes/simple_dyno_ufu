import numpy as np
import scipy.stats as stats

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

data_file = './resultados/teste_dino_ufu_2025-04-17-16:48:35.csv'
vel_motor = 2000 #rpm
num_dentes = 40
d_rolo = 790/1000 #metros

# Ler arquivo, separar por vírgula e converter str em int
with open(data_file, 'r') as file:
    data = file.read()
data = data.split(',')
# Converter todos os elementos em int se esse elemento não for vazio
data = [ int(x) for x in data if x ]
data = np.array(data)

# Limpar outliars
data = chauvenet(data)
media = np.mean(data)/1000000 # converter em segundos/dente
razao = vel_motor*num_dentes*media/60 
print(f'Razão velocidade do motor/velocidade do dino = {razao}')


'''Temperature = 29.23 *C
16:31:28.769 -> Pressure = 91.65 kPa
16:31:28.769 -> Humidity = 57.57 %


Temperature = 29.14 *C
16:50:06.779 -> Pressure = 91.64 kPa
16:50:06.779 -> Humidity = 56.62 %'''