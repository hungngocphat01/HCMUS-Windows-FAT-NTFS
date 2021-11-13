from abc import ABCMeta, abstractmethod
"""
File định nghĩa các Abstract Base Classes (ABC)
"""

class AbstractVolume(metaclass=ABCMeta):
    @property
    @abstractmethod
    def root_directory(self):
        """
        Con trỏ đến thư mục gốc của volume
        """
        pass
    
    @property
    @abstractmethod
    def size(self) -> int:
        """
        Kích thước (byte) của volume
        """
        pass
    
    @property
    @abstractmethod
    def volume_label(self) -> str:
        """
        Nhãn (tên) của volume
        """
        pass

    @property
    @abstractmethod
    def file_object(self):
        """
        Kích thước (byte) của volume
        """
        pass

class AbstractEntry(metaclass=ABCMeta):
    """
    Lớp đối tượng thể hiện một entry
    """
    @property
    @abstractmethod
    def path(self) -> str:
        """
        Đường dẫn đến entry
        """
        pass

    @property
    @abstractmethod
    def volume(self) -> AbstractVolume:
        """
        Con trỏ đến volume chứa entry này (để truy cập vào bảng FAT/MFT và duyệt các cluster)
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Tên của thư mục này
        """
        pass

    @property
    @abstractmethod
    def attr(self) -> list:
        """
        Tên của thư mục này
        """
        pass

    @abstractmethod
    def describe_attr(self) -> str:
        """
        Diễn giải các thuộc tính dưới dạng chuỗi
        """
        pass

    @property
    @abstractmethod
    def sectors(self) -> list:
        """
        Là mảng các chỉ số sector chứa dữ liệu nhị phân của SDET/RDET của thư mục này
        """
        pass

class AbstractDirectory(AbstractEntry):
    @property
    @abstractmethod
    def subentries(self) -> list:
        """
        Mảng của các subentries (file/subdirectory) của thư mục này.
        """
        pass

    @abstractmethod
    def build_tree(self):
        """
        Hàm để dựng được danh sách các subentry tương ứng với thư mục này (dữ liệu là từ SDET/RDET của thư mục). Danh sách này lưu vào mảng subentries[].
        """
        pass


class AbstractFile(AbstractEntry):
    @property
    @abstractmethod
    def size(self) -> int:
        """
        Kích thước (byte) của file
        """
        pass

    @abstractmethod
    def dump_binary_data(self) -> bytes:
        pass