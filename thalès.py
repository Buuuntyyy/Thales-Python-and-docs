from datetime import datetime
import binascii
import time
import struct

def read_binary_file_bits(path) -> list:
    with open(path, 'rb') as f:
        binary_data = f.read()

    return binary_data

path = "C:\\Users\\Utlisateur\\Desktop\\programmation\\thales\\ethernet.result_data"
print(read_binary_file_bits(path))

