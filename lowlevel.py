"""
File này định nghĩa những hàm cấp thấp cần thiết cho việc đọc/ghi nhị phân trên các tập tin/buffer
"""

def dec(hex: str) -> int: 
    """
    Hàm đổi số hex ra số hệ thập phân (tham số nhận vào là chuỗi)
    Vd:
    >>> dec('0B')
    >>> dec('0C')
    """
    return int(hex, 16)

def read_string_file(file, offset, size) -> bytes:
    """
    Hàm đọc chuỗi từ file tại vị trí `offset` với kích thước `size`.
    Trả về: bytes string.
    Ví dụ: đọc tên HĐH (8 byte tại offset `03`)
    >>> read_string(file, '03', 8)
    """
    int_offset = dec(offset)
    file.seek(int_offset)
    buffer = file.read(size)
    return buffer

def read_number_file(file, offset, size) -> int:
    """
    Hàm đọc số nguyên từ file tại vị trí `offset` với kích thước `size`.
    Trả về: int (hàm này đã xử lý số little endian).
    Ví dụ: đọc số bảng FAT NF (1 byte tại offset `10`)
    >>> read_string(file, '10', 1)
    """
    buffer = read_string_file(file, offset, size)
    # Reverse bytes (x86 is little endian)
    return int(buffer[::-1].hex(), 16)

def read_sectors(file, sector_begin, n_sector=1) -> bytes:
    """
    Hàm đọc `n_sector` sectors, bắt đầu tại sector có chỉ số `sector_begin`.
    Trả về: buffer đọc được.
    
    Ví dụ: đọc 4 sector bắt đầu từ sector 256
    >>> read_sectors(file, 256, 4)
    """
    file.seek(512 * sector_begin)
    return file.read(512 * n_sector)

def read_string_buffer(buffer, offset, size=1) -> bytes:
    """
    Hàm đọc chuỗi từ buffer tại vị trí `offset` với kích thước `size`.
    Nếu offset viết theo hex, truyền vào dưới dạng chuỗi (vd: '0B', '0D', ...)
    Nếu offset viết ở hệ 10, truyền vào dưới dạng số (vd: 110, 4096, ...)
    
    Ví dụ: đọc tên file trên entry chính (8 byte tại offset `00`).
    >>> read_string(buffer, '00', 8)
    >>> read_string(buffer, 0, 8)
    """
    if isinstance(offset, str):
        int_offset = dec(offset)
    elif isinstance(offset, int):
        int_offset = offset
    else:
        raise 'Offset không phù hợp! Chỉ có thể là số hoặc chuỗi!'
        
    return buffer[offset:offset+size]
    
def read_number_buffer(buffer, offset, size) -> int:
    """
    Hàm đọc số nguyên không dấu từ buffer tại vị trí `offset` với kích thước `size`.
    Nếu offset viết theo hex, truyền vào dưới dạng chuỗi (vd: '0B', '0D', ...)
    Nếu offset viết ở hệ 10, truyền vào dưới dạng số (vd: 110, 4096, ...)
    Hàm này đã xử lý số little endian.
    
    Cách dùng tương tự `read_string_buffer`
    """
    buffer = read_string_buffer(buffer, offset, size)
    return dec(buffer[::-1].hex())
