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
