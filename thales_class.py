
class Paquet:

    def __init__(self, file_path) -> None:
        
        self.path = file_path
        self.resullt = []
        self.bit_array = []
    
    #obligation de lire dans un premier temps le fichier binaire avec cette fonction, pour initialiser self.bit_array
    def read_binary_file(self) -> None:
        with open(self.path, 'rb') as f:
            binary_data = f.read()

        for byte in binary_data:
            for i in range(7, -1, -1):
                bit = (byte >> i) & 1
                self.bit_array.append(bit)

    def get_bit_array(self) -> list:
        return self.bit_array

    def order_bits(self):
        bytes_array = []
        i = 0
        while i < len(self.bit_array):
            bytes_array.append(self.bit_array[i:i+8])
            i = i + 8
        return bytes_array

    def readBit_asOctet(self, OctetDeb, OctetFin) -> list:
        toRead = self.bit_array[OctetDeb*8:OctetFin*8]
        return toRead
    
    def conv2dec(self):
        res = 0
        for i in range(0, len(array)):
            if array[i] == 1:
                res += 2**i
        return res