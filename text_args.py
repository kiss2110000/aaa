def func(functionName):
    b = 1000
    def func_in(*args, **kwargs):
        b= 100
        ret = functionName(b,*args, **kwargs)
        return ret
    return func_in

@func
def test(a,b):
    print("0000{}00000".format(a))
    print("0000{}00000".format(b))

test(5)