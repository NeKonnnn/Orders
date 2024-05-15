import os

folder = os.path.dirname(os.path.abspath(__file__)) + '\\'
pyuic_path = 'C:\\Users\\Andrey\\anaconda3\\Library\\bin\\pyuic5'

files = os.listdir(folder)
for file in files:
    if os.path.splitext(file)[1] == '.ui':
        py_ui_name = os.path.splitext(file)[0] + '_ui.py'
        command = pyuic_path + ' "' + folder + file + '" -o "' + folder + py_ui_name + '"'
        os.system(command)
        print(command)
