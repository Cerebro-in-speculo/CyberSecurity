from abc import ABC, abstractmethod

class BaseExploit(ABC):
    def __init__(self, name, sername):
        self.name = name
        self.sername = sername

    def adress(self):
        print(f"{self.name} {self.sername} живет по адресу: МО, г. Одинцово")

    def __work():
        print('Analitik')

    @abstractmethod
    def print_info(self):
        pass


class MyAge(BaseExploit):
    def __init__(self, name, sername, age):
        super().__init__(name, sername)
        self.age = age

    def age_curr(self):
        return self.age

    def print_info(self):
        print(self.name)
        print(self.sername)
        print(self.age)

# p1 = BaseExploit('Roman', 'Ledovskih')
# p1.adress()

p2 = MyAge('Roman', 'Ledovskih',47)
p2.print_info()

