import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
from uuid import uuid4
from typing import List, Dict
import html2text
import re
import time

load_dotenv()

class WebScraperVectorDB:
    def __init__(self):
        # Initialize embeddings
        self.embeddings = OllamaEmbeddings(
            model="llama3"
        )
        
        # Initialize vector store
        self.vector_store = Chroma(
            collection_name="google_search_db",
            embedding_function=self.embeddings,
            persist_directory="../temp/chroma_db",
            collection_metadata={"hnsw:space": "cosine"}
        )
        
        # Load API keys
        self.SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
        self.SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
        
        if not all([self.SEARCH_API_KEY, self.SEARCH_ENGINE_ID]):
            raise ValueError("Missing required environment variables")
        
        # Initialize HTML to text converter
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = True
        self.h2t.ignore_images = True
        
    def measure_latency(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            print(f"Time taken by {func.__name__}: {elapsed_time:.2f} seconds")
            return result
        return wrapper
    
    def reset_database(self):
        """Clear the vector database"""
        self.vector_store.delete_collection()
        self.vector_store = Chroma(
            collection_name="google_search_db",
            embedding_function=self.embeddings,
            persist_directory="../temp/chroma_db",
            collection_metadata={"hnsw:space": "cosine"}
        )
    
    def fetch_google_results(self, query: str, num_results: int = 10) -> List[str]:
        """Fetch search results from Google Custom Search API"""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': query,
            'key': self.SEARCH_API_KEY,
            'cx': self.SEARCH_ENGINE_ID,
            'num': num_results
        }
        
        try:
            response = requests.get(url=url, params=params)
            response.raise_for_status()
            search_results = response.json()
            
            if 'items' not in search_results:
                return []
            
            return [item['link'] for item in search_results['items']]
        except requests.RequestException as e:
            print(f"Error fetching Google results: {e}")
            return []
    
    def fetch_and_parse_url(self, url: str) -> str:
        """Fetch and parse content from a URL"""
        try:
            # Add user agent to avoid blocks
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            # soup = soup.find('body').findChildren(recursive=False)
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'img', 'svg']):
                element.decompose()
            
            # Convert to plain text
            text = self.h2t.handle(str(soup))
            
            # Clean up the text
            text = re.sub(r'\s+', ' ', text).strip()
            return text
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        if len(text) <= chunk_size:
            return [text]
        
        start = 0
        while start < len(text):
            end = start + chunk_size
            
            # Adjust chunk end to nearest sentence if possible
            if end < len(text):
                next_period = text.find('.', end)
                if next_period != -1 and next_period - end < 100:
                    end = next_period + 1
            
            chunks.append(text[start:end])
            start = end - overlap
            
        return chunks
    
    def filter_relevant_chunks(self, query: str, documents: List[Document], top_n: int = 10) -> List[Document]:
        tokenized_corpus = [doc.page_content.split(" ") for doc in documents]
        bm25 = BM25Okapi(tokenized_corpus)
        scores = bm25.get_scores(query.split(" "))
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
        return [documents[i] for i in top_indices]
    
    @measure_latency
    def process_query(self, query: str, num_results: int = 10, batch_size: int = 10) -> None:
        """Process a search query and store results in vector database"""
        # Reset database
        self.reset_database()
        
        # Fetch URLs
        urls = self.fetch_google_results(query, num_results)
        
        # Process each URL
        documents = []
        for url_index, url in enumerate(urls):
            content = self.fetch_and_parse_url(url)
            if content:
                chunks = self.chunk_text(content)
                for chunk_index, chunk in enumerate(chunks):
                    # documents.append({
                    #     "page_content": chunk,
                    #     "metadata": {"source": url}
                    # })
                    documents.append(
                        Document(
                            page_content=chunk,
                            metadata={"source": url},
                            # id=f"{url_index}_{chunk_index}_{uuid4()}"
                        )
                    )
        
        # # Generate UUIDs for documents
        # uuids = [str(uuid4()) for _ in range(len(documents))]
        
        # # Add to vector store
        # self.vector_store.add_documents(documents=documents, ids=uuids)
        
        # Filter relevant chunks with BM25
        filtered_documents = self.filter_relevant_chunks(query, documents, top_n=20)
        
        # Batch the addition to vector store
        for i in range(0, len(filtered_documents), batch_size):
            batch = filtered_documents[i:i + batch_size]
            uuids = [str(uuid4()) for _ in range(len(batch))]
            self.vector_store.add_documents(documents=batch, ids=uuids)
    
    @measure_latency
    def get_context(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve relevant context for a query"""
        results = self.vector_store.similarity_search(query=query, k=k)
        return [{
            'content': doc.page_content,
            'source': doc.metadata.get('source', 'Unknown')
        } for doc in results]