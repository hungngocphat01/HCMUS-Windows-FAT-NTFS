from lowlevel import * 
from AbstractBaseClasses import AbstractVolume, AbstractDirectory, AbstractFile

class FATVolume(AbstractVolume):
    # Override các abstract attribute 
    root_directory = None 
    size = None
    volume_label = None 
    file_object = None

    def __init__(self, file_object):
        """
        Constructor nhận vào 1 tham số là `file_object`, là một Python file object.
        
        TODO: constructor sẽ làm các yêu cầu sau:
        - Đọc các thông tin volume cần thiết: SC, SB, NF, ...
        - Đọc bảng FAT vào biến fat_table_buffer.
        - Đọc RDET vào biến rdet_buffer.
        - Dựng cây thư mục gốc từ RDET và lưu vào self.root_directory.
        """
        self.file_object = file_object
              
        # Đọc Sc (số sector cho 1 cluster): 1 byte tại 0x0D
        self.sc = read_number_file(self.file_object, '0x0D', 1)
        # Đọc Sb (số sector để dành trước bảng FAT): 2 byte tại 0x0E
        self.sb = ...
        # Đọc Nf (số bảng FAT): 1 byte tại offset 0x10
        self.nf = ...
        # Đọc Sf (số sector cho 1 bảng FAT): 4 byte tại 0x20
        self.sf = ...
        # Đọc chỉ số cluster bắt đầu của RDET: 4 byte tại 0x2C
        self.root_cluster = ...

        # Đọc bảng FAT (sf byte tại offset sb)
        self.fat_table_buffer = read_sectors(self.file_object, self.sb, self.sf)

        # Con trỏ đến thư mục gốc của volume này
        self.root_directory = None
        self.volume_label = ...

        # TODO: dựng cây thư mục gốc

    def access_fat_table(self):
        return self.fat_table_buffer[0:256]


    @staticmethod
    def read_cluster_chain(n) -> list: 
        """
        Hàm dò bảng FAT để tìm ra dãy các cluster cho một entry nhất định, bắt đầu từ cluster thứ `n` truyền vào.
        """
        # End-of-cluster sign
        eoc_sign = [dec('0ffffff8'), dec('0fffffff'), dec('ffffffff')]
        chain = [n]

        # TODO: viết hàm đọc một dãy các cluster, bắt đầu tại cluster thứ n. Biết nếu đọc được cluster có giá trị nằm trong mảng eoc_sign thì việc đọc sẽ kết thúc và ta phải trả về dữ liệu đọc được
        # Trong python, để kiểm ra phần tử k có nằm trong mảng arr hay không thì dùng cú pháp: 
        # if (k in arr): 
        
        return chain 
        
    @staticmethod
    def cluster_chain_to_sector_chain(cluster_chain) -> list: 
        sector_chain = []
        
        # TODO: 

        return sector_chain


class FATDirectory(AbstractDirectory):
    """
    Lớp đối tượng thể hiện một thư mục trong FAT
    """
    # Override các abstract attribute 
    volume = None 
    subentries = None 
    name = None 
    attr = None 
    sectors = None
    modified_date = None 
    modified_time = None

    def __init__(self, main_entry_buffer: bytes, volume: FATVolume):
        """
        Constructor nhận vào một buffer thể hiện các byte cho entry này.
        TODO: đọc các thông tin như như tên, kích thước, attribute, ...
        """
        self.volume = volume # con trỏ đến volume đang chứa thư mục này
        self.name = None 
        self.attr = [] # attribute đọc thành một mảng các chuỗi. Vd: ['Hidden', 'System', ...]
        self.subentries = None
        self.sectors = []
    
    def get_binary_content(self):
        pass

    def build_tree(self):
        """
        Dựng cây thư mục con cho thư mục này
        """
        pass

    def process_subentry(self, binary_data):
        """
        Hàm xử lý subentry với entry hiện tại
        Cần gán lại filename của entry hiện tại cho dữ liệu nhận được từ subentry truyền vào từ tham số
        """
        pass

class FATFile(AbstractFile):
    # TODO: Override các abstract attribute 

    # TODO: Constructor 
    pass 