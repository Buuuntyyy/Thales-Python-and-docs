import datetime
import binascii
import time
import struct
import threading

_resultat = []
path = "C:\\Users\\barfl\\Desktop\\saé_thalès\\ethernet.result_data"
path_out = "C:\\Users\\barfl\\Desktop\\output.txt"
path2 = "C:\\Users\\Utlisateur\\Desktop\\programmation\\thales\\ethernet.result_data"

def read_binary_file_bits(path) -> list:
    with open(path, 'rb') as f:
        binary_data = f.read()

    bit_array = []
    for byte in binary_data:
        for i in range(7, -1, -1):
            bit = (byte >> i) & 1
            bit_array.append(bit)
    return bit_array

"""Non utilisé pour l'instant"""
#fonction permettant de trier la liste de bits en octets (liste de 8 bits)
def order_octet(bit_array) -> list:
    bytes_array = []
    i = 0
    while i < len(bit_array):
        bytes_array.append(bit_array[i:i+8])
        i = i + 8
    return bytes_array

"""Non utilisé pour l'instant"""
#fonction permettant de lire les octets préalablement triés, dans un intervalle donné par leur index respectif
def read_octet(bytes_array, num_octet_deb, num_octet_fin) -> list:
    octet = bytes_array[num_octet_deb:num_octet_fin]
    #print(f"octet = {octet}")
    #bin2deci(octet)
    return octet

#permet de lire le fichiers en considérant des groupes de bits comme octet.
def readBitsASoctet(liste, OctetDeb, OctetFin) -> list:#l'octet 1 se trouve à l'index 0
    toRead = liste[OctetDeb*8:OctetFin*8]
    #toRead = toRead[::-1] #on inverse la liste pour avoir les bonnes puissances de 2
    #print(type(toRead))
    return toRead

#convertit les octets en entrée en décimal et retourne cette valeur
def conv2dec(array) -> int:
    res = 0
    for i in range(0, len(array)):
        if array[i] == 1:
            res += 2**i
    #print(res)
    return res

#nombre de seconde depuis 1 janvier 1970 --> passer en float double
def read_date(path) -> str:
    with open(path, 'rb') as f:
        binary_data = f.read()
    date = struct.unpack('>d', binary_data[8:16])
    date_base = datetime.datetime(1970,1,1,0,0,0)
    date_data = datetime.timedelta(seconds=date[0])
    date_result = date_base + date_data
    return date_result.strftime("%d:%m:%Y:%H:%M:%S")

#permet de lire la taille du paquet en octet
def taille_paquet(liste, decalage) -> int:
    print(f"{decalage} dans taille")
    array = readBitsASoctet(liste, decalage + 24, decalage + 28)
    print(array)
    array = array[::-1]
    print(bin2hex(array))
    return conv2dec(array)

def lire_addr_mac(liste, decalage) -> int: #octet 28 à 40
    bdata = readBitsASoctet(liste, decalage + 28, decalage + 40)
    hex = bin2hex(bdata)
    addr1 = hex[0:13]
    addr2 = hex[12:26]
    s_addr = ""
    d_addr = ""

    for i in range(0, 12, 2):
        s_addr += addr1[i:i+2] + ":"
        d_addr += addr2[i:i+2] + ":"
    s_addr = s_addr[0:17]
    d_addr = d_addr[0:17]

    return s_addr, d_addr

def lire_addr_ip(liste, decalage) -> str: #octet 54 à 62
    addrIp1 = ""
    addrIp2 = ""
    bdata = readBitsASoctet(liste, decalage + 54, decalage + 62)
    addresses = conv_ip(bdata)
    if addresses == None:
        return None
    else:
        s_addr = addresses[0]
        d_addr = addresses[1]
        for element in s_addr:
            addrIp1 += str(element) + "."
        for element in d_addr:
            addrIp2 += str(element) + "."
        addrIp1 = addrIp1[0:13]
        addrIp2 = addrIp2[0:13]

        return addrIp1, addrIp2

#lire packet date
def packet_date(fields_liste, decalage):
    packet_dateListe = []
    for i in range(decalage + 19,decalage + 22):
        packet_dateListe.append(fields_liste[i])


