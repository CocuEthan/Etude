from Message import Message
class ChiffreurCA(object):
    """Un chiffreur doit surcharger les méthodes __init__ __repr__ __str__
    ainsi que chiffre et dechiffre
    C'est une forme de classe abstraites"""
    def __init__(self ):
        raise NotImplementedError # Ne pas toucher

    def __str__(self):
        raise NotImplementedError# Ne pas toucher
    def __repr__(self):
        raise NotImplementedError# Ne pas toucher

    def chiffre(self,m):
        "Renvoie le chiffré du Message m"
        raise NotImplementedError# Ne pas toucher
    def dechiffre(self,c):
        "Renvoie le déchiffré du Message m"
        raise NotImplementedError# Ne pas toucher



if __name__ == "__main__":
    import doctest
    doctest.testmod()
##    mon_chiffreur=ChiffreurCA() #A modifier si repris dans une classe en héritant
##    for k in range(5):
##        mon_message=Message("Hello les amis")
##        print("En clair :",mon_bytes)
##        mon_bytes_chiffre=mon_chiffreur.chiffre(mon_bytes)
##        print("Chiffré :",mon_bytes_chiffre)
##        print("mon_bytes_chiffre décodé est égal à mon_bytes ?",mon_chiffreur.dechiffre(mon_bytes_chiffre)==mon_bytes)


