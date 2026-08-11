from src.app.retrieval.web_loader import (
    load_webpage,
    split_into_chunks,
)


URL = "https://www.python-httpx.org/quickstart/"


title, text = load_webpage(URL)
chunks = split_into_chunks(text)


print("TITLE:")
print(title)

print("\nTEXT LENGTH:")
print(len(text))

print("\nNUMBER OF CHUNKS:")
print(len(chunks))

print("\nFIRST CHUNK:")
print(chunks[0])

print("\nSECOND CHUNK:")
print(chunks[1])