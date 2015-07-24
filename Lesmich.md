# Allgemeines:

WRF_Stuve.py wird als freie software veröffentlicht unter der Allgemeienen Öffentlichen Lizenz (GPL) von GNU. (http://www.gnu.org/licenses/gpl.html).

Dieses Skript ist für all diejenigen gedacht die Stüve Diagramme bevorzugen.
Die Liebhaber des Skew-T's können sich des GrADS Skript bedienen.
Wer Indizes für die Atmosphärische Satbilität braucht, dem kann dieses Skript nützlich sein.  

# Funktionen:

* Stellt in einem Stüve diagramm die Höhenprofile für das WRF Modell dar zusammen mit den entsprechenden Messdaten des Radiosondenaufstiegs.     

* Berechnet die Sturmindizes anhand der WRF-Daten (Mischungsverhältnis in der Mischungsschicht, Cape, Lift, Hebungskondensationsniveau, Niveau der freien Konvektion, Wolkenobergrenze) 


# Voraussetzungen:

* wget (http://www.gnu.org/software/wget/)
* nco (http://nco.sourceforge.net/, ncrcat in /usr/local installieren)
* python
* matplotlib
* scipy

# Installation:
Mit den Befehlen

```
apt-get install nco wget
pip install -r requirements.pip

```


# So wird's benutzt:

1. namelist ausfüllen/ändern
2. python WRF_Stuve.py
(namelist und Skript müssen im selben Verzeichnis gespeichert sein)

namelist:
ruta = Absoluter Pfad zum Verzeichnis das die Dateien wrfout* beinhaltet
Soll nur eine Datei benutzt werden dann den Namen der Datei im Pfad angeben
codigo = WMO Kennziffern der Radiosondenstation 
wfecha = Datum der ersten WRF Ausgabedatei
ifecha = Datum der ersten Radiosondenmessung  
efecha = Datum der letzten Radiosondenmessung
dh = Intervall zwischen Radiosondenaufstiegen (normalerweise 12 oder 24 je nach Land)
wfecha muss früher oder gleich mit ifecha sein


# So funktioniert's:

Das Skript muss für jede Radiosondenstation neu ausgeführt werden, dabei "codigo" im namelist ändern.
In einer Schleife von ifecha bis efecha werden für jedes Intervall dh zwei Dateien (eine Grafik und eine Tablle) ausgegeben. 
Die Eingabedateien (=Ausgabedateien von WRF) wrfout* können mehrere Zeiten beinhalten und die Intervalle zwischen den Zeiten kann kleiner als dh sein. Die Zeitspanne von ifecha bis efecha kann durch mehrere Dateien wrfout* gefüllt sein. 
Das Skript sucht alle Dateien wrfout* mit Datum zwischen ifecha und efecha. Dabei muss der Name der netcdf Dateien dem üblichen Format ähneln: Der Name muss mit "wrfout" anfangen und muss das Anfangsdatum in der Form YYYY-MM-dd_HH:mm beinhalten. 
Für jede Stunde eines Radiosondenaufstiegs zwischen ifecha und efecha (ifecha+n*dh) sucht das Skript die Datei mit dem Anfangsdatum unmittelbar vor dem Datum und Stunde der Radiosondenmessung.  

Mit Hilfe der Stationskennziffer (codigo) und wget lädt das Skript die Messdaten des Radiosondenaufstiegs im Textformat herunter und zwar von der Seite http://weather.uwyo.edu/. Die Textdatei wird als <Kennziffer>_<Datum>.csv im selben Verzeichnis abgespeichert. 
Dabei wird die Option -c (continue) benutzt -> Die Messdaten werden nicht wiederholt runtergeladen. 
Anhand der Koordinaten der Station, die im Textarchiv angegeben sind, werden die entsprechenden Daten aus der entsprechenden netcdf Datei gelesen mit Hilfe der Funktion "ncrcat" (=Teil der NCO Bibliothek). Dabei entstehen die Hilfsdateien "lonlat.nc", "tiempos.nc" und "wrftmp.nc" die in jedem Schleifenzyklus überschrieben werden. 

**_Anm.:_** Die Funktion ncrcat hilft wesentlich kleinere Dateien zu erzeugen. Das Skript könnte aber auch ohne NCO auskommen und die komplette Datei wrfout* mit scipy.io.netcdf lesen: Die Kommandos os.system('ncrcat ... archiv ... ') durch io.netcdf.netcdf_file(archivo,'r') ersetzen, Koordinaten lesen (lat=a.variables['XLAT'][0], lon=a.variables['XLONG'][0]), Gitterpunkt i,j bestimmen, restlichen Variablen im Punkt i,j lesen.]


# Ausgabedateien:

Für jede Radiosondenmessung enstehen zwei Dateien:

<Kennziffer>_<Datum>.png:
Stuve Diagramm mit dem simulierten und gemessenen Radiosondenaufstieg 
Rot = simulierter Taupunkt (ºC)
Blau = simulierte Temperatur (ºC)
Grün = simuliertes Mischungsverhältnis (g/kg) in der Mischungsschicht
Dunkelgrau = gemessener Taupunkt (ºC) 
Hellgrau = gemessene Temperatur (ºC) 
Die Farben können in der Funktion stuve() ab der Linie 400 geändert werden. 

<Kennziffer>_<Datum>.csv:
Tabelle mit den simulierten (2.Spalte) und gemessenen (3.Spalte) Sturmindizes 
Das Skript rechnet mehrere Indizes die zur Zeit nicht im heruntergeladenen Datei enthalten sind. 
