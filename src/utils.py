def dump_gen_in_alchemy_fmt(gen, n):
    print("1\n")
    for i in range(n):
        s = gen.random_lambda()
        s = "eval " + s + ";"
        print(s)

def dump_gen(gen, n):
    for i in range(n):
        print(gen.random_lambda())
