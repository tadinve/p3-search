from sentence_transformers import SentenceTransformer
import os

# Define the model name and the path to save it
model_name = 'all-MiniLM-L6-v2'
save_path = os.path.join('/app/models', model_name)

# Download and save the model
print(f"Downloading model '{model_name}' to '{save_path}'...")
model = SentenceTransformer(model_name)
model.save(save_path)
print("Model downloaded and saved successfully.")