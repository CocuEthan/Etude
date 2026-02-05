from FBijection8bitsCA import FBijection8bitsCA
class FBijFeistel(FBijection8bitsCA):
    def __init__(self, nbTours=4, graine=0):
        self.nbTours = nbTours
        random.seed(graine)
        self.cles = [random.randint(0, 255) for _ in range(nbTours)]

    def __repr__(self):
        return f"FBijFeistel(nbTours={self.nbTours})"

    def fonctionDeTour(self, demiOctet, cle):
        return demiOctet ^ cle

    def __call__(self, octet):
        gauche = octet >> 4
        droite = octet & 0x0F
        for cle in self.cles:
            nouvelleGauche = droite
            droite = gauche ^ self.fonctionDeTour(droite, cle)
            gauche = nouvelleGauche
        return (gauche << 4) | droite

    def valInv(self, octetC):
        gauche = octetC >> 4
        droite = octetC & 0x0F
        for cle in reversed(self.cles):
            nouvelleDroite = gauche
            gauche = droite ^ self.fonctionDeTour(gauche, cle)
            droite = nouvelleDroite
        return (gauche << 4) | droite