def conv_ip(liste) -> tuple:

    if len(liste) != 64:
        return None
    else:
        octet_val_ip1 = []
        ipList = order_octet(liste)
        #print(ipList)
        val = 0
        octet_val_ip2 = []

        for i in range(0, 4):
            val = 0
            inv = ipList[i][::-1]
            #print(f"octet : {inv}")
            for i in range(0, 8):
                if inv[i] == 1:
                    val += 2**i
            octet_val_ip1.append(val)
        
        for i in range(4, 8):
            val = 0
            inv = ipList[i][::-1]
            #print(f"octet : {inv}")
            for i in range(0, 8):
                if inv[i] == 1:
                    val += 2**i
            octet_val_ip2.append(val)    
        return octet_val_ip1, octet_val_ip2      

def lire_fields(liste, decalage) -> list:
    fields = []
    fields.append(readBitsASoctet(liste, decalage + 40, decalage +42)) #field 1
    fields.append(readBitsASoctet(liste, decalage +42, decalage +44)) #field 2
    fields.append(readBitsASoctet(liste, decalage +44, decalage +46)) #field 3
    fields.append(readBitsASoctet(liste, decalage +46, decalage +48)) #field 4
    fields.append(readBitsASoctet(liste, decalage +48, decalage +50)) #field 5
    fields.append(readBitsASoctet(liste, decalage +50, decalage +51)) #field 6
    fields.append(readBitsASoctet(liste, decalage +51, decalage +52)) #field 7
    #octets IP et à ignorer
    fields.append(readBitsASoctet(liste, decalage +62, decalage +64)) #field 9
    fields.append(readBitsASoctet(liste, decalage +64, decalage +66)) #field 10
    fields.append(readBitsASoctet(liste, decalage +66, decalage +68)) #field 11

    #octets 68 à 70 => ignorer, 70 à 74 séparés en plusieurs fieds/FT
    #octets 70 à 72 (71 et 72 inclus) : fields 14, 16, 17, 18
        #field 14 : 1 bit (4ème bit de l'octet)
    fields.append(readBitsASoctet(liste, decalage +71, decalage +72)) # => bit 564 #liste[563]
        #field 16 : 3 bits (Bits 6 à 8 inclus)
    fields.append(readBitsASoctet(liste, decalage +71, decalage +72)) #liste[564:566]
        #field 17 : 3 bits (Bits 9 à 11 inclus)
    fields.append(readBitsASoctet(liste, decalage +71, decalage +72)) #liste[567:569]
        #field 18 : 5 bits (Bits 12 à 16 inclus)
    fields.append(readBitsASoctet(liste, decalage +71, decalage +72)) #liste[570:574]
    #otets 72 à 74 (73 et 74 inclus) : field 20
        #field 20 : 14 bits (bits 3 à 16 inclus)
    fields.append(readBitsASoctet(liste, decalage +71, decalage +72)) #liste[578:594]

    fields.append(readBitsASoctet(liste, decalage +74, decalage +76)) #field 21

    #field 22 à ignorer

    #octets 76 à 77 (77 inclu seulement) : field 23, 25, 26
        #field 23 : 1 bit (5eme bit)
    fields.append((liste[decalage +613:decalage +614]))
        #field 25 : 1 bit (7eme bit)
    fields.append((liste[decalage +614:decalage +615]))
        #field 26 : 1 bit (8eme bit)
    fields.append((liste[decalage +615:decalage +616]))
    #octets 77 à 78 (78 inclu seulement): field 27, 28
        #field 27 : 2 bits (2 premiers bits), ne pas lire
    #fields.append((liste[decalage +616:decalage +618]))
        #field 28 : 6 bits (6 derniers bits)
    fields.append((liste[decalage +618:decalage +623]))
    #octet 78 à 80 (79 et 80 inclus) : fields 29, 30
        #field 29 : 6 bits (6 premiers bits)
    fields.append((liste[decalage +624:decalage +629]))
        #field 30 : 10 bits (10 derniers bits)
    fields.append((liste[decalage +630:decalage +639]))
    #octet 81 à ignorer

    fields.append(readBitsASoctet(liste, decalage +81, decalage +82)) #octet 82 -> field 32 & FT_1
    fields.append(readBitsASoctet(liste, decalage +82, decalage +84)) #octet 83 et 84 === field 33
    fields.append(readBitsASoctet(liste, decalage +84, decalage +86)) #octets 85 et 86 === field 34 #83 à 88 = packet_date
    fields.append(readBitsASoctet(liste, decalage +86, decalage +88)) #octets 87 et 88 === field 35

    return fields

