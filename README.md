### Imports
* pip install PyQt5
* pip install pyinstaller
* 

### Commands
* pyrcc5 -o resource.py resource.qrc
* pyinstaller -F -w app.py

### Start automatically
* Pressione Windows+R para abrir o “Executar”;
* Digite “shell:startup” e pressione Enter para abir a pasta “Inicializar”;
* Crie um atalho do arquivo "/dist/app.exe" na pasta “Inicializar” 
para que o programa seja executado na incialização do SO.