from enum import StrEnum


class MemberRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    EMPLOYEE = "employee"

class MemberStatus(StrEnum):
    ACTIVE = "active"
    INVITED = "invited"
    BLOCKED = "blocked"