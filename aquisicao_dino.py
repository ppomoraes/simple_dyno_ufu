import serial
import numpy as np
import keyboard
from datetime import datetime

##########################################
# Esse código deve ser rodado dentro de um ambiente virtual com privilégios de SUDO:
# sudo ./venv/bin/python ./aquisicao_dino.py 

# Configuração da porta serial e taxa transferência
port = '/dev/ttyACM0'  # Porta COM à qual o Arduino está conectado
baud_rate = 115200  # Taxa de transferência que deve corresponder à configuração do Arduino

# Inicializar a comunicação serial
try:
  ser = serial.Serial(port, baud_rate)
except:
  print('\n'+'#'*50+'\n')
  print(f"Erro na comunicação serial, verifique que a porta usada é: {port}, e o baud rate é: {baud_rate}.".upper())
  print('\n'+'#'*50+'\n')
  raise

print('\nComunicação serial estabelecida.')

# Esperar o usuário apertar Enter para começar a leitura
input("\nAperte 'Enter' para começar, e 'f' para finalizar o teste.")

# Inicializar a lista para armazenar os valores lidos e limpar o buffer serial
delta_time_values = []
ser.reset_input_buffer()

# Ler dados do Arduino
print(f"\n Lendo dados, aperte 'f' para finalizar teste.")
while True:
    # Do your stuff
    if ser.in_waiting > 0:
        # Ler uma linha de dados da porta serial
        line = ser.readline().decode('utf-8').strip()
        try:
            # Converter o valor para int e adicionar à lista
            value = int(line)
            delta_time_values.append(value)
            #print(f"Valor lido: {value}")
        except ValueError:
            # Se a conversão falhar, ignore a leitura
            print(f"Falha ao converter valor: {line}")
    if keyboard.is_pressed("f"):
        break

# Fechar a comunicação serial
ser.close()

# Exibir os valores lidos
print(f"\n Foram lidos {len(delta_time_values)} valores lidos do Arduino:\n")
print(delta_time_values)

# Salvar os valores em um arquivo chamado com data e hora
timestamp=datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
output_file = './resultados/teste_dino_ufu_'+timestamp+'.csv'

with open(output_file, 'w') as file:
    for value in delta_time_values:
        file.write(str(value)+',')

print(f"Valores salvos em '{output_file}'")