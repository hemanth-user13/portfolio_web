from openai import OpenAI
from .models import *
client = OpenAI()

def gernerate_embedded():
    items=MyData.objects.all()
    for item in items:
        emb = client.embeddings.create(
            model="text-embedding-3-large",
            input=item.text
        )
        item.embedding=emb.data[0].embedding
        item.save()
    print("All embeddings generated successfully!")
    