import os
from FAT import FATDirectory, FATFile, FATVolume
from LowLevel import *

fd = os.open('../drive_fat.bin', os.O_RDONLY)
f = os.fdopen(fd, mode='rb')

volume = FATVolume(f)
volume.root_directory.build_tree()

for entry in volume.root_directory.subentries:
    print(entry.name)