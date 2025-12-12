# from Data import summaries
from unstructured.documents.elements import Table, CompositeElement
import json
from unstructured.staging.base import dict_to_elements

# Load chunks.json
with open("chunks.json", "r", encoding="utf-8") as f:
    chunks_dict = json.load(f)

chunks = dict_to_elements(chunks_dict)


# separate tables from texts
tables = []
texts = []
# images = []

for chunk in chunks:
    if "Table" in str(type(chunk)):
        tables.append(chunk)

    if "CompositeElement" in str(type((chunk))):
        texts.append(chunk)

# Get the images from the CompositeElement objects
def get_images_base64(chunks):
    images_b64 = []
    for chunk in chunks:
        if "CompositeElement" in str(type(chunk)):
            chunk_els = chunk.metadata.orig_elements
            for el in chunk_els:
                if "Image" in str(type(el)):
                    images_b64.append(el.metadata.image_base64)
    return images_b64



def get_tables(chunks):
    tables = []
    for chunk in chunks:
        if isinstance(chunk, CompositeElement):
            for el in chunk.metadata.orig_elements:
                if isinstance(el, Table):
                    tables.append(el)
    return tables
tables = get_tables(chunks)
images = get_images_base64(chunks)



# print(len(texts))
# print(len(tables))
# print(len(images))









