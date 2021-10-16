import sys
import os
import traceback
from Navigator import Navigator
from zipfile import ZipFile

def main():
    if sys.platform == 'win32': os.system('cls')
    else: os.system('clear')

    print("FAT and NTFS Reader")
    print("Operating System Project 01")
    print("VNU-HCMUS, 2021")
    print("By 19120615, 19120729, 19120688, 19120630") #TODO: thêm 2 đứa kia vào
    print()

    try:
        nav = Navigator()
        nav.select_volume()
        with ZipFile(nav.volume_path, 'r') as f:
            nav.initialize_root_directory(f)
            print('Root directory initialized!\n')
            nav.start_shell()
    except KeyboardInterrupt: 
        pass
    print('\nGood bye!')

if __name__ == '__main__':
    main()