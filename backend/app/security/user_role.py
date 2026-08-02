from enum import Enum


class UserRole(str, Enum):
    PLATFORM_OWNER = "PLATFORM_OWNER"
    YONETICI = "YONETICI"
    PERSONEL = "PERSONEL"