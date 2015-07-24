# Introducción:

WRF_Stuve.py se publicó como software libre bajo la Licencia Pública General de GNU (http://www.gnu.org/licenses/gpl.html)

Este script se creó para los que acostumbran usar diagramas Stüve.
Los amantes del Skew-T pueden servirse del script para grads. 
Si les interesa obtener los indices de estabilidad atmosférica (o índices de tormenta) utilicen este script.


# Funciones:

* Genera radiosondeos de las salidas del modelo WRF y los grafica junto con el radiosondeo observado correspondiente en un mismo diagrama Stüve
* Calcula índices de tormenta desde las salidas de WRF (Raz'on de mezcla de la capa de mezcla, Cape, Lift, Nivel de Condensación Forzada, Nivel de Libre Conveccion, Nivel de Flotabilidad Neutral) y los compara con los índices del radiosondeo observado en una tabla.

# Requisitos:

* wget (http://www.gnu.org/software/wget/) 
* nco (http://nco.sourceforge.net/)
* python 
* matplotlib
* scipy 

# Instalación:
Ejecute los siguientes comandos.

```
apt-get install nco wget
pip install -r requirements.pip

```

# Ejecución:

1. Editar el archivo "namelist".
2. python WRF_Stuve.py
(namelist y el script tienen que estar en el mismo directorio)

namelist:
ruta = ruta absoluta a la carpeta que contiene los archivos wrfout*
Si se quiere procesar un solo archivo incluir el nombre del archivo en la ruta 
codigo = código OMM de la estación
wfecha = fecha del primer archivo wrfout* (en UTC)
ifecha = fecha del primer radiosondeo (en UTC)
efecha = fecha del último radiosondeo (en UTC)
dh = intervalo de horas entre radiosondeos (múltiples de 12)
ifecha debe tener hora 00 o 12 para coincidir con los radiosondeos.
wfecha debe ser anterior o igual a ifecha.  


# Funcionamiento:

El script se debe ejecutar por cada estación de radiosondeo aparte indicada mediante "codigo" en namelist. 
Genera las salidas en un ciclo sobre las fechas indicadas por el usuario en intervalos "dh" desde "ifecha" hasta "efecha".
Puede haber varias fechas en un solo archivo wrfout* y puede haber varios archivos.
El intervalo de tiempo entre diferentes archivos wrfout* puede ser menor de dh.
El script selecciona todos los archivos wrfout* con fecha inicial entre wfecha y efecha.
Para cada una de las n horas de radiosondeos entre wfecha y efecha (ifecha+n*dh) se lee el archivo wrfout* con la fecha inicial y hora anterior más cercana.
El nombre de cada uno de los archivos netcdf de WRF debe iniciar con "wrfout" y debe contener la fecha inicial en el formato YYYY-MM-dd_HH:mm

Con base en el código de estación el script descarga el radiosondeo en forma de texto desde http://weather.uwyo.edu/ mediante wget al archivo llamado 
<codigo>_<fecha>.csv. El comando de descarga usa la opción -c "continue" -> Se pueden hacer varias pruebas sin volver a descargar el mismo archivo.
Con base en las coordenadas de la estación indicadas en el radiosondeo extrae la información simulada del archivo netcdf para el punto de grilla más cercano  con la herramienta "ncrcat" de NCO.
Se generan los archivos intermedios lonlat.nc, tiempos.nc y wrftmp.nc que se sobreescriben en cada ciclo. 

**_Nota:_** Se usa nco para reducir el tamaño de los archivos antes de procesarlos con scipy.io.netcdf. El script también puede funcionar sin NCO -> cambiar las lineas os.system('ncrcat ... archivo ... ') por "io.netcdf.netcdf_file(archivo,'r')", extraer coordenadas (lat=a.variables['XLAT'][0], lon=a.variables['XLONG'][0]), determinar puntos de grilla i,j, extraer las demás variables en el punto i,j  


# Salidas:

Por cada radiosondeo se generan dos archivos:

<codigo>_<fecha>.png:
Diagrama Stuve con radiosondeo simulado y medido 
rojo = punto de rocío (ºC) simulado
azul = temperatura (ºC) simulada
verde = razón de mezcla (g/kg) de la capa de mezcla simulada
gris oscuro = punto de rocío (ºC) observado
gris claro = temperatura (ºC) observada
Pueden cambiar los colores en la función stuve() desde la línea 400 en adelante.

<codigo>_<fecha>.csv:
Tabla con índices de tormenta/estabilidad simulados (2. columna) y observados (3.columna) 
Actualmente el script calcula varios índices adicionales con base en los datos simulados que no están incluidos en los datos observados.
