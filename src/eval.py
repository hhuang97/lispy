from parser import lispy_parser
from scope import scope
from shared import Syn

def plusBuiltin(current_scope, args):
    vals = [eval(current_scope, v) for v in args]
    if 'FLOAT' in [v.type for v in args]:
        return Syn(type='FLOAT', value=sum(vals))
    else:
        return Syn(type='INT', value=sum(vals))

def difference(vals):
    d = vals[0]
    for v in vals[1:]:
        d -= v
    return d


def minusBuiltin(current_scope, args):
    vals = [eval(current_scope, v) for v in args]
    if 'FLOAT' in [v.type for v in args]:
        return Syn(type='FLOAT', value=difference(vals))
    else:
        return Syn(type='INT', value=difference(vals))

def product(vals):
    p = 1
    for v in vals:
        p *= v
    return p


def timesBuiltin(current_scope, args):
    vals = [eval(current_scope, v) for v in args]
    if 'FLOAT' in [v.type for v in args]:
        return Syn(type='FLOAT', value=product(vals))
    else:
        return Syn(type='INT', value=product(vals))

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
    if 'FLOAT' in [v.type for v in args]:
        return Syn(type='FLOAT', value=quotientF(vals))
    else:
        return Syn(type='INT', value=quotientI(vals))

def ltBuiltin(current_scope, args):
    if len(args) != 2:
        #TODO ERROR HANDLING
        return None
    return Syn(type='BOOL', value=eval(current_scope, args[0]) < eval(current_scope, args[1]))


def ifBuiltin(current_scope, args):
    if len(args) != 3:
        # TODO ERROR HANDLING
        return None
    cond = eval(current_scope, args[0])
    if cond:
        return args[1]
    else:
        return args[2]

def eval(current_scope, ast):
    if ast.type in ['INT', 'FLOAT', 'STRING', 'BOOL']:
        return ast.value
    if ast.type == 'ID':
        return current_scope.get(ast.value)
    if ast.type == 'FUNC_CALL' and ast.value['name'].value == 'let':
        name = ast.value['arg_exprs'].value[0].value
        value = ast.value['arg_exprs'].value[1]
        if value.type in ['FUNC_CALL', 'ID']:
            value = eval(current_scope, value)
        current_scope.add(name, value)
        return value
    if ast.type == 'FUNC_CALL':
        args = ast.value['arg_exprs'].value
        for (i, a) in enumerate(args):
            if a.type in ['FUNC_CALL', 'ID']:
                args[i] = eval(current_scope, args[i])
        return current_scope.get(ast.value['name'].value)(current_scope, args)

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
