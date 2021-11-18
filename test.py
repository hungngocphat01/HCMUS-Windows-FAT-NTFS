import os
from FAT import FATDirectory, FATFile, FATVolume
from LowLevel import *
from NTFS import NTFSVolume

fd = os.open(r'\\.\F:', os.O_RDONLY | os.O_BINARY)
f = os.fdopen(fd, mode='rb')

volume = NTFSVolume(f)
try:
    volume.readInfoEntry()
except:
    pass