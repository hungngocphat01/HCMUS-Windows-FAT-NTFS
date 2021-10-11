Chú thích các file 
- `AbstractBaseClass`: chứa mấy cái abstract class để implement thành các concrete class (vd: `FATVolume` extends `AbstractVolume`, `FATFile` extends `AbstractFile`, `NTFSDirectory` extends `AbstractDirectory`).
- `FAT`: chứa tất cả các concrete class cho FAT. 
- `NTFS`: chứa tất cả các concrete class cho NTFS.