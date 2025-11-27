from openai import OpenAI
from django.conf import settings
import numpy as np
from .models import *

client = OpenAI(api_key=settings.SECRET_API_KEY)
# print(settings.SECRET_API_KEY)


def generate_api_response(promptdata:str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": promptdata}
        ]
    )
    return response.choices[0].message.content
def similarity(a,b):
    a=np.array(a)
    b=np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve_relevant_chunks(query):
    query_emb = client.embeddings.create(
        model="text-embedding-3-large",
        input=query
    ).data[0].embedding

    data = MyData.objects.all()
    scored = []

    for d in data:
        score = similarity(query_emb, d.embedding)
        scored.append((score, d.text))

    # sort by similarity (desc)
    scored.sort(reverse=True, key=lambda x: x[0])

    # return top 3 chunks
    return [text for _, text in scored[:3]]

def ask_agent(query):
    print("query",query)
    chunks = retrieve_relevant_chunks(query)

    system_prompt = f"""
    You are a chatbot for Hemanth's personal portfolio.
    Only answer using the information below.
    If the answer does not exist in the knowledge base, say:
    "Sorry, I don't have information about that."

    Knowledge Base:
    {chunks}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )

    return response.choices[0].message.content

