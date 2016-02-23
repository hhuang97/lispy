import pprint

from ply import lex, yacc

from shared import Syn

P = pprint.PrettyPrinter(indent=4)

class lispy_parser(object):
    def __init__(self, lex_kwargs=None, yacc_kwargs=None):
        lex_kwargs = lex_kwargs if lex_kwargs else dict()
        yacc_kwargs = yacc_kwargs if yacc_kwargs else dict()
        self._lexer = lex.lex(module=self, **lex_kwargs)
        self._parser = yacc.yacc(module=self, **yacc_kwargs)

    def parse(self, input_text):
        result = self._parser.parse(input_text, lexer=self._lexer)
        return result

    def get_syn(self, tok, s_type, s_value):
        return Syn(s_type, s_value)

    tokens = (
        'STRING',
        'BOOL',
        'FLOAT',
        'INT',
        'LPAREN',
        'RPAREN',
        'DEFUN',
        'SET',
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
        t.value = self.get_syn(t, 'STRING', t.value[1:-1])
        return t

    def t_BOOL(self, t):
        r'\#[tf]'
        t.value = self.get_syn(t, 'BOOL', (t.value == '#t'))
        return t

    def t_FLOAT(self, t):
        r'-?[0-9]+\.[0-9]*([eE](-?[0-9]+))?'
        t.value = self.get_syn(t, 'FLOAT', float(t.value))
        return t

    def t_INT(self, t):
        r'-?[0-9]+'
        t.value = self.get_syn(t, 'INT', int(t.value))
        return t

    t_LPAREN = r'\('
    t_RPAREN = r'\)'

    def t_ID(self, t):
        r'[-+]|([a-zA-Z_!$%*/:<=>?~^][a-zA-Z_!$%^*/:<=>?~0-9.+\-^]*)'
        if t.value == 'defun':
            t.type = 'DEFUN'
            t.value = self.get_syn(t, 'DEFUN', t.value)
        elif t.value == 'set':
            t.type = 'SET'
            t.value = self.get_syn(t, 'SET', t.value)
        else:
            t.value = self.get_syn(t, 'ID', t.value)
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
                | set
                | func_call
                | list
        '''
        p[0] = p[1]

    def p_func_call(self, p):
        '''func_call : LPAREN ID exprseq RPAREN
        '''
        p[0] = Syn('FUNC_CALL', {'name': p[2], 'arg_exprs': p[3]})

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
            p[0] = Syn('EXPRSEQ', [p[1]])
        else:
            p[0] = Syn('EXPRSEQ', [p[1]] + p[2].value)

    def p_list(self, p):
        '''list : LPAREN exprseq RPAREN
                | LPAREN RPAREN
        '''
        if len(p) == 3:
            p[0] = Syn('LIST', list())
        else:
            p[0] = Syn('LIST', p[2].value)

    def p_defun(self, p):
        '''defun : LPAREN DEFUN ID LPAREN ids RPAREN exprseq RPAREN
        '''
        p[0] = Syn('DEFUN', {'name': p[3], 'args': p[5], 'body': p[7]})

    def p_set(self, p):
        '''set : LPAREN SET ID expr RPAREN
        '''
        p[0] = Syn('SET', {'name': p[3], 'value': p[4]})


if __name__ == '__main__':
    lispy = lispy_parser()
    while(True):
        ast = lispy.parse(input())
        P.pprint(ast)
