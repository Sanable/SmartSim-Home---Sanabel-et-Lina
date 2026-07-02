import threading
import time
import webbrowser
import json
import random
import pyttsx3
import ollama
from http.server import HTTPServer, BaseHTTPRequestHandler
from assistant.connaissances import CONNAISSANCES_IA

class MaisonIntelligente:
    def __init__(self):
        print("🏠 Initialisation de la maison intelligente...")
        self.generer_alerte_vocale(
            "Bonjour. La simulation de la maison intelligente est démarrée."
        )


        self.capteurs = {
            "temperature": type("Capteur", (), {"valeur": 21.5})(),
            "luminosite": type("Capteur", (), {"valeur": 65})(),
            "presence": type("Capteur", (), {"valeur": True})(),
            "energie": type("Capteur", (), {"valeur": 1.8})(),
            "humidite": type("Capteur", (), {"valeur": 45})(),
            "qualite_air": type("Capteur", (), {"qualite": "Bonne", "co2": 450})(),
            "monoxyde_carbone": type("Capteur", (), {"valeur": 5})(),

        }

        self.actionneurs = {
            "eclairage": type("Actionneur", (), {"etat": False, "intensite": 0})(),  
            "chauffage": type("Actionneur", (), {"etat": False, "temperature_cible": 21})(),
            "climatisation": type("Actionneur", (), {"etat": False, "temperature_cible": 22})(),
            "securite": type("Actionneur", (), {"etat": True})(),
            "volet": type("Actionneur", (), {"position": 50})(),
            "prise_salon": type("Actionneur", (), {"etat": False})(),
        }

        self.modes = {"vacances": False, "automatique": True, "eco": False,"simulation_co": False,"alarme":False}
        self.alarme_auto_active = False
        print("DEBUG modes init:", self.modes)
        self.alertes = []
        self.derniere_alerte_co = 0
        self.historique = ["Système démarré"]
        self.regles = []  
        self.regle_id = 1  
        self.derniere_modification = time.time()
        

        print("✅ Maison initialisée avec valeurs stables"),
    def mettre_a_jour_capteurs(self):
        """Mise à jour très lente des capteurs"""
      
        if self.modes.get("simulation_co"):
            self.capteurs["monoxyde_carbone"].valeur = 300
            self.automatiser_actions()
            return
        current_time = time.time()
        
        if current_time - self.derniere_modification > 60:
            temp_variation = random.uniform(-0.1, 0.1)
            self.capteurs["temperature"].valeur = round(
                self.capteurs["temperature"].valeur + temp_variation, 1
            )

            lum_variation = random.randint(-2, 2)
            new_lum = self.capteurs["luminosite"].valeur + lum_variation
            self.capteurs["luminosite"].valeur = max(0, min(100, new_lum))

            
            hum_variation = random.uniform(-1, 1)
            new_hum = self.capteurs["humidite"].valeur + hum_variation
            self.capteurs["humidite"].valeur = round(max(30, min(70, new_hum)), 1)

           
            if random.random() < 0.98:
                self.capteurs["monoxyde_carbone"].valeur = max(
                    0,
                    self.capteurs["monoxyde_carbone"].valeur - 1
                )
            else:
                self.capteurs["monoxyde_carbone"].valeur = random.choice([20, 40, 250])


            self.derniere_modification = current_time
    
    def automatiser_actions(self):
        """Automatisation + sécurité vitale"""

        co = float(self.capteurs["monoxyde_carbone"].valeur)

        if co < 200 and self.modes.get("alarme") and self.alarme_auto_active:
          self.modes["alarme"] = False
          self.alarme_auto_active = False
          self.historique.append("✅ ALARME désactivée automatiquement (CO revenu < 200 ppm)")
        if co >= 200:
           
            print("DEBUG modes runtime:", self.modes)
            if not self.modes["alarme"]:
               self.modes["alarme"] = True
               self.historique.append("🚨 ALARME activée automatiquement (CO > 200 ppm)")
            self.actionneurs["chauffage"].etat = False
            self.actionneurs["climatisation"].etat = False
            self.actionneurs["prise_salon"].etat = False
            if not self.modes["alarme"]:
                self.modes["alarme"] = True
                self.alarme_auto_active = True
                self.historique.append("🚨 ALARME activée automatiquement (CO > 200 ppm)")
           
            self.actionneurs["volet"].position = 100
                
            self.actionneurs["eclairage"].etat = True
            self.actionneurs["eclairage"].intensite = 100
            current_time = time.time()
            if current_time - self.derniere_alerte_co > 60:
               alerte_msg = f"🛑 ALERTE CO: {co} ppm détecté ! Danger immédiat."
               self.alertes.append({
                "type": "co_critique",
                "message": alerte_msg,
                "timestamp": current_time,
                "valeur": co
            })
               self.derniere_alerte_co = current_time
               self.historique.append(alerte_msg)
              

               self.generer_alerte_vocale(alerte_msg)
            
               self.actionneurs["eclairage"].etat = True
               self.actionneurs["eclairage"].intensite = 100
  
            
               self.historique.append(
                "🛑 ALERTE CO CRITIQUE : Gaz mortel détecté ! "
                "Ouvrez immédiatement les fenêtres, sortez et appelez les pompiers (18 / 112)."
            )
            return
        self.appliquer_regles()
        if self.modes["vacances"]:
            self._appliquer_mode_vacances()
            return

        if self.modes["eco"]:
           self._appliquer_mode_eco()
           return  
        if self.modes["automatique"]:
            self._automatisation_normale()
             
        


    def _appliquer_mode_vacances(self):
        """Mode vacances : sécurité activée, tout le reste éteint"""
        self.actionneurs["eclairage"].etat = False
        self.actionneurs["eclairage"].intensite = 0
        self.actionneurs["chauffage"].etat = False
        self.actionneurs["climatisation"].etat = False
        self.actionneurs["securite"].etat = True
        self.actionneurs["volet"].position = 0
        self.actionneurs["prise_salon"].etat = False

    def _appliquer_mode_eco(self):
         """Mode éco : vraies économies (prioritaire après l'automatique)."""
         presence = self.capteurs["presence"].valeur
         luminosite = self.capteurs["luminosite"].valeur
         temperature = self.capteurs["temperature"].valeur
        
         if temperature >= 18:
          self.actionneurs["chauffage"].etat = False
        
         if temperature <= 27:
            self.actionneurs["climatisation"].etat = False
       
         self.actionneurs["prise_salon"].etat = False
         
         if temperature < 18:
            self.actionneurs["chauffage"].etat = True
         if temperature > 27:
            self.actionneurs["climatisation"].etat = True
        
         if self.actionneurs["eclairage"].etat:
            
            if self.actionneurs["eclairage"].intensite > 35:
               self.actionneurs["eclairage"].intensite = 35

         if presence and luminosite < 40:
           
               self.actionneurs["volet"].position = max(self.actionneurs["volet"].position, 80)

          
               self.actionneurs["eclairage"].intensite = min(self.actionneurs["eclairage"].intensite, 35)


         if not presence:
            self.actionneurs["eclairage"].etat = False
            self.actionneurs["eclairage"].intensite = 0
            self.actionneurs["chauffage"].etat = False
            self.actionneurs["climatisation"].etat = False
            self.actionneurs["prise_salon"].etat = False
    def _automatisation_normale(self):
        """Automatisation basée sur présence et conditions"""
        presence = self.capteurs["presence"].valeur
        luminosite = self.capteurs["luminosite"].valeur
        temperature = self.capteurs["temperature"].valeur

      
        if presence:
            if luminosite < 40:
                self.actionneurs["eclairage"].etat = True
                self.actionneurs["eclairage"].intensite = min(100, 100 - luminosite)
            else:
                self.actionneurs["eclairage"].etat = False
                self.actionneurs["eclairage"].intensite = 0
        else:
            self.actionneurs["eclairage"].etat = False
            self.actionneurs["eclairage"].intensite = 0

       
        if presence:
            if temperature < 19:
                self.actionneurs["chauffage"].etat = True
                self.actionneurs["climatisation"].etat = False
            elif temperature > 25:
                self.actionneurs["chauffage"].etat = False
                self.actionneurs["climatisation"].etat = True
            else:
                self.actionneurs["chauffage"].etat = False
                self.actionneurs["climatisation"].etat = False
        else:
            self.actionneurs["chauffage"].etat = False
            self.actionneurs["climatisation"].etat = False

     
        if presence:
            if luminosite > 80:
                self.actionneurs["volet"].position = 30
            elif luminosite < 30:
                self.actionneurs["volet"].position = 80
            else:
                self.actionneurs["volet"].position = 50
        else:
            self.actionneurs["volet"].position = 20

       
        self.actionneurs["securite"].etat = not presence

     
        self.actionneurs["prise_salon"].etat = presence

    def ajouter_regle(self, condition: dict, actions: list, nom: str = ""):
        """
        condition ex:
          {"sensor":"temperature","op":"<","value":18}
           actions ex:
           [{"type":"toggle_actionneur","nom":"chauffage","etat":True}]
           [{"type":"set_mode","mode":"eco","value":True}]
           [{"type":"set_volet","position":80}]
         """
        rid = self.regle_id
        self.regle_id += 1

        regle = {
            "id": rid,
            "nom": nom or f"Règle {rid}",
            "enabled": True,
            "condition":condition,
            "actions":actions,
        }
        self.regles.append(regle)
        self.historique.append(f"📌 Règle ajoutée: {regle['nom']} (id={rid})")
        return regle

    def supprimer_regle(self, regle_id: int):
        before = len(self.regles)
        self.regles = [r for r in self.regles if r["id"] != regle_id]
        after = len(self.regles)
        if after < before:
            self.historique.append(f"🗑️ Règle supprimée (id={regle_id})")
            return True
        return False

    def _condition_ok(self, cond: dict) -> bool:
        """
        Supporte capteurs:
          temperature, luminosite, presence, humidite, monoxyde_carbone
        Ops: ==, !=, <, <=, >, >=
        """
        sensor = cond.get("sensor")
        op = cond.get("op")
        value = cond.get("value")

        if sensor not in self.capteurs:
            return False

       
        v = getattr(self.capteurs[sensor], "valeur", None)
        if v is None:
            return False

      
        if sensor == "presence":
            v = bool(v)
            value = bool(value)
        else:
            try:
                v = float(v)
                value = float(value)
            except:
                return False

        if op == "==": return v == value
        if op == "!=": return v != value
        if op == "<":  return v < value
        if op == "<=": return v <= value
        if op == ">":  return v > value
        if op == ">=": return v >= value
        return False

    def _appliquer_actions_regle(self, actions: list):
        for a in actions:
            t = a.get("type")

            if t == "toggle_actionneur":
                nom = a.get("nom")
                etat = a.get("etat")
                if nom in self.actionneurs and etat is not None:
                    self.modifier_actionneur(nom, etat=bool(etat))

            elif t == "set_mode":
                mode = a.get("mode")
                val = a.get("value")
                if mode in self.modes:
                    self.modifier_mode(mode, bool(val))

            elif t == "set_volet":
                pos = a.get("position")
                if pos is not None:
                    self.modifier_actionneur("volet", valeur=int(pos))

    def appliquer_regles(self):
        """
        Exécutée à chaque boucle: si condition vraie -> actions.
        Anti-spam: si une règle se déclenche, on log 1 fois, et on ne relance
        pas en boucle si l'état n'a pas changé (simple).
        """
       
        if not hasattr(self, "_regles_last_fire"):
            self._regles_last_fire = {}

        for r in self.regles:
            if not r.get("enabled", True):
                continue

            ok = self._condition_ok(r.get("condition", {}))
            rid = r["id"]

           
            prev = self._regles_last_fire.get(rid, False)
            if ok and not prev:
                self.historique.append(f"✅ Règle déclenchée: {r['nom']} (id={rid})")
                self._appliquer_actions_regle(r.get("actions", []))
                self._regles_last_fire[rid] = True
            elif not ok and prev:
                self._regles_last_fire[rid] = False

    def get_etat_maison(self):
        """Retourne l'état complet de la maison"""
        return {
            "sensors": {
                "temperature": self.capteurs["temperature"].valeur,
                "luminosite": self.capteurs["luminosite"].valeur,
                "presence": self.capteurs["presence"].valeur,
                "energy": self._calculer_consommation(),
                "humidite": self.capteurs["humidite"].valeur,
                "qualite_air": self.capteurs["qualite_air"].qualite,
                "co2": self.capteurs["qualite_air"].co2,
                "monoxyde_carbone": self.capteurs["monoxyde_carbone"].valeur,
            },
            "devices": {  # frontend attend "devices"
                "eclairage": self.actionneurs["eclairage"].etat,
                "chauffage": self.actionneurs["chauffage"].etat,
                "climatisation": self.actionneurs["climatisation"].etat,
                "securite": self.actionneurs["securite"].etat,
                "volet": self.actionneurs["volet"].position,
                "prise_salon": self.actionneurs["prise_salon"].etat,
            },
            "modes": self.modes,
            "alertes": self.alertes[-5:],          
           "historique": self.historique[-10:],  
        }

    def _calculer_consommation(self):
        """Calcule la consommation énergétique totale"""
        consommation = 0.5  
        if self.actionneurs["eclairage"].etat:
            consommation += 0.3 * (self.actionneurs["eclairage"].intensite / 100)
        if self.actionneurs["chauffage"].etat:
            consommation += 1.5
        if self.actionneurs["climatisation"].etat:
            consommation += 2.0
        if self.actionneurs["prise_salon"].etat:
            consommation += 0.8
        return round(consommation, 2)

    def modifier_capteur(self, capteur, valeur): 
        """Modifie un capteur manuellement (sauf humidité qui est en lecture seule)"""
        try:
            if capteur == "humidite":
                return False, "L'humidité est en lecture seule"

            if capteur not in self.capteurs:
                return False, f"Capteur inconnu : {capteur}"

            old_value = getattr(self.capteurs[capteur], "valeur", None)

            if capteur == "temperature":
                new_value = float(valeur)
                if 15 <= new_value <= 30:
                    self.capteurs["temperature"].valeur = new_value
                    self.historique.append(
                        f"🌡️ Température: {old_value} → {new_value}°C"
                    )
                else:
                    return False, "Température hors limites (15-30°C)"

            elif capteur == "luminosite":
                new_value = int(valeur)
                if 0 <= new_value <= 100:
                    self.capteurs["luminosite"].valeur = new_value
                    self.historique.append(
                        f"💡 Luminosité: {old_value} → {new_value}%"
                    )
                else:
                    return False, "Luminosité hors limites (0-100%)"

            elif capteur == "presence":
                new_value = str(valeur).lower() in [
                    "true", "1", "yes", "on", "vrai", "oui"
                ]
                self.capteurs["presence"].valeur = new_value
                etat = "PRÉSENT" if new_value else "ABSENT"
                self.historique.append(f"👤 Présence: {etat}")

            elif capteur == "energie":
                new_value = float(valeur)
                if new_value >= 0:
                    self.capteurs["energie"].valeur = new_value
                    self.historique.append(
                        f"⚡ Consommation: {old_value} → {new_value}kWh"
                    )
                else:
                    return False, "Consommation négative impossible"
            
           
            elif capteur == "monoxyde_carbone":
                new_value = float(valeur)
                if new_value >= 0:
                    self.capteurs["monoxyde_carbone"].valeur = new_value
                    self.historique.append(
                        f"⚠️ CO: {old_value} → {new_value} ppm"
                    )
                else:
                    return False, "Valeur CO négative impossible"

            self.derniere_modification = time.time()
            self.automatiser_actions()
            return True, "Capteur modifié avec succès"

        except Exception as e:
            print(f"❌ Erreur modification {capteur}: {e}")
            return False, f"Erreur: {str(e)}"


    def modifier_actionneur(self, actionneur, etat=None, valeur=None):
        """Modifie un actionneur manuellement"""
        if etat is not None:
            self.actionneurs[actionneur].etat = bool(etat)

            if actionneur == "eclairage":
                if not etat:
                    self.actionneurs["eclairage"].intensite = 0
                else:
                    self.actionneurs["eclairage"].intensite = 80

            etat_str = "activé" if etat else "désactivé"
            self.historique.append(f"🔧 {actionneur} {etat_str}")

        if valeur is not None and hasattr(self.actionneurs[actionneur], "position"):
            self.actionneurs[actionneur].position = int(valeur)
            self.historique.append(f"🔧 {actionneur} position → {valeur}%")
            self.derniere_modification = time.time()

    def generer_alerte_vocale(self, texte: str):
        """Fait parler la maison (offline)."""
        if not texte:
          return
        engine = pyttsx3.init()
        engine.say(texte)
        engine.runAndWait()
    def repondre_question(self, question: str) -> str:  
         question_lower = question.lower()
        
         if any(mot in question_lower for mot in ["bonjour", "salut", "hello", "bonsoir"]):
           return "Bonjour 👋 Je suis votre assistant SmartSim Home. Comment puis-je vous aider ?"
        
         if any(mot in question_lower for mot in ["aide", "help", "que peux-tu", "commandes"]):
            return (
                "Je peux :\n"
            "- répondre aux salutations\n"
            "- recommander une température (jour/nuit/éco)\n"
            "- analyser température/humidité/air et donner des alertes\n"
            "- vous donner l'état actuel de la maison\n"
            "- analyser les niveaux de monoxyde de carbone\n"
        )
         
         if "nuit" in question_lower:
          return "🌙 Pour bien dormir, une chambre entre 15 et 19°C est souvent recommandée. Je peux régler à 18.5°C."
         if "éco" in question_lower or "eco" in question_lower:
            return "🌱 Pour économiser l'énergie, je conseille 19°C (en évitant de descendre sous 18°C)."
         if "température" in question_lower or "temperature" in question_lower:
           return "🏠 En journée, viser autour de 21°C est un bon compromis confort/santé."
         
         if any(mot in question_lower for mot in ["santé", "sante", "humidité", "humidite", "moisissure", "analyse"]):
              temp = self.capteurs["temperature"].valeur
              hum = self.capteurs["humidite"].valeur  
              alertes = []
        
         if temp < 18:
            alertes.append(f"⚠️ Température basse ({temp:.1f}°C). En dessous de 18°C, cela peut être défavorable à la santé.")
        
         if hum > 60:
            alertes.append(f"🛑 Humidité très élevée ({hum:.0f}%). Au-delà de 60%, risque de moisissures. Aérer conseillé.")
         elif hum > 50:
            alertes.append(f"⚠️ Humidité un peu haute ({hum:.0f}%). Idéal: 30%-50%.")
         elif hum < 30:
            alertes.append(f"ℹ️ Air sec ({hum:.0f}%). En dessous de 30%, gêne possible (gorge/peau).")
         if not alertes:
            return "✅ Tous les paramètres environnementaux sont dans les normes acceptables."
        
         reponse = "📊 Analyse environnementale :\n"
         for alerte in alertes:
            reponse += f"\n• {alerte}"
            return reponse
        
         if "monoxyde" in question_lower or "co " in question_lower or "carbone" in question_lower:
             co_val = self.capteurs["monoxyde_carbone"].valeur
        
         if co_val >= 200:
            return f"🚨 ALERTE CRITIQUE CO > 200ppm - ÉVACUER IMMÉDIATEMENT et appeler pompiers (18/112) - CO actuel: {co_val} ppm"
         elif co_val >= 100:
            return f"⚠️ DANGER de CO - évacuer et appeler assistance - CO actuel: {co_val} ppm"
         elif co_val >= 50:
            return f"Niveau élevé de CO - aérer la pièce immédiatement - CO actuel: {co_val} ppm"
         elif co_val >= 10:
            return f"Niveau modéré de CO - surveiller la situation - CO actuel: {co_val} ppm"
        
         if "état" in question_lower or "etat" in question_lower or "status" in question_lower:
             etat = self.get_etat_maison()
             return (
                  f"🏠 État actuel de la maison :\n"
                  f"• 🌡️ Température: {etat['sensors']['temperature']}°C\n"
                  f"• 💧 Humidité: {etat['sensors']['humidite']}%\n"
                  f"• ⚡ Consommation: {etat['sensors']['energy']} kWh\n"
                  f"• 💡 Luminosité: {etat['sensors']['luminosite']}%\n"
                  f"• 👤 Présence: {'Oui' if etat['sensors']['presence'] else 'Non'}\n"
                  f"• ⚠️ CO: {etat['sensors']['monoxyde_carbone']} ppm"
                  )
          
         return "Je n'ai pas compris votre question."
    def demander_ia(self, texte_utilisateur: str):
        """
        Envoie la demande à l'IA locale et applique les actions proposées.
        """
        etat_maison = self.get_etat_maison()

        prompt = f"""
Tu es l'assistant d'une maison intelligente.
=== CONNAISSANCES À RESPECTER ===
{CONNAISSANCES_IA}

ÉTAT ACTUEL (JSON) :
{json.dumps(etat_maison, ensure_ascii=False, indent=2)}

RÈGLES :
- Essaie de répondre en JSON quand c’est possible
- Si impossible, réponds en texte clair
- Si l'utilisateur pose une question générale, explique l'état de la maison
- Si une amélioration est possible, propose-la dans la réponse
- Clés autorisées : reply, actions
- actions est une liste
- Actions possibles :
  - set_mode (mode, value)
  - toggle_actionneur (nom)
  - set_actionneur (nom, etat)
  - set_volet (position)
  - rien si impossible

EXEMPLE :
{{
  "reply": "J'active le mode éco.",
  "actions": [{{"type": "set_mode", "mode": "eco", "value": true}}]
}}

DEMANDE UTILISATEUR :
{texte_utilisateur}
"""

        try:
            response = ollama.generate(
                model="mistral",
                prompt=prompt
            )
            data = self._extraire_json(response.get("response", ""))
            
            if not data:
              reply = response.get("response", "").strip()
              if not reply:
                 reply = "Je n'ai pas compris, peux-tu reformuler ?"
              self.generer_alerte_vocale(reply)
              return reply
            reply = data.get("reply", "")
            actions = data.get("actions", [])
            
            for action in actions:
                 t = action.get("type")
                 if t == "set_mode":
                    mode = action.get("mode")
                    value = action.get("value") 
                    if mode in self.modes:
                        self.modifier_mode(mode, value)
                 elif t == "toggle_actionneur":
                    nom = action.get("nom")
                    if nom in self.actionneurs:
                       self.modifier_actionneur(
                           nom,
                           etat=not self.actionneurs[nom].etat
                      )
                 elif t == "set_actionneur":
                      nom = action.get("nom")
                      etat = action.get("etat")
                      if nom in self.actionneurs and etat is not None:
                         self.modifier_actionneur(nom, etat=bool(etat))

                 elif t == "set_volet":
                     position = action.get("position")
                     if position is not None:
                       self.modifier_actionneur("volet", valeur=int(position))
            
            self.generer_alerte_vocale(reply)

            return reply

        except Exception as e:
            erreur = "Je n'ai pas compris la demande."
            print("❌ Erreur IA :", e)
            self.generer_alerte_vocale(erreur)
            return erreur
    def _extraire_json(self, texte: str):
         import re, json
         m = re.search(r"\{[\s\S]*\}", texte)
         if not m:
            return None
         try:
             return json.loads(m.group(0))
         except Exception:
              return None
    def modifier_mode(self, mode, etat):
        """Modifie un mode manuellement"""
        self.modes[mode] = bool(etat)
        self.derniere_modification = time.time()
        etat_str = "activé" if etat else "désactivé"
        self.historique.append(f"⚙️ Mode {mode} {etat_str}")
        if mode == "alarme":
         self.alarme_auto_active = False
        
        self.automatiser_actions()


