-------------------- English version follows -------------------------------

**Bila** est un logiciel d'aide à l'observation en spectroscopie astronomique et permet de trouver une étoile de référence de type spectral A ou B qui soit proche de celle étudiée.

#### Crédits
Il reprend une idée originale de F. Teyssier et implémentée dans une feuille de calcul. L'algorithme de recherche des étoiles de référence est fortement inspiré du code de S. Golovanow ( https://github.com/serge-golovanow/SpectroStars ). Merci à eux deux.

#### Présentation
Bila diffère un peu d'avec les approches précédentes : ce code écrit en Python fonctionne de façon similaire sous Linux et Windows, ne requiert pas d'utiliser un tableur propriétaire, et d'avoir un ordinateur connecté au réseau Internet. Il fonctionne donc en mode autonome.

#### Utilisation
L'utilisateur doit rentrer l'heure d'observation, les coordonnées équatoriales de l'étoile visée et les coordonnées géographiques du site d'observation. Pour des étoiles souvent observées, il peut s'aider du menu défilant à droite de "Etoiles cibles". Ce menu reprend le contenu du fichier cibles.csv que l'utilisateur peut enrichier et modifier à son gré. Même chose pour la sélection d'un site d'observation via le fichier obs.csv.
Les résultats sont affichés dans la fenêtre de droite. Les lignes colorées en jaune correspondent à une étoile dont le type spectral est présent dans la base Pickles, celles colorées en vert ont un spectre dans la base Miles*(1)*.

#### Installation
Ce code requiert Python 3.5 et au-delà, **Python 2.x n'est pas supporté**. Il utilise intensivement les bibliothèques astropy (calculs astronomiques) et wxpython (interface graphique). Comme d'habitude, il est très fortement conseillé d'utiliser un environment virtuel (via virtualenv ou Anaconda, par exemple) pour installer une version de Python et les bibliothèques associées de façon cohérente.
Il a été testé dans les configurations suivantes :

+ Linux Debian 9 + virtualenv + Python 3.5
+ Linux Debian9 + Anaconda + Python 3.6
+ Windows 10 + Anaconda + Python 3.7

#### Exemple d'installation sur une machine Linux Debian 9 via virtualenv:

Installation de python 3.5 et de virtualenv. En mode 'root':

    $ apt install python3.5 virtualenv

Création de l'environnement virtuel et activation:

    $ virtualenv -p /usr/bin/python3.5 venv_bila
    $ source ./venv_bila/bin/activate

Installation des bibliothèques nécessaires et de leur dépendances:

    $ pip install pathlib2 astropy wxpython

Lancement du programme:

    $ cd <répertoire_où_est_installé_bila>
    $ python ./bila.py



(1) *Un bogue de wxpython sous Windows 10 empêche l'apparition de ces couleurs. cf* http://github.com/wxWidgets/Phoenix/issues/808


--------------------------------------------- English version --------------------------------------------------------

**Bila** is a software for astronomical spectroscopy observers, which helps them in selecting a A or B spectral type reference star that is close to a target star.

#### Credits
It derives from an original idea from F. Teyssier who implemented it in a spread-sheet. The reference star research algorithm comes from a similar software designed by S. Golovanow ( https://github.com/serge-golovanow/SpectroStars ). Many thanks to both.

#### Introduction
Bila has some differences with the 2 previous implementations, as this Python code works similarly under Linux and Windows, does not request using a proprietary spread-sheet, or having a computer connected to the Internet. It works in an autonomous way.

#### Usage
The user has to manually enter the observing time, the equatorial coordinates of the target and the geopgraphical coordinates of the observatory. For stars that are commonly studied, it main be convenient to use the dropdown menu located at the right of "Etoiles cibles" label. This menu entries are provided by the cible.csv file that the user can modify and enrich to his liking. Same thing for selecting an observation site, using the obs.csv file.
The results are displayed in the right pane. Yellow-coloured lines are for a star which spectral type is included in the Pickles database. Green-coloured lines are stars which spectrum exists in the Miles database (1).
So far, this software is in French only. As the French astronomical vocabulary is pretty close to the English one, that should not be a major issue.

#### Installation
This piece of code requires at least Python 3.5, **Python 2.x is not supported**. It intensively uses the astropy library for astronomical calculations and the wxpython library for the GUI. As usual, it is highly advised to build and use a virtual environment (through virtualenv or Anaconda) to get a clean Python version and its consistent libraries.
The software has been successfully tested with the following environments :

+ Linux Debian 9 + virtualenv + Python 3.5
+ Linux Debian9 + Anaconda + Python 3.6
+ Windows 10 + Anaconda + Python 3.7

#### Example of installation on a Linux Debian 9 machine, through virtualenv.

Installation of python 3.5 and virtualenv. Beeing 'root':

    $ apt install python3.5 virtualenv

Création of the virtual environment and activation:

    $ virtualenv -p /usr/bin/python3.5 venv_bila
    $ source ./venv_bila/bin/activate

Installation of the libraries and their dependencies:

    $ pip install pathlib2 astropy wxpython

Program run:

    $ cd <folder_where_bila_is_deployed>
    $ python ./bila.py
	


(1) *Actually, there is a bug under Windows 10 that prevents colours to be displayed. cf* http://github.com/wxWidgets/Phoenix/issues/808