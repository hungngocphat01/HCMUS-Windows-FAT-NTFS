from LowLevel import *
from AbstractBaseClasses import AbstractVolume, AbstractDirectory, AbstractFile
from datetime import datetime, timedelta

ATTR_NAME = 48
EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as MS file time


class NTFSVolume(AbstractVolume):
    # Override các abstract attribute
    # Trong python để "khai báo" là mình sẽ override các abstract attribute của class cha thì mình khởi tạo giá trị đầu cho nó (ở đây khởi tạo là None [giống null của C++])
    root_directory = None
    size = None
    volume_label = None
    file_object = None

    def __init__(self, file_object):
        """
        Constructor nhận vào 1 tham số là `file_object`, là một Python file object.
        """
        self.file_object = file_object

        # Đọc partition boot sector
        PBS_buffer = read_sectors(self.file_object, 0, 1)  # đọc sector thứ 0 (sector đầu tiên) và đọc 1 sector

        # Đọc số byte/sector
        self.sector_size = read_number_buffer(PBS_buffer, 0x0B, 2)

        # Đọc số sector/cluster
        self.sc = read_number_buffer(PBS_buffer, 0x0D, 1)

        # Đọc số sector để dành
        self.sb = read_number_buffer(PBS_buffer, 0x0E, 2)

        # Đọc tổng sector trong Volume
        self.nv = read_number_buffer(PBS_buffer, 0x28, 8)

        # Vị trí bắt đầu của MFT
        self.mft_begin = self.sc * read_number_buffer(PBS_buffer, 0x30, 8)
        # Đọc Bảng MFT
        self.mft_table = read_sectors(self.file_object, self.mft_begin, ...)

        print('Volume information:')
        print('Bytes per sector:', self.sector_size)
        print('Sectors per cluster (Sc):', self.sc)
        print('Reserved sectors (Sb):', self.sb)
        print('Sector number of logical drive (nv):', self.nv)
        print('MFT begin sector:', self.mft_begin)
        print('\n')

    def readInfoEntry(self):
        sectorsIndex = self.mft_begin

        while (sectorsIndex < self.nv):
            attrTypeID = 99
            attribOffset = 20   # 0x14

            # mỗi lần duyệt 2 sector <=> 1024 bytes
            buffer = read_sectors(self.file_object, sectorsIndex, 2)

            totalAttrs = read_number_buffer(buffer, 0x28, 2) - 1
            # Đọc nơi bắt đầu (offset) của phần nội dung (attr đầu đọc tại byte thứ 20-21)
            attribOffset = read_number_buffer(buffer, attribOffset, 2)

            for i in range(0, totalAttrs):
                # Đọc mã loại attribute byte thứ 0-3
                attrTypeID = read_number_buffer(buffer, attribOffset, 4)
                # Đọc kích thước attribute byte thứ 4-7
                attrLength = read_number_buffer(buffer, attribOffset + 4, 4)
                # Đọc kiểu attribite (resident non-resident)
                resident = read_number_buffer(buffer, attribOffset + 8, 1)

                if (resident > 1):
                    break

                # Đọc kích thước của phần nội dung, đọc byte thứ 16-19
                contentSize = read_number_buffer(buffer, attribOffset + 16, 4)
                # Đọc nơi bắt đầu (offset) của phần nội dung, đọc tại byte thứ 20-21)
                contentOffset = read_number_buffer(buffer, attribOffset + 20, 2)

                if (attrTypeID == ATTR_NAME):  # Attribute loại $FILE_NAME
                    # Đọc chiều dài tên tại byte thứ 64 (từ phần nội dung attr)
                    nameLength = read_number_buffer(buffer, attribOffset + contentOffset + 64, 1)
                    # Đọc tên tại byte thứ 66 (từ phần nội dung attr)
                    name = read_bytes_buffer(buffer, attribOffset + contentOffset + 66, nameLength * 2)
                    name = toASCII(name)
                    # thời gian tạo tập tin, đọc byte thứ 8-15
                    timeCreate = filetime_to_dt(read_number_buffer(buffer, attribOffset + contentOffset + 8, 8))
                    # thời gian tập tin có sự thay đổi, đọc byte thứ 16-23
                    timeModified = filetime_to_dt(read_number_buffer(buffer, attribOffset + contentOffset + 16, 8))
                    # thời gian truy cập tập tin mới nhất, đọc byte thứ 32-39
                    timeAccessed = filetime_to_dt(read_number_buffer(buffer, attribOffset + contentOffset + 32, 8))

                    print('\nTên: {}\n'
                          'Sector begin: {}\n'
                          'Create: {}\n'
                          'Modified: {}\n'
                          'Accessed: {}\n'.format(name, sectorsIndex, timeCreate, timeModified, timeAccessed))

                if (attrTypeID == 128):  # Attribute loại $DATA
                    # Đọc phần nội dung
                    content = read_bytes_buffer(buffer, attribOffset + contentOffset, contentSize)
                    print('Nội dung: {}\n'.format(content))

                attribOffset = (attribOffset + attrLength)

            # Tăng vị trí sector lên 2 <=> 1024 bytes
            sectorsIndex += 2

    @staticmethod
    def toASCII(str):
        """
            Hàm chuyển đổi kết quả từ hàm read_bytes_buffer() thành chuỗi ASCII
        """
        tmp = ''.join([hex(character)[2:].upper().zfill(2) \
                       for character in str]).lower()
        tmp = bytes.fromhex(tmp).decode('utf-8', errors='ignore')[::2]
        return tmp

    @staticmethod
    def filetime_to_dt(ft):
        '''
            Đổi số nano giây ra ngày giờ
        '''
        us = (ft - EPOCH_AS_FILETIME) // 10
        return datetime(1970, 1, 1) + timedelta(microseconds=us)


class NTFSDirectory(AbstractDirectory):
    pass