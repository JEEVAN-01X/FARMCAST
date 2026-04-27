import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = chromadb.Client()
ef = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="crop_diseases",
    embedding_function=ef
)

# Same disease data - in production this loads from file
diseases = [
    {"id": "1", "doc": "Jowar stem borer: leaves show dead heart, small holes in stem, caterpillar inside. Treat with chlorpyrifos spray.", "meta": {"crop": "jowar", "disease": "stem_borer"}},
    {"id": "2", "doc": "Ragi blast: oval grey spots with brown border on leaves, neck rot. Spray tricyclazole.", "meta": {"crop": "ragi", "disease": "blast"}},
    {"id": "3", "doc": "Tomato late blight: dark water soaked patches, white mold underside. Apply mancozeb.", "meta": {"crop": "tomato", "disease": "late_blight"}},
    {"id": "4", "doc": "Cotton bollworm: holes in bolls, larvae inside, shedding of squares. Spray spinosad.", "meta": {"crop": "cotton", "disease": "bollworm"}},
    {"id": "5", "doc": "Groundnut leaf spot: circular brown spots, yellowing leaves, early defoliation. Apply chlorothalonil.", "meta": {"crop": "groundnut", "disease": "leaf_spot"}},
]

collection.add(
    documents=[d["doc"] for d in diseases],
    ids=[d["id"] for d in diseases],
    metadatas=[d["meta"] for d in diseases]
)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def diagnose(farmer_query: str):
    # Step 1: find closest disease from DB
    results = collection.query(query_texts=[farmer_query], n_results=1)
    matched_disease = results["documents"][0][0]
    
    # Step 2: Groq generates simple farmer-friendly advice
    prompt = f"""You are an agricultural expert helping a Karnataka farmer.

The farmer says: "{farmer_query}"

Relevant disease information: {matched_disease}

Give a short, simple response in 3 lines max:
1. What disease this likely is
2. What to do immediately
3. What medicine/spray to use

Use simple language a farmer understands."""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    
    return response.choices[0].message.content

# Test
query = "my jowar crop has holes in the stem and the leaves are dying"
print("Farmer query:", query)
print("\nDiagnosis:")
print(diagnose(query))