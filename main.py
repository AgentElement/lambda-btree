from src.random_btree import random_btree
from src.lambda_parse import LambdaLexer, LambdaParser


def main():
    NODES = 20
    MAX_FREE_VARIABLES = 10
    EXPRESSIONS = 10

    # If you need a single tree
    tree = random_btree(NODES)

    for i in range(EXPRESSIONS):
        tree = random_btree(NODES)
        tree.display()
        print()
        lambda_expr = tree.tolambda(MAX_FREE_VARIABLES)
        print(lambda_expr)
        print()
        lexer = LambdaLexer(lambda_expr)
        parser = LambdaParser(lexer)
        ast = parser.parse()
        ast.display()
        print()


if __name__ == '__main__':
    main()
