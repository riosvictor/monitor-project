### Imports
* pip install PyQt5
* pip install pyinstaller
* 

### Commands
* pyrcc5 -o resource.py resource.qrc
* pyinstaller --noconfirm --onefile --windowed
  --hidden-import "statsmodels.tsa.statespace._kalman_initialization"
  --hidden-import "statsmodels.tsa.statespace._kalman_filter" 
  --hidden-import "statsmodels.tsa.statespace._kalman_smoother" 
  --hidden-import "statsmodels.tsa.statespace._representation" 
  --hidden-import "statsmodels.tsa.statespace._simulation_smoother" 
  --hidden-import "statsmodels.tsa.statespace._statespace" 
  --hidden-import "statsmodels.tsa.statespace._tools" 
  --hidden-import "statsmodels.tsa.statespace._filters._conventional" 
  --hidden-import "statsmodels.tsa.statespace._filters._inversions" 
  --hidden-import "statsmodels.tsa.statespace._filters._univariate" 
  --hidden-import "statsmodels.tsa.statespace._filters._univariate_diffuse" 
  --hidden-import "statsmodels.tsa.statespace._smoothers._alternative" 
  --hidden-import "statsmodels.tsa.statespace._smoothers._classical" 
  --hidden-import "statsmodels.tsa.statespace._smoothers._conventional" 
  --hidden-import "statsmodels.tsa.statespace._smoothers._univariate" 
  --hidden-import "statsmodels.tsa.statespace._smoothers._univariate_diffuse" 
  --additional-hooks-dir "."  
  "C:/Users/Trizy/PycharmProjects/monitor/app.py"

### Start automatically
* Pressione Windows+R para abrir o “Executar”;
* Digite “shell:startup” e pressione Enter para abir a pasta “Inicializar”;
* Crie um atalho do arquivo "/dist/app.exe" na pasta “Inicializar” 
para que o programa seja executado na incialização do SO.