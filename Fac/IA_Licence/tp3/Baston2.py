import random

class IABaston:
    def __init__(self, N, k):
        self.N = N
        self.k = k
        self.compteurs = [[2] * k for _ in range(N)]

    def faireMouvement(self, batonsRestants):
        i = self.N - batonsRestants
        somme_compteurs = sum(self.compteurs[i])
        if somme_compteurs == 0:
            probabilites = [1 / self.k] * self.k  # Si la somme des compteurs est nulle, attribuer une probabilité égale à chaque mouvement
        else:
            probabilites = [compteur / somme_compteurs for compteur in self.compteurs[i]]
        mouvement = random.choices(range(1, self.k + 1), probabilites)[0]
        return mouvement


    def MAJCompteurs(self, batonsRestants, gagne):
        i = self.N - batonsRestants
        if gagne:
            for j in range(self.k):
                self.compteurs[i][j] += 1
        else:
            for j in range(self.k):
                self.compteurs[i][j] -= 1
                if self.compteurs[i][j] < 0:
                    self.compteurs[i][j] = 2

def jouerPartie(N, k):
    IA = IABaston(N, k)
    while True:
        batonsRestants = N
        while batonsRestants > 0:
            print("Bâtons restants:", batonsRestants)
            mouvementIA = IA.faireMouvement(batonsRestants)
            print("IA enlève", mouvementIA, "bâtons")
            batonsRestants -= mouvementIA
            IA.MAJCompteurs(batonsRestants + mouvementIA, gagne=False)
            if batonsRestants <= 0:
                print("Vous gagnez!")
                break
            print("Bâtons restants:", batonsRestants)
            mouvementHumain = int(input("Votre mouvement (1 à {}): ".format(min(k, batonsRestants))))
            batonsRestants -= mouvementHumain
            IA.MAJCompteurs(batonsRestants + mouvementHumain, gagne=True) 
            if batonsRestants <= 0:
                print("IA gagne!")
                break
        print("État des compteurs après cette partie :")
        for i, compteur in enumerate(IA.compteurs):
            print("Compteurs pour {} bâtons restants :".format(i))
            print(compteur)
        rejouer = input("Voulez-vous rejouer ? (Oui/Non) ")
        if rejouer.lower() != 'oui':
            break

jouerPartie(8, 2)
