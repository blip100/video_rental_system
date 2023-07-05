class A:
    def __init__(self):
        pass

    def __call__(self, x):
        return x+1


a = A()

print(a(1))