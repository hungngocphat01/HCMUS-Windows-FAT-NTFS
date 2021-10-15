import sys 
from FAT import *
from NTFS import *
from NavigatorTest import *

class Navigator:
    """
    Lớp đối tượng hỗ trợ duyệt cây thư mục bằng giao diện dòng lệnh
    """

    def title_print(self, *args):
        LEADING = '======================='
        print(LEADING, *args, LEADING)

    def __init__(self):
        self.platform =  sys.platform
        if self.platform not in ['win32', 'linux']:
            raise 'Unsupported platform. Only supports win32 and linux'

    def select_volume(self):
        """
        Chọn phân vùng cần thiết 
        """
        self.title_print('PLEASE SELECT YOUR VOLUME')
        print('NOTICE: The program detected that you are using', self.platform)
        print('Please enter the volume path in the FOLLOWING CONVENTION.')
        if self.platform == 'win32':
            print('Enter one CAPITAL LETTER. Example: C, D, E, ...')
        else: 
            print('Enter the path to your block device. Example: /dev/sda1, /dev/sdc, ...')

        print('\nTIP: You can also enter the path to a raw disk image.')
        print('Also make sure that you are running the program with ROOT/ADMIN role if youre reading a physical volume.')
        print('!!!NAIVE DEVELOPERS WARNING: DO NOT USE ON IMPORTANT PARTITIONS!!!!')

        print('\nWe do not check for a wrong drive path, use with caution.')
        volume_path = input('=> Enter your drive path:')


