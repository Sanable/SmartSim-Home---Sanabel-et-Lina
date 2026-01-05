# actionneurs.py
import time
from datetime import datetime


class Actionneur:
"""Classe de base pour tous les actionneurs"""
def __init__(self, nom, consommation):
self.nom = nom
self.consommation = consommation
self.etat = False
self.historique_etat = []
self.dernier_changement = datetime.now()
def ajouter_historique(self, action):
timestamp = datetime.now().strftime("%H:%M:%S")
self.historique_etat.append(f"{timestamp} - {action}")
if len(self.historique_etat) > 10:
self.historique_etat.pop(0)
def get_consommation(self):
return self.consommation if self.etat else 0.0
def get_statut(self):
return "ON" if self.etat else "OFF"


class Chauffage(Actionneur):
def __init__(self):
super().__init__("Chauffage", 1.5)
self.temperature_cible = 21.0
self.mode = "auto" # auto, manuel, eco
def activer(self):
self.etat = True
self.ajouter_historique("Chauffage activé")
def desactiver(self):
self.etat = False
self.ajouter_historique("Chauffage désactivé")
def toggle(self):
if self.etat:
self.desactiver()
else:
self.activer()
def regler_temperature(self, temperature):
if 15 <= temperature <= 28:
self.temperature_cible = temperature
self.ajouter_historique(f"Température réglée à {temperature}°C")
return True
return False
def set_mode(self, mode):
if mode in ["auto", "manuel", "eco"]:
self.mode = mode
self.ajouter_historique(f"Mode changé à {mode}")
if mode == "eco":
self.consommation = 1.0 # Consommation réduite en mode eco


class Eclairage(Actionneur):
def __init__(self):
super().__init__("Éclairage", 0.3)
self.intensite = 100 # %
self.couleur = "blanc" # blanc, chaud, froid
self.auto_off = False
def activer(self):
self.etat = True
self.ajouter_historique("Éclairage activé")
def desactiver(self):
self.etat = False
self.ajouter_historique("Éclairage désactivé")
def toggle(self):
if self.etat:
self.desactiver()
else:
self.activer()
def regler_intensite(self, intensite):
if 0 <= intensite <= 100:
self.intensite = intensite
self.consommation = 0.3 * (intensite / 100) # Consommation proportionnelle
self.ajouter_historique(f"Intensité réglée à {intensite}%")
def set_couleur(self, couleur):
if couleur in ["blanc", "chaud", "froid"]:
self.couleur = couleur
self.ajouter_historique(f"Couleur changée à {couleur}")


class SystemeSecurite(Actionneur):
def __init__(self):
super().__init__("Sécurité", 0.1)
self.etat = True # Activé par défaut
self.alarme_active = False
self.capteurs = [] # Liste des capteurs surveillés
def activer(self):
self.etat = True
self.ajouter_historique("Sécurité activée")
def desactiver(self):
self.etat = False
self.ajouter_historique("Sécurité désactivée")
def toggle(self):
if self.etat:
self.desactiver()
else:
self.activer()
def declencher_alarme(self):
if self.etat and not self.alarme_active:
self.alarme_active = True
self.ajouter_historique("ALARME DÉCLENCHÉE!")
return True
return False
def arreter_alarme(self):
if self.alarme_active:
self.alarme_active = False
self.ajouter_historique("Alarme arrêtée")
def ajouter_capteur(self, capteur):
self.capteurs.append(capteur)


class Climatisation(Actionneur):
def __init__(self):
super().__init__("Climatisation", 2.0)
self.temperature_cible = 22.0
self.mode = "auto" # auto, dry, fan
self.vitesse_ventilateur = "auto" # auto, faible, moyen, fort
def activer(self):
self.etat = True
self.ajouter_historique("Climatisation activée")
def desactiver(self):
self.etat = False
self.ajouter_historique("Climatisation désactivée")
def toggle(self):
if self.etat:
self.desactiver()
else:
self.activer()
def regler_temperature(self, temperature):
if 18 <= temperature <= 26:
self.temperature_cible = temperature
self.ajouter_historique(f"Température réglée à {temperature}°C")
return True
return False
def set_mode(self, mode):
if mode in ["auto", "dry", "fan"]:
self.mode = mode
self.ajouter_historique(f"Mode changé à {mode}")
def set_vitesse_ventilateur(self, vitesse):
if vitesse in ["auto", "faible", "moyen", "fort"]:
self.vitesse_ventilateur = vitesse
# Ajuster consommation selon vitesse
if vitesse == "fort":
self.consommation = 2.5
elif vitesse == "moyen":
self.consommation = 2.0
elif vitesse == "faible":
self.consommation = 1.5
else:
self.consommation = 2.0


class Volet:
def __init__(self):
self.nom = "Volet"
self.position = 0
self.consommation = 0.05
self.consommation_mouvement = 0.1
self.historique_positions = []
self.dernier_mouvement = None
def regler_position(self, pos):
if 0 <= pos <= 100:
ancienne_position = self.position
self.position = pos
self.dernier_mouvement = datetime.now()
# Calculer la consommation du mouvement
mouvement = abs(pos - ancienne_position)
consommation_mvt = self.consommation_mouvement * (mouvement / 100)
self.ajouter_historique(f"Position réglée à {pos}%")
return consommation_mvt
return 0.0
def fermer(self):
return self.regler_position(0)
def ouvrir(self):
return self.regler_position(100)
def get_consommation(self):
return self.consommation # Consommation statique
def ajouter_historique(self, action):
timestamp = datetime.now().strftime("%H:%M:%S")
self.historique_positions.append(f"{timestamp} - {action}")
if len(self.historique_positions) > 10:
self.historique_positions.pop(0)


class PriseIntelligente(Actionneur):
def __init__(self, nom="Prise intelligente"):
super().__init__(nom, 0.02)
self.consommation_appareil = 0.0
self.appareil_connecte = "Aucun"
self.programmation = [] # Programmes horaires
def activer(self):
self.etat = True
self.ajouter_historique("Prise activée")
def desactiver(self):
self.etat = False
self.ajouter_historique("Prise désactivée")
def toggle(self):
if self.etat:
self.desactiver()
else:
self.activer()
def connecter_appareil(self, appareil, consommation):
self.appareil_connecte = appareil
self.consommation_appareil = consommation
self.ajouter_historique(f"Appareil connecté: {appareil}")
def get_consommation(self):
return self.consommation + (self.consommation_appareil if self.etat else 0.0)
def ajouter_programme(self, heure, action):
self.programmation.append({"heure": heure, "action": action})
self.ajouter_historique(f"Programme ajouté: {action} à {heure}")


# Test des actionneurs
if __name__ == "__main__":
print("🔧 Test des actionneurs...")
chauffage = Chauffage()
eclairage = Eclairage()
securite = SystemeSecurite()
chauffage.activer()
eclairage.regler_intensite(75)
securite.desactiver()
print(f"Chauffage: {chauffage.get_statut()}")
print(f"Éclairage: {eclairage.get_statut()} ({eclairage.intensite}%)")
print(f"Sécurité: {securite.get_statut()}")



