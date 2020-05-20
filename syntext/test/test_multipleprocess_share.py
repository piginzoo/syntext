from multiprocessing import Process,Queue

class A():
    def __init__(self):
        self.name = "test123"
        self.value = 123

    def callit(self,data):
        print(data)
        print(self.name)
        print(self.value)

a = A()

p1 = Process(target=a.callit, args=("data1...",))
p2 = Process(target=a.callit, args=("data2...",))

p1.start()
p2.start()

