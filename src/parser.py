from ply import lex, yacc

from shared import get_syn

class lispy_parser(object):
    def __init__(self, lex_kwargs=None, yacc_kwargs=None):
        lex_kwargs = lex_kwargs if lex_kwargs else dict()
        yacc_kwargs = yacc_kwargs if yacc_kwargs else dict()
        self._lexer = lex.lex(module=self, **lex_kwargs)
        self._parser = yacc.yacc(module=self, **yacc_kwargs)

    def parse(self, input_text):
        result = self._parser.parse(input_text, lexer=self._lexer)
        return result

    tokens = (
        'STRING',
        'BOOL',
        'FLOAT',
        'INT',
        'LPAREN',
        'RPAREN',
        'DEFUN',
        'LET',
        'IF',
        'ID'
        # 'SQUOTE',
        # 'COMMENT'
    )

    r_id_initial = ''
    r_id_subsequent = '[a-zA-Z_!$%^*/:<=>?~^]'

    def t_newline(self, t):
        r'\n+'
        # char_idx = self._lexer.lexpos
        # for n in t.value:
        #     if n == '\n':
        #         self._tracker.inc_line(char_idx)
        #         char_idx += 1
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    t_ignore = ' \t'

    def t_STRING(self, t):
        r'"([^"]|(\\")|\\)*"'
        t.value = get_syn('STRING', t.value[1:-1])
        return t

    def t_BOOL(self, t):
        r'\#[tf]'
        t.value = get_syn('BOOL', (t.value == '#t'))
        return t

    def t_FLOAT(self, t):
        r'-?[0-9]+\.[0-9]*([eE](-?[0-9]+))?'
        t.value = get_syn('FLOAT', float(t.value))
        return t

    def t_INT(self, t):
        r'-?[0-9]+'
        t.value = get_syn('INT', int(t.value))
        return t

    t_LPAREN = r'\('
    t_RPAREN = r'\)'

    def t_ID(self, t):
        r'[-+]|([a-zA-Z_!$%*/:<=>?~^][a-zA-Z_!$%^*/:<=>?~0-9.+\-^]*)'
        if t.value == 'defun':
            t.type = 'DEFUN'
            t.value = get_syn('DEFUN', t.value)
        elif t.value == 'let':
            t.type = 'LET'
            t.value = get_syn('LET', t.value)
        elif t.value == 'if':
            t.type = 'IF'
            t.value = get_syn('IF', t.value)
        else:
            t.value = get_syn('ID', t.value)
        return t

    # t_SQUOTE = r"'"

    # def t_COMMENT(self, t):
    #     r';[^\n]'
    #     pass

    # Begin grammar

    def p_error(self, p):
        print("Syntax error at token", p.type)
        raise SyntaxError

    def p_expr(self, p):
        '''expr : atom
                | defun
                | let
                | func_call
                | list
                | if
        '''
        p[0] = p[1]

    def p_func_call(self, p):
        '''func_call : LPAREN ID exprseq RPAREN
        '''
        p[0] = get_syn('FUNC_CALL', {'name': p[2], 'arg_exprs': p[3]})

    def p_ids(self, p):
        '''ids : ID
               | ID ids
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]

    def p_atom(self, p):
        '''atom : BOOL
                | STRING
                | INT
                | FLOAT
                | ID
        '''
        p[0] = p[1]

    def p_exprseq(self, p):
        '''exprseq : expr
                   | expr exprseq
        '''
        if len(p) == 2:
            p[0] = get_syn('EXPRSEQ', [p[1]])
        else:
            p[0] = get_syn('EXPRSEQ', [p[1]] + p[2]['value'])

    def p_list(self, p):
        '''list : LPAREN exprseq RPAREN
                | LPAREN RPAREN
        '''
        if len(p) == 3:
            p[0] = get_syn('LIST', list())
        else:
            p[0] = get_syn('LIST', p[2]['value'])

    def p_defun(self, p):
        '''defun : LPAREN DEFUN ID LPAREN ids RPAREN exprseq RPAREN
        '''
        p[0] = get_syn('DEFUN', {'name': p[3], 'args': p[5], 'body': p[7]})

    def p_let(self, p):
        '''let : LPAREN LET ID expr RPAREN
        '''
        p[0] = get_syn('LET', {'name': p[3], 'value': p[4]})

    def p_if(self, p):
        '''if : LPAREN IF expr expr expr RPAREN
        '''
        p[0] = get_syn('IF', {'cond': p[3], 'then': p[4], 'else': p[5]})

import pprint

if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=2, width=60)
    lispy = lispy_parser()
    while(True):
        ast = lispy.parse(input())
        # pp.pprint(dict(ast._asdict()))
        pp.pprint(ast)
