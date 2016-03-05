import rlcompleter
import readline
from parser import lispy_parser
from eval import global_scope, eval
import sys

if len(sys.argv) == 1:
    readline.parse_and_bind("set editing-mode emacs")

    lispy = lispy_parser()
    while True:
        try:
            line = input('>>> ')
        except KeyboardInterrupt:
            print('\n')
            break
        if line != '':
            ast = lispy.parse(line)
            if ast:
                e = eval(global_scope, ast)
                if e is not None:
                    print(eval(global_scope, ast))

else:
    lispy = lispy_parser()

    file_name = sys.argv[1]
    f = open(file_name, 'r')
    code = f.read()
    code = '(' + code + ')'
    code = lispy.parse(code)

    for sexp in code['value']:
        eval(global_scope, sexp)

