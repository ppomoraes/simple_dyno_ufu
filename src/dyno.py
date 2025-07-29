import numpy as np
import scipy.stats as stats
import yaml
import keyboard
from datetime import datetime
import serial
import time

class Aquisition:
    ''' Responsible for serial communication with arduino,
    and data aquisition.'''
    def __init__(self,serial_config:dict):
        ''' Inicialize serial communication.'''
        '''
        port = serial_config['port']
        baud_rate = serial_config['baud_rate']
        try:
            self.ser = serial.Serial(port, baud_rate)
        except:
            print('\n'+'#'*50+'\n')
            print(f"Erro na comunicação serial, verifique que a porta usada é: {port}, e o baud rate é: {baud_rate}.".upper())
            print('\n'+'#'*50+'\n')
            raise
            '''

        print('\nComunicação serial estabelecida.')
    
    def test_pull(self)->list:
        '''    Activates arduino to start transmitting dt,
        reads dt from serial until "Enter" key is pressed,
        stops arduino from transmitting dt and returns dt list.    '''
        # Pass signal to arduino to start outputting dt!!!!!!!

        self.test_data = []
        # Reading data from serial
        print(f'\n\n Lendo dados...\n\nAperte "Enter" para finalizar o teste.\n')
        while True:
            '''
            if self.ser.in_waiting > 0:
                # Read a line from serial buffer
                line = self.ser.readline().decode('utf-8').strip()
                try:
                    # Convert value to int and append to list
                    value = int(line)
                    self.test_data.append(value)
                except ValueError:
                    # If conversion fails, print failed value and ignore it
                    print(f"Falha ao converter valor: {line}")
                    '''
            self.test_data.append(1)
            time.sleep(1)
            if keyboard.is_pressed("enter"):
                break
        # Pass signal to arduino to stop outputting dt!!!!!!!
        return self.test_data

    def get_atm_conditions()->dict:
        ''' Gets atmospheric contitions from Arduino.
        Temperature (C)
        Pressure (kPa)
        humidity (relative %)'''
        # com with arduino
        return {'temperature':20.09,
                'pressure':91.87,
                'humidity':80.30
                }
            
class Analysis:
    ''' Responsible for data science, all calculations and graph generations.'''
    def __init__(self,manual_config:dict,test_data:list,atm_data:dict={}):
                
        self.sae_correction = manual_config.get('sae_j1349') # Boolean
        self.power_unit = manual_config.get('power_unit') # cv/kW
        self.torque_unit = manual_config.get('torque_unit') # nm/kgfm
        self.rpm_test = manual_config.get('rpm_test')
        self.smoothing_factor = manual_config.get('smoothing_factor')
        self.num_teeth = manual_config.get('num_teeth')
        self.mom_inertia = manual_config.get('mom_inertia') # kg*m²
        
        self.test_data = test_data
        self.atm_data = atm_data

    def gen_single_graph():

        pass

    def get_rpm_ratio(self)->float:
        #TODO
        ''' Calculates rpm ratio, 
        engine rpm/dyno rpm.'''
        data = Aquisition.get_data(time=0.5)
        rpm_ratio = self.__calculate_rpm_ratio(data)

        return rpm_ratio
    

    def __calculate_rpm_ratio(self,dt_list:list)->float:     
        dt_list = self.__chauvenet(dt_list) # Limpar outliars
        mean_dt = np.mean(dt_list)/1000000 # converter em segundos/dente
        ratio = self.rpm_test*self.num_teeth*mean_dt/60 
        return ratio

    def __chauvenet(data:list)->list:
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

class CarsAndFilesHandler:
    ''' Handles car configuration and general reading/writing of save files.'''
    def __init__(self,manual_config_path:str='./manual_config.yaml'):

        with open(manual_config_path, 'r') as file:
            self.manual_config_dict = yaml.safe_load(file)

        self.car_config_path = self.manual_config_dict.get('car_config_path')
        self.results_directory = self.manual_config_dict.get('results_folder')
    
    def get_current_car_config(self)->dict:
        with open(self.car_config_path, 'r') as file:
            car_config_dict = yaml.safe_load(file)

        return car_config_dict
    
    def get_serial_config(self)->dict:
        return {'port':self.manual_config_dict.get('port'),
                'baud_rate':self.manual_config_dict.get('baud_rate')}
    
    def get_manual_config(self)->dict:
        return self.manual_config_dict

    def __open_csv_data(filename:str)->np.array:
        # Ler arquivo, separar por vírgula e converter str em int
        with open(filename, 'r') as file:
            data = file.read()
        data = data.split(',')
        # Converter todos os elementos em int se esse elemento não for vazio
        data = [ int(x) for x in data if x ]
        dt_list = np.array(data)
        return dt_list