HTML_CONTENT = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>SmartSim Home 🌟</title>
<style>
  :root { --bg:#0b1020; --card:#121a33; --muted:#9aa6c1; --text:#e8eeff; --ok:#3ddc97; --bad:#ff5c7a; --warn:#ffd166; --line:rgba(255,255,255,.08); }
  *{box-sizing:border-box}
  body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial;background:radial-gradient(1200px 800px at 10% 10%, #18224a 0%, var(--bg) 55%);color:var(--text)}
  .wrap{max-width:1100px;margin:0 auto;padding:22px}
  header{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:18px}
  h1{font-size:22px;margin:0;font-weight:800;letter-spacing:.2px}
  .pill{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.04);color:var(--muted);font-size:13px}
  .dot{width:9px;height:9px;border-radius:999px;background:var(--warn)}
  .grid{display:grid;grid-template-columns:repeat(12,1fr);gap:14px}
  .card{grid-column:span 6;background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:16px;padding:14px}
  .card h2{margin:0 0 10px 0;font-size:14px;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.12em}
  .row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 0;border-top:1px solid var(--line)}
  .row:first-of-type{border-top:none}
  .k{display:flex;flex-direction:column;gap:2px}
  .k b{font-size:14px}
  .k span{font-size:12px;color:var(--muted)}
  .v{display:flex;align-items:center;gap:10px}
  button{cursor:pointer;border:none;border-radius:12px;padding:10px 12px;font-weight:700;color:var(--text);background:#243059;transition:.15s transform,.15s opacity}
  button:hover{transform:translateY(-1px)}
  button:active{transform:translateY(0px);opacity:.85}
  .btn-on{background:rgba(61,220,151,.18);outline:1px solid rgba(61,220,151,.35)}
  .btn-off{background:rgba(255,92,122,.18);outline:1px solid rgba(255,92,122,.35)}
  .btn-ghost{background:rgba(255,255,255,.06);outline:1px solid var(--line);color:var(--text)}
  .badge{font-size:12px;padding:6px 10px;border-radius:999px;border:1px solid var(--line);color:var(--muted)}
  .btn-danger { background: rgba(255, 92, 122, 0.2); border: 1px solid #ff5c7a; color: #ff5c7a; }
  .btn-danger.active { background: #ff5c7a; color: white; }
  input[type="range"]{width:220px}
  .two{display:grid;grid-template-columns:1fr 1fr;gap:10px}
  .full{grid-column:span 12}
  .small{grid-column:span 6}
  @media (max-width:900px){
    .card{grid-column:span 12}
    input[type="range"]{width:180px}
  }
  .footer{margin-top:14px;color:var(--muted);font-size:12px;display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap}
  code{background:rgba(255,255,255,.06);border:1px solid var(--line);padding:3px 6px;border-radius:8px;color:var(--text)}
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>🏠 SmartSim Home</h1>
      <div class="pill"><span class="dot" id="statusDot"></span><span id="statusTxt">Connexion…</span></div>
    </header>

    <div class="grid">
      <section class="card" id="cardSensors">
        <h2>Capteurs</h2>


        <div class="row">
          <div class="k"><b>🌡️ Température</b><span>°C</span></div>
          <div class="v">
            <span class="badge" id="tempVal">–</span>
            <input id="tempRange" type="range" min="15" max="30" step="0.1" />
            <button class="btn-ghost" onclick="setCapteur('temperature', document.getElementById('tempRange').value)">Appliquer</button>
          </div>
        </div>

        <div class="row">
          <div class="k"><b>💡 Luminosité</b><span>%</span></div>
          <div class="v">
            <span class="badge" id="lumVal">–</span>
            <input id="lumRange" type="range" min="0" max="100" step="1" />
            <button class="btn-ghost" onclick="setCapteur('luminosite', document.getElementById('lumRange').value)">Appliquer</button>
          </div>
        </div>

        <div class="row">
          <div class="k"><b>👤 Présence</b><span>Présent / Absent</span></div>
          <div class="v">
            <span class="badge" id="presVal">–</span>
            <button class="btn-ghost" onclick="setCapteur('presence', true)">Présent</button>
            <button class="btn-ghost" onclick="setCapteur('presence', false)">Absent</button>
          </div>
        </div>
<div class="row">
  <div class="k"><b>💧 Humidité</b><span>%</span></div>
  <div class="v">
    <span class="badge" id="humVal">–</span>
  </div>
</div>

<div class="row">
  <div class="k"><b>🌬️ Qualité de l'air</b><span>CO₂ simulé côté serveur</span></div>
  <div class="v">
    <span class="badge" id="airVal">–</span>
    <span class="badge" id="energyVal">⚡ – kWh</span>
  </div>
</div>
<div class="row">
  <div class="k"><b>⚠️ Monoxyde de carbone (CO)</b><span>ppm</span></div>
  <div class="v">
    <span class="badge" id="coVal">–</span>
  </div>
</div>

      </section>

      <section class="card" id="cardDevices">
        <h2>Appareils</h2>

        <div class="row">
          <div class="k"><b>💡 Éclairage</b><span>ON/OFF</span></div>
          <div class="v">
            <span class="badge" id="devEclairage">–</span>
            <button id="btnEclairage" onclick="toggleDevice('eclairage')">Basculer</button>
          </div>
        </div>

        <div class="row">
          <div class="k"><b>🔥 Chauffage</b><span>ON/OFF</span></div>
          <div class="v">
            <span class="badge" id="devChauffage">–</span>
            <button id="btnChauffage" onclick="toggleDevice('chauffage')">Basculer</button>
          </div>
        </div>

        <div class="row">
          <div class="k"><b>❄️ Climatisation</b><span>ON/OFF</span></div>
          <div class="v">
            <span class="badge" id="devClim">–</span>
            <button id="btnClim" onclick="toggleDevice('climatisation')">Basculer</button>
          </div>
        </div>

        <div class="row">
          <div class="k"><b>🔒 Sécurité</b><span>ON/OFF</span></div>
          <div class="v">
            <span class="badge" id="devSecurite">–</span>
            <button id="btnSecurite" onclick="toggleDevice('securite')">Basculer</button>
          </div>
        </div>

        <div class="row">
          <div class="k"><b>🔌 Prise salon</b><span>ON/OFF</span></div>
          <div class="v">
            <span class="badge" id="devPrise">–</span>
            <button id="btnPrise" onclick="toggleDevice('prise_salon')">Basculer</button>
          </div>
        </div>

        <div class="row">
          <div class="k"><b>🪟 Volet</b><span>Position %</span></div>
          <div class="v">
            <span class="badge" id="devVolet">–</span>
            <input id="voletRange" type="range" min="0" max="100" step="1" />
            <button class="btn-ghost" onclick="setVolet(document.getElementById('voletRange').value)">Appliquer</button>
          </div>
        </div>
      </section>

      <section class="card full" id="cardModes">
        <h2>Modes</h2>
        <div class="two">
          <div class="row" style="border-top:none">
            <div class="k"><b>🏖️ Vacances</b><span>Priorité absolue</span></div>
            <div class="v">
              <span class="badge" id="modeVacances">–</span>
              <button id="btnVacances" onclick="toggleMode('vacances')">Basculer</button>
            </div>
          </div>
          <div class="row" style="border-top:none">
  <div class="k"><b>🚨 Alarme</b><span>Auto si CO dangereux</span></div>
  <div class="v">
    <span class="badge" id="modeAlarme">–</span>
    <button class="btn-ghost" disabled>Automatique</button>
  </div>
</div>


          <div class="row" style="border-top:none">
            <div class="k"><b>🤖 Automatique</b><span>Règles présence / météo</span></div>
            <div class="v">
              <span class="badge" id="modeAuto">–</span>
              <button id="btnAuto" onclick="toggleMode('automatique')">Basculer</button>
            </div>
          </div>
          <div class="row" style="border-top:none">
  <div class="k"><b>🚨 Simulation CO</b><span>Danger > 200ppm</span></div>
  <div class="v">
    <span class="badge" id="modeSimuCO">–</span>
    <button id="btnSimuCO" class="btn-danger" onclick="toggleMode('simulation_co')">TEST ALERTE</button>
  </div>
</div>

          <div class="row" style="border-top:none">
            <div class="k"><b>🌱 Éco</b><span>Limite la conso</span></div>
            <div class="v">
              <span class="badge" id="modeEco">–</span>
              <button id="btnEco" onclick="toggleMode('eco')">Basculer</button>
            </div>
          </div>

          <div class="row" style="border-top:none">
            <div class="k"><b>🔄 Rafraîchir</b><span>Récupérer l’état</span></div>
            <div class="v">
              <button class="btn-ghost" onclick="refresh()">Rafraîchir maintenant</button>
            </div>
          </div>
        </div>
      </section>
      <section class="card full" id="cardAlerts">
  <h2>Alertes</h2>

  <div class="row" style="border-top:none">
    <div class="k">
      <b id="alertBanner">✅ Aucune alerte</b>
      <span id="alertSub">–</span>
    </div>
    <div class="v">
      <button class="btn-ghost" onclick="refresh()">Rafraîchir</button>
    </div>
  </div>

  <div id="alertsList"></div>
</section>
<section class="card full" id="cardAssistant">
  <h2>Assistant IA (Ollama)</h2>

  <div class="row" style="border-top:none">
    <div class="k" style="width:100%">
      <b>💬 Pose une question / donne une instruction</b>
      <span>Ex: “mets le mode éco”, “ouvre les volets à 70%”, “éteins la prise salon”, “allume la lumière”</span>

      <div style="display:flex; gap:10px; margin-top:10px">
        <input id="iaInput"
               placeholder="Tape ta demande…"
               style="flex:1; padding:10px; border-radius:12px; border:1px solid rgba(255,255,255,.12); background:rgba(255,255,255,.06); color:var(--text)" />
        <button class="btn-ghost" onclick="askIA()">Envoyer</button>
      </div>

      <div style="margin-top:10px; color:var(--muted)" id="iaReply">—</div>
    </div>
  </div>
</section>
    </div>

    <div class="footer">
      <div>API: <code>/api/etat</code> • <code>/api/controle/&lt;device&gt;</code> • <code>/api/mode/&lt;mode&gt;</code></div>
      <div id="lastUpdate">–</div>
    </div>
  </div>

<script>
  const statusDot = document.getElementById('statusDot');
  const statusTxt = document.getElementById('statusTxt');
  const lastUpdate = document.getElementById('lastUpdate');

  function setStatus(ok, msg){
    statusDot.style.background = ok ? 'var(--ok)' : 'var(--bad)';
    statusTxt.textContent = msg;
  }

  function badge(el, on){
    el.textContent = on ? 'ON' : 'OFF';
  }

  function styleBtn(btn, on){
    btn.className = on ? 'btn-on' : 'btn-off';
    btn.textContent = on ? 'Éteindre' : 'Allumer';
  }

  async function apiGet(url){
    const r = await fetch(url);
    if(!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }

  async function apiPost(url, data){
    const r = await fetch(url, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: data ? JSON.stringify(data) : null
    });
    if(!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }

  async function refresh(){
    try{
      const d = await apiGet('/api/etat');
      setStatus(true, 'Connecté');
      render(d);
      lastUpdate.textContent = 'Dernière mise à jour: ' + new Date().toLocaleTimeString();
    } catch(e){
      setStatus(false, 'Déconnecté');
      console.error(e);
    }
  }

  function render(d){
    // Sensors
    document.getElementById('tempVal').textContent = d.sensors.temperature + ' °C';
    document.getElementById('lumVal').textContent = d.sensors.luminosite + ' %';
    document.getElementById('presVal').textContent = d.sensors.presence ? 'PRÉSENT' : 'ABSENT';
    document.getElementById('humVal').textContent = d.sensors.humidite + ' %';
    document.getElementById('airVal').textContent = d.sensors.qualite_air;
    document.getElementById('energyVal').textContent = '⚡ ' + d.sensors.energy + ' kWh';
    document.getElementById('coVal').textContent = d.sensors.monoxyde_carbone + ' ppm';

    // Sync sliders (sans faire sauter le curseur si tu bouges)
    const t = document.getElementById('tempRange');
    const l = document.getElementById('lumRange');
    
    const v = document.getElementById('voletRange');
    if(!t.matches(':active')) t.value = d.sensors.temperature;
    if(!l.matches(':active')) l.value = d.sensors.luminosite;
    
    if(!v.matches(':active')) v.value = d.devices.volet;
    // Devices
    const eclairage = d.devices.eclairage;
    const chauffage = d.devices.chauffage;
    const clim = d.devices.climatisation;
    const secu = d.devices.securite;
    const prise = d.devices.prise_salon;

    badge(document.getElementById('devEclairage'), eclairage);
    badge(document.getElementById('devChauffage'), chauffage);
    badge(document.getElementById('devClim'), clim);
    badge(document.getElementById('devSecurite'), secu);
    badge(document.getElementById('devPrise'), prise);
    document.getElementById('devVolet').textContent = d.devices.volet + ' %';

    styleBtn(document.getElementById('btnEclairage'), eclairage);
    styleBtn(document.getElementById('btnChauffage'), chauffage);
    styleBtn(document.getElementById('btnClim'), clim);
    styleBtn(document.getElementById('btnSecurite'), secu);
    styleBtn(document.getElementById('btnPrise'), prise);

    // Modes
    const vacances = d.modes.vacances;
    const auto = d.modes.automatique;
    const eco = d.modes.eco;
    const simuCO = d.modes.simulation_co; 
    const alarme = d.modes.alarme;


    badge(document.getElementById('modeVacances'), vacances);
    badge(document.getElementById('modeAuto'), auto);
    badge(document.getElementById('modeEco'), eco);
    badge(document.getElementById('modeSimuCO'), simuCO);
    badge(document.getElementById('modeAlarme'), alarme);

    styleBtn(document.getElementById('btnVacances'), vacances);
    styleBtn(document.getElementById('btnAuto'), auto);
    styleBtn(document.getElementById('btnEco'), eco);

    const btnSimu = document.getElementById('btnSimuCO');
    btnSimu.textContent = simuCO ? "ARRÊTER TEST" : "LANCER TEST";
    btnSimu.className = simuCO ? "btn-danger active" : "btn-danger";
    // ===== ALERTES =====
    const banner = document.getElementById('alertBanner');
     const sub = document.getElementById('alertSub');
     const list = document.getElementById('alertsList');
     const co = d.sensors && d.sensors.monoxyde_carbone;
     const hist = d.historique || [];
     const lastCrit = [...hist].reverse().find(x => (x || "").includes("CRITIQUE")) || "";


if (alarme || (typeof co === "number" && co >= 200)) {
  banner.textContent = "🚨 ALERTE CO ACTIVE";
  sub.textContent = lastCrit || "Ouvrez immédiatement les fenêtres, sortez et appelez les pompiers (18 / 112).";
  banner.style.color = "var(--bad)";
} else {
  banner.textContent = "✅ Aucune alerte";
  sub.textContent = "–";
  banner.style.color = "var(--ok)";
}

  }

  async function toggleDevice(device){
    try{
      await apiPost('/api/controle/' + device, {});
      await refresh();
    } catch(e){
      alert('Erreur device: ' + e.message);
    }
  }

  async function setVolet(pos){
    try{
      await apiPost('/api/controle/volet', {position: Number(pos)});
      await refresh();
    } catch(e){
      alert('Erreur volet: ' + e.message);
    }
  }

  async function toggleMode(mode){
    try{
      await apiPost('/api/mode/' + mode, {});
      await refresh();
    } catch(e){
      alert('Erreur mode: ' + e.message);
    }
  }

  async function setCapteur(capteur, valeur){
    try{
      await apiPost('/api/modifier/capteur', {capteur, valeur});
      await refresh();
    } catch(e){
      alert('Erreur capteur: ' + e.message);
    }
  }
  async function askIA(){
  const input = document.getElementById('iaInput');
  const out = document.getElementById('iaReply');
  const texte = (input.value || '').trim();
  if(!texte) return;

  out.textContent = "⏳ Ollama réfléchit…";

  try{
    const r = await apiPost('/api/assistant', { texte });
    out.textContent = "🤖 " + (r.reply || "—");
    input.value = "";
    await refresh();
  }catch(e){
    out.textContent = "❌ Erreur: " + e.message;
  }
}

// BONUS : envoyer avec Entrée
document.addEventListener('keydown', (e) => {
  if(e.key === 'Enter' && document.activeElement?.id === 'iaInput'){
    askIA();
  }
});
  refresh();
  setInterval(refresh, 3000);
</script>
</body>
</html>
"""
from http.server import HTTPServer, BaseHTTPRequestHandler

class SmartHomeHandler(BaseHTTPRequestHandler):
    def __init__(self, maison, *args, **kwargs):
        self.maison = maison
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """Gère les requêtes OPTIONS pour CORS"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")  # Important !
        self.end_headers()
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode("utf-8"))

    def do_GET(self):
        if self.path == "/":
           self.send_response(200)
           self.send_header("Content-type", "text/html; charset=utf-8")
           self.send_header("Access-Control-Allow-Origin", "*")
           self.end_headers()
           self.wfile.write(HTML_CONTENT.encode("utf-8"))

        elif self.path == "/api/etat":
             self.handle_api_etat()

        else:
              self.send_response(404)
              self.send_header("Content-type", "text/plain; charset=utf-8")
              self.send_header("Access-Control-Allow-Origin", "*")
              self.end_headers()
              self.wfile.write("Not found".encode("utf-8"))

    def handle_api_etat(self):
        """Gère la requête GET /api/etat"""
        try:
            etat = self.maison.get_etat_maison()
            self.send_json_response(etat)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def do_POST(self):
        try:
          
             if self.path.startswith("/api/mode/"):
                 mode = self.path.split("/")[-1]
                 self.handle_mode(mode)
             
             elif self.path.startswith("/api/controle/"):
                  device = self.path.split("/")[-1]
                  self.handle_control(device)
           
             elif self.path == "/api/modifier/capteur":
                  self.handle_modifier_capteur() 
             elif self.path == "/api/regles/add":
                 self.handle_regles_add()
             elif self.path == "/api/regles/delete":
                  self.handle_regles_delete()
                
             elif self.path == "/api/assistant":
                  self.handle_assistant()  
             
             else:
                 self.send_error(404, "Endpoint non trouvé")
        except Exception as e:
                self.send_json_response({"error": str(e)}, 500)    

                 
    def handle_modifier_capteur(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode("utf-8"))

        capteur = data.get("capteur")
        valeur = data.get("valeur")

        if not capteur or valeur is None:
            self.send_json_response({"error": "Paramètres manquants"}, 400)
            return

        success, message = self.maison.modifier_capteur(capteur, valeur)

        if not success:
            self.send_json_response({"error": message}, 400)
        else:
            self.send_json_response({
                "status": "success",
                "capteur": capteur,
                "valeur": valeur,
                "message": message
            })
    def handle_assistant(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
          data = json.loads(post_data.decode("utf-8"))
        except Exception:
            self.send_json_response({"error": "JSON invalide"}, 400)
            return

        texte = (data.get("texte") or "").strip()
        if not texte:
          self.send_json_response({"error": "Champ 'texte' manquant"}, 400)
          return
        
        reponse_locale = self.maison.repondre_question(texte)
        if reponse_locale != "Je n'ai pas compris votre question.":
            self.send_json_response({
               "status": "success",
                "reply": reponse_locale,
                "etat": self.maison.get_etat_maison()
            })
            return
          
        reply = self.maison.demander_ia(texte)
        self.send_json_response({
        "status": "success",
        "reply": reply,
        "etat": self.maison.get_etat_maison()
    })
     

    def handle_regles_add(self):
          content_length = int(self.headers.get("Content-Length", 0))
          post_data = self.rfile.read(content_length)
          data = json.loads(post_data.decode("utf-8"))    

          condition = data.get("condition")
          actions = data.get("actions")
          nom = data.get("nom", "")  
          if not condition or not actions:
             self.send_json_response({"error": "condition/actions manquants"}, 400)
             return
          regle = self.maison.ajouter_regle(condition, actions, nom=nom)
          self.send_json_response({"status": "success", "regle": regle})

    def handle_regles_delete(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode("utf-8"))

        rid = data.get("id")
        if rid is None:
           self.send_json_response({"error": "id manquant"}, 400)
           return

        ok = self.maison.supprimer_regle(int(rid))
        if not ok:
           self.send_json_response({"error": "règle introuvable"}, 404)
        else:
           self.send_json_response({"status": "success", "id": int(rid)})  

    def handle_control(self, device):
        content_length = int(self.headers.get("Content-Length", 0))
        data = {}
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))

        if device in ["eclairage", "chauffage", "climatisation", "securite", "prise_salon"]:
            self.maison.modifier_actionneur(device, etat=not self.maison.actionneurs[device].etat)
        elif device == "volet" and "position" in data:
            position = int(data["position"])
            if 0 <= position <= 100:
                self.maison.modifier_actionneur("volet", valeur=position)

        self.send_json_response({"status": "success", "device": device})

    def handle_mode(self, mode):
        if mode in self.maison.modes:
            self.maison.modifier_mode(mode, not self.maison.modes[mode])
        self.send_json_response({"status": "success", "mode": mode})

    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode("utf-8"))

    def log_message(self, format, *args):
        pass


class Application:
    def __init__(self):
        self.maison = MaisonIntelligente()
        self.running = True
        self.server = None

    def demarrer_simulation(self):
        while self.running:
            try:
                self.maison.mettre_a_jour_capteurs()
                self.maison.automatiser_actions()
                time.sleep(5)
            except Exception as e:
                print(f"⚠️ Erreur simulation: {e}")
                time.sleep(5)

    def demarrer_serveur(self):
        from functools import partial
        handler = partial(SmartHomeHandler, self.maison)
        self.server = HTTPServer(("localhost", 8000), handler)
        print("🌐 Serveur web démarré sur http://localhost:8000")
        self.server.serve_forever()

    def executer(self):
        print("🚀 Lancement de SmartSim Home")
        threading.Thread(target=self.demarrer_simulation, daemon=True).start()
        threading.Thread(target=self.demarrer_serveur, daemon=True).start()

        print("✅ Système prêt !")
        print("🎨 Interface: http://localhost:8000")
        print("🛑 Ctrl+C pour arrêter")

        try:
            time.sleep(1)
            webbrowser.open("http://localhost:8000")
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ Arrêt...")
            self.running = False


if __name__ == "__main__":
    Application().executer()
