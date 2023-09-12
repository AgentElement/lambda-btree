from __future__ import annotations
from enum import Enum
import re

import collections


class ASTNode:
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left: ASTNode = left
        self.right: ASTNode = right
        self.value: Token.VAR = None
        self.id: int = 0
        self.depth: int = 0

    def set_value(self, value: Token.VAR) -> ASTNode:
        self.value = value.lexeme
        return self

    def set_depth(self, depth: int) -> ASTNode:
        self.depth = depth
        return self

    def set_id(self, id: int) -> ASTNode:
        self.id = id
        return self

    def __str__(self) -> str:
        left = "" if self.left is None else str(self.left)
        right = "" if self.right is None else str(self.right)
        return f"({self.value}{left}{',' if left and right else ''}{right})"

    # display() and _display_aux() copied from
    # https://stackoverflow.com/a/54074933
    def display(self):
        lines, *_ = self._display_aux()
        for line in lines:
            print(line)

    def _display_aux(self, ob=lambda x: x.id):
        """Returns list of strings, width, height, and horizontal coordinate
        of the root."""
        # No child.
        if self.right is None and self.left is None:
            line = f"{ob(self)}"
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Only left child.
        if self.right is None:
            lines, n, p, x = self.left._display_aux()
            s = f"{ob(self)}"
            u = len(s)
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
            second_line = x * ' ' + '/' + (n - x - 1 + u) * ' '
            shifted_lines = [line + u * ' ' for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

        # Only right child.
        if self.left is None:
            lines, n, p, x = self.right._display_aux()
            s = f"{ob(self)}"
            u = len(s)
            first_line = s + x * '_' + (n - x) * ' '
            second_line = (u + x) * ' ' + '\\' + (n - x - 1) * ' '
            shifted_lines = [u * ' ' + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        # Two children.
        left, n, p, x = self.left._display_aux()
        right, m, q, y = self.right._display_aux()
        s = f"{ob(self)}"
        u = len(s)
        first_line = (x + 1) * ' ' + (n - x - 1) * \
            '_' + s + y * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + \
            (n - x - 1 + u + y) * ' ' + '\\' + (m - y - 1) * ' '
        if p < q:
            left += [n * ' '] * (q - p)
        elif q < p:
            right += [m * ' '] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + \
            [a + u * ' ' + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2

    def edges_breadth(self):
        queue = collections.deque([self])
        while queue:
            parent = queue.popleft()
            for child in (parent.left, parent.right):
                if child:
                    yield ((parent.id, child.id))
                    queue.append(child)

    def vertices_breadth(self):
        queue = collections.deque([self])
        while queue:
            parent = queue.popleft()
            yield ((parent.id, parent.value))
            for child in (parent.left, parent.right):
                if child:
                    queue.append(child)


class TokenType(Enum):
    LBRACE = 0
    RBRACE = 1
    LAMBDA = 2
    DOT = 3
    VAR = 4
    EOF = 5


class Token:
    def __init__(self, t, lexeme=""):
        self.tok_type = t
        self.lexeme = lexeme

    def __str__(self) -> str:
        return f"({self.tok_type}" + (")" if self.lexeme == "" else f", {self.lexeme})")

    def __repr__(self) -> str:
        return str(self)


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

        node = ASTNode(ltree, None).set_value(lvar).set_id(self.index)
        return node

    def parse_term(self) -> ASTNode:
        ltree = self.parse_lambda()
        rtree = None
        if self.lexer.peek(1).tok_type in {TokenType.LAMBDA, TokenType.LBRACE, TokenType.VAR}:
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
                node = ASTNode(None, None).set_value(lvar).set_id(self.index)
                return node
            case _:
                # "snytax rrrrrr" is a reference to Prof. Rida Bazzi
                print("snytax rrrrrr")


def main():
    lexer = LambdaLexer("\ x . \ y . x y (x y)")
    parser = LambdaParser(lexer)
    ast = parser.parse()
    ast.display()

    print([e for e in ast.edges_breadth()])
    print([v for v in ast.vertices_breadth()])


if __name__ == '__main__':
    main()
