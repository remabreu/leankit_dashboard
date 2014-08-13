'''
Created on Jul 28, 2014

@author: rodrigo.abreu
'''

class A(object):

    def __init__(self, a):
        self.a = a

    def __eq__(self, other):
        return self.a == other.a

class MyClass(object):

    def __init__(self, *args, **kwargs):
        print args
        print kwargs
        for i in kwargs.keys():
            setattr(self, i, kwargs[i])



    def print_value(self):
        print self.param4



from datetime import timedelta
import datetime

def week_range(date):
    """Find the first/last day of the week for the given day.
    Assuming weeks start on Sunday and end on Saturday.

    Returns a tuple of ``(start_date, end_date)``.

    """
    # isocalendar calculates the year, week of the year, and day of the week.
    # dow is Mon = 1, Sat = 6, Sun = 7
    year, week, dow = date.isocalendar()

    # Find the first day of the week.
    if dow == 7:
        # Since we want to start with Sunday, let's test for that condition.
        start_date = date
    else:
        # Otherwise, subtract `dow` number days to get the first day
        start_date = date - timedelta(dow)

    # Now, add 6 for the last day of the week (i.e., count up to Saturday)
    end_date = start_date + timedelta(6)

    return (start_date, end_date)


if __name__ == "__main__":
    l1 = [A(1), A(2), A(3)]
    l2 = [A(1), A(3), A(4), A(6)]

    s1 = set(l1)
    s2 = set(l2)

    v = l1.append(l2)
    for i in l1:
        print i

    
#     l = filter(lambda x: x.a,l1)
#     print l(l1)


#     inters = s1 & s2
#     print inters

#     x = {"param1": "value1",
#          "param2": "value2",
#          "param3": "value3",
#          "param4": "value4",
#          "param5": "value5",
#          "param6": "value6",
#          "param7": "value7",
#          "param8": "value8"}
#
#     y = MyClass(**x)
#     print y.param7
#     print y.param3
#     y.print_value()
#     t = datetime.date.today()
#     print week_range(t)
