import sys
from src.dyno import Aquisition, Analysis, CarsAndFilesHandler

##########################################
# Esse código deve ser rodado dentro de um ambiente virtual com privilégios de SUDO:
# sudo ./.venv/bin/python ./dyno_pull.py 

file_handler = CarsAndFilesHandler()
car_config = file_handler.get_current_car_config()
aquisitor = Aquisition(file_handler.get_serial_config())

# Check necessary info:
correct_info = input(f'''

    Confirme as seguintes informações, 
        Dono: {car_config['owner']}
        Modelo do carro: {car_config['model']}
        Modificações no carro: {car_config['spec']}
        Marcha para o teste: {car_config['gear']}
      
    As informações estão corretas? (s/n)
      ''')
if correct_info == 'n': # Stop execution if car info is wrong
    sys.exit('\nRode primeiro o script "set_car_config.py" para corrigir as informações.\n Interrompendo execução.')

# Get data
input('\n\n     Aperte "Enter" para começar o teste, e aperte "Enter" novamente para finalizar o teste.\n')
test_data = aquisitor.test_pull()
atm_data = aquisitor.get_atm_conditions()

# Process data
analyzer = Analysis(manual_config=file_handler.get_manual_config(),
                    test_data=test_data, atm_data=atm_data)

print('Caboooooo')
print(len(test_data))
print(test_data)