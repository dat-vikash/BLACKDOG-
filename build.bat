rmdir Distribution\Windows /S /Q
mkdir Distribution\Windows
cd VGO\
python setup.py py2exe
rmdir build /S /Q
ren dist BlackdogConsole
move BlackdogConsole ..\Distribution\Windows\BlackdogConsole
cd ..\GUIfinal\
python setup.py py2exe
rmdir build /S /Q
copy *.gif dist\
copy *.jpg dist\
copy *.txt dist\
ren dist BlackdogGUI
move BlackdogGUI ..\Distribution\Windows\BlackdogGUI
