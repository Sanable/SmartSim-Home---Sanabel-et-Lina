"""
Module principal de la maison intelligente - Version corrigée
"""


import time
from datetime import datetime
from .capteurs import CapteurTemperature, CapteurLuminosite, CapteurPresence, CapteurEnergie, CapteurHumidite, CapteurQualiteAir
from .actionneurs import Chauffage, Eclairage, SystemeSecurite, Climatisation, Volet, PriseIntelligente


class MaisonIntelligente:
def __init__(self):
print("🏠 Initialisation de la maison intelligente...")
# Capteurs
self.capteurs = {
'temperature': CapteurTemperature(),
'luminosite': CapteurLuminosite(),
'presence': CapteurPresence(),
'energie': CapteurEnergie(),
'humidite': CapteurHumidite(),
'qualite_air': CapteurQualiteAir()
}
# Actionneurs
self.actionneurs = {
'chauffage': Chauffage(),
'eclairage': Eclairage(),
'securite': SystemeSecurite(),
'climatisation': Climatisation(),
'volet': Volet(),
'prise_salon': PriseIntelligente("Prise Salon")
}


# Modes
self.mode_vacances = False
self.mode_automatique = True
self.mode_eco = False


# Historique
self.historique_actions = []
self.historique_temperature = []
self.historique_energie = []
# Programmation horaire
self.programmes = {
'reveil': {'heure': "07:00", 'actions': ['chauffage_on', 'volets_ouvrir']},
'nuit': {'heure': "23:00", 'actions': ['tout_eteindre', 'securite_on']}
}


print("Maison prête ✔️")


# -------------------------
# Mise à jour des capteurs
# -------------------------
def mettre_a_jour_capteurs(self):
presence = self.capteurs['presence'].valeur


self.capteurs['temperature'].mettre_a_jour(self.actionneurs)
self.capteurs['luminosite'].mettre_a_jour(self.actionneurs)
self.capteurs['presence'].mettre_a_jour(heure_pointe=self._est_heure_pointe())
self.capteurs['energie'].mettre_a_jour(self.actionneurs)
self.capteurs['humidite'].mettre_a_jour(self.actionneurs)
self.capteurs['qualite_air'].mettre_a_jour(presence)


def _est_heure_pointe(self):
heure = datetime.now().hour
return (7 <= heure < 9) or (17 <= heure < 20)


# -------------------------
# Automatisation
# -------------------------
def automatiser_actions(self):
if not self.mode_automatique:
return


# Mode vacances
if self.mode_vacances:
self._appliquer_mode_vacances()
return


# Mode éco
if self.mode_eco:
self._appliquer_mode_eco()
return


# Mode normal
presence = self.capteurs['presence'].valeur
temperature = self.capteurs['temperature'].valeur
luminosite = self.capteurs['luminosite'].valeur
heure = datetime.now().hour


if presence:
self._scenario_occupation(temperature, luminosite, heure)
else:
self._scenario_absence()


self._optimisation_energetique()
self._gestion_qualite_air()
self._executer_programmes_horaires()


# -------------------------
# Modes
# -------------------------
def _appliquer_mode_vacances(self):
self.actionneurs['chauffage'].desactiver()
self.actionneurs['eclairage'].desactiver()
self.actionneurs['climatisation'].desactiver()
self.actionneurs['securite'].activer()
self.actionneurs['volet'].fermer()


def _appliquer_mode_eco(self):
temperature = self.capteurs['temperature'].valeur


if temperature > 19:
self.actionneurs['chauffage'].desactiver()
if temperature < 26:
self.actionneurs['climatisation'].desactiver()
if self.actionneurs['eclairage'].etat:
self.actionneurs['eclairage'].regler_intensite(70)


# -------------------------
# Scénarios occupation / absence
# -------------------------
def _scenario_occupation(self, temperature, luminosite, heure):
# Chauffage / clim
if temperature < 20:
self.actionneurs['chauffage'].activer()
self.actionneurs['climatisation'].desactiver()
elif temperature > 25:
self.actionneurs['chauffage'].desactiver()
self.actionneurs['climatisation'].activer()
else:
self.actionneurs['chauffage'].desactiver()
self.actionneurs['climatisation'].desactiver()


# Lumière
if luminosite < 40:
self.actionneurs['eclairage'].activer()
else:
self.actionneurs['eclairage'].desactiver()


