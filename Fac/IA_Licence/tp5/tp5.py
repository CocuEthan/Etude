import random

class IA:
    def __init__(self):
        self.historique = []

    def entrainement(self, adversaire, rounds=15):
        for _ in range(rounds):
            choix = random.choice([0, 1])
            choix_adversaire = adversaire.jouer()
            self.historique.append((choix, choix_adversaire))

    def analyser(self):
        profil = {}

        for i in range(len(self.historique) - 1):
            propre_choix, choix_adversaire = self.historique[i]
            prochain_choix_adversaire = self.historique[i + 1][1]

            if choix_adversaire not in profil:
                profil[choix_adversaire] = {'total': 1, 'prochains_counts': {prochain_choix_adversaire: 1}}
            else:
                profil[choix_adversaire]['total'] += 1
                if prochain_choix_adversaire not in profil[choix_adversaire]['prochains_counts']:
                    profil[choix_adversaire]['prochains_counts'][prochain_choix_adversaire] = 1
                else:
                    profil[choix_adversaire]['prochains_counts'][prochain_choix_adversaire] += 1

        return profil

    def jouer(self, profil_adversaire=None):
        if profil_adversaire is None:
            # Si aucun profil n'est fourni, jouer au hasard
            return random.choice([0, 1])
        else:
            # Utiliser le profil pour prendre une décision
            # Ici, nous allons simplement deviner le prochain coup basé sur les tendances observées
            choix_adversaire = max(profil_adversaire.keys(), key=lambda x: profil_adversaire[x]['total'])
            prochains_counts = profil_adversaire[choix_adversaire]['prochains_counts']
            prochain_choix_predit = max(prochains_counts.keys(), key=lambda x: prochains_counts[x])
            return prochain_choix_predit

class JoueurHumain:
    def jouer(self):
        return int(input("Choisissez 0 ou 1 : "))

# Entraînement de l'IA
ia = IA()
humain = JoueurHumain()
ia.entrainement(humain)

# Analyse du profil psychologique du joueur
profil = ia.analyser()
print("Profil psychologique du joueur :", profil)

# Évaluation de la performance de l'IA
victoires = 0
for _ in range(15):
    choix_ia = ia.jouer(profil)
    choix_humain = humain.jouer()
    if choix_ia == choix_humain:
        victoires += 1

print("Taux de victoire de l'IA :", victoires / 15)
