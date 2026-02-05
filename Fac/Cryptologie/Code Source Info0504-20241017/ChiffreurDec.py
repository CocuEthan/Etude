import matplotlib.pyplot as plt
from frequences import lFrequences, afficheHistogrammeDesFrequences
class ChiffreurDec(object):
    def __init__(self, decalage):
        self.decalage = decalage

    def __str__(self):
        return f"Chiffrement par décalage {self.decalage}"

    def __repr__(self):
        return f"Chiffrement par décalage ({self.decalage})"

    def chiffre(self, m):
        """Renvoie le message chiffré de m"""
        c = [(self.decalage + ord(m_j)) % 256 for m_j in m]
        return c

    def dechiffre(self, c):
        """Renvoie le message déchiffré de c"""
        m = ''.join([chr((c_j - self.decalage) % 256) for c_j in c])
        return m




if __name__ == "__main__":
    import doctest
    doctest.testmod()
    decalage = 3
    chiff = ChiffreurDec(decalage)
    print(chiff)
    messageOriginal = "Voici mon message !"
    print(f"Message original: {messageOriginal}")
    messageChiffre = chiff.chiffre(messageOriginal)
    print(f"Message chiffré: {messageChiffre}")
    messageDechiffre = chiff.dechiffre(messageChiffre)
    print(f"Message déchiffré: {messageDechiffre}")
    frequences = lFrequences(messageChiffre)
    print(f"Fréquences des caractères chiffrés: {frequences}")
    afficheHistogrammeDesFrequences(messageChiffre, titre="Histogramme des fréquences du message chiffré")
