import os
from FAT import FATDirectory, FATFile, FATVolume
from LowLevel import *

fd = os.open('../drive.bin', os.O_RDONLY)
f = os.fdopen(fd, mode='rb')

volume = FATVolume(f)
volume.root_directory.build_tree()

for dir in volume.root_directory.subentries:
    dir.build_tree()