print("Les opérations binaires en Python")
for (a,b) in [ (0,255) , (0b11110000 , 0xff) , (0b1010101 , 0x0f) ]:
    print(f"Le Xor : 0x{a:02x} ^ 0x{b:02x} = 0x{a^b:02x} = 0b{a:08b} ^ 0b{b:08b} = 0b{a^b:08b}" )
    print(f"Le Or  : 0x{a:02x} | 0x{b:02x} = 0x{a|b:02x} = 0b{a:08b} | 0b{b:08b} = 0b{a|b:08b}" )
    print(f"Le And : 0x{a:02x} & 0x{b:02x} = 0x{a&b:02x} = 0b{a:08b} & 0b{b:08b} = 0b{a&b:08b}" )
    print(f"Le >>  : 0x{a:02x} >> 2 = 0x{a>>2:02x} = 0b{a:08b} >>2 = 0b{a>>2:08b}" )
    print()