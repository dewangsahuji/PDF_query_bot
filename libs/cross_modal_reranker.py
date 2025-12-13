import torch
import clip
from PIL import Image
from base64 import b64decode
from io import BytesIO

# device = "cuda" if torch.cuda.is_available() else "cpu"
device = "cpu"

clip_model, preprocess = clip.load("ViT-B/32", device=device)
clip_model.eval()

def compute_image_similarity(question, base64_img):
    """Return cosine similarity between the question and the image."""
    
    # Decode image
    img_bytes = b64decode(base64_img)
    img = Image.open(BytesIO(img_bytes)).convert("RGB")

    # Preprocess
    image_input = preprocess(img).unsqueeze(0).to(device)
    text_input = clip.tokenize([question]).to(device)

    with torch.no_grad():
        img_features = clip_model.encode_image(image_input)
        txt_features = clip_model.encode_text(text_input)

        # Normalize (VERY IMPORTANT for CLIP)
        img_features = img_features / img_features.norm(dim=-1, keepdim=True)
        txt_features = txt_features / txt_features.norm(dim=-1, keepdim=True)

    return torch.cosine_similarity(img_features, txt_features).item()

# libs/cross_modal_reranker.py

def rerank_images(query, images_b64):
    """
    Returns images sorted by CLIP similarity score
    """
    scored_images = []

    for img in images_b64:
        try:
            score = compute_image_similarity(query, img)
            scored_images.append({
                "image": img,
                "score": score
            })
        except Exception:
            continue

    # sort descending (higher similarity = better)
    scored_images.sort(key=lambda x: x["score"], reverse=True)
    return scored_images


def compute_text_similarity(query, text_content):
    """
    Compute similarity between query and text using CLIP text encoder.
    This allows cross-modal comparison.
    
    Args:
        query: The user's question/query string
        text_content: Text content to compare
    
    Returns:
        Cosine similarity score (float)
    """
    try:
        # Tokenize both texts
        query_input = clip.tokenize([query]).to(device)
        text_input = clip.tokenize([text_content[:77]]).to(device)  # CLIP has 77 token limit
        
        with torch.no_grad():
            query_features = clip_model.encode_text(query_input)
            text_features = clip_model.encode_text(text_input)
            
            # Normalize
            query_features = query_features / query_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        
        return torch.cosine_similarity(query_features, text_features).item()
    except Exception as e:
        print(f"Error computing text similarity: {e}")
        return 0.0