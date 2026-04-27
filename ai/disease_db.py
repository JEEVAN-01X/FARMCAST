import os
import chromadb
from chromadb.utils import embedding_functions

DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

def get_collection():
    client = chromadb.PersistentClient(path=DB_PATH)
    ef = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection(
        name="crop_diseases",
        embedding_function=ef
    )
    return collection

DISEASES = [
    {"id": "jowar_01", "doc": "Jowar stem borer: dead heart in young plants, small round holes in stem, whitish caterpillar found inside stem when split open, leaves dry from center outward. Treat with Chlorpyrifos 20EC at 2.5ml per litre, spray at base of plant. Repeat after 15 days.", "meta": {"crop": "jowar", "kannada": "ಜೋಳ", "disease": "stem_borer", "type": "pest"}},
    {"id": "jowar_02", "doc": "Jowar shoot fly: dead heart in seedlings within 30 days of sowing, maggot found at base of central shoot, plant pulls out easily, no holes visible on outside. Treat with Imidacloprid 17.8SL seed treatment at 5ml per kg seed before sowing.", "meta": {"crop": "jowar", "kannada": "ಜೋಳ", "disease": "shoot_fly", "type": "pest"}},
    {"id": "jowar_03", "doc": "Jowar grain mold: pink red grey or black fungal growth on grain, shrivelled grain, poor germination. Caused by Fusarium and Curvularia in wet weather at maturity. Spray Mancozeb 75WP at 2g per litre at 50% flowering. Harvest early if rains continue.", "meta": {"crop": "jowar", "kannada": "ಜೋಳ", "disease": "grain_mold", "type": "disease"}},
    {"id": "jowar_04", "doc": "Jowar downy mildew: white downy growth on underside of leaves, yellowing and striping on upper surface, plant becomes bushy and stunted called green ear. Spray Metalaxyl plus Mancozeb at 2.5g per litre. Remove and burn infected plants.", "meta": {"crop": "jowar", "kannada": "ಜೋಳ", "disease": "downy_mildew", "type": "disease"}},
    {"id": "ragi_01", "doc": "Ragi blast: oval to spindle shaped grey spots with brown or reddish border on leaves, neck of ear head turns black and breaks called neck rot, grain becomes shrivelled. Spray Tricyclazole 75WP at 0.6g per litre at tillering and again at boot stage.", "meta": {"crop": "ragi", "kannada": "ರಾಗಿ", "disease": "blast", "type": "disease"}},
    {"id": "ragi_02", "doc": "Ragi foot rot: plants wilt suddenly, lower stem and roots turn brown and rot, plant pulls out easily, white fungal growth at base. Caused by Sclerotium rolfsii. Treat soil with Carbendazim 50WP at 2g per litre as drench around base. Remove infected plants.", "meta": {"crop": "ragi", "kannada": "ರಾಗಿ", "disease": "foot_rot", "type": "disease"}},
    {"id": "ragi_03", "doc": "Ragi aphids: small soft black or green insects clustered on underside of leaves and young shoots, yellowing curling leaves, sticky honeydew on plant, ants present. Spray Dimethoate 30EC at 1.5ml per litre or Imidacloprid 17.8SL at 0.5ml per litre.", "meta": {"crop": "ragi", "kannada": "ರಾಗಿ", "disease": "aphids", "type": "pest"}},
    {"id": "tomato_01", "doc": "Tomato late blight: dark water soaked patches on leaves and stems turning brown to black, white downy mold on underside of leaf in humid weather, fruit shows dark firm rot. Spray Mancozeb 75WP at 2g per litre or Cymoxanil plus Mancozeb at 2g per litre every 7 days.", "meta": {"crop": "tomato", "kannada": "ಟೊಮೇಟೊ", "disease": "late_blight", "type": "disease"}},
    {"id": "tomato_02", "doc": "Tomato leaf curl virus: leaves curl upward and inward, become thick leathery and yellowish, plant stunted, no fruit set. Spread by whitefly. No cure once infected. Remove infected plants. Control whitefly with Imidacloprid 17.8SL at 0.5ml per litre. Use yellow sticky traps.", "meta": {"crop": "tomato", "kannada": "ಟೊಮೇಟೊ", "disease": "leaf_curl_virus", "type": "virus"}},
    {"id": "tomato_03", "doc": "Tomato fruit borer: pin hole entry on fruit, caterpillar inside fruit eating pulp, fruit becomes rotten and drops, frass visible at entry hole. Spray Spinosad 45SC at 0.3ml per litre or Chlorantraniliprole 18.5SC at 0.4ml per litre. Install pheromone traps.", "meta": {"crop": "tomato", "kannada": "ಟೊಮೇಟೊ", "disease": "fruit_borer", "type": "pest"}},
    {"id": "tomato_04", "doc": "Tomato damping off: seedlings collapse at soil level, stem becomes thin and water soaked at base, seedlings die in patches in nursery. Drench nursery bed with Copper oxychloride 50WP at 3g per litre or Carbendazim 50WP at 1g per litre before sowing.", "meta": {"crop": "tomato", "kannada": "ಟೊಮೇಟೊ", "disease": "damping_off", "type": "disease"}},
    {"id": "tomato_05", "doc": "Tomato bacterial wilt: plant wilts suddenly without yellowing, lower leaves droop, cut stem shows brown discoloration in vascular ring, milky bacterial ooze in water. No chemical cure. Remove and destroy plant. Avoid waterlogging. Use resistant varieties.", "meta": {"crop": "tomato", "kannada": "ಟೊಮೇಟೊ", "disease": "bacterial_wilt", "type": "disease"}},
    {"id": "cotton_01", "doc": "Cotton bollworm American: pin holes on young bolls, caterpillar feeds inside boll, bolls shed and fall, green caterpillar with white stripes visible. Spray Chlorantraniliprole 18.5SC at 0.4ml per litre or Spinosad 45SC at 0.3ml per litre. Install pheromone traps for monitoring.", "meta": {"crop": "cotton", "kannada": "ಹತ್ತಿ", "disease": "american_bollworm", "type": "pest"}},
    {"id": "cotton_02", "doc": "Cotton pink bollworm: square and boll shedding, entry hole in boll sealed with frass, pink coloured caterpillar inside boll eating seed, lint staining. Spray Profenofos 50EC at 2ml per litre. Collect and destroy fallen bolls. Use pheromone traps.", "meta": {"crop": "cotton", "kannada": "ಹತ್ತಿ", "disease": "pink_bollworm", "type": "pest"}},
    {"id": "cotton_03", "doc": "Cotton whitefly and sucking pests: yellowing of leaves, curling, honeydew and sooty mold blackening on leaves, silvering of leaf underside, stunted plant. Spray Flonicamid 50WG at 0.3g per litre or Spiromesifen 22.9SC at 0.9ml per litre. Avoid Imidacloprid after 60 days.", "meta": {"crop": "cotton", "kannada": "ಹತ್ತಿ", "disease": "whitefly", "type": "pest"}},
    {"id": "cotton_04", "doc": "Cotton bacterial blight: angular water soaked spots on leaves, blackening of veins, black arm on stem and branches, boll rot with dark lesions. Spray Streptomycin sulphate plus Copper oxychloride at 400g plus 1250g per acre. Remove infected plant parts.", "meta": {"crop": "cotton", "kannada": "ಹತ್ತಿ", "disease": "bacterial_blight", "type": "disease"}},
    {"id": "groundnut_01", "doc": "Groundnut early leaf spot: circular dark brown spots with yellow halo on upper leaf surface, spots first appear on lower leaves and move upward, early defoliation in severe cases. Spray Chlorothalonil 75WP at 2g per litre or Mancozeb 75WP at 2g per litre every 10 days from 30 days after sowing.", "meta": {"crop": "groundnut", "kannada": "ಕಡಲೆಕಾಯಿ", "disease": "early_leaf_spot", "type": "disease"}},
    {"id": "groundnut_02", "doc": "Groundnut late leaf spot: dark brown to black circular spots on both surfaces, no yellow halo, severe defoliation, yield loss up to 50 percent. Spray Propiconazole 25EC at 1ml per litre or Tebuconazole at 1ml per litre. Start sprays at first sign of spots.", "meta": {"crop": "groundnut", "kannada": "ಕಡಲೆಕಾಯಿ", "disease": "late_leaf_spot", "type": "disease"}},
    {"id": "groundnut_03", "doc": "Groundnut stem rot: collar rot at soil level, white cottony mycelium and small brown seed like sclerotia on stem and soil, plant wilts and dies, pods rot in soil. Treat seed with Thiram 75WS at 3g per kg seed. Drench with Carbendazim 50WP at 1g per litre.", "meta": {"crop": "groundnut", "kannada": "ಕಡಲೆಕಾಯಿ", "disease": "stem_rot", "type": "disease"}},
    {"id": "groundnut_04", "doc": "Groundnut thrips and virus: silvery streaks on leaves, leaf tip curling, plant stunted, bud necrosis virus spread by thrips causes terminal bud death and bushy appearance. Spray Imidacloprid 17.8SL at 0.5ml per litre or Fipronil 5SC at 1.5ml per litre to control thrips vector.", "meta": {"crop": "groundnut", "kannada": "ಕಡಲೆಕಾಯಿ", "disease": "thrips_bud_necrosis", "type": "pest"}},
]

