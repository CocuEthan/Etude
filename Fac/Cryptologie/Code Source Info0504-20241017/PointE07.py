
def estPremier(n):
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n**0.5)+1, 2):
            if n % i == 0:
                return False
        return True

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
            assert estPremier(p) and p != 7
            if isinstance(y,str):
                self.x, self.y, self.p = x%p, "inf",x.p
            else:
                assert((y**2)%p == (x**3+7)%p )
                self.x, self.y , self.p = x%p, y%p, p

    def __str__(self):
        """
        >>> print(PointE07(3,9,47))
        (3,9)[47]
        """
        if self==0: return "O(à l'infini)"
        else: return f"({self.x},{self.y})[{self.p}]"
    def __repr__(self):
        """
        """
        if isinstance(self.y,str) :
            valy=f'"{self.y}"'
        else :
            valy=self.y
        return f"PointE07({self.x},{valy},{self.p})"
    def sontPremiersEntreEux(a, b):

        while b != 0:
            a, b = b, a % b
        return a == 1

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
        assert sontPremiersEntreEux(7,p) and p>2 and estPremier(p)
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
        p = self.p
        x1, y1 = self.x, self.y
        x2, y2 = other.x, other.y

        if x1 == x2 and (y1 + y2) % p == 0:
            return PointE07('Inf', 'Inf', p)
        if x1 == x2:
            if y1 == 0:
                return PointE07('Inf', 'Inf', p)
            s = (3 * x1 * x1) * pow(2 * y1, -1, p) % p
        else:
            s = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (s * s - x1 - x2) % p
        y3 = (s * (x1 - x3) - y1) % p
        return PointE07(x3, y3, p)
    def double(self):
        """
        >>> PointE07(2,2,11).double()
        """
        return self + self

    def __mul__(self,k):
        """
        >>> PointE07(6,5,11)*3
        PointE07(5,0,11)
        >>> PointE07(15,13,17)*0
        PointE07(0,"INF",17)
        >>> PointE07(15,13,17)*1
        PointE07(15,13,17)
        >>> PointE07(15,13,17)*(-1) #car 4=-13[17]
        PointE07(15,4,17)
        """
        self.x = (self.x*k)%self.p
        self.y = (self.y*k)%self.p
        if k<0:
            return -self * (-k)
        elif k < 0:
            return PointE07('Inf', 'Inf', self.p)
        elif k == 1:
            return PointE07(self)
        else:
            if k%2 ==0:
                return k/2*double(self)
            else:
                return self((k/2)*(self.double))

    def __rmul__(self,other):
        """
        >>> 2*(PointE07(3,"INF",47)+3*PointE07(3,9,47))+PointE07(3,"INF",47)
        PointE07(43,32,47)
        """
        return self * other


    def __eq__(self, other):
        if isinstance(other, PointE07):
            if self.x is None and other.x is None:
                return True
            return self.x == other.x and self.y == other.y and self.p == other.p
        elif isinstance(other, int):
            if other == 0:
                return self.x is None
            else:
                return False
        else:
            return False

    def __neg__(self):
        """
        >>> -PointE07(7,3,11)
        PointE07(7,8,11)
        """
        return PointE07(self.x, (-self.y) % self.p, self.p)


    def __sub__(self,other):
        """
        >>> PointE07(3,10,11)-PointE07(7,3,11)
        PointE07(4,7,11)
        >>> PointE07(3,9,47)-PointE07(3,9,47)==0
        True
        """
        return self + (-other)


def main():
    # Test __init__
    p2 = PointE07(7,8,11)
    print(f"PointE07(7,8,11): {p2}")

    p3 = PointE07(1,"Inf",11)
    print(f"PointE07(1,'Inf',11): {p3}")

    # Test __str__
    print("\nTesting __str__")
    p4 = PointE07(3,9,47)
    print("print(PointE07(3,9,47)):")
    print(p4)

    # Test lDesPoints
    print("\nTesting lDesPoints")
    points_p5 = PointE07.lDesPoints(5)
    print(f"PointE07.lDesPoints(5): {points_p5}")
    print(f"len(PointE07.lDesPoints(11)): {len(PointE07.lDesPoints(11))}")
    print(f"PointE07(6,5,11) in PointE07.lDesPoints(11): {PointE07(6,5,11) in PointE07.lDesPoints(11)}")

    # Test __add__
    print("\nTesting __add__")
    p5 = PointE07(2,2,11) + PointE07(3,1,11)
    print(f"PointE07(2,2,11) + PointE07(3,1,11): {p5}")

    p6 = (PointE07(3,"Inf",47) + PointE07(3,9,47)) + PointE07(3,"Inf",47)
    print(f"(PointE07(3,'Inf',47) + PointE07(3,9,47)) + PointE07(3,'Inf',47): {p6}")

    # Test double
    print("\nTesting double")
    p7 = PointE07(2,2,11).double()
    print(f"PointE07(2,2,11).double(): {p7}")

    # Test __mul__
    print("\nTesting __mul__")
    p8 = PointE07(6,5,11) * 3
    print(f"PointE07(6,5,11) * 3: {p8}")

    p9 = PointE07(15,13,17) * 0
    print(f"PointE07(15,13,17) * 0: {p9}")

    p10 = PointE07(15,13,17) * 1
    print(f"PointE07(15,13,17) * 1: {p10}")

    p11 = PointE07(15,13,17) * (-1)
    print(f"PointE07(15,13,17) * (-1): {p11}")  # Devrait donner PointE07(15,4,17)

    # Test __sub__
    print("\nTesting __sub__")
    p12 = PointE07(3,10,11) - PointE07(7,3,11)
    print(f"PointE07(3,10,11) - PointE07(7,3,11): {p12}")

    p13 = PointE07(3,9,47) - PointE07(3,9,47)
    print(f"PointE07(3,9,47) - PointE07(3,9,47): {p13}")
    print(f"PointE07(3,9,47) - PointE07(3,9,47) == 0: {p13 == 0}")

    # Test __eq__
    print("\nTesting __eq__")
    p14 = 3 * PointE07(6,5,11) == PointE07(5,0,11)
    print(f"3 * PointE07(6,5,11) == PointE07(5,0,11): {p14}")

    p15 = PointE07('Inf','Inf',47) == 0
    print(f"PointE07('Inf','Inf',47) == 0: {p15}")

    p16 = PointE07(3,9,47) == PointE07(3,'Inf',47) or PointE07(3,'Inf',47) == PointE07(3,9,47)
    print(f"PointE07(3,9,47) == PointE07(3,'Inf',47) ou PointE07(3,'Inf',47) == PointE07(3,9,47): {p16}")

    # Test __neg__
    print("\nTesting __neg__")
    p17 = -PointE07(7,3,11)
    print(f"-PointE07(7,3,11): {p17}")

    # Test __rmul__
    print("\nTesting __rmul__")
    p18 = 2 * (PointE07(3,"Inf",47) + 3 * PointE07(3,9,47)) + PointE07(3,"Inf",47)
    print(f"2*(PointE07(3,'Inf',47) + 3*PointE07(3,9,47)) + PointE07(3,'Inf',47): {p18}")

if __name__ == "__main__":
    main()
