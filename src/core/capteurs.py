# capteurs.py
import random
from datetime import datetime


class CapteurTemperature:
def __init__(self):
self.valeur = 21.0
self.tendance = 0 # -1: baisse, 0: stable, 1: hausse
self.historique = []
self.max_historique = 50
def mettre_a_jour(self, actionneurs=None):
"""Température influencée par le chauffage/climatisation et environnement"""
# Variation naturelle
variation = random.uniform(-0.2, 0.2)
# Influence des actionneurs si fournis
if actionneurs:
if actionneurs.get('chauffage') and actionneurs['chauffage'].etat:
variation += 0.3
if actionneurs.get('climatisation') and actionneurs['climatisation'].etat:
variation -= 0.4
if actionneurs.get('volet') and actionneurs['volet'].position > 50:
variation += 0.1 # Effet de serre avec volets ouverts
# Effet jour/nuit (simulation basique)
heure = datetime.now().hour
if 6 <= heure < 18: # Jour
variation += 0.1
else: # Nuit
variation -= 0.15
# Appliquer la variation
self.valeur = round(max(15, min(35, self.valeur + variation)), 1)
# Mettre à jour la tendance
self._calculer_tendance()
return self.valeur
def _calculer_tendance(self):
"""Calcule la tendance température"""
if len(self.historique) > 1:
derniere_valeur = self.historique[-1]
if self.valeur > derniere_valeur + 0.2:
self.tendance = 1 # Hausse
elif self.valeur < derniere_valeur - 0.2:
self.tendance = -1 # Baisse
else:
self.tendance = 0 # Stable
# Ajouter à l'historique
self.historique.append(self.valeur)
if len(self.historique) > self.max_historique:
self.historique.pop(0)


class CapteurLuminosite:
def __init__(self):
self.valeur = 50
self.cycle_jour = True
self.historique = []
self.max_historique = 50
def mettre_a_jour(self, actionneurs=None):
"""Luminosité influencée par l'heure et les volets"""
heure = datetime.now().hour
# Cycle jour/nuit réaliste
if 6 <= heure < 20: # Jour
base_lum = random.randint(40, 90)
# Variation douce selon l'heure
if 10 <= heure < 16: # Milieu de journée
base_lum = random.randint(70, 95)
elif heure < 10 or heure >= 18: # Matin/soir
base_lum = random.randint(30, 60)
else: # Nuit
base_lum = random.randint(5, 20)
# Effet des volets si fournis
if actionneurs and actionneurs.get('volet'):
position_volet = actionneurs['volet'].position
# Les volets fermés réduisent la luminosité
reduction = (100 - position_volet) / 100
if 6 <= heure < 20: # Seulement le jour
base_lum = int(base_lum * (1 - reduction * 0.8))
# Petites variations aléatoires
variation = random.randint(-5, 5)
self.valeur = max(0, min(100, base_lum + variation))
# Mettre à jour l'historique
self.historique.append(self.valeur)
if len(self.historique) > self.max_historique:
self.historique.pop(0)
return self.valeur


class CapteurPresence:
def __init__(self):
self.valeur = False
self.duree_presence = 0
self.duree_absence = 0
self.probabilite_changement = 0.1
self.dernier_changement = datetime.now()
def mettre_a_jour(self, heure_pointe=False):
"""Détection de présence avec patterns réalistes"""
maintenant = datetime.now()
delai = (maintenant - self.dernier_changement).total_seconds()
# Ajuster la probabilité selon le contexte
proba = self.probabilite_changement
# Heures de pointe (plus de mouvement)
if heure_pointe or (7 <= maintenant.hour < 9 or 17 <= maintenant.hour < 20):
proba *= 1.5
# Si présence actuelle, probabilité de partir
if self.valeur:
# Rester présent entre 5 min et 2 heures
if delai > random.randint(300, 7200): # 5 min à 2 heures
if random.random() < proba:
self.valeur = False
self.dernier_changement = maintenant
self.duree_absence = 0
self.duree_presence = 0
else:
# Rester absent entre 30 min et 8 heures
if delai > random.randint(1800, 28800): # 30 min à 8 heures
if random.random() < proba:
self.valeur = True
self.dernier_changement = maintenant
self.duree_presence = 0
self.duree_absence = 0
# Mettre à jour les durées
if self.valeur:
self.duree_presence += 1
else:
self.duree_absence += 1
return self.valeur


