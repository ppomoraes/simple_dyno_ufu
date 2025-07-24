# simple_dyno_ufu
Simplest software possible for an inertial chassis dyno at UFU,
with an arduino based data aquisition system.

Dyno rollers have 40 teeth, polar moment of inertia is 105 kg*m².

4th gear on my e36 results in a rpm ratio 5.0185

## To use
Set up a virtual environment with Python 3.10 and install requirements.txt.
```bash
#Create and activate the virtual environment
python3.10.12 -m venv .venv
# On macOS/Linux:
source .venv/bin/activate
# On Windows (Command Prompt):
# .venv\Scripts\activate.bat
# On Windows (PowerShell):
# .venv\Scripts\Activate.ps1

# Install  dependencies
pip install --upgrade pip
pip install -r requirements.txt
```
Run `dyno_pull.py` with sudo privilege to access serial ports.


# Improvements Due:

## dt oscilations
Dt is oscilating quite a lot, the cause is still to be determined.
Avoid the oscilations if possible, if not, integrate more robust filtering strategies.

Possible culprits:
 - Vibrations on the sensor mounting.
 - Problems inherent to the toothed wheel (wrong profile, out of center).
 - Vibrations due to poorly balanced rollers.
 - Vibrations inherent to cars (unlikely).

Try and increase sensor mount stiffness.

## Moment of Inertia
New experiment for calculating a more precise moment of inertia:
 - Avoid the string rubbing on anything
 - take the slack of the chains out by tensioning from the other cylinder
 - measure carefully the time and height of the drop

## Code changes:
 Make a config file that will be filled during rpm ratio calculation (car name, owner, gear used), also this aquisition should be separate from the pull aquisition.

 During pull aquisition the file will be saved with a timestamp as a csv of data, and a json of the car statuses and enviromental conditions.
 aquisition code and arduino should add a mean to check environment conditions at the beginning or end of a pull (or both?)
 
 During analysis, this json will be loaded to fill graph titles, make the SAE correction, and after, max power and torque, max rpm, and rpm, torque and power lists will be added to the json. (will graph also be saved? maybe)




