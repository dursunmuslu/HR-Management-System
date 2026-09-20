from enum import Enum


class UserRole(str, Enum):
    PLATFORM_OWNER = "PLATFORM_OWNER"
    YONETICI = "YONETICI"
    TAKIM_LIDERI = "TAKIM_LIDERI"
    PERSONEL = "PERSONEL"