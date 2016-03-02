from parser import lispy_parser
from scope import scope
from shared import get_syn

import pprint

pp = pprint.PrettyPrinter(indent=2, width=60)



def plusBuiltin(current_scope, args):
    vals = [eval(current_scope, v) for v in args]
    if 'FLOAT' in [v['type'] for v in args]:
        return get_syn('FLOAT', sum(vals))
    else:
        return get_syn('INT', sum(vals))

def difference(vals):
    d = vals[0]
    for v in vals[1:]:
        d -= v
    return d


def minusBuiltin(current_scope, args):
    vals = [eval(current_scope, v) for v in args]
    if 'FLOAT' in [v['type'] for v in args]:
        return get_syn('FLOAT', difference(vals))
    else:
        return get_syn('INT', difference(vals))

def product(vals):
    p = 1
    for v in vals:
        p *= v
    return p


def timesBuiltin(current_scope, args):
    vals = [eval(current_scope, v) for v in args]
    if 'FLOAT' in [v['type'] for v in args]:
        return get_syn('FLOAT', product(vals))
    else:
        return get_syn('INT', product(vals))

def quotientF(vals):
    q = vals[0]
    for v in vals[1:]:
        q /= v
    return q

def quotientI(vals):
    q = vals[0]
    for v in vals[1:]:
        q = q // v
    return q


def divideBuiltin(current_scope, args):
    vals = [eval(current_scope, v) for v in args]
    if 'FLOAT' in [v['type'] for v in args]:
        return get_syn('FLOAT', quotientF(vals))
    else:
        return get_syn('INT', quotientI(vals))

def ltBuiltin(current_scope, args):
    if len(args) != 2:
        #TODO ERROR HANDLING
        return None
    print(eval(current_scope, args[0]))
    return get_syn('BOOL', eval(current_scope, args[0]) < eval(current_scope, args[1]))


def ifBuiltin(current_scope, args):
    if len(args) != 3:
        # TODO ERROR HANDLING
        return None
    cond = eval(current_scope, args[0])
    if cond:
        return args[1]
    else:
        return args[2]

class User_func:
    def __init__(self, args, body):
        self._args = args
        self._body = body

    def __call__(self, current_scope, args):
        new_scope = current_scope
        for a,b in zip(self._args, args):
            new_scope.add(a, b)
        for e in self._body[:-1]:
            eval(new_scope, e)
        return eval(new_scope, self._body[-1])




def eval(current_scope, ast):
    if ast['type'] in ['INT', 'FLOAT', 'STRING', 'BOOL']:
        return ast['value']

    if ast['type'] == 'ID':
        return current_scope.get(ast['value'])

    if ast['type'] == 'LET':
        name = ast['value']['name']['value']
        value = ast['value']['value']
        if value['type'] in ['FUNC_CALL', 'ID']:
            value = eval(current_scope, value)
        current_scope.add(name, value)
        return value

    if ast['type'] == 'DEFUN':
        function_name = ast['value']['name']['value']
        args = ast['value']['args'] # TODO if any of these aren't IDs crash
        args = [a['value'] for a in args]
        body = ast['value']['body']['value']
        current_scope.add(function_name, User_func(args, body))


    if ast['type'] == 'FUNC_CALL':
        args = ast['value']['arg_exprs']['value']
        for (i, a) in enumerate(args):
            if a['type'] in ['FUNC_CALL', 'ID']:
                args[i] = eval(current_scope, args[i])
        return current_scope.get(ast['value']['name']['value'])(current_scope, args)

if __name__ == '__main__':
    global_scope = scope({
        '+': plusBuiltin,
        '-': minusBuiltin,
        '*': timesBuiltin,
        '/': divideBuiltin,
        '<': ltBuiltin,
        'if': ifBuiltin
    })
    lispy = lispy_parser()
    while(True):
        ast = lispy.parse(input())
        print(eval(global_scope, ast))
