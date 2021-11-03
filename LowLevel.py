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

def read_sectors(file, sector_begin, n_sector=1) -> bytes:
    """
    Hàm đọc `n_sector` sectors, bắt đầu tại sector có chỉ số `sector_begin`.
    Trả về: buffer đọc được.
    
    Ví dụ: đọc 4 sector bắt đầu từ sector 256
    >>> read_sectors(file, 256, 4)
    """
    file.seek(512 * sector_begin)
    return file.read(512 * n_sector)

def read_bytes_buffer(buffer, offset, size=1) -> bytes:
    """
    Hàm đọc chuỗi từ buffer tại vị trí `offset` với kích thước `size`.
    Nếu offset ở hệ 16 thì viết thêm tiền tố `0x`. Vd: `0x0DC`.
    
    Ví dụ: đọc tên file trên entry chính (8 byte tại offset `00`).
    >>> read_string(buffer, '00', 8)
    >>> read_string(buffer, 0, 8)
    """
        
    return buffer[offset:offset+size]
    
def read_number_buffer(buffer, offset, size) -> int:
    """
    Hàm đọc số nguyên không dấu từ buffer tại vị trí `offset` với kích thước `size`.
    Nếu offset viết theo hex, truyền vào dưới dạng chuỗi (vd: '0B', '0D', ...)
    Nếu offset viết ở hệ 10, truyền vào dưới dạng số (vd: 110, 4096, ...)
    Hàm này đã xử lý số little endian.
    
    Cách dùng tương tự `read_string_buffer`
    """
    buffer = read_bytes_buffer(buffer, offset, size)
    return dec(buffer[::-1].hex())
