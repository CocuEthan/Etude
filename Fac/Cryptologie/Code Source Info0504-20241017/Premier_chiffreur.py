from ChiffreurCA import ChiffreurCA
from Message import *
class Premier_chiffreur(ChiffreurCA):
    """Un chiffreur doit surcharger les méthodes __init__ __repr__ __str__
    ainsi que chiffre et dechiffre
    C'est une forme de classe abstraites"""
    def __init__(self, decalage=2 ):
        self.decalage=decalage

    def __str__(self):
        return f"Premier chiffreur avec {self.decalage=}"
    def __repr__(self):
        return f"Premier_chiffreur(decalage={self.decalage})"

    def chiffre(self,m):
        "Renvoie le chiffré du Message m"
        mc=[(b+self.decalage)%256 for b in m]
        return Message(mc)
    def dechiffre(self,mc):
        "Renvoie le déchiffré du Message chiffré mc"
        md=[(b-self.decalage)%256 for b in mc]
        return Message(md)
if __name__ == "__main__":
    import doctest
    doctest.testmod()

    mon_chiffreur=Premier_chiffreur(13)

    mon_message=Message("Oh !")
    print("En clair :",mon_message)
    print("   affiché comme chaîne :",mon_message.to_string())

    mon_message_chiffre=mon_chiffreur.chiffre(mon_message)
    print("Chiffré :",mon_message_chiffre)
    print("   affiché comme chaîne :",mon_message_chiffre.to_string())

    mon_message2=mon_chiffreur.dechiffre(mon_message_chiffre)
    print("Déchiffré :",mon_message2)
    print("   affiché comme chaîne :",mon_message.to_string())
    print("mon_message_chiffre déchiffré est-il égal à mon_message ? ",mon_message2==mon_message)


