import chromadb
from chromadb.utils import embedding_functions

# Use default embedding (no API key needed)
client = chromadb.Client()
ef = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="crop_diseases",
    embedding_function=ef
)

diseases = [
    {
        "id": "1",
        "doc": "Jowar stem borer: leaves show dead heart, small holes in stem, caterpillar inside. Treat with chlorpyrifos spray.",
        "meta": {"crop": "jowar", "disease": "stem_borer"}
    },
    {
        "id": "2", 
        "doc": "Ragi blast: oval grey spots with brown border on leaves, neck rot. Spray tricyclazole.",
        "meta": {"crop": "ragi", "disease": "blast"}
    },
    {
        "id": "3",
        "doc": "Tomato late blight: dark water soaked patches, white mold underside. Apply mancozeb.",
        "meta": {"crop": "tomato", "disease": "late_blight"}
    },
    {
        "id": "4",
        "doc": "Cotton bollworm: holes in bolls, larvae inside, shedding of squares. Spray spinosad.",
        "meta": {"crop": "cotton", "disease": "bollworm"}
    },
    {
        "id": "5",
        "doc": "Groundnut leaf spot: circular brown spots, yellowing leaves, early defoliation. Apply chlorothalonil.",
        "meta": {"crop": "groundnut", "disease": "leaf_spot"}
    },
]

collection.add(
    documents=[d["doc"] for d in diseases],
    ids=[d["id"] for d in diseases],
    metadatas=[d["meta"] for d in diseases]
)

# Test query
results = collection.query(query_texts=["jowar holes in stem dead leaves"], n_results=2)
print("Top match:", results["documents"][0][0])