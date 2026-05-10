import networkx as nx
from pathlib import Path
import json
from pyvis.network import Network

proj_root = Path(__file__).parent.parent
RAW = proj_root / "artifacts" / "youtubeData-metGala.json"
OUTPUTGRAPH = proj_root / "artifacts" / "graph" / "metgalaNetwork.graphml"

class graph:
# INIT ===========================================================================================================

    def __init__(self):
        self.G = nx.MultiDiGraph()
        try:
            self.G = nx.read_graphml(path=OUTPUTGRAPH)
        except FileNotFoundError as e:
            print(f"Tried reading graph from memory, failed. Graph doesn't exist yet.")
        
# BUILD ==========================================================================================================

    def build(self, rawPath=RAW):

        with open(rawPath) as f:
            data = json.load(f)

        for video in data["videos"]:

            # Add channel and video nodes
            self.G.add_node(video["channelId"], label=video["channelTitle"], node_type="channel")
            self.G.add_node(video["videoId"],   label=video["title"],        node_type="video",
                    view_count=video["viewCount"], like_count=video["likeCount"])

            # Channel to Video edge
            self.G.add_edge(video["channelId"], video["videoId"], edge_type="UPLOADED")

            for comment in video["comments"]:
                # Add user node setdefault pattern avoids overwriting existing nodes
                if comment["authorId"] not in G:
                    self.G.add_node(comment["authorId"], label=comment["author"], node_type="user")

                # User to Video edge
                self.G.add_edge(comment["authorId"], comment["videoId"],
                        edge_type="COMMENTED_ON",
                        weight=max(comment["likeCount"], 1),
                        published_at=comment["publishedAt"])

                # User replies edge
                if comment["isReply"] and comment["replyToAuthorId"]:
                    if comment["replyToAuthorId"] not in G:
                        self.G.add_node(comment["replyToAuthorId"], node_type="user")
                    self.G.add_edge(comment["authorId"], comment["replyToAuthorId"],
                            edge_type="REPLIED_TO",
                            comment_id=comment["commentId"])


        print(f"Nodes: {self.G.number_of_nodes()}")
        print(f"Edges: {self.G.number_of_edges()}")

# VISUALIZE ======================================================================================================================

    def visualize(self):
        # Get top nodes
        top_nodes = sorted(self.G.degree(), key=lambda x: x[1], reverse=True)[:1000]
        G_sub = self.G.subgraph([n for n, d in top_nodes])

        net = Network(height="750px", width="100%", directed=False, notebook=False)
        net.from_nx(G_sub)

        # Colour by node type
        for node in net.nodes:
            if self.G.nodes[node["id"]].get("node_type") == "channel":
                node["color"] = "#e74c3c"   # channel
            elif self.G.nodes[node["id"]].get("node_type") == "video":
                node["color"] = "#3498db"   # video
            else:
                node["color"] = "#95a5a6"   # user

        for edge in net.edges:
            edge["label"] = ""
            edge["title"] = ""
            edge["width"] = 0.5
            edge["color"] = "#cccccc"
            
        net.set_options("""
        {
        "edges": {
            "arrows": { "to": { "enabled": false } },
            "color": { "color": "#cccccc", "opacity": 0.75 },
            "width": 0.5,
            "smooth": { "enabled": false }
        },
        "physics": {
            "forceAtlas2Based": {
            "gravitationalConstant": -50,
            "springLength": 100
            },
            "solver": "forceAtlas2Based"
        }
        }
        """)

        net.show("metgala_graph.html", notebook=False)

# EXPORT =========================================================================================================================

    def export(self, outPath = OUTPUTGRAPH):
        nx.write_graphml(self.G, outPath)
