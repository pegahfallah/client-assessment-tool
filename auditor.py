from llama_index.core import Document, VectorStoreIndex
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from fuzzywuzzy import fuzz
import time

Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.llm = OpenAI(model="gpt-3.5-turbo")

def audit_features(documents, features, scraped_labels, batch_size=10):
    docs = [Document(text=d["text"], metadata={"url": d["url"]}) for d in documents]
    index = VectorStoreIndex.from_documents(docs)
    query_engine = index.as_query_engine()

    logic_results = {}
    for f in features:
        match = any(fuzz.partial_ratio(f.lower(), label.lower()) > 80 for label in scraped_labels)
        logic_results[f] = True if match else None

    results = []
    for i in range(0, len(features), batch_size):
        batch = features[i:i + batch_size]
        prompt = (
            "You are auditing airline service availability. For each item below, say YES, NO, or UNCLEAR based only on the airline web content.\n\n"
            "### Features:\n"
            + "\n".join([f"- {b}" for b in batch]) +
            "\n\nFormat:\nFeature | Found | Justification"
        )
        response = query_engine.query(prompt)

        for line in str(response).splitlines():
            if "|" in line:
                parts = [p.strip(" |") for p in line.split("|")]
                if len(parts) >= 3:
                    feature, found, justification = parts[0], parts[1].capitalize(), parts[2]
                    results.append({
                        "Feature": feature,
                        "Found (GPT)": found,
                        "Justification": justification,
                        "Found (Logic)": logic_results.get(feature)
                    })
        time.sleep(1)

    for r in results:
        justification = r["Justification"].lower()
        vague = any(word in justification for word in ["not mentioned", "unclear", "seems", "might", "unknown"])
        r["Final Decision"] = (
            True if r["Found (Logic)"] else
            True if r["Found (GPT)"] == "Yes" and not vague else
            False if r["Found (GPT)"] == "No" else
            "Unclear"
        )
        r["Manual Review"] = r["Final Decision"] == "Unclear" or vague

    return results