def build_db():
    collection = get_collection()
    existing = collection.get()
    existing_ids = set(existing["ids"])
    new_docs = [d for d in DISEASES if d["id"] not in existing_ids]
    if not new_docs:
        print(f"DB already has {len(existing_ids)} entries. Nothing to add.")
        return collection
    collection.add(
        documents=[d["doc"] for d in new_docs],
        ids=[d["id"] for d in new_docs],
        metadatas=[d["meta"] for d in new_docs]
    )
    print(f"Added {len(new_docs)} entries. Total: {len(existing_ids) + len(new_docs)}")
    return collection

def query_disease(symptom_text, crop=None, n=3):
    collection = get_collection()
    where = {"crop": crop.lower()} if crop else None
    results = collection.query(query_texts=[symptom_text], n_results=n, where=where)
    matches = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        matches.append({"doc": doc, "crop": meta["crop"], "disease": meta["disease"], "type": meta["type"], "distance": round(dist, 4)})
    return matches

if __name__ == "__main__":
    build_db()
    print("\n--- Test: jowar holes in stem dead center leaf ---")
    for m in query_disease("jowar holes in stem dead center leaf", n=2):
        print(f"[{m['crop']} / {m['disease']}] dist={m['distance']}")
        print(f"  {m['doc'][:120]}...")
    print("\n--- Test: tomato leaves curling upward thickening ---")
    for m in query_disease("tomato leaves curling upward thickening", crop="tomato", n=2):
        print(f"[{m['crop']} / {m['disease']}] dist={m['distance']}")
        print(f"  {m['doc'][:120]}...")
