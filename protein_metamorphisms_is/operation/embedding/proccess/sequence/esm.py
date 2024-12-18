from transformers import AutoTokenizer, EsmModel
import torch


def load_model(model_name):
    return EsmModel.from_pretrained(model_name)


def load_tokenizer(model_name):
    return AutoTokenizer.from_pretrained(model_name)


def embedding_task(sequences, model, tokenizer):
    """
    Processes sequences to generate embeddings.

    Args:
    - sequences: List of sequences to process.
    - model: Preloaded EsmModel.
    - tokenizer: Preloaded AutoTokenizer.

    Returns:
    A list of embedding records.
    """
    if not torch.cuda.is_available():
        raise Exception("CUDA is not available. This script requires a GPU with CUDA.")

    device = torch.device("cuda")
    model.to(device)

    embedding_records = []
    with torch.no_grad():
        for sequence in sequences:
            tokens = tokenizer(sequence, return_tensors="pt", truncation=True, padding="max_length", max_length=512)
            tokens = {k: v.to(device) for k, v in tokens.items()}

            try:
                outputs = model(**tokens)
                embeddings = outputs.last_hidden_state.mean(dim=1)
                embedding_shape = embeddings.shape

                # Prepare the record
                record = {
                    'sequence': sequence,
                    'embedding': embeddings.cpu().numpy().tolist()[0],
                    'shape': embedding_shape
                }

                embedding_records.append(record)
            except Exception as e:
                print(f"Failed to process sequence {sequence}: {e}")
                continue

    return embedding_records
