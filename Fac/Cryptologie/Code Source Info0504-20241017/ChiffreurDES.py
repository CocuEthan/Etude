 from ChiffreurCA import ChiffreurCA
#le chiffreur DES :
class ChiffreurDES(ChiffreurCA):
    """Théorie des codes p 150"""
    #2**32=4294967296 ~~ 4.3E9
    def __init__(self ,cle=0x123556789ABDDEF0,verbose=False):
        self.cle=int(cle)
        self.f=FBij64BitsDES(cle,verbose=verbose)
    def __str__(self):
        return f"Chiffreur DES de clé {self.cle:08x}"
    def __repr__(self):
        return f"ChiffreurDES({self.cle=:08x})"

    def chiffre(self,m):
        mC=Message([])
        #On doit mémoriser la longueur totale de la liste à chiffrer
        mC.ajouteLongueValeur(len(m))
        pos=0
        while pos<len(m):
            x,pos=m.lisMot64Bits(pos)
            mC.ajouteMot64Bits( self.f(x) )
        return mC

    def dechiffre(self,mC):
        mD=Message([])
        longueur,pos=mC.lisLongueValeur(0)

        while pos<len(mC):
            y,pos=mC.lisMot64Bits(pos)
            mD.ajouteMot64Bits( self.f.valInv(y) )
        return Message(mD[:longueur])

    def demo():
        m=Message("Bonjour les amis !! Vous allez bien ?")
        monChiffreur=ChiffreurDES(0x123556789ABDDEF0)
        print(f"Chiffrement avec {monChiffreur} :")
        print("   Message           :",m.to_string())
        mC=monChiffreur.chiffre(m)
        print("   Message Chiffré   :",mC.to_string())
        mD=monChiffreur.dechiffre(mC)
        print("   Message déchiffré :",mD.to_string())
        print("   Le message déchiffré est égal au Message ?",mD==m)
