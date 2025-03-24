import json
import os
import numpy as np
import faiss, datetime
from sentence_transformers import SentenceTransformer
from transformers import pipeline

class RAGLLM:
    def __init__(self, booking_data_path='Data/formatted_analysis.json', index_path='Data/faiss_index.index', storage_file='Data/local_db.json'):
        """
        Initialize the RAG system with actual data and proper error handling
        """
        # Validate data paths first
        if not os.path.exists(booking_data_path):
            raise FileNotFoundError(f"Booking data file not found at {booking_data_path}")
            
        self.index, self.documents = self.load_or_build_faiss_index(booking_data_path, index_path)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.storage_file = storage_file
        self.local_storage = self.load_local_storage()
        self.llm = self.connect_local_llm()

    def load_local_storage(self):
        """Load local storage with better error handling"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load local storage - {str(e)}")
                return []
        return []

    def connect_local_llm(self):
        """Initialize LLM with better model parameters"""
        try:
            # Using a more modern small model
            llm_pipeline = pipeline(
                "text-generation",
                model="openai-community/gpt2-medium",
                device_map="auto",
            )
            return llm_pipeline
        except Exception as e:
            raise RuntimeError(f"LLM initialization failed: {str(e)}")

    def load_or_build_faiss_index(self, booking_data_path, index_path):
        """Build/load FAISS index with actual data validation"""
        with open(booking_data_path, 'r') as f:
            documents = json.load(f)
            
        if not documents:
            raise ValueError("No documents found in booking data")

        # Create embeddings with batching
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        texts = [doc["text"] for doc in documents]
        
        # Batch processing for large datasets
        batch_size = 32
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            embeddings.append(embedder.encode(batch, convert_to_numpy=True))
        embeddings = np.concatenate(embeddings)

        d = embeddings.shape[1]
        if os.path.exists(index_path):
            index = faiss.read_index(index_path)
        else:
            index = faiss.IndexFlatIP(d)  # Using inner product for similarity
            index = faiss.IndexIDMap2(index)
            index.add_with_ids(embeddings, np.array([i for i in range(len(documents))]))
            faiss.write_index(index, index_path)
            
        return index, documents
    
    def retrieve_documents(self, query, top_k=5):
        """Retrieve and preprocess documents for better context clarity"""
        query_embedding = self.embedder.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k)
    
        retrieved_docs = []
        for idx in indices[0]:
            if idx < len(self.documents):
                doc = self.documents[idx]
                # Preprocess the document text for better readability
                doc_text = f"{doc['metadata']['category'].title()}: {doc['text']}"
                retrieved_docs.append({"text": doc_text, "metadata": doc["metadata"]})
        return retrieved_docs
    
    def preprocess_query(self, query):
        """
        Preprocess and enhance the user query to get better insights
        """
        # Normalize query text
        normalized_query = query.strip().lower()
        
        # Extract potential intent and entities
        intent_keywords = {
            "cancellation": ["cancel", "refund", "cancellation rate"],
            "booking": ["book", "reservation", "booking rate"],
            "stay": ["stay", "duration", "night"],
            "analysis": ["analysis", "statistics", "report"]
        }
        
        # Detect intent
        detected_intent = None
        for intent, keywords in intent_keywords.items():
            if any(keyword in normalized_query for keyword in keywords):
                detected_intent = intent
                break
        
        # Add annotations
        query_info = {
            "original_query": query,
            "normalized_query": normalized_query,
            "detected_intent": detected_intent,
            "is_question": query.endswith("?") or any(q in query.lower() for q in ["what", "how", "why", "when", "where", "who", "tell me"]),
            "requires_numerical_answer": any(term in normalized_query for term in ["rate", "percentage", "number", "count", "how many"]),
        }
        
        return query_info
    
    def extract_answer_from_response(self, full_response, prompt):
        """
        Extract just the answer part from the LLM's full response
        """
        # Try to find where the answer starts after the full prompt
        if "Answer:" in full_response:
            # If we can find the Answer: tag, extract everything after it
            answer_part = full_response.split("Answer:")[-1].strip()
            return answer_part
        
        # If the model didn't include "Answer:" in its response, try another approach
        # Remove the prompt from the beginning of the response if it's there
        if full_response.startswith(prompt):
            clean_response = full_response[len(prompt):].strip()
            return clean_response
        
        # If we can't cleanly extract, just return the last part of the response
        # which is likely to be the generated answer
        lines = full_response.split('\n')
        if len(lines) > 5:  # If response has many lines, get last few
            return '\n'.join(lines[-3:]).strip()
        
        return full_response  # Return as is if we can't extract cleanly

    def generate_response_with_llm(self, query, retrieved_docs, query_info=None):
        """Improved generation with context validation"""
        # Use only the top 3 most relevant documents for context
        context = "\n".join([doc["text"] for doc in retrieved_docs][:3])
        context_snippet = context[:200]  # Store first 200 chars for verification
        
        # Add query intent to prompt if available
        intent_guidance = ""
        if query_info and query_info["detected_intent"]:
            intent_guidance = f"The user seems to be asking about {query_info['detected_intent']}. "
            if query_info["requires_numerical_answer"]:
                intent_guidance += "Try to provide specific numerical data. "

        prompt = (
            f"Context information:\n{context}\n\n"
            f"Instructions:\n"
            f"{intent_guidance}"
            f"1. You are an AI assistant that answers questions based strictly on the context above.\n"
            f"2. If the query is not a question or is irrelevant to the context, say 'I don't know'.\n"
            f"3. Keep your answer concise and directly based on the context.\n\n"
            f"Query: {query}\n"
            f"Answer:"
        )
        
        try:
            full_response = self.llm(
                prompt,
                max_new_tokens=50,
                temperature=0.1,  # Less creative, more factual
                repetition_penalty=1.2,
                do_sample=False
            )[0]['generated_text']
            
            # Extract just the answer part
            clean_answer = self.extract_answer_from_response(full_response, prompt)
            
            return clean_answer, context_snippet
        except Exception as e:
            print(f"Generation error: {str(e)}")
            return "I'm having trouble answering that right now.", context_snippet

    def postprocess_response(self, response, query_info=None):
        """
        Clean and enhance the response for better user experience
        """
        # Basic cleaning
        clean_response = response.strip()
        
        # Remove common useless phrases
        filler_phrases = [
            "Based on the context provided,",
            "According to the information,",
            "As per the context,",
            "From the context, I can tell you that",
            "I can answer that"
        ]
        
        for phrase in filler_phrases:
            if clean_response.startswith(phrase):
                clean_response = clean_response[len(phrase):].strip()
        
        # Ensure response is capitalized and ends with proper punctuation
        if clean_response and not clean_response.endswith(('.', '!', '?')):
            clean_response += '.'
            
        # Format numerical responses when detected
        if query_info and query_info["requires_numerical_answer"]:
            # Try to highlight numerical values if present
            for word in clean_response.split():
                if any(c.isdigit() for c in word):
                    if "%" not in word and any(term in query_info["normalized_query"] for term in ["rate", "percentage"]):
                        # If talking about a rate but no % symbol, format it as percentage if it looks like a decimal
                        try:
                            num = float(word.strip('.,;:()'))
                            if 0 <= num <= 1:
                                clean_response = clean_response.replace(word, f"{num*100:.2f}%")
                        except:
                            pass
        
        return clean_response

    def store_response(self, query, response, context_snippet, retrieved_docs, query_info=None):
        """Store responses with context verification"""
        document = {
            "query": query,
            "response": response,
            "context_snippet": context_snippet,
            "retrieved_docs": retrieved_docs,  # Store all retrieved docs
            "query_info": query_info,  # Store the query analysis
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.local_storage.append(document)
        
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.local_storage, f, indent=2)
        except IOError as e:
            print(f"Storage error: {str(e)}")

    def process_message(self, message):
        """Complete RAG workflow with preprocessing and postprocessing"""
        # Step 1: Preprocess the query
        query_info = self.preprocess_query(message)
        
        # Step 2: Retrieve relevant documents
        retrieved_docs = self.retrieve_documents(message)
        
        # Step 3: Generate initial response
        raw_response, context_snippet = self.generate_response_with_llm(message, retrieved_docs, query_info)
        
        # Step 4: Postprocess the response
        final_response = self.postprocess_response(raw_response, query_info)
        
        # Step 5: Store the complete interaction
        self.store_response(message, final_response, context_snippet, retrieved_docs, query_info)
        
        # Return the result with all necessary fields
        return {
            "response": final_response,
            "retrieved_docs": retrieved_docs,
            "context_snippet": context_snippet,
            "query_info": query_info,
            "raw_response": raw_response  # For debugging
        }

    def run_all(self, message):
        return self.process_message(message)