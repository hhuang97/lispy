from parser import lispy_parser
from scope import scope
from shared import Syn

def plusBuiltin(current_scope, args):
    vals = [eval(current_scope, v) for v in args]
    if 'FLOAT' in [v.type for v in args]:
        return Syn(type='FLOAT', value=sum(vals))
    else:
        return Syn(type='INT', value=sum(vals))

def eval(current_scope, ast):
    if ast.type in ['INT', 'FLOAT', 'STRING', 'BOOL']:
        return ast.value
    if ast.type == 'FUNC_CALL':
        return current_scope.get(ast.value['name'].value)(current_scope, ast.value['arg_exprs'].value)

if __name__ == '__main__':
    global_scope = scope({
        '+': plusBuiltin
    })
    lispy = lispy_parser()
    while(True):
        ast = lispy.parse(input())
        print(eval(global_scope, ast))