# Volets
if luminosite > 80:
self.actionneurs['volet'].regler_position(70)
elif luminosite > 60:
self.actionneurs['volet'].regler_position(50)
else:
self.actionneurs['volet'].regler_position(80)


self.actionneurs['securite'].desactiver()


def _scenario_absence(self):
self.actionneurs['eclairage'].desactiver()
self.actionneurs['securite'].activer()
self.actionneurs['volet'].fermer()
self.actionneurs['chauffage'].desactiver()
self.actionneurs['climatisation'].desactiver()


# -------------------------
# Fonctions annexes
# -------------------------
def _optimisation_energetique(self):
conso = self.calculer_consommation_totale()
if conso > 5:
self.actionneurs['prise_salon'].desactiver()


def _gestion_qualite_air(self):
qa = self.capteurs['qualite_air']
if qa.qualite == "Mauvaise":
if not self.actionneurs['securite'].etat:
self.actionneurs['volet'].regler_position(80)


# -------------------------
# Programmation horaire
# -------------------------
def _executer_programmes_horaires(self):
maintenant = datetime.now().strftime("%H:%M")


for nom, programme in self.programmes.items():
if programme['heure'] == maintenant:
self._executer_actions_programme(programme['actions'])


def _executer_actions_programme(self, actions):
for action in actions:
if action == 'chauffage_on':
self.actionneurs['chauffage'].activer()
elif action == 'tout_eteindre':
for a in ['chauffage', 'eclairage', 'climatisation']:
self.actionneurs[a].desactiver()
elif action == 'securite_on':
self.actionneurs['securite'].activer()
elif action == 'volets_ouvrir':
self.actionneurs['volet'].ouvrir()


# -------------------------
# Méthodes manquantes ajoutées
# -------------------------
def ajouter_historique(self, action):
"""Ajoute une action à l'historique"""
timestamp = datetime.now().strftime("%H:%M:%S")
self.historique_actions.append(f"{timestamp} - {action}")
if len(self.historique_actions) > 50:
self.historique_actions.pop(0)


def set_mode_eco(self, actif):
"""Active/désactive le mode éco"""
self.mode_eco = actif
if actif:
self.ajouter_historique("🌱 Mode éco activé")
else:
self.ajouter_historique("🌱 Mode éco désactivé")


# -------------------------
# Consultation état
# -------------------------
def calculer_consommation_totale(self):
total = sum(a.get_consommation() for a in self.actionneurs.values())
total += self.capteurs['energie'].valeur
return total


def get_etat_maison(self):
etat = {
'capteurs': {
'temperature': self.capteurs['temperature'].valeur,
'luminosite': self.capteurs['luminosite'].valeur,
'presence': self.capteurs['presence'].valeur,
'energie': self.capteurs['energie'].valeur,
'humidite': self.capteurs['humidite'].valeur,
'qualite_air': self.capteurs['qualite_air'].qualite,
'co2': self.capteurs['qualite_air'].co2
},
'actionneurs': {
'chauffage': self.actionneurs['chauffage'].etat,
'eclairage': self.actionneurs['eclairage'].etat,
'securite': self.actionneurs['securite'].etat,
'climatisation': self.actionneurs['climatisation'].etat,
'volet': self.actionneurs['volet'].position,
'prise_salon': self.actionneurs['prise_salon'].etat
},
'modes': {
'vacances': self.mode_vacances,
'automatique': self.mode_automatique,
'eco': self.mode_eco
},
'statistiques': {
'consommation_totale': self.calculer_consommation_totale(),
'duree_fonctionnement': f"{len(self.historique_actions)} cycles"
}
}
# Mettre à jour les historiques
self.historique_temperature.append({
'temperature': etat['capteurs']['temperature'],
'timestamp': datetime.now().strftime("%H:%M")
})
if len(self.historique_temperature) > 100:
self.historique_temperature.pop(0)
self.historique_energie.append({
'consommation': etat['statistiques']['consommation_totale'],
'timestamp': datetime.now().strftime("%H:%M")
})
if len(self.historique_energie) > 100:
self.historique_energie.pop(0)
return etat


def get_etat_api(self):
return {
'sensors': self.get_etat_maison()['capteurs'],
'devices': self.get_etat_maison()['actionneurs'],
'modes': self.get_etat_maison()['modes'],
'history': self.historique_actions[-10:] # 10 dernières actions
}



