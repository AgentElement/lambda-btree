from src.btree_generator import BtreeGen
from src.fontana_generator import FontanaGen
from src.lambda_parse import LambdaLexer, LambdaParser

from ete3 import Tree, TreeStyle, CircleFace, TextFace, AttrFace, faces


def my_layout(node):
    print(node.name)
    if node.is_leaf():
        name_face = AttrFace("name")  # draw name for leaves
    else:  # internal node
        if node.name == "":
            name_face = CircleFace(5, "red")
        else:
            name_face = AttrFace("name", fsize=10)  # draw label with small font

    # Add the name face to the image at the preferred position
    faces.add_face_to_node(name_face, node, column=0)



def main():
    NODES = 20
    MAX_FREE_VARIABLES = 10
    EXPRESSIONS = 10

    # If you need a single tree
    for gix, gen in enumerate([FontanaGen(), BtreeGen()]):
        for i in range(6):
            lambda_expr = gen.random_lambda()

            lexer = LambdaLexer(lambda_expr)
            parser = LambdaParser(lexer)

            ast = parser.parse()
            t = ast.to_ete3()
            ts = TreeStyle()
            ts.show_leaf_name = False
            ts.layout_fn = my_layout
            ts.show_scale = False
            #  ts.mode = 'c'
            #  ts.arc_start = -180 # 0 degrees = 3 o'clock
            #  ts.arc_span = 180
            #  ts.force_topology = True
            t.render(f"tree_{gix}_{i}.svg", tree_style=ts, w=512, units='px')
            print(t.get_ascii(show_internal=True))

    #
    #  for i in range(EXPRESSIONS):
    #      tree = random_btree(NODES)
    #      tree.display()
    #      print()
    #      lambda_expr = tree.tolambda(MAX_FREE_VARIABLES)
    #      print(lambda_expr)
    #      print()
    #      lexer = LambdaLexer(lambda_expr)
    #      parser = LambdaParser(lexer)
    #      ast = parser.parse()
    #      ast.display()
    #      print()


if __name__ == '__main__':
    main()
