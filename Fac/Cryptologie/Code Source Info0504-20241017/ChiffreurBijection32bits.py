from arithmetiqueDansZ import ElementDeZnZ,PGCD
from LBinaire603 import LBinaire603
from  CodeurCA import CodeurCA
from FBijection32BitsCA import FBijection32BitsCA,FAffine32bits,FMasque32bits,FPermutation32Bits
from FFeistel32bits import FFeistel32bits
class ChiffreurBijection32Bits(CodeurCA):
    """Théorie des codes p 150"""
    #2**32=4294967296 ~~ 4.3E9
    def __init__(self ,f):
        assert isinstance(f,FBijection32BitsCA)
        self.f=f
    def __str__(self):
        return f"Chiffreur chiffrant mot par mot de 32 bits avec la bijection {self.f}"
    def __repr__(self):
        return f"ChiffreurBijection32Bits(f={self.f.__repr__()})"

    def binCode(self,monBin):
        monBinC=LBinaire603([])
        #On doit mémoriser la longueur totale de la liste à chiffrer
        monBinC.ajouteLongueValeur(len(monBin))
        pos=0
        while pos<len(monBin):
            x,pos=monBin.lisMot32Bits(pos)
            monBinC.ajouteMot32Bits( self.f(x) )
        return monBinC

    def binDecode(self,monBinC):
        monBinD=LBinaire603([])
        longueur,pos=monBinC.lisLongueValeur(0)

        while pos<len(monBinC):
            y,pos=monBinC.lisMot32Bits(pos)
            monBinD.ajouteMot32Bits( self.f.valInv(y) )
        return LBinaire603(monBinD[:longueur])

    def demo():
        monBin=LBinaire603([0x01,0x02,0x010,0x20,0x40,0x80,0x00,0x01,0x02,0x010,0x20,0x40,0x80])
        for maBij in [FAffine32bits(a=2341234567,b=1234567890),
              FMasque32bits(masque32bits=0xf1d2b3a4),
              FPermutation32Bits(lp=[9,2,1,4,3,6,5,8,7,0,19,12,11,14,13,16,15,18,17,10,29,22,21,24,23,26,25,28,27,20,31,30]),
              FFeistel32bits()]:
            monCodeur=ChiffreurBijection32Bits(maBij)
            print(f"Codage avec {monCodeur} :")
            print("   Bin:       ",monBin)
            monBinC=monCodeur.binCode(monBin)
            print("   Bin Codé:  ",monBinC)
            monBinD=monCodeur.binDecode(monBinC)
            print("   Bin Décodé:",monBinD)
            print("   monBinD (décodé) est égal à Monbin ?",monBinD==monBin)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    ChiffreurBijection32Bits.demo()

