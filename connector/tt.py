
class A(object):

    def __init__(self, **kwargs):
        for k,v in kwargs.iteritems():
            self.__setattr__(k,v)
        #self.a = a

    def __eq__(self, other):
        return self.a == other.a

l1 = [A(1), A(2), A(3)]
l2 = [A(1), A(3), A(4), A(6)]

s1 = set(l1)
s2 = set(l2)

# for i in l1:
#     print i.a
#l1.append(l2)

print [x for x in l1 if x.a == y.a ]
