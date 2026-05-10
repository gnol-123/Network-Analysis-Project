from graph.buildNetwork import graph

def main():
    G = graph()
    G.build()
    G.export()
    G.visualize()


if __name__ == "__main__":
    main()