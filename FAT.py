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

        
        self.byte_per_sec = read_number_buffer(bootsec_buffer, 0xB, 2)
        # Đọc Sc (số sector cho 1 cluster): 1 byte tại 0x0D
        self.sc = read_number_buffer(bootsec_buffer, 0x0D, 1)
        # Đọc Sb (số sector để dành trước bảng FAT): 2 byte tại 0x0E
        self.sb = read_number_buffer(bootsec_buffer, 0x0E, 2)
        # Đọc Nf (số bảng FAT): 1 byte tại offset 0x10
        self.nf = read_number_buffer(bootsec_buffer, 0x10, 1)
        # Đọc Sf (số sector cho 1 bảng FAT): 4 byte tại 0x24
        self.sf = read_number_buffer(bootsec_buffer, 0x24, 4)
        # Đọc chỉ số cluster bắt đầu của RDET: 4 byte tại 0x2C
        self.root_cluster = read_number_buffer(bootsec_buffer, 0x2C, 4)
        # Chỉ số sector bắt đầu của data 
        self.data_begin_sector = self.sb + self.nf * self.sf

        print('Volume information:')
        print('Bytes per sector:', self.byte_per_sec)
        print('Sectors per cluster (Sc):', self.sc)
        print('Reserved sectors (Sb):', self.sb)
        print('No. of FAT tables (Nf):', self.nf)
        print('FAT size in sectors (Sf):', self.sf)
        print('RDET cluster:', self.root_cluster)
        print('Data begin sector:', self.data_begin_sector)
        print('\n')

        # Đọc bảng FAT (sf byte tại offset sb)
        self.fat_table_buffer = read_sectors(self.file_object, self.sb, self.sf)

        # RDET buffer
        rdet_cluster_chain = self.read_cluster_chain(self.root_cluster)
        rdet_sector_chain = self.cluster_chain_to_sector_chain(rdet_cluster_chain)
        rdet_buffer = read_sector_chain(self.file_object, rdet_sector_chain)

        self.root_directory = FATDirectory(rdet_buffer, '', self, isrdet=True)
        # self.volume_label = read_bytes_buffer(bootsec_buffer, 0x2B, 11)

    def read_cluster_chain(self, n) -> list: 
        """
        Hàm dò bảng FAT để tìm ra dãy các cluster cho một entry nhất định, bắt đầu từ cluster thứ `n` truyền vào.
        """
        # End-of-cluster sign
        eoc_sign = [0x00000000, 0xFFFFFF0, 0xFFFFFFF, 0XFFFFFF7, 0xFFFFFF8, 0xFFFFFFF0]
        if n in eoc_sign:
            return []
        
        next_cluster = n
        chain = [next_cluster]

        while True:
            # Phần tử FAT 2 ứng với cluster số 1
            next_cluster = read_number_buffer(self.fat_table_buffer, next_cluster * 4, 4)
            if next_cluster in eoc_sign:
                break 
            else:
                chain.append(next_cluster)
        return chain 
        
    def cluster_chain_to_sector_chain(self, cluster_chain) -> list: 
        """
        Hàm chuyển dãy các cluster sang dãy các sector
        Biết rằng 1 cluster có Sc sectors 
        Với cluster k thì nó bắt đầu chiếm từ cluster thứ `data_begin_sector + k * Sc`, và chiếm Sc sectors
        """
        sector_chain = []
        
        for cluster in cluster_chain:
            begin_sector = self.data_begin_sector + (cluster - 2) * self.sc
            for sector in range(begin_sector, begin_sector + self.sc):
                sector_chain.append(sector)
        return sector_chain

    @staticmethod
    def process_fat_lfnentries(subentries: list):
        """
        Hàm join các entry phụ lại thành tên dài
        """
        name = b''
        for subentry in subentries:
            name += read_bytes_buffer(subentry, 1, 10)
            name += read_bytes_buffer(subentry, 0xE, 12)
            name += read_bytes_buffer(subentry, 0x1C, 4)
        name = name.decode('utf-16le')

        if name.find('\x00') > 0:
            name = name[:name.find('\x00')]
        return name


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
    path = None

    def __init__(self, main_entry_buffer: bytes, parent_path: str, volume: FATVolume, isrdet=False, lfn_entries=[]):
        # Dãy byte entry chính
        self.entry_buffer = main_entry_buffer
        self.volume = volume # con trỏ đến volume đang chứa thư mục này
        # Danh sách các subentry
        self.subentries = None

        # Nếu thư mục này là RDET (file thì ko cần xét RDET)
        if not isrdet:
            # Tên entry 
            if len(lfn_entries) > 0:
                lfn_entries.reverse()
                self.name = FATVolume.process_fat_lfnentries(lfn_entries)
                lfn_entries.clear()
            else:
                self.name = read_bytes_buffer(main_entry_buffer, 0, 11).decode('utf-8').strip()
            # Status
            self.attr = read_number_buffer(main_entry_buffer, 0xB, 1)

            # Các byte thấp và cao của chỉ số cluster đầu
            highbytes = read_number_buffer(main_entry_buffer, 0x14, 2)
            lowbytes = read_number_buffer(main_entry_buffer, 0x1A, 2)
            self.begin_cluster = highbytes * 0x100 + lowbytes
            self.path = parent_path + '/' + self.name
        else:
            self.begin_cluster = self.volume.root_cluster
            self.path = ''

        cluster_chain = self.volume.read_cluster_chain(self.begin_cluster)
        self.sectors = self.volume.cluster_chain_to_sector_chain(cluster_chain)
            

    def build_tree(self):
        """
        Dựng cây thư mục cho thư mục này (đọc các sector trong mảng `self.sectors` được SDET rồi xử lý)
        """
        if self.subentries != None: 
            # Nếu đã dựng rồi thì ko làm lại nữa
            return 
        self.subentries = []
        subentry_index = 0

        # Đọc SDET (dữ liệu nhị phân) của thư mục
        sdet_buffer = read_sector_chain(self.volume.file_object, self.sectors)
        lfn_entries_queue = []

        while True:
            subentry_buffer = read_bytes_buffer(sdet_buffer, subentry_index, 32)
            # Read type
            entry_type = read_number_buffer(subentry_buffer, 0xB, 1)
            if entry_type & 0x10 == 0x10:
                # Là thư mục
                self.subentries.append(FATDirectory(subentry_buffer, self.path, self.volume, lfn_entries=lfn_entries_queue))
            elif entry_type & 0x20 == 0x20:
                # Là thư mục
                self.subentries.append(FATFile(subentry_buffer, self.path, self.volume, lfn_entries=lfn_entries_queue))
            elif entry_type & 0x0F == 0x0F:
                lfn_entries_queue.append(subentry_buffer)
            if entry_type == 0:
                break
            subentry_index += 32

    def process_subentry(self, binary_data):
        """
        Hàm xử lý subentry với entry hiện tại
        Cần gán lại filename của entry hiện tại cho dữ liệu nhận được từ subentry truyền vào từ tham số
        """
        pass

    def describe_attr(self):
        """
        Lấy chuỗi mô tả các thuộc tính
        """
        desc_map = {
            0x10: 'D',
            0x20: 'A',
            0x01: 'R', 
            0x02: 'H',
            0x04: 'S',
        }

        desc_str = ''
        for attribute in desc_map:
            if self.attr & attribute == attribute:
                desc_str += desc_map[attribute]
        
        return desc_str

class FATFile(AbstractFile):
    volume = None 
    name = None 
    attr = None 
    sectors = None
    path = None
    size = None


    def __init__(self, main_entry_buffer: bytes, parent_path: str, volume: FATVolume, lfn_entries=[]):
        ...

    def dump_binary_data(self):
        ...

    def describe_attr(self):
        ...