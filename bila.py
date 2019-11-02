# -*- coding: UTF-8 -*-

import datetime
import math
import wx
import csv
import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle

# On enlève les avertissements relatifs à iers dus à la fonction transform_to()
import warnings
from astropy.utils.exceptions import AstropyWarning
warnings.filterwarnings(action='ignore', category=AstropyWarning, module=r'.*astropy.coordinates',)

# Principe de base : pas d'accès à Internet
from astropy.utils import iers
iers.conf.auto_download = False
iers.conf.auto_max_age = None

fichier_csv_base = 'base.csv'
fichier_csv_obs = 'obs.csv'
fichier_csv_cibles = 'cibles.csv'
separations = ['5', '10', '20', '30']
ecarts_bv = ['0.05', '0.1', '0.2', '0.5']
type_pickles = ['A0I', 'A0III', 'A0IV', 'A0V', 'A2I', 'A2V', 'A3III', 'A3V', 'A5III', 'A5V', 'A7III', 'A7V',
                'B0I', 'B0V', 'B1I', 'B1V', 'B2II', 'B2IV', 'B3I', 'B3III', 'B3V', 'B5I', 'B5III', 'B5V', 'B6IV', 'B8I', 'B8V', 'B9III', 'B9V']

couleur_resultat_defaut = wx.LIGHT_GREY
couleur_resultat_pickles = wx.YELLOW
couleur_resultat_miles = wx.GREEN
couleur_resultat_fond = wx.Colour(40, 40, 40)


