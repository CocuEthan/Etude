# toujours gérer l'emlement neutre
class PointE07(object):
    """Ensemble des solutions de Y²=X^3+7 dans Fp Courbe secp256k1 Y^3=X²+7
    Le point O, élément neutre de l'addition est défini par : self.y='Inf' """
    def __init__(self,x,y=None,p=None):
        """
        p doit être premier et différent de 7
        PointE07(7,6,11) doit renvoyer une erreur
        >>> PointE07(7,8,11)
        PointE07(7,8,11)
        >>> PointE07(1,"Inf",11)
        PointE07(1,"INF",11)
        """
        if isinstance(x,PointE07):
            self.x, self.y, self.p = x.x, x.y,x.p
        else:
            assert isprime(p) and p != 7:
            if isinstance(y,str):
                self.x, self.y, self.p = x%p, "inf",x.p
            else:
                assert((y**2)%p == (x**3+7)%p ):
                self.x, self.y , self.p = x%p, y%p, p



        
    def lDesPoints(p=47):
        """
        Renvoie la liste des Points de la courbe modulo p
        >>> PointE07.lDesPoints(5)
        [PointE07(0,"INF",5), PointE07(2,0,5), PointE07(3,2,5), 
        PointE07(3,3,5), PointE07(4,1,5), PointE07(4,4,5)]
        >>> len(PointE07.lDesPoints(11))
        12
        >>> PointE07(6,5,11) in (PointE07.lDesPoints(11))
        True
        """
        assert sontPremiersEntreEux(7,p) and p>2 estPremier(p),"ne rend"
        points = [PointE07(0, 'Inf', p)]
        for x in range(p):
            x37 = (x ** 3 + 7) % p
            for y in range(p):
                if (y ** 2) % p == x37:
                    points.append(PointE07(x, y, p))
        return points
    
    def __add__(self,other):
        """
        >>> PointE07(2,2,11)+PointE07(3,1,11)
        ...
        >>> (PointE07(3,"INF",47)+PointE07(3,9,47))+PointE07(3,"INF",47)
        """
        if self.y == 'Inf':
            return other
        if x1 == x2 and (y1 + y2) % p == 0:
            return PointE07('Inf', 'Inf', p)
        if x1 != x2:
            # Cas P ≠ Q
            inv = pow(x2 - x1, -1, p)
            lam = ((y2 - y1) * inv) % p
        else:
            # Cas P = Q (doublement)
            if y1 == 0:
                return PointE07('Inf', 'Inf', p)
            inv = pow(2 * y1, -1, p)
            lam = ((3 * x1 * x1) * inv) % p

        # Calcul des nouvelles coordonnées
        x3 = (lam * lam - x1 - x2) % p
        y3 = (lam * (x1 - x3) - y1) % p

        return PointE07(x3, y3, p)
    def double(self):
        >>> PointE07(2,2,11).double()

        return self + self
    
on va le chiffre sur le point M(4,4)
Alice a pour clé publique a= 5, A(4,7) et sa clé privé b = 8 B(3,1)

elle chiffre pour bob  MPrime = M+aB = (4,4)+5*(3,1) = (4,4)+(3,10) = (7)