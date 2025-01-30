IDE:  
visual studio code  
  
windows:  
python -m venv venv  
.\venv\Scripts\Activate.ps1  
python.exe -m pip install --upgrade pip  
pip install pynput  
$env:PYTHONPATH = "."  
  
notes:  
pip install tkinter  
  
run windows:  
python frontend/frontend.py  
    
linux:   
python3 -m venv venv   
source venv/bin/activate   
sudo apt update    
sudo apt-get install python3-tk  
pip install pynput   
   
run linux:   
PYTHONPATH=. python frontend/frontend.py  

