from __future__ import annotations
import re

from src.lambda_ast import ASTNode
from src.lambda_token import Token, TokenType

from ete3 import Tree, TreeStyle


class LambdaLexer:
    def __init__(self, input: str):
        self.input = input
        self.tokens = []
        self.pos = 0

        n = 0

        while n < len(input):
            while input[n].isspace() and n < len(input):
                n += 1
            match input[n]:
                case "(":
                    self.tokens.append(Token(TokenType.LBRACE))
                    n += 1
                case ")":
                    self.tokens.append(Token(TokenType.RBRACE))
                    n += 1
                case "\\":
                    self.tokens.append(Token(TokenType.LAMBDA))
                    n += 1
                case ".":
                    self.tokens.append(Token(TokenType.DOT))
                    n += 1
                case _:
                    match = re.match(r"[a-z]+\d*", input[n:])
                    if match is not None:
                        self.tokens.append(Token(TokenType.VAR, match[0]))
                        n += len(match[0])
                    else:
                        print("lexer error")
                        return

    def peek(self, n: int) -> Token:
        peek_index = self.pos + n - 1
        if peek_index >= len(self.tokens):
            return Token(TokenType.EOF)
        return self.tokens[peek_index]

    def eat(self, tok: TokenType) -> Token:
        peek = self.peek(1)
        if peek.tok_type != tok:
            print("snytax eorrr")
        self.pos += 1
        return peek


class LambdaParser:
    def __init__(self, lex: LambdaLexer):
        self.lexer = lex

        # We use the following grammar:
        # abs := \ id . term
        # term := lambda | lambda term
        # lambda := abs | ( term ) | id
        # main := lambda EOF
        self.index = 0

    def parse(self) -> ASTNode:
        self.index = 0
        expr = self.parse_term()
        self.lexer.eat(TokenType.EOF)
        self.index = 0
        return expr

    def parse_abstraction(self) -> ASTNode:
        self.lexer.eat(TokenType.LAMBDA)
        lvar = self.lexer.eat(TokenType.VAR)
        self.lexer.eat(TokenType.DOT)
        ltree = self.parse_term()

        self.index += 1

        node = ASTNode(ltree, None).set_value(lvar.lexeme).set_id(self.index)
        return node

    def parse_term(self) -> ASTNode:
        ltree = self.parse_lambda()
        rtree = None
        if self.lexer.peek(1).tok_type in {
            TokenType.LAMBDA,
            TokenType.LBRACE,
            TokenType.VAR,
        }:
            rtree = self.parse_term()
            self.index += 1
            return ASTNode(ltree, rtree).set_id(self.index)
        else:
            return ltree

    def parse_lambda(self) -> ASTNode:
        match self.lexer.peek(1).tok_type:
            case TokenType.LAMBDA:
                return self.parse_abstraction()
            case TokenType.LBRACE:
                self.lexer.eat(TokenType.LBRACE)
                term = self.parse_term()
                self.lexer.eat(TokenType.RBRACE)
                return term
            case TokenType.VAR:
                lvar = self.lexer.eat(TokenType.VAR)
                self.index += 1
                node = ASTNode(None, None).set_value(lvar.lexeme).set_id(self.index)
                return node
            case _:
                # "snytax rrrrrr" is a reference to Prof. Rida Bazzi
                print("snytax rrrrrr")


def main():
    lexer = LambdaLexer(r"\ x . \ y . x y (x y)")
    parser = LambdaParser(lexer)
    ast = parser.parse()
    t = ast.to_ete3()
    ts = TreeStyle()
    ts.mode = "c"
    ts.arc_start = -180  # 0 degrees = 3 o'clock
    ts.arc_span = 180
    ts.force_topology = True
    t.show(tree_style=ts)
    print(t.get_ascii(show_internal=True))

    print([e for e in ast.edges_breadth()])
    print([v for v in ast.vertices_breadth()])


if __name__ == "__main__":
    main()
