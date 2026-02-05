import random
class IABaston:
    def __init__(self, N, k):
        self.N = N
        self.k = k
        self.compteurs = {1: [[2] * k for _ in range(N)],
                          2: [[2] * k for _ in range(N)]}

    def faireMouvement(self, joueur, batonsRestants):
        i = self.N - batonsRestants
        somme_compteurs = sum(self.compteurs[joueur][i])
        if somme_compteurs == 0:
            probabilites = [1 / self.k] * self.k  # Si la somme des compteurs est nulle, attribuer une probabilité égale à chaque mouvement
        else:
            probabilites = [compteur / somme_compteurs for compteur in self.compteurs[joueur][i]]
        mouvement = random.choices(range(1, self.k + 1), probabilites)[0]
        return mouvement

    def MAJCompteurs(self, joueur, batonsRestants, gagne):
        i = self.N - batonsRestants
        if gagne:
            for j in range(self.k):
                self.compteurs[joueur][i][j] += 1
        else:
            for j in range(self.k):
                self.compteurs[joueur][i][j] -= 1
                if self.compteurs[joueur][i][j] < 0:
                    self.compteurs[joueur][i][j] = 2

def jouerPartie_IAvsIA(N, k):
    IA1 = IABaston(N, k)
    IA2 = IABaston(N, k)
    victoires_IA1 = 0
    victoires_IA2 = 0
    for _ in range(10000):
        batonsRestants = N
        while batonsRestants > 0:
            mouvement_IA1 = IA1.faireMouvement(1, batonsRestants)
            batonsRestants -= mouvement_IA1
            IA1.MAJCompteurs(1, batonsRestants + mouvement_IA1, gagne=False)
            if batonsRestants <= 0:
                victoires_IA2 += 1
                break
            mouvement_IA2 = IA2.faireMouvement(2, batonsRestants)
            batonsRestants -= mouvement_IA2
            IA2.MAJCompteurs(2, batonsRestants + mouvement_IA2, gagne=False)
            if batonsRestants <= 0:
                victoires_IA1 += 1
                break
    return victoires_IA1, victoires_IA2

victoires_IA1, victoires_IA2 = jouerPartie_IAvsIA(8, 2)
print("Nombre de parties gagnées par l'IA 1:", victoires_IA1)
print("Nombre de parties gagnées par l'IA 2:", victoires_IA2)
