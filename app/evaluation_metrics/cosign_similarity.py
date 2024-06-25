import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from cloud_services.llm_services import AzureLLMClients, get_llm_client
from settings.settings import Settings

# Initialize settings and Azure client
settings = Settings()
azure_llm_client: AzureLLMClients = get_llm_client(api_type='azure',
                                                   api_version=settings.OPENAI_API_VERSION,
                                                   endpoint=settings.AZURE_OPENAI_ENDPOINT,
                                                   model=settings.GPT35_MODEL_NAME,
                                                   deployment=settings.GPT35_DEPLOYMENT_NAME,
                                                   embedding_deployment=settings.EMBEDDING)

# Load the CSV file
file_path = 'aggregated_results.csv'
df = pd.read_csv(file_path)

# Check if the necessary columns are present
if 'description' not in df.columns or 'content' not in df.columns:
    raise ValueError("The CSV file must contain 'description' and 'content' columns.")

# Fill NaN values with empty strings to avoid issues with vectorization
df['description'] = df['description'].fillna('')
df['content'] = df['content'].fillna('')

# Initialize the embedding function
def embed_text(text):
    return azure_llm_client.embed_to_array(text)

# Apply embedding to each row
df['description_embedding'] = df['description'].apply(embed_text)
df['content_embedding'] = df['content'].apply(embed_text)

# Initialize the TF-IDF Vectorizer
vectorizer = TfidfVectorizer()

# Fit and transform the text data
tfidf_matrix_description = vectorizer.fit_transform(df['description'])
tfidf_matrix_content = vectorizer.transform(df['content'])

# Compute the cosine similarity for each pair of embeddings
def compute_cosine_similarity(row):
    description_embedding = row['description_embedding']
    content_embedding = row['content_embedding']
    return cosine_similarity([description_embedding], [content_embedding])[0][0]

# Apply the cosine similarity function for embeddings to each row
df['cosine_similarity_oai_large-v3'] = df.apply(compute_cosine_similarity, axis=1)

# Compute the cosine similarity for each pair of TF-IDF vectors
def compute_cosine_similarity_tfidf(row_idx):
    description_vector = tfidf_matrix_description[row_idx]
    content_vector = tfidf_matrix_content[row_idx]
    return cosine_similarity(description_vector, content_vector)[0][0]

# Apply the cosine similarity function for TF-IDF vectors to each row index
#df['cosine_similarity_tfidf'] = [compute_cosine_similarity_tfidf(i) for i in range(len(df))]

# Remove the embedding columns
df = df.drop(columns=['description_embedding', 'content_embedding'])

# Save the updated dataframe back to the CSV file
df.to_csv(file_path, index=False)

print(f"Cosine similarity scores have been appended and saved to {file_path}")
