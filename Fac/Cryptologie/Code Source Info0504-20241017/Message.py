from math import log
from random import randint
import arithmetiqueDansZ
import matplotlib.pyplot as plt
class Message(list):
    # Liste d'octets adaptée au cours de cryptographie.
    #On passe facilement d''un texte/image ou autre à un Message et vice versa
    lchr=[chr(k) for k in range(256)] #List des 256 caractères imprimables
    for k in list(range(32))+list(range(0x7f,0xa1))+[0xad]:  lchr[k]=chr(k+256)
    #dict pour transformer un caractère en octet
    dbin=dict()
    for k in range(256):
        dbin[lchr[k]]=k  #Dictionnaire faisant correspondre un caractère à un octet
    #Le mieux est d'éviter les caractères suivants dans les fichiers à traiter
    dbin['’']=dbin["'"] ; dbin['\n']=13 ; dbin['œ']=dbin['æ'] ; dbin['—']=dbin['-'] ; dbin['…']=dbin['.'];
    def __init__(self,param=[]):
        """param est soit une liste d'octets soit une chaine de caractère
        >>> Message([2,3])
        Message([ 0x02, 0x03])
        >>> Message("Trop tôt !")
        Message([ 0x54, 0x72, 0x6f, 0x70, 0x20, 0x74, 0xf4, 0x74, 0x20, 0x21])
        """
        if isinstance(param,str):
            #bc=param.encode('ascii', 'ignore') #byte
            #super().__init__([b for b in param.encode('ascii', 'ignore')])
            lb=[]
            for k,c in enumerate(param):
                if c in Message.dbin:
                    lb.append(Message.dbin[c])
                else:
                    lb.append(Message.dbin[' '])
                    print(f"{c=}:{ascii(c)}",end=' | ')
            super().__init__(lb)
            #super().__init__( [Message.dbin[c] for c in chaine] )
        else:
            lb=[]
            for b in param:
                assert Message.estOctet(b),"Les éléments d'un Message doivent convertible en octets"
                lb.append(int(b))
            super().__init__(lb )
    def to_string(self):
        """
        >>> Message("Trop tôt !").to_string()
        'Trop tôt !'
        """
        ch=""
        for b in self:
                if b==13:
                     ch+="\n"
                else:
                    ch+=Message.lchr[b]
        return ch
    def __hash__(self):
        """Renvoie un index afin de pouvoir mettre un message dans un dictionnaire
        >>> hash(Message([ 2,3]))
        131587
        """
        res=len(self)
        for b in self:
            res=(256*res+b)%0x10000000000000000
        return res

    def message_exemple(taille=1000,num=0):
        """Renvoie une instance Exemples de cette classe avec pour num :
        0: 255 fois 255 puis 254 fois 254 etc...
        1: un octet de chaque
        2: octets aléatoires
        3: 254 13 puis 255 14 puis 254 13 puis 255 14 ...
        4: 254 13 puis 255 14 puis 256 15 répétés
        5: et plus: 1000 fois un octet sur deux à 255
        """
        if num==0:
            data=[]
            for i in range(255,0,-1):
                data+=[i]*i
        elif num==1:
            data=[k for k in range(256)]
        elif num==2:
            data=[randint(0,255) for k in range(256)]
        elif num==3:
            data=[13]*254+[14]*255
        elif num==4:
            data=[13]*254+[14]*255+[15]*256
        else:
            data=[(k%2)*255 for k in range(256)]
        while len(data)<taille:
            data+=data
        return Message(data[:taille])

    def sauvegarde_dans_fichier(self,nomFic,verbose=False):
        "Enregistre dans un fichier nommé nomFic"
        if verbose:print(f"lecture du fichier :{nomFic}")

        if nomFic[-4:].upper()==".TXT":
            with open(nomFic,"wt") as f:
                    f.write(self.toString())
        else:
            with open(nomFic,"wb") as f:
                    for b in self:
                        f.write(bytes([b]))

    def message_depuis_fichier(nomFic,verbose=False):
        """renvoie un Message d'après les données du fichier nommé nomFic
        >>> Message([0,1,2,255]).sauvegarde_dans_fichier("MonMessage.bin")
        >>> Message.message_depuis_fichier("MonMessage.bin")
        Message([ 0x00, 0x01, 0x02, 0xff])
        """
        if verbose:print(f"lecture du fichier :{nomFic}")
        if nomFic[-4:].upper()==".TXT": #Si c'est un fichier texte'
            with open(nomFic, 'r') as f:
                txt = f.read()
            return Message(txt)
        else:
            with open(nomFic,"rb") as f:#Si c'est un fichier binaire'
                data = f.read()
                if verbose:print(f"data est de type : {type(data)}")
                b=Message(data)
                if verbose:print(f"data : {b}")
            return b
    def estOctet(val):
        """Renvoie true si val est un entier et si il se trouve dans [0..255]
        >>> Message.estOctet(255) and not(Message.estOctet(256))
        True
        >>> not(Message.estOctet(-1))and not(Message.estOctet("coucou")) and not(Message.estOctet([128,12]))
        True
        """
        return isinstance(val,int) and val>=0 and val <=255

    def ajouteOctet(self,data):
        """Ajoute un octet ou une liste d'octets tout en vérifiant la validité des données
        >>> a=Message([1,2,3,4]); a.ajouteOctet(10); a
        Message([ 0x01, 0x02, 0x03, 0x04, 0x0a])
        >>> a.ajouteOctet([11,12]);a
        Message([ 0x01, 0x02, 0x03, 0x04, 0x0a, 0x0b, 0x0c])
        """
        if isinstance(data,list):
            for oc in data:
                assert Message.estOctet(oc)
                self+=[oc]
        else:
            assert Message.estOctet(data)
            self+=[data]
    def ajouteMot64Bits(self,mot):
        """Ajoute un mot entier de 64bits
        >>> lb=Message([1,2,3,4]); lb.ajouteMot64Bits(65537);lb.ajouteMot64Bits(0x56789abc56789abc); lb
        Message([ 0x01, 0x02, 0x03, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x56, 0x78, 0x9a, 0xbc, 0x56, 0x78, 0x9a, 0xbc])
        """
        assert isinstance(mot,int) and mot>=0 and mot<0x10000000000000000,"Erreur mot de 32 bits exigé"
        val=mot
        l=[]
        for _ in range(8):
            l=[val%256]+l
            val//=256
        self+=l
    def ajouteMot32Bits(self,mot):
        """Ajoute un mot entier de 32bits
        >>> lb=Message([1,2,3,4]); lb.ajouteMot32Bits(65537);lb.ajouteMot32Bits(0x56789abc); lb
        Message([ 0x01, 0x02, 0x03, 0x04, 0x00, 0x01, 0x00, 0x01, 0x56, 0x78, 0x9a, 0xbc])
        """
        assert isinstance(mot,int) and mot>=0 and mot<4294967296,"Erreur mot de 32 bits exigé"
        div=256
        val=mot
        l=[]
        for _ in range(4):
            l=[val%256]+l
            val//=256
        self+=l
    def ajouteMot40Bits(self,mot):
        """Ajoute un mot entier de 32bits
        >>> lb=Message([1,2,3,4]); lb.ajouteMot40Bits(65537);lb.ajouteMot40Bits(0x3456789abc); lb
        Message([ 0x01, 0x02, 0x03, 0x04, 0x00, 0x00, 0x01, 0x00, 0x01, 0x34, 0x56, 0x78, 0x9a, 0xbc])
        """
        assert isinstance(mot,int) and mot>=0 and mot<1099511627776,"Erreur mot de 40 bits exigé"
        div=256
        val=mot
        l=[]
        for _ in range(5):
            l=[val%256]+l
            val//=256
        self+=l

    def lisOctet(self,pos):
        """Lis un octet et incrémente pos
        Exemple d'uUtilisation : val,pos=monMes.lisOctet(pos) comme suit
        >>> Message([10,20,30,40]).lisOctet(2)
        (30, 3)
        """
        return self[pos],pos+1
    def lisMot32Bits(self,pos):
        """Lis un mot de 32bits et incrémente pos de 4
            Complète éventuellement par des 0
            >>> val,pos = Message([1,2,3,4 , 0,1,0,0 , 0,1]).lisMot32Bits(4)

            >>> val,pos
            (65536, 8)
            >>> Message([0xab,0xcd,0xab,0xcd,0xab,0xcd,0xab,0xcd]).lisMot32Bits(4)
            (2882382797, 8)
            """
        l=self[pos:pos+4]
        if len(l)<4:l+=[0]*(4-len(l))
        return l[3]+256*(l[2]+256*(l[1]+256*l[0])),pos+4
    def lisMot40Bits(self,pos):
        """Lis un mot de 40bits et incrémente pos de 5
            Complète éventuellement par des 0
        >>> Message([1,2,3,1,1, 0,0,0,1,0]).lisMot40Bits(5)
        (256, 10)
        >>> hex(Message([0xab,0xcd,0xab,0xcd,0xab,0xcd,0xab,0xcd,0xab,0xcd,0xab,0xcd]).lisMot40Bits(4)[0])
        '0xabcdabcdab'
        """
        l=self[pos:pos+5]
        if len(l)<5:l+=[0]*(5-len(l))
        res=0
        for v in l:
            res=(res<<8)+v
        return res,pos+5

    def lisMot64Bits(self,pos):
        """Lis un mot de 64bits et incrémente pos de 8
            Complète éventuellement par des 0
            >>> Message([1,2,3,4 , 0,0,0,0 , 0,1,0,0]).lisMot64Bits(4)
            (65536, 12)
            >>> hex(Message([0xab,0xcd,0xab,0xcd,0xab,0xcd,0xab,0xcd,0xab,0xcd,0xab,0xcd]).lisMot64Bits(4)[0])
            '0xabcdabcdabcdabcd'
            """
        l=self[pos:pos+8]
        if len(l)<8:l+=[0]*(8-len(l))
        res=0
        for v in l:
            res=(res<<8)+v
        return res,pos+8
    def __str__(self):
        """Renvoie une chaine de caractère permettant de visualiser Message self
        >>> str(Message([12,128]))
        '2 octets : 0c80'
        """
        res=f"{len(self)} octets : "
        if len(self)<=150 :
            for oc in self:
                res+=f"{oc:02x}"
        else:
            for oc in self[:100]:
                res+=" "+f"{oc:02x}"
            res+="........"
            for oc in self[-50:-1]:
                res+=" "+f"{oc:02x}"
        return res
    def __repr__(self):
        """Renvoie une chaine de caractère représentant TOUTES les données du Message self
        sous la forme d'un appel à son constructeur ex: Message([ 0x57, 0x26, 0xfd])
        >>> Message("Bonjour")
        Message([ 0x42, 0x6f, 0x6e, 0x6a, 0x6f, 0x75, 0x72])
        """

        res="Message(["
        for oc in self:
            res+=" "+f"0x{oc:02x}," # https://docs.python.org/fr/3/library/string.html
        return res[:-1]+ "])"
    def __eq__(self,other):
        """Renvoie True lorsque les octets sont égaux deux à deux
        >>> Message([ 0xcb, 0xba])==Message([ 0xcb, 0xba])
        True
        >>> Message("Bon")==Message([ 0x42, 0x6f, 0x6e])
        True
        >>> Message([ 0xcb, 0xba])==Message([ 0xcb, 0xbb])
        False
        """
        #todo:  voir le super pour comparé les références
        if len(self)!=len(other): return False
        k,n = 0, len(self)
        res= True
        while res and k<n:
            res= (self[k]==other[k])
            k+=1
        return res

    def nbOctets(val):
        """Renvoie le nb d'octets nécessaire pour coder l'entier val
        >>> Message.nbOctets(12) , Message.nbOctets(0) , Message.nbOctets(110000)
        (1, 1, 3)
        """
        if val==0:return 1
        return  int(log(val,256)+1)
    def ajouteLongueValeur(self,val):
        """Ajoute une valeur entière de taille qulconque de telle façon qu'elle
        puisse être récupérable par lisLongueValeur"""
        nbo=Message.nbOctets(val)
        self.ajouteOctet(nbo) #Nb d 'octets de la longueur du fichier
        l=val
        for k in range(nbo):
            self.ajouteOctet(l%256)
            l=l//256
    def lisLongueValeur(self,pos):
        """Renvoie tout ce qu'il faut pour enregistrer/ajouter une valeur entière
        de taille qulconque"à la position pos
        Renvoie cette valeur et la nouvelle valeur de pos
        >>> monMes=Message([12,13])        ; monMes.ajouteOctet(15)
        >>> monMes.ajouteLongueValeur(100) ; monMes.ajouteLongueValeur(1000)
        >>> pos=2
        >>> v0,pos=monMes.lisOctet(pos)
        >>> v1,pos=monMes.lisLongueValeur(pos)
        >>> v2,pos=monMes.lisLongueValeur(pos)
        >>> v0,v1,v2
        (15, 100, 1000)
        """
        nbo=self[pos]
        pos+=1
        val=0
        for k in range(nbo):
            val+=self[pos]*256**k
            pos+=1
        return val,pos


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    m0=Message("Bonjour les amis !")
    print(m0)

    m1=Message([1,2,3,3,3,3,4,8,8,128,253,253,253,253,253,253,254,254,254,255])
    print(m1)
    m2=Message.message_depuis_fichier("Germinal.txt")
    print(m2)
