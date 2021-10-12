Chú thích các file 
- `AbstractBaseClass`: chứa mấy cái abstract class để implement thành các concrete class (vd: `FATVolume` extends `AbstractVolume`, `FATFile` extends `AbstractFile`, `NTFSDirectory` extends `AbstractDirectory`).
- `FAT`: chứa tất cả các concrete class cho FAT. 
- `NTFS`: chứa tất cả các concrete class cho NTFS.

Link data: https://studenthcmusedu-my.sharepoint.com/:f:/g/personal/19120615_student_hcmus_edu_vn/EkQYwCz-ZUBPlqRwELwESsEB3Fi9-i6o_urAORbGUVW5Wg?e=pFjNHP
Gồm các file
- `drive_ntfs.bin`: file ổ đĩa ảo NTFS.
- `drive_fat.bin`: file ổ đĩa ảo FAT32.
- `TEST_DRIVE_DATA.zip`: nội dung của ổ đĩa ảo (để tiện so sánh khi test).
- `MD5SUM.txt`: MD5 của 2 file ổ đĩa ảo.
