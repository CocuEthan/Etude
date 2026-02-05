## Exemple de base de Code Infor0504
##
from arithmetiqueDansZ import est_inversible_modulo,inverse_modulo
from ChiffreurCA import ChiffreurCA
from Message import Message
class ChiffreurAffine(ChiffreurCA):
    """Théorie des codes p 150"""
    def __init__(self ,a=13,b=5):
        assert isinstance(a,int) and a>0 and a<256 and est_inversible_modulo(a,256),f"{a} doit être inversible dans Z/256Z"
        self.a=a
        self.b=b%256
    def __str__(self):
        return f"Chiffreur affine avec a={self.a} et b={self.b}"
    def __repr__(self):
        return f"ChiffreurAffine({repr(self.a)},{repr(self.b)})"

    def chiffre(self,m):
        """
        >>> ChiffreurAffine(3,1).chiffre(Message("Bonjour"))
        Message([ 0xc7, 0x4e, 0x4b, 0x3f, 0x4e, 0x60, 0x57])
        """
        mc=[(self.a*x+self.b)%256 for x in m]
        return Message(mc)

    def dechiffre(self,mc):
        """
        >>> ChiffreurAffine(3,1).dechiffre(Message([ 0xc7, 0x4e, 0x4b, 0x3f, 0x4e, 0x60, 0x57])).to_string()
        'Bonjour'
        """
        ia=inverse_modulo(self.a,256)
        md=[((y-self.b) * ia)%256 for y in mc]  # md est une donc une liste d octets
        return Message(md)                    # on retourne un Message


    def chiffreurAffine_dapres_deux_valeurs(b1,bc1,b2,bc2):
        """ Renvoie le Chiffreur affine décodant ces deux valeurs
        >>> ChiffreurAffine.chiffreurAffine_dapres_deux_valeurs(1,8,6,23)
        ChiffreurAffine(3,5)
        """
        deltax,deltay = (b2-b1)%256 , (bc2-bc1)%256
        assert est_inversible_modulo(deltax,256 ),f"Attention {b2}-{b1}={deltax} doit être inversible dans Z/256Z"
        a=(deltay * inverse_modulo(deltax,256)) %256
        b=(bc1-a*b1) %256
        return ChiffreurAffine(a,b)

    def demo():
        m=Message([0x00,0x01,0x02,0x010,0x20,0x40,0x80])
        m2=Message("Bonjour !")
        for monChiffreur in [ChiffreurAffine(3,5),ChiffreurAffine(1,1),ChiffreurAffine(1,0)]:
            print()
            print(f"Chiffrement avec {monChiffreur} :")
            print("   Bin   :         ",m)
            mc=monChiffreur.chiffre(m)
            print("   Bin Chiffré:    ",mc)
            md=monChiffreur.dechiffre(mc)
            print("   Bin Déchiffré : ",md)
            print("   md (déchiffré) est égal à m ?",md==m)
            mc2=monChiffreur.chiffre(m2);md2=monChiffreur.dechiffre(mc2)
            print(f"Avec une chaine : {m2.to_string()} -> {mc2.to_string()} -> {md2.to_string()}")

            print()
            print("On cherche le déchiffreur à l'aide de simplement deux valeurs'")
            dch=ChiffreurAffine.chiffreurAffine_dapres_deux_valeurs(m[1],mc[1],m[2],mc[2])
            print(f"chiffreurAffine_dapres_deux_valeurs({m[1]},{mc[1]},{m[2]},{mc[2]}) : {dch}")
            print("   Le déchiffré est alors ",dch.dechiffre(mc))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    ChiffreurAffine.demo()

