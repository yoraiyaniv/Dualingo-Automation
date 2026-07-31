from transformers import AutoTokenizer, AutoModelForMaskedLM
import torch


model_name = "xlm-roberta-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForMaskedLM.from_pretrained(model_name)

def fill_blank(sentence: str, candidates: list[str]) -> str:
    inputs = tokenizer(sentence, return_tensors="pt")
    mask_index = (inputs.input_ids == tokenizer.mask_token_id).nonzero(as_tuple=True)[1]
    
    with torch.no_grad():
        logits = model(**inputs).logits
    
    scores = {}

    for word in candidates:
        token_id = tokenizer.encode(word, add_special_tokens=False)[0]
        scores[word] = logits[0, mask_index, token_id].item()
        
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[0]

# Example inputs and outputs:
# sentence = "Ella fue al <mask> para comprar pan."
# candidates = ["store", "car", "keyboard", "cloud"]