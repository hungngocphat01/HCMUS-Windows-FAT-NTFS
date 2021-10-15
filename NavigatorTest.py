"""
Module giả lập ổ đĩa bằng file zip để thuận tiện cho việc test
"""
from zipfile import ZipFile, Path, ZipInfo
from AbstractBaseClasses import AbstractDirectory, AbstractFile, AbstractVolume

class TestVolume(AbstractVolume):
    """
    Phân vùng dummy để test navigator
    Tạo ra từ 1 tập tin zip
    """
    root_directory = None 
    size = None
    volume_label = None 
    file_object = None

    def __init__(self, fileobject: ZipFile):
        # Đọc file zip 
        self.file_object = fileobject
        self.volume_label = fileobject.filename
        self.root_directory = TestDirectory(self, '', Path(self.file_object))

class TestDirectory(AbstractDirectory):
    """
    Thư mục dummy để test navigator
    """
    volume = None 
    subentries = None 
    name = None 
    attr = None 
    sectors = None
    modified_date = None 
    modified_time = None
    path = None

    def __init__(self, volume: TestVolume, parent_path, path_obj: Path):
        self.volume = volume
        self.path_obj: Path = path_obj
        self.name = path_obj.name
        self.path = parent_path + '/' + self.name
        
        if (self.path != '/'):
            info: ZipInfo = self.volume.file_object.getinfo(self.path.lstrip('/') + '/')
            year, month, day, hr, min, sec = info.date_time
            self.modified_date = '%d-%d-%d' % (year, month, day)
            self.modified_time = '%d-%d-%d' % (hr, min, sec)
            self.attr = info.external_attr

    def build_tree(self):
        if self.subentries is not None:
            return 
    
        self.subentries = []
        for entry in self.path_obj.iterdir():
            entry_path = self.path_obj / entry.name

            if entry.is_file():
                self.subentries.append(TestFile(self.volume, self.path, entry_path))
            else: 
                self.subentries.append(TestDirectory(self.volume, self.path, entry_path))

class TestFile(AbstractFile):
    """
    Tập tin dummy để test navigator
    """
    path = None 
    volume = None 
    name = None 
    attr = None 
    sectors = None 
    modified_date = None 
    modified_time = None
    path = None
    size = None

    def __init__(self, volume: TestVolume, parent_path, path_obj: Path):
        self.volume = volume
        self.path_obj: Path = path_obj
        self.name = path_obj.name
        self.path = parent_path + '/' + self.name
        
        info: ZipInfo = self.volume.file_object.getinfo(self.path.strip('/'))
        year, month, day, hr, min, sec = info.date_time
        self.modified_date = '%d-%d-%d' % (year, month, day)
        self.modified_time = '%d-%d-%d' % (hr, min, sec)
        self.attr = info.external_attr
        self.size = info.file_size
    
    def dump_binary_data(self):
        return self.path_obj.read_bytes()