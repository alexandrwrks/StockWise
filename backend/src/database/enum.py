from enum import StrEnum


class MemberRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    EMPLOYEE = "employee"

class MemberStatus(StrEnum):
    ACTIVE = "active"
    INVITED = "invited"
    BLOCKED = "blocked"

class IngredientUnit(StrEnum):
    ml = "ml" # миллилитр
    gr = "gr" # грамм
    pcs = "pcs" # штука