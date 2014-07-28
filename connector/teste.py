'''
Created on Jul 28, 2014

@author: rodrigo.abreu
'''

class MyClass(object):

    def __init__(self, *args, **kwargs):
        print args
        print kwargs
        for i in kwargs.keys():
            setattr(self, i, kwargs[i])

    def print_value(self):
        print self.param4


if __name__ == "__main__":
    x = {"param1": "value1",
         "param2": "value2",
         "param3": "value3",
         "param4": "value4",
         "param5": "value5",
         "param6": "value6",
         "param7": "value7",
         "param8": "value8"}

    y = MyClass(**x)
    print y.param7
    print y.param3
    y.print_value()