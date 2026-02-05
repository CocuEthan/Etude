from FBijection8bitsCA import FBijection8bitsCA
class FBijParDecallge(FBijection8bitsCA):
    def __init__(self,dec):
        self.dec = des%256

    def __repr__(self):
        return f"FBijParDecallage(dec={self.dec})"

    def __call__(self,octet):
        return (octet + self.dec)%256

    def valInv(self,octetC):
        return (octetC + self.dec)%256