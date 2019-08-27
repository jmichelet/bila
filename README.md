**Bila** est un logiciel d'aide à l'observation en spectroscopie astronomique et permet de trouver une étoile de référence de type spectral A ou B qui soit proche de celle étudiée.

#### Crédits
Il reprend une idée originale de F. Teyssier et implémentée dans une feuille de calcul. L'algorithme de recherche des étoiles de référence est fortement inspiré du code de S. Golovanow ( https://github.com/serge-golovanow/SpectroStars ). Merci à eux deux.

#### Présentation
La différence avec les approches précédentes est que ce code écrit en Python fonctionne de façon similaire sous Linux et Windows, ne requiert pas d'utiliser un tableur propriétaire, et d'avoir un ordinateur connecté au réseau Internet. Il fonctionne donc en mode autonome.

#### Utilisation
L'utilisateur doit rentrer l'heure d'observation, les coordonnées équatoriales de l'étoile visée et les coordonnées géographiques du site d'observation. Pour des étoiles souvent observées, il peut s'aider du menu défilant à droite de "Etoiles cibles". Ce menu reprend le contenu du fichier cibles.csv que l'utilisateur peut enrichier et modifier à son gré. Même chose pour la sélection d'un site d'observation via le fichier obs.csv.
Les résultats sont affichés dans la fenêtre de droite. Les lignes colorées en jaune correspondent à une étoile dont le type spectral est présent dans la base Pickles, celles colorées en vert ont un spectre dans la base Miles*(1)*.

#### Installation
Ce code requiert Python 3.5 et au-delà, **Python 2.x n'est pas supporté**. Il utilise intensivement les bibliothèques astropy (calculs astronomiques) et wxpython (interface graphique). Comme d'habitude, il est très fortement conseillé d'utiliser un environment virtuel (virtualenv ou Anaconda, par exemple) pour installer une version de Python et les bibliothèques associées de façon cohérente.
Il a été testé dans les configurations suivantes :

+ Linux Debian 9 + virtualenv + Python 3.5
+ Linux Debian9 + Anaconda + Python 3.6
+ Windows 10 + Anaconda + Python 3.7

#### Exemple d'installation sur une machine Linux Debian 9 via virtualenv:

+ Installation de python 3.5 et de virtualenv. En mode 'root':
>$ apt install python3.5 virtualenv
>
+ Création de l'environnement virtuel et activation:
>$ virtualenv -p /usr/bin/python3.5 venv_bila
>$ source ./venv_bila/bin/activate
>
+ Installation des bibliothèques nécessaires et de leur dépendances:
>$ pip install pathlib2 astropy wxpython
>
+ Lancement du programme:
>$ cd répertoire_où_est_installé_bila
>$ python ./bila.py
>


(1) *Un bogue de wxpython sous Windows 10 empêche l'apparition de ces couleurs. cf* http://github.com/wxWidgets/Phoenix/issues/808
