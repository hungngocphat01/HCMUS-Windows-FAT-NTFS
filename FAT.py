from LowLevel import * 
from AbstractBaseClasses import AbstractVolume, AbstractDirectory, AbstractFile

class FATVolume(AbstractVolume):
    # Override các abstract attribute 
    # Trong python để "khai báo" là mình sẽ override các abstract attribute của class cha thì mình khởi tạo giá trị đầu cho nó (ở đây khởi tạo là None [giống null của C++])
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

        # Đọc boot sector
        bootsec_buffer = read_sectors(self.file_object, 0, 1) # đọc sector thứ 0 (sector đầu tiên) và đọc 1 sector

        # Đọc magic number 0xAA55
        # Đọc 2 byte tại offset 0x1FA
        magic_number = read_number_buffer(bootsec_buffer, 0x1FE, 2)
        assert magic_number == 0xAA55, "Invalid boot sector: 0xAA55 not found at offset 0x1FA"

              
        # Đọc Sc (số sector cho 1 cluster): 1 byte tại 0x0D
        self.sc = read_number_buffer(bootsec_buffer, 0x0D, 1)
        # Đọc Sb (số sector để dành trước bảng FAT): 2 byte tại 0x0E
        self.sb = ...
        # Đọc Nf (số bảng FAT): 1 byte tại offset 0x10
        self.nf = ...
        # Đọc Sf (số sector cho 1 bảng FAT): 4 byte tại 0x20
        self.sf = ...
        # Đọc chỉ số cluster bắt đầu của RDET: 4 byte tại 0x2C
        self.root_cluster = ...
        # Chỉ số sector bắt đầu của data 
        self.data_begin_sector = self.sb + self.nf * self.sf

        # Đọc bảng FAT (sf byte tại offset sb)
        self.fat_table_buffer = read_sectors(self.file_object, self.sb, self.sf)

        # Con trỏ đến thư mục gốc của volume này
        # TODO: đọc RDET và tạo thư mục gốc (làm bên class FATDirectory)
        self.root_directory = None
        self.volume_label = ...


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
        """
        Hàm chuyển dãy các cluster sang dãy các sector
        Biết rằng 1 cluster có Sc sectors 
        Với cluster k thì nó bắt đầu chiếm từ cluster thứ `data_begin_sector + k * Sc`, và chiếm Sc sectors
        """
        sector_chain = []
        
        # TODO

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
    path = None

    def __init__(self, main_entry_buffer: bytes, parent_path: str, volume: FATVolume):
        """
        Constructor nhận vào một buffer thể hiện các byte cho entry này.
        TODO: đọc các thông tin như như tên, kích thước, attribute, ...
        """
        self.volume = volume # con trỏ đến volume đang chứa thư mục này
        self.name = None 
        self.attr = [] # attribute đọc thành một mảng các chuỗi. Vd: ['Hidden', 'System', ...]
        self.subentries = None
        self.sectors = []
        
        # self.path là đường dẫn của thư mục hiện tại = parent_path + '/' + self.name
        # set biến này sau khi đọc được tên của entry

    def build_tree(self):
        """
        Dựng cây thư mục cho thư mục này (đọc các sector trong mảng `self.sectors` được SDET rồi xử lý)
        """
        if self.subentries != None: 
            # Nếu đã dựng rồi thì ko làm lại nữa
            return 

    def process_subentry(self, binary_data):
        """
        Hàm xử lý subentry với entry hiện tại
        Cần gán lại filename của entry hiện tại cho dữ liệu nhận được từ subentry truyền vào từ tham số
        """
        pass

class FATFile(AbstractFile):
    # TODO: Override các abstract attribute 

    # TODO: Constructor 
    def __init__(self, main_entry_buffer: bytes, parent_path: str, volume: FATVolume):
        pass