class CapteurEnergie:
def __init__(self):
self.valeur = 0.5
self.consommation_de_base = 0.3
self.historique = []
self.max_historique = 100
self.pics_consommation = []
def mettre_a_jour(self, actionneurs=None):
"""Calcule la consommation basée sur les actionneurs"""
consommation = self.consommation_de_base
# Ajouter consommation des actionneurs si fournis
if actionneurs:
for nom, actionneur in actionneurs.items():
if hasattr(actionneur, 'get_consommation'):
consommation += actionneur.get_consommation()
# Variations aléatoires mineures
variation = random.uniform(-0.05, 0.05)
self.valeur = round(max(0.1, consommation + variation), 2)
# Détection de pics de consommation
self._detecter_pics()
# Mettre à jour l'historique
self.historique.append(self.valeur)
if len(self.historique) > self.max_historique:
self.historique.pop(0)
return self.valeur
def _detecter_pics(self):
"""Détecte les pics de consommation anormaux"""
if len(self.historique) > 10:
moyenne = sum(self.historique[-10:]) / 10
if self.valeur > moyenne * 1.5: # Pic de +50%
pic = {
'timestamp': datetime.now(),
'valeur': self.valeur,
'seuil': moyenne
}
self.pics_consommation.append(pic)
# Garder seulement les 10 derniers pics
if len(self.pics_consommation) > 10:
self.pics_consommation.pop(0)


class CapteurHumidite:
def __init__(self):
self.valeur = 45.0 # Pourcentage d'humidité
self.historique = []
self.max_historique = 50
def mettre_a_jour(self, actionneurs=None):
"""Humidité relative avec variations réalistes"""
# Base selon la saison (simulée)
heure = datetime.now().hour
mois = datetime.now().month
# Saison simulée : hiver (décembre-février) vs été (juin-août)
if mois in [12, 1, 2]: # Hiver
base_humidite = random.uniform(30, 60)
elif mois in [6, 7, 8]: # Été
base_humidite = random.uniform(40, 80)
else: # Printemps/Automne
base_humidite = random.uniform(35, 70)
# Variation jour/nuit
if 6 <= heure < 18:
base_humidite -= 5 # Plus sec le jour
else:
base_humidite += 5 # Plus humide la nuit
# Effet de la climatisation (assèche l'air)
if actionneurs and actionneurs.get('climatisation') and actionneurs['climatisation'].etat:
base_humidite -= 10
self.valeur = round(max(20, min(90, base_humidite)), 1)
# Historique
self.historique.append(self.valeur)
if len(self.historique) > self.max_historique:
self.historique.pop(0)
return self.valeur


class CapteurQualiteAir:
def __init__(self):
self.co2 = 400 # ppm
self.tvoc = 50 # ppb
self.qualite = "Bonne"
self.historique = []
self.max_historique = 50
def mettre_a_jour(self, presence=False):
"""Qualité de l'air influencée par la présence et la ventilation"""
# Base selon l'occupation
if presence:
self.co2 += random.randint(5, 20)
self.tvoc += random.randint(1, 5)
else:
self.co2 = max(400, self.co2 - random.randint(1, 10))
self.tvoc = max(10, self.tvoc - random.randint(1, 3))
# Limites réalistes
self.co2 = min(2000, self.co2)
self.tvoc = min(500, self.tvoc)
# Déterminer la qualité
if self.co2 < 800 and self.tvoc < 100:
self.qualite = "Excellente"
elif self.co2 < 1200 and self.tvoc < 200:
self.qualite = "Bonne"
elif self.co2 < 1500 and self.tvoc < 300:
self.qualite = "Moyenne"
else:
self.qualite = "Mauvaise"
# Historique
self.historique.append({
'co2': self.co2,
'tvoc': self.tvoc,
'qualite': self.qualite,
'timestamp': datetime.now()
})
if len(self.historique) > self.max_historique:
self.historique.pop(0)
return {
'co2': self.co2,
'tvoc': self.tvoc,
'qualite': self.qualite
}


# Test des capteurs
if __name__ == "__main__":
print("🧪 Test des capteurs...")
# Créer des instances
temp = CapteurTemperature()
lum = CapteurLuminosite()
presence = CapteurPresence()
energie = CapteurEnergie()
humidite = CapteurHumidite()
air = CapteurQualiteAir()
# Simuler quelques mises à jour
for i in range(5):
print(f"\n--- Cycle {i+1} ---")
print(f"🌡️ Température: {temp.mettre_a_jour()}°C (Tendance: {temp.tendance})")
print(f"💡 Luminosité: {lum.mettre_a_jour()}%")
print(f"👤 Présence: {presence.mettre_a_jour()}")
print(f"⚡ Énergie: {energie.mettre_a_jour()} kWh")
print(f"💧 Humidité: {humidite.mettre_a_jour()}%")
qualite_air = air.mettre_a_jour(presence.valeur)
print(f"🌫️ Qualité air: {qualite_air['qualite']} (CO2: {qualite_air['co2']} ppm)")