def lire_FT(liste, decalage) -> list:
    FT_val = []
    FT_val.append(liste[decalage +172:decalage +176]) #FT_0
    FT_val.append(liste[decalage +645:decalage +653]) #FT_1
    FT_val.append(liste[decalage +570:decalage +575]) #FT_2
    FT_val.append(liste[decalage +617:decalage +623]) #FT_3
    FT_val.append(liste[decalage +623:decalage +629]) #FT_4
    FT_val.append(liste[decalage +567:decalage +580]) #FT_5
    FT_val.append(liste[decalage +563]) #FT_7

    return FT_val

def lire_FT6(FT_liste, fields_liste) -> list:
    FT6 = []
    FT6.append(FT_liste[6])
    FT6.append(FT_liste[2])
    FT6.append(FT_liste[3])
    FT6.append(FT_liste[4])
    FT6.append(fields_liste[21])
    return FT6

#permet de convertir un octet en décimal
def bin2deci(liste) -> int:
    val = 0
    for octet in liste:
        inv = octet[::-1]
        #print(f"octet après : {inv}")
        for i in range(0, len()):
            if inv[i] == 1:
                val += 2**i
                #print(f"val : {2**i}")
                #print(f"dans val on a : {val}")
    #print(f"val = {val}")
    return val

#permet de convertir 1 octet donné en hexadécimal, la liste en entrée doit être préalablement inversée
def bin2hex(byte) -> str:
    chaine = ""
    #print(f"byte = {byte}")
    res1 = 0

    for i in range(0, len(byte), 4):
        temp = byte[i:i+4]
        temp = temp[::-1]
        j = 0
        res1 = 0
        for n in temp:
            res1 += n * 2**j
            j += 1
        hexval = hex(res1)
        #print(f"demi octet : {temp}, val : {hexval[2::]}")

        chaine += hexval[2::]
    
    return chaine

def is_UDP():
    file = read_binary_file_bits(path)
    test = file[40*8:42*8]
    #print(test)
    #print(test)
    #print(bin2hex(test))
    t = bin2hex(test)
    #print(t)
    return t == "0800"

def ecrire(result):
        fic = open("C:\\Users\\barfl\\Documents\\GitHub\\thales\\output.txt", "a")
        for element in result:
            fic.write(str(element))
        fic.close()

def extracteur() -> tuple:
    decalage_lec = 0
    file_bin = read_binary_file_bits(path) #on garde le fichier binaire en mémoire pour rapidement y accéder et ne le lire qu'une seule fois
    i = 0
    while True:
        print(f"{decalage_lec}==============")
        i += 1
        print(i)
        ips = lire_addr_ip(file_bin, decalage_lec)
        if ips == None:
            return 0
        else:
            date_exec = read_date(path)
            size = taille_paquet(file_bin, decalage_lec)
            macs = lire_addr_mac(file_bin, decalage_lec)
            fields = lire_fields(file_bin, decalage_lec)
            FT = lire_FT(file_bin, decalage_lec)
            FT6 = lire_FT6(file_bin, fields)
            _resultat.append((date_exec, size, macs, ips, fields, FT, FT6))
        decalage_lec += size
        print(decalage_lec)


def extracteur_ARP(fic, decalage):
    date = read_date(path)
    macs = lire_addr_mac(fic, decalage)
    ips = lire_addr_ip(fic, decalage)
    date = packet_date(fic, decalage)
    fields = lire_fields(fic, decalage)

    _resultat.append((date, macs, ips, fields))

def lire_rep(path):
    entete = []
    fic = open("C:\\Users\\barfl\\Desktop\\saé_thalès\\Vt_DEMO_mem_observability.rep")
    for i in range(0, 28):
        line = fic.readline()
        entete.append(line)
    rep = [entete[7][39:len(entete[7])], entete[8][39:len(entete[8])], entete[9][39:len(entete[9])], 
           entete[10][39:len(entete[10])], entete[14][39:len(entete[14])], entete[27][39:len(entete[27])]]
    print(rep)

    #le fichier rep doit être exactement comme donné lors des test. Aucun titre de ligne ne doit être changé

if __name__ == "__main__":

    #print(f"taille : {len(_resultat)}")

    extracteur()
    fic = open(path_out, "w")
    for element in _resultat:
        fic.write(str(element) + "\n")
    fic.close()
    print("fini")

    #print(_resultat[262])