class FenetrePrincipale(wx.Frame):
    def __init__(self, parent, titre):
        wx.Frame.__init__(self, parent, title=titre)

        # Menu enfant
        filemenu = wx.Menu()
        self.menu_apropos = filemenu.Append(wx.ID_ABOUT, "&A Propos", " Informations sur ce programme")
        self.menu_sortie = filemenu.Append(wx.ID_EXIT, "E&xit", " Sortie")

        # Barre de menu minimaliste
        barre_menu = wx.MenuBar()
        barre_menu.Append(filemenu, '&Gestion')
        self.SetMenuBar(barre_menu)

        # Initialisation des valeurs
        # -- Etoile cible (Sirius)
        self.heure_alpha = '6'
        self.minute_alpha = '45'
        self.degre_delta = '16'
        self.minute_delta = '43'
        self.signe_delta = -1
        # -- Position observatoire
        self.degre_lat = '45'
        self.minute_lat = '07'
        self.signe_lat = 1
        self.degre_long = '5'
        self.minute_long = '40'
        self.signe_long = 1
        self.metre_alt = '310'
        # -- Temps de l'observation
        self.date = datetime.date.today()
        self.annee = str(self.date.year)
        self.mois = str(self.date.month)
        self.jour = str(self.date.day)
        self.heure = datetime.time(22)  # 22 h TU par défaut
        self.heure_temps = str(self.heure.hour)
        self.minute_temps = str(self.heure.minute)
        # -- Critères de tri
        self.ecart_bv_max = '0.1'
        self.separation_max = '10'
        self.hauteur_min = '10'
        # -- Bases de données
        self.obs, self.nom_obs = self.lecture_fichier_csv(fichier_csv_obs)
        self.cibles, self.nom_cibles = self.lecture_fichier_csv(fichier_csv_cibles)

        # Panneau de saisie
        self.panneau_saisie = wx.Panel(self, name='Saisie')

        # 1 Etoile cible
        self.titre_etoile = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Etoile cible')
        self.cb_cible = wx.ComboBox(self.panneau_saisie, choices=self.nom_cibles, style=wx.CB_DROPDOWN)
        self.cb_cible.SetSelection(0)

        # 1-1 Ascension droite
        self.etiq_alpha = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Asc. droite')
        self.etiq_heure_alpha = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Heures')
        self.edit_heure_alpha = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.heure_alpha)
        self.etiq_minute_alpha = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Minutes')
        self.edit_minute_alpha = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.minute_alpha)

        # 1-2 Déclinaison
        self.etiq_delta = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Déclinaison')
        self.etiq_degre_delta = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Degrés')
        self.edit_degre_delta = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.degre_delta)
        self.etiq_minute_delta = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Minutes')
        self.edit_minute_delta = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.minute_delta)
        self.br_signe_delta = wx.RadioBox(self.panneau_saisie, wx.ID_ANY, choices=['N', 'S'], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.br_signe_delta.SetSelection(int((1 - self.signe_delta) / 2))

        # 2 Site d'observation
        self.titre_site = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Site d\'observation')
        self.cb_site = wx.ComboBox(self.panneau_saisie, choices=self.nom_obs, style=wx.CB_DROPDOWN)
        self.cb_site.SetSelection(0)

        # 2-1 Latitude
        self.etiq_lat = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Latitude')
        self.etiq_degre_lat = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Degrés')
        self.edit_degre_lat = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.degre_lat)
        self.etiq_minute_lat = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Minutes')
        self.edit_minute_lat = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.minute_lat)
        self.br_signe_lat = wx.RadioBox(self.panneau_saisie, wx.ID_ANY, choices=['N', 'S'], majorDimension=1, style=wx.RA_SPECIFY_ROWS)

        # 2-2 Longitude
        self.etiq_long = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Longitude')
        self.etiq_degre_long = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Degrés')
        self.edit_degre_long = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.degre_long)
        self.etiq_minute_long = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Minutes')
        self.edit_minute_long = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.minute_long)
        self.br_signe_long = wx.RadioBox(self.panneau_saisie, wx.ID_ANY, choices=['E', 'O'], majorDimension=1, style=wx.RA_SPECIFY_ROWS)

        # 2-3 Altitude
        self.etiq_alt = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Altitude')
        self.etiq_metre_alt = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Mètres')
        self.edit_metre_alt = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.metre_alt)

        # 3 Temps de l'observation
        self.titre_temps = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Date et heure')

        # 3-1 Date
        self.etiq_annee = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Année')
        self.edit_annee = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.annee)
        self.etiq_mois = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Mois')
        self.edit_mois = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.mois)
        self.etiq_jour = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Jour')
        self.edit_jour = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.jour)

        # 3-2 Heure
        self.etiq_heure = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Heure TU')
        self.etiq_heure_temps = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Heures')
        self.edit_heure_temps = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.heure_temps)
        self.etiq_minute_temps = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Minutes')
        self.edit_minute_temps = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.minute_temps)

        # 4 Critères de sélection
        self.titre_critere = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Critères de sélection')

        self.etiq_separation = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Séparation max (degrés)')
        self.cb_separation = wx.ComboBox(self.panneau_saisie, choices=separations, style=wx.CB_DROPDOWN)
        self.cb_separation.SetSelection(separations.index(self.separation_max))

        self.etiq_ecart_bv = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Ecart B-V max')
        self.cb_ecart_bv = wx.ComboBox(self.panneau_saisie, choices=ecarts_bv, style=wx.CB_DROPDOWN)
        self.cb_ecart_bv.SetSelection(ecarts_bv.index(self.ecart_bv_max))

        self.etiq_hauteur_min = wx.StaticText(self.panneau_saisie, wx.ID_ANY, 'Hauteur min (degrés)')
        self.edit_hauteur_min = wx.TextCtrl(self.panneau_saisie, wx.ID_ANY, self.hauteur_min)

        # 5 Boutons d'action
        self.bouton_calcul = wx.Button(self.panneau_saisie, wx.ID_ANY, 'Calculer')
        self.bouton_arret = wx.Button(self.panneau_saisie, wx.ID_ANY, 'Fermer')

        # Panneau des résultats
        self.resultat = wx.TextCtrl(self, wx.ID_ANY, size=(600, 600), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)
        self.resultat.SetBackgroundColour(couleur_resultat_fond)
        self.resultat.SetForegroundColour(couleur_resultat_defaut)
        police_resultat = wx.Font((0, 13), family=wx.FONTFAMILY_MODERN, style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL)
        attribut = wx.TextAttr(couleur_resultat_defaut, colBack=couleur_resultat_fond, font=police_resultat)
        self.resultat.SetDefaultStyle(attribut)

        self.placement_saisie()
        self.affectation_evenements()
        self.Show()

    def placement_saisie(self):
        hor = wx.BoxSizer(wx.HORIZONTAL)
        vert = wx.BoxSizer(wx.VERTICAL)
        etoile1 = wx.BoxSizer(wx.HORIZONTAL)
        etoile2 = wx.BoxSizer(wx.HORIZONTAL)
        etoile3 = wx.BoxSizer(wx.HORIZONTAL)
        site1 = wx.BoxSizer(wx.HORIZONTAL)
        site2 = wx.BoxSizer(wx.HORIZONTAL)
        site3 = wx.BoxSizer(wx.HORIZONTAL)
        site4 = wx.BoxSizer(wx.HORIZONTAL)
        temps1 = wx.BoxSizer(wx.HORIZONTAL)
        temps2 = wx.BoxSizer(wx.HORIZONTAL)
        temps3 = wx.BoxSizer(wx.HORIZONTAL)
        critere1 = wx.BoxSizer(wx.HORIZONTAL)
        critere2 = wx.BoxSizer(wx.HORIZONTAL)
        b = wx.BoxSizer(wx.HORIZONTAL)

        etoile1.Add(self.titre_etoile, 0, wx.ALL, 5)
        etoile1.Add(self.cb_cible, 0, wx.ALL, 5)

        etoile2.Add(self.etiq_alpha, 0, wx.ALL, 5)
        etoile2.Add(self.etiq_heure_alpha, 0, wx.ALL, 5)
        etoile2.Add(self.edit_heure_alpha, 1, wx.ALL, 5)
        etoile2.Add(self.etiq_minute_alpha, 0, wx.ALL, 5)
        etoile2.Add(self.edit_minute_alpha, 1, wx.ALL, 5)

        etoile3.Add(self.etiq_delta, 0, wx.ALL, 5)
        etoile3.Add(self.etiq_degre_delta, 0, wx.ALL, 5)
        etoile3.Add(self.edit_degre_delta, 1, wx.ALL, 5)
        etoile3.Add(self.etiq_minute_delta, 0, wx.ALL, 5)
        etoile3.Add(self.edit_minute_delta, 1, wx.ALL, 5)
        etoile3.Add(self.br_signe_delta, 1, wx.ALL, 5)

        site1.Add(self.titre_site, 0, wx.ALL, 5)
        site1.Add(self.cb_site, 0, wx.ALL, 5)

        site2.Add(self.etiq_lat, 0, wx.ALL, 5)
        site2.Add(self.etiq_degre_lat, 0, wx.ALL, 5)
        site2.Add(self.edit_degre_lat, 1, wx.ALL, 5)
        site2.Add(self.etiq_minute_lat, 0, wx.ALL, 5)
        site2.Add(self.edit_minute_lat, 1, wx.ALL, 5)
        site2.Add(self.br_signe_lat, 1, wx.ALL, 5)

        site3.Add(self.etiq_long, 0, wx.ALL, 5)
        site3.Add(self.etiq_degre_long, 0, wx.ALL, 5)
        site3.Add(self.edit_degre_long, 1, wx.ALL, 5)
        site3.Add(self.etiq_minute_long, 0, wx.ALL, 5)
        site3.Add(self.edit_minute_long, 1, wx.ALL, 5)
        site3.Add(self.br_signe_long, 1, wx.ALL, 5)

        site4.Add(self.etiq_alt, 0, wx.ALL, 5)
        site4.Add(self.etiq_metre_alt, 0, wx.ALL, 5)
        site4.Add(self.edit_metre_alt, 0, wx.ALL, 5)
        
        temps1.Add(self.titre_temps, 0, wx.ALL, 5)

        temps2.Add(self.etiq_annee, 0, wx.ALL, 5)
        temps2.Add(self.edit_annee, 0, wx.ALL, 5)
        temps2.Add(self.etiq_mois, 0, wx.ALL, 5)
        temps2.Add(self.edit_mois, 0, wx.ALL, 5)
        temps2.Add(self.etiq_jour, 0, wx.ALL, 5)
        temps2.Add(self.edit_jour, 0, wx.ALL, 5)

        temps3.Add(self.etiq_heure, 0, wx.ALL, 5)
        temps3.Add(self.etiq_heure_temps, 0, wx.ALL, 5)
        temps3.Add(self.edit_heure_temps, 1, wx.ALL, 5)
        temps3.Add(self.etiq_minute_temps, 0, wx.ALL, 5)
        temps3.Add(self.edit_minute_temps, 1, wx.ALL, 5)

        critere1.Add(self.titre_critere, 0, wx.ALL, 5)

        critere2.Add(self.etiq_separation, 0, wx.ALL, 5)
        critere2.Add(self.cb_separation, 0, wx.ALL, 5)
        critere2.Add(self.etiq_ecart_bv, 0, wx.ALL, 5)
        critere2.Add(self.cb_ecart_bv, 0, wx.ALL, 5)
        critere2.Add(self.etiq_hauteur_min, 0, wx.ALL, 5)
        critere2.Add(self.edit_hauteur_min, 0, wx.ALL, 5)

        b.Add(self.bouton_calcul, 0, wx.ALL, 5)
        b.Add(self.bouton_arret, 0, wx.ALL, 5)

        vert.Add(etoile1, 0, wx.CENTER)
        vert.Add(etoile2, 0, wx.ALL | wx.EXPAND, 5)
        vert.Add(etoile3, 0, wx.ALL | wx.EXPAND, 5)
        vert.Add(wx.StaticLine(self.panneau_saisie,), 0, wx.ALL | wx.EXPAND, 5)
        vert.Add(site1, 0, wx.CENTER)
        vert.Add(site2, 0, wx.ALL | wx.EXPAND, 5)
        vert.Add(site3, 0, wx.ALL | wx.EXPAND, 5)
        vert.Add(site4, 0, wx.ALL | wx.EXPAND, 5)
        vert.Add(wx.StaticLine(self.panneau_saisie,), 0, wx.ALL | wx.EXPAND, 5)
        vert.Add(temps1, 0, wx.CENTER)
        vert.Add(temps2, 0, wx.ALL | wx.EXPAND, 5)
        vert.Add(temps3, 0, wx.ALL | wx.EXPAND, 5)
        vert.Add(wx.StaticLine(self.panneau_saisie,), 0, wx.ALL | wx.EXPAND, 5)
        vert.Add(critere1, 0, wx.CENTER)
        vert.Add(critere2, 0, wx.ALL | wx.EXPAND, 5)
        vert.Add(wx.StaticLine(self.panneau_saisie,), 0, wx.ALL | wx.EXPAND, 5)
        vert.Add(b, 0, wx.CENTER, 5)

        self.panneau_saisie.SetSizer(vert)
        # self.panneau_saisie.SetAutoLayout(1)
        vert.Fit(self)

        hor.Add(self.panneau_saisie, 0, wx.ALL | wx.EXPAND, 5)
        hor.Add(self.resultat, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(hor)
        hor.Fit(self)

    def affectation_evenements(self):
        self.Bind(wx.EVT_MENU, self.sortie, self.menu_sortie)
        self.Bind(wx.EVT_MENU, self.a_propos, self.menu_apropos)
        self.Bind(wx.EVT_BUTTON, self.calcul, self.bouton_calcul)
        self.Bind(wx.EVT_BUTTON, self.sortie, self.bouton_arret)
        self.Bind(wx.EVT_COMBOBOX, self.lecture_cible, self.cb_cible)
        self.Bind(wx.EVT_TEXT, self.lecture_heure_alpha, self.edit_heure_alpha)
        self.Bind(wx.EVT_TEXT, self.lecture_minute_alpha, self.edit_minute_alpha)
        self.Bind(wx.EVT_TEXT, self.lecture_degre_delta, self.edit_degre_delta)
        self.Bind(wx.EVT_TEXT, self.lecture_minute_delta, self.edit_minute_delta)
        self.Bind(wx.EVT_RADIOBOX, self.lecture_signe_delta, self.br_signe_delta)
        self.Bind(wx.EVT_COMBOBOX, self.lecture_site, self.cb_site)
        self.Bind(wx.EVT_TEXT, self.lecture_degre_lat, self.edit_degre_lat)
        self.Bind(wx.EVT_TEXT, self.lecture_minute_lat, self.edit_minute_lat)
        self.Bind(wx.EVT_RADIOBOX, self.lecture_signe_lat, self.br_signe_lat)
        self.Bind(wx.EVT_TEXT, self.lecture_degre_long, self.edit_degre_long)
        self.Bind(wx.EVT_TEXT, self.lecture_minute_long, self.edit_minute_long)
        self.Bind(wx.EVT_RADIOBOX, self.lecture_signe_long, self.br_signe_long)
        self.Bind(wx.EVT_TEXT, self.lecture_metre_alt, self.edit_metre_alt)
        self.Bind(wx.EVT_TEXT, self.lecture_annee, self.edit_annee)
        self.Bind(wx.EVT_TEXT, self.lecture_mois, self.edit_mois)
        self.Bind(wx.EVT_TEXT, self.lecture_jour, self.edit_jour)
        self.Bind(wx.EVT_TEXT, self.lecture_heure_temps, self.edit_heure_temps)
        self.Bind(wx.EVT_TEXT, self.lecture_minute_temps, self.edit_minute_temps)
        self.Bind(wx.EVT_COMBOBOX, self.lecture_separation, self.cb_separation)
        self.Bind(wx.EVT_COMBOBOX, self.lecture_ecart_bv, self.cb_ecart_bv)
        self.Bind(wx.EVT_TEXT, self.lecture_hauteur_min, self.edit_hauteur_min)

    def lecture_cible(self, evt):
        nom_cible = evt.GetString()
        cible = [element for element in self.cibles if element['Nom'] == nom_cible][0]
        if '---' not in cible['Nom']:
            coord = SkyCoord(cible['Alpha'], cible['Delta'])
            self.edit_heure_alpha.SetValue(str(int(coord.ra.hms[0])))
            self.edit_minute_alpha.SetValue(str(int(coord.ra.hms[1] + coord.ra.signed_dms[2] / 60.0)))
            self.edit_degre_delta.SetValue(str(int(coord.dec.signed_dms[1])))
            self.edit_minute_delta.SetValue(str(int(coord.dec.signed_dms[2] + coord.dec.signed_dms[2] / 60.0)))
            self.br_signe_delta.SetSelection(int((1 - int(coord.dec.signed_dms[0]) / 2)))
            self.signe_delta = int(coord.dec.signed_dms[0])  # Pas d'évènement généré quand on change la sélection d'une radiobox

    def lecture_heure_alpha(self, evt):
        self.heure_alpha = evt.GetString()

    def lecture_minute_alpha(self, evt):
        self.minute_alpha = evt.GetString()

    def lecture_degre_delta(self, evt):
        self.degre_delta = evt.GetString()

    def lecture_minute_delta(self, evt):
        self.minute_delta = evt.GetString()

    def lecture_signe_delta(self, evt):
        self.signe_delta = -2 * evt.GetInt() + 1

    def lecture_site(self, evt):
        nom_obs = evt.GetString()
        obs = [element for element in self.obs if element['Nom'] == nom_obs][0]
        if '---' not in obs['Nom']:
            coord = EarthLocation.from_geodetic(obs['Longitude'], obs['Latitude'], obs['Altitude'])
            self.edit_degre_lat.SetValue(str(int(coord.lat.signed_dms[1])))
            self.edit_minute_lat.SetValue(str(int(coord.lat.signed_dms[2] + coord.lat.signed_dms[3] / 60.0)))
            self.br_signe_lat.SetSelection(int((1 - int(coord.lat.signed_dms[0]) / 2)))
            self.signe_lat = int(coord.lat.signed_dms[0])  # Pas d'évènement généré quand on change la sélection d'une radiobox
            self.edit_degre_long.SetValue(str(int(coord.lon.signed_dms[1])))
            self.edit_minute_long.SetValue(str(int(coord.lon.signed_dms[2] + coord.lon.signed_dms[3] / 60.0)))
            self.br_signe_long.SetSelection(int((1 - int(coord.lon.signed_dms[0]) / 2)))
            self.signe_long = int(coord.lon.signed_dms[0])  # Pas d'évènement généré quand on change la sélection d'une radiobox
            self.edit_metre_alt.SetValue(str(int(coord.height.value + .5)))

    def lecture_degre_lat(self, evt):
        self.degre_lat = evt.GetString()

    def lecture_minute_lat(self, evt):
        self.minute_lat = evt.GetString()

    def lecture_signe_lat(self, evt):
        self.signe_lat = -2 * evt.GetInt() + 1

    def lecture_degre_long(self, evt):
        self.degre_long = evt.GetString()

    def lecture_minute_long(self, evt):
        self.minute_long = evt.GetString()

    def lecture_signe_long(self, evt):
        self.signe_long = -2 * evt.GetInt() + 1

    def lecture_metre_alt(self, evt):
        self.metre_alt = evt.GetString()

    def lecture_annee(self, evt):
        self.annee = evt.GetString()

    def lecture_mois(self, evt):
        self.mois = evt.GetString()

    def lecture_jour(self, evt):
        self.jour = evt.GetString()

    def lecture_heure_temps(self, evt):
        self.heure_temps = evt.GetString()

    def lecture_minute_temps(self, evt):
        self.minute_temps = evt.GetString()

    def lecture_separation(self, evt):
        self.separation_max = evt.GetString()

    def lecture_ecart_bv(self, evt):
        self.ecart_bv_max = evt.GetString()

    def lecture_hauteur_min(self, evt):
        self.hauteur_min = evt.GetString()

    @staticmethod
    def lecture_fichier_csv(nom_fichier):
        try:
            with open(nom_fichier, newline='\n') as csvfile:
                nom_items = list()
                items = list()
                lecteur = csv.DictReader(csvfile, delimiter=',')
                for item in lecteur:
                    nom_items.append(item['Nom'])
                    items.append(item)
            return items, nom_items
        except EnvironmentError as e:
            return None, ['-----']

    def lecture_saisies(self):
        try:
            if int(self.metre_alt) < -400 or int(self.metre_alt) > 8840:
                self.boite_erreur('Altitude invraisemblable')
            else:
                # Récupère les valeurs saisies et détecte éventuellement des impossibilités
                # -- Etoile cible
                if self.signe_delta > 0:
                    alpha_delta = '{0} {1} +{2} {3}'.format(self.heure_alpha, self.minute_alpha, self.degre_delta, self.minute_delta)
                else:
                    alpha_delta = '{0} {1} -{2} {3}'.format(self.heure_alpha, self.minute_alpha, self.degre_delta, self.minute_delta)
                etoile_cible = dict()
                etoile_cible['equat'] = SkyCoord(alpha_delta, unit=(u.hourangle, u.deg))
                etoile_cible['const'] = etoile_cible['equat'].get_constellation(short_name=True)
                # -- Position observatoire
                latitude = Angle((self.signe_lat * int(self.degre_lat), int(self.minute_lat)), unit=u.deg)
                longitude = Angle((self.signe_long * int(self.degre_long), int(self.minute_long)), unit=u.deg)
                altitude = int(self.metre_alt)
                observatoire = EarthLocation.from_geodetic(longitude, latitude, altitude)
                # -- Temps de l'observation
                self.date = datetime.date(int(self.annee), int(self.mois), int(self.jour))
                self.heure = datetime.time(int(self.heure_temps), int(self.minute_temps))
                date_obs = '{0} {1}'.format(self.date, self.heure)
                criteres = {'sep_max': int(self.separation_max),
                            'ecart_bv_max': float(self.ecart_bv_max),
                            'hauteur_min': int(self.hauteur_min)}
                return etoile_cible, observatoire, date_obs, criteres
        except Exception as e:
            self.boite_erreur(str(e))

    def generation_etoile(self, etoile, cible, altaz, criteres):
        try:
            if float(etoile['EB-V']) < 0: 
                etoile['EB-V'] = '0'
            if float(etoile['EB-V']) > criteres['ecart_bv_max']:
                return None
            etoile['equat'] = SkyCoord(etoile['RA_dec'], etoile['de_dec'], unit='deg')
            if not Angle(etoile['de_dec'] + 'd').is_within_bounds(
                    (cible['equat'].dec.degree - criteres['sep_max']) * u.deg,
                    (cible['equat'].dec.degree + criteres['sep_max']) * u.deg):
                return None
            etoile['distance'] = cible['equat'].separation(etoile['equat']).deg
            if etoile['distance'] > criteres['sep_max']:
                return None
            etoile['horiz'] = etoile['equat'].transform_to(altaz)
            if etoile['horiz'].alt.degree < criteres['hauteur_min']:
                return None
            etoile['dhauteur'] = etoile['horiz'].alt - cible['horiz'].alt
        except Exception as e:
            self.boite_erreur(str(e))
            exit(1)

        return etoile

    def generation_liste(self, etoile_cible, altaz, criteres):
        with open(fichier_csv_base, newline='\n') as csvfile:
            base_etoiles = csv.DictReader(csvfile, delimiter=',')
            etoiles = [self.generation_etoile(etoile, etoile_cible, altaz, criteres) for etoile in base_etoiles]
        return etoiles

    @staticmethod
    def formatage_sortie_etoile(num, etoile):
        nom = etoile["Name"]
        separation = '{0:.1f}°'.format(etoile['distance'])
        coords = etoile['equat'].to_string(style='hmsdms', precision=0, fields=2)
        hauteur = '{0:02d}°'.format(round(etoile['horiz'].alt.degree))
        dhauteur = '{0:+.1f}°'.format(etoile['dhauteur'].degree)
        vmag = etoile['V']
        bv = etoile['B-V']
        if bv == '':
            bv = '    '
        ecart_bv = etoile['EB-V']
        if ecart_bv is '':
            ecart_bv = '\t'
        type_spectral = etoile['Sp']
        if etoile['horiz'].alt.degree >= 1:
            decimales = 2
            if etoile['horiz'].secz >= 100:
                decimales = 1
            masse_air = str(round(etoile['horiz'].secz.value, decimales))
        else:
            masse_air = '  '
        miles = etoile['Miles']
        return '{0:02d}  {1}\t{2}\t{3}\t{4}\t{5} Δh={6}\t{7}\t{8}\t{9}\t{10}\t{11}\n'.format(
            num, nom, separation, vmag, coords, hauteur, dhauteur, bv, ecart_bv, type_spectral, masse_air, miles)

    def calcul(self, _):
        # Nettoyage de l'écran des résultats
        self.resultat. Clear()
        # Calcul proprement dit
        etoile_cible, observatoire, date_obs, criteres = self.lecture_saisies()
        altaz = AltAz(obstime=date_obs, location=observatoire, pressure=101300*u.Pa, temperature=10*u.deg_C, relative_humidity=60*u.pct)
        etoile_cible['horiz'] = etoile_cible['equat'].transform_to(altaz)
        self.resultat.AppendText('Cible        : {0} ({1}), altitude={2}, azimuth={3}, masse d\'air={4:.2f}\n'.format(
            etoile_cible['equat'].to_string(style='hmsdms', precision=0, fields=2),
            etoile_cible['const'],
            etoile_cible['horiz'].alt.to_string(sep='dms', fields=1),
            etoile_cible['horiz'].az.to_string(sep='dms', fields=1),
            etoile_cible['horiz'].secz))
        self.resultat.AppendText('Observatoire : lat={0}, lon={1}, alt={2:.0f}, t={3}\n'.format(
            observatoire.lat.to_string(fields=2, precision=0),
            observatoire.lon.to_string(fields=2, precision=0),
            observatoire.height,
            str(date_obs).replace('.000', '')+' UTC'))
        if etoile_cible['horiz'].alt < 0.0:
            self.boite_erreur('Etoile cible sous l\'horizon')
            return
        etoiles = self.generation_liste(etoile_cible, altaz, criteres)
        if not etoiles:
            self.boite_erreur('Erreur dans le fichier de la base de données ou dans son traitement')
            return
        # Sélection des étoiles les plus proches
        selection = []
        for num, etoile in enumerate(etoiles):
            if etoile is not None \
                    and etoile['distance'] <= criteres['sep_max'] \
                    and float(etoile['EB-V']) < criteres['ecart_bv_max']:
                selection.append(etoile)
        # Tri par différence de hauteur :
        selection = sorted(selection, key=lambda item: math.fabs(item['dhauteur'].degree))
        # Sortie des résultats
        self.resultat.AppendText('\n\nNum  Nom\tSép.\tMagV\tCoordonnées\tH. Dif haut\tB-V\tDif B-V\tType\tM. Air\tMiles\n')
        ligne = 1
        for etoile in selection:
            if etoile['Sp'] in type_pickles:
                self.resultat.SetForegroundColour(couleur_resultat_pickles)
            if etoile['Miles']:
                self.resultat.SetForegroundColour(couleur_resultat_miles)
            self.resultat.AppendText(self.formatage_sortie_etoile(ligne, etoile))
            self.resultat.SetForegroundColour(couleur_resultat_defaut)
            ligne += 1

    def a_propos(self, _):
        texte = 'Un outil pour chercher une étoile de référence en spectroscopie\n\n\n' \
                + 'D\'après une idée originale de F. Teyssier et implémentée dans une feuille de calcul \n' \
                + 'Algorithme de recherche copié sur le code de S. Golovanow \n' \
                + '( https://github.com/serge-golovanow/SpectroStars ) \n' \
                + 'Merci à eux deux'
        dlg = wx.MessageDialog(self, texte, 'Chercheur d\'étoiles de référence', wx.OK)
        dlg.ShowModal()  # Mode bloquant
        dlg.Destroy()  #

    def boite_erreur(self, texte):
        dlg = wx.MessageDialog(self, texte, 'Erreur', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def sortie(self, _):
        self.Close(True)  # Sortie propre


app = wx.App(False)
frame = FenetrePrincipale(None, "Chercheur d'étoiles de référence")
app.MainLoop()
