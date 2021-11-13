import sys 
import os
import zipfile
from FAT import *
from NTFS import *
from VirtualZip import *

class Navigator:
    """
    Lớp đối tượng hỗ trợ duyệt cây thư mục bằng giao diện dòng lệnh
    """

    def title_print(self, *args):
        LEADING = '======================='
        print(LEADING, *args, LEADING)

    def __init__(self):
        self.platform =  os.name
        if self.platform not in ['nt', 'posix']:
            raise AttributeError('Unsupported platform. Only supports Windows NT and POSIX.')
        # Tham chiếu đến object thư mục hiện tại 
        self.current_dir: AbstractDirectory = None 
        # Lịch sử duyệt (FIFO)
        self.dir_hist = []

    def select_volume(self):
        """
        Chọn phân vùng cần thiết 
        """
        self.title_print('PLEASE SELECT YOUR VOLUME')
        print('NOTICE: The program detected that you are using', end=' ')
        if self.platform == 'nt':
            print('Windows NT')
        else: 
            print('POSIX (Linux, OS X, BSD, ...)')

        print('Please enter the volume path in the FOLLOWING CONVENTION.')
        if self.platform == 'nt':
            print('Enter one CAPITAL LETTER. Example: C, D, E, ...')
        else: 
            print('Enter the path to your block device. Example: /dev/sda1, /dev/disk1s1, ...')

        print('\nTIP: You can also enter the path to a raw disk image.')
        print('Also make sure that you have sufficient permission to read the block device.')

        volume_path = input('=> Enter your drive path: ')

        if not os.path.exists(volume_path):
            raise FileNotFoundError('Drive path does not exist')
        self.volume_path = volume_path

    def create_fileobject(self):
        if self.volume_path.endswith('.zip'):
            return ZipFile(self.volume_path, 'r')
        else: 
            if os.name == 'nt':
                fd = os.open(self.volume_path, os.O_RDONLY | os.O_BINARY)
            else: 
                fd = os.open(self.volume_path, os.O_RDONLY)
            return os.fdopen(fd, 'rb')

    def initialize_root_directory(self, file_object):
        """
        Tạo một thể hiện cụ thể của AbstractDrive từ tham chiếu file nhận được.
        Dựng cây thư mục gốc
        """
        # Detect zip file 
        if isinstance(file_object, zipfile.ZipFile):
            self.volume = TestVolume(file_object)
            self.volume.root_directory.build_tree()
            self.current_dir = self.volume.root_directory
            return 

        # Detect FAT32 
        # Read boot sector
        bootsec_buffer = read_sectors(file_object, 0, 1)
        fat32_volfs = read_bytes_buffer(bootsec_buffer, 0x52, 8)
        if b'FAT32' in fat32_volfs:
            self.volume = FATVolume(file_object)
            print('FAT32 detected.')
        # TODO: Detect NTFS
        else: 
            raise AttributeError('Filesystem not supported')

        self.volume.root_directory.build_tree()
        self.current_dir = self.volume.root_directory


    def generate_table_view(self):
        """
        Hàm để tạo ra một bảng thống kê tập tin
        """
        entry_info_list = []
        max_width = dict()

        def update_max_width(key, value):
            if key not in max_width:
                max_width[key] = len(str(value)) + 4
            elif max_width[key] < len(str(value)): 
                max_width[key] = len(str(value)) + 4

        for entry in self.current_dir.subentries:
            entry_info = {
                'name': entry.name, 
                'size': 0 if isinstance(entry, AbstractDirectory) else entry.size, 
                'attr': entry.describe_attr(),
                'sector': '' if len(entry.sectors) == 0 else entry.sectors[0]
            }
            if entry_info['name'] in ('.', '..'):
                continue
            
            entry_info_list.append(entry_info)

            update_max_width('name', entry_info['name'])
            update_max_width('attr', entry_info['attr'])
            update_max_width('sector', entry_info['sector'])

            if isinstance(entry, AbstractFile):
                update_max_width('size', entry.size)
            else:
                update_max_width('size', 5)
        
        format_str = '{0: <%d} {1: <%d} {2: <%d} {3: <%d}\n' % (
            max_width['name'], max_width['size'], max_width['attr'], max_width['sector'])

        print_str = ''
        print_str += format_str.format('name', 'size', 'attr', 'sector')
        for entry in entry_info_list:
            print_str += format_str.format(entry['name'], entry['size'], entry['attr'], entry['sector'])

        return print_str
    
    def list_entries(self):
        """
        Handler function for 'ls'
        """
        assert self.current_dir != None, 'An error occurred. Pointer to current directory is null'
        self.current_dir.build_tree()

        table = self.generate_table_view()
        print(table)
    
    def history_list(self):
        """
        Handler funciton for 'history list'
        """
        if len(self.dir_hist) == 0:
            print('History is empty')
            return 

        for entry in self.dir_hist:
            print(entry.name)

    def history_go_back(self):
        """
        Handler function for 'history pop'
        """
        if len(self.dir_hist) == 0:
            print('History is empty')
            return 

        last_entry = self.dir_hist[-1]
        self.dir_hist.pop()
        self.current_dir = last_entry

    def go_into_subdir(self, subdir_name):
        """
        Handler function for 'cd'
        """
        for entry in self.current_dir.subentries: 
            if entry.name == subdir_name:
                if isinstance(entry, AbstractFile):
                    print('Cannot cd into a file!')
                else:
                    self.dir_hist.append(self.current_dir)
                    self.current_dir = entry 
                    return
        print('Bad command or filename:', subdir_name)


    def show_help(self):
        print('fkfbrwsrsh (fake file browser shell) version 1.0\n' +
        'By 19120615, 19120729, 1912630, 19120688 @ VNU-HCMUS\n' +
        '\n' +
        '- ls: list all entries in current directory.\n' +
        '- cd <dir>: go into directory <dir> (only supports 1 level).\n' +
        '- dump <file>: dump content of file <file> into program working directory.\n' +
        '- tree: recursively list all files of current directory.\n' +
        '- history list: list browsing history.\n' +
        '- history pop: go back to previously visited directory.\n' +
        '- back: alias for history pop.\n' +
        '\n' +
        'Commands are CASE-SENSITIVE!\n')

    def show_tree(self):
        # TODO: implement tree command
        pass

    def dump_file(self, filename):
        for file in self.current_dir.subentries:
            if file.name == filename:
                binary_data: bytes = file.dump_binary_data()
                with open(filename, mode='wb') as out_file:
                    print('Dumping', file.size, 'bytes to', filename, '...')
                    out_file.write(binary_data)
                    print('Done.')
                return 
        raise FileNotFoundError('Bad filename: ' + filename)

    def read_text_file(self, filename):
        assert filename != None, 'Filename not specified.'

        for file in self.current_dir.subentries:
            if file.name == filename:
                binary_data: bytes = file.dump_binary_data()
                string_data = binary_data.decode('utf8')
                print('\n', string_data, '\n')
                return 
        raise FileNotFoundError('Bad filename: ' + filename)

    def start_shell(self):
        if self.current_dir == None: 
            raise RuntimeError('You did not select the root directory. This is due to a bug in the program')
        
        print('Type help for help.')
        while True: 
            try:
                user_inp = input('%s> ' % self.current_dir.name)

                # Parse command
                user_inp_lst = user_inp.split(' ', 1)
                if (len(user_inp_lst)) == 0:
                    return

                command_verb = user_inp_lst[0]
                if len(user_inp_lst) == 1:
                    command_arg = None 
                else: 
                    command_arg = user_inp_lst[1]
                
                # Process command
                if command_verb == 'help':
                    self.show_help()
                elif command_verb == 'cd':
                    self.go_into_subdir(command_arg)
                elif command_verb == 'ls':
                    self.list_entries()
                elif command_verb == 'dump':
                    self.dump_file(command_arg)
                elif command_verb == 'cat':
                    self.read_text_file(command_arg)
                elif command_verb == 'history':
                    if command_arg == 'list':
                        self.history_list()
                    elif command_arg == 'pop':
                        self.history_go_back()
                    else:
                        print('Action not supported. Type help for help.')
                elif command_verb == 'back':
                    self.history_go_back()
                elif command_verb == 'tree':
                    raise NotImplementedError('Command not implemented!')
                elif command_verb == 'exit':
                    return
                else: 
                    print('Bad command: %s. Type help for help.' % command_verb)
            except Exception as e:
                print('An error occurred:', e)
                    