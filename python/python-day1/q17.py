class Bird:
    pass 
class Flyable:
    def fly(self):
        pass
class Swimmable:
    def swim(self):
        pass 
class Sparrow(Bird,Flyable):
    def fly(self):
        print("Sparrow files")
class Penguin(Bird,Swimmable):
    def swim(self):
        print("Penguin swims")
Sparrow=Sparrow()
Penguin=Penguin()
Sparrow.fly()
Penguin.swim()