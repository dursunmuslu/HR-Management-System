from enum import Enum


class UserRole(str, Enum):
    PERSONEL = "PERSONEL"
    YONETICI = "YONETICI"