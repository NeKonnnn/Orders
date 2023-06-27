from typing import Set
from .employee import Employee, Manager
from .exception import NoSuchMemberError

class Team:
    name: str
    manager: Manager
    __members: Set[Employee]

    def __init__(self, name: str, manager: Manager):
        self.name = name
        self.manager = manager
        self.__members = set()

    def add_member(self, member: Employee) -> None:
        if not isinstance(member, Employee):
            raise TypeError("Member should be an instance of Employee")
        self.__members.add(member)

    def remove_member(self, member: Employee) -> None:
        if not isinstance(member, Employee):
            raise TypeError("Member should be an instance of Employee")
        if member not in self.__members:
            raise NoSuchMemberError(f"No such member: {member.name} in the team", member)
        self.__members.remove(member)

    def get_members(self) -> Set[Employee]:
        return set(self.__members)

    def __str__(self) -> str:
        return f'team: {self.name} manager: {self.manager.name} number of members: {len(self.__members)}'

    def show(self) -> None:
        print(self)