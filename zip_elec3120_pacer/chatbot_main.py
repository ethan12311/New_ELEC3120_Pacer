class ImprovedLectureNotesChatbot:
    def __init__(self):
        # Initialize the embedding model with a better one
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        
        # Initialize the QA model with a better model from Hugging Face
        model_name = "deepset/roberta-base-squad2"
        self.qa_pipeline = pipeline(
            "question-answering", 
            model=model_name,
            tokenizer=model_name
        )
        
        # Initialize data structures
        self.chunks = []
        self.chunk_metadata = []  # Store metadata for each chunk
        self.index = None
        self.concept_keywords = {}  # Track concepts and their occurrences
        
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF file"""
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            text += f"--- Page {page_num+1} ---\n"
            text += page.extract_text() + "\n\n"
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into manageable chunks"""
        # Split by pages first
        pages = text.split("--- Page ")
        chunks = []
        metadata = []
        
        for page_content in pages[1:]:  # Skip the first empty split
            # Extract page number
            page_match = re.match(r'(\d+) ---', page_content)
            if page_match:
                page_num = int(page_match.group(1))
                page_content = page_content[page_match.end():]
            
            # Split page content into smaller chunks
            words = page_content.split()
            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i+chunk_size])
                chunks.append(chunk)
                metadata.append({
                    'page': page_num,
                    'chunk_num': len(chunks),
                    'content_preview': chunk[:100] + '...' if len(chunk) > 100 else chunk
                })
                
                # Extract potential concepts/keywords from chunk
                self._extract_concepts(chunk, page_num)
        
        return chunks, metadata
    
    def _extract_concepts(self, text: str, page: int):
        """Extract potential concepts from text"""
        # Look for capitalized words, technical terms, etc.
        concepts = re.findall(r'[A-Z][a-zA-Z]{3,}(?:\s+[A-Z][a-zA-Z]{3,})*', text)
        for concept in concepts:
            if concept not in self.concept_keywords:
                self.concept_keywords[concept] = []
            self.concept_keywords[concept].append(page)
    
    def build_index(self, chunks: List[str]):
        """Create FAISS index for semantic search"""
        embeddings = self.embedding_model.encode(chunks)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(np.array(embeddings))
        return embeddings
    
    def search_chunks(self, query: str, k: int = 5) -> List[Tuple[int, float]]:
        """Search for relevant chunks using semantic search"""
        query_embedding = self.embedding_model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding), k)
        return [(idx, distances[0][i]) for i, idx in enumerate(indices[0])]
    
    def answer_question(self, question: str, context: str) -> Dict:
        """Answer question based on provided context"""
        try:
            result = self.qa_pipeline(question=question, context=context)
            return result
        except:
            # Fallback if the model fails
            return {'answer': 'I cannot find a specific answer to this question in the provided context.', 'score': 0.0}
    
    def process_lecture_notes(self, pdf_file):
        """Process uploaded PDF file"""
        print("Extracting text from PDF...")
        text = self.extract_text_from_pdf(pdf_file)
        
        print("Chunking text and identifying concepts...")
        self.chunks, self.chunk_metadata = self.chunk_text(text)
        
        print("Building search index...")
        self.build_index(self.chunks)
        
        print(f"Processed {len(self.chunks)} chunks from lecture notes")
        print(f"Found {len(self.concept_keywords)} potential concepts")
        return True
    
    def ask_question(self, question: str):
        """Main method to ask questions and get answers"""
        if not self.index:
            return {
                "type": "error",
                "message": "Please upload and process lecture notes first."
            }
        
        # Search for relevant chunks
        results = self.search_chunks(question)
        
        # Check if we have any relevant results with good confidence
        relevant_results = []
        for idx, score in results:
            if score < 1.0:  # FAISS L2 distance, lower is better
                relevant_results.append((idx, score))
        
        if not relevant_results:
            return {
                "type": "not_found",
                "message": "This concept was not found in the lecture notes. Please try a different question or check your spelling."
            }
        
        # Use the most relevant chunk
        best_idx, best_score = min(relevant_results, key=lambda x: x[1])
        context = self.chunks[best_idx]
        page = self.chunk_metadata[best_idx]['page']
        
        # Get answer from model
        answer_result = self.answer_question(question, context)
        
        # Check if the answer is useful or just a low-confidence guess
        if answer_result['score'] < 0.2:
            # Check if the question contains any known concepts
            question_concepts = []
            for concept in self.concept_keywords:
                if concept.lower() in question.lower():
                    question_concepts.append(concept)
            
            if question_concepts:
                concept_pages = {}
                for concept in question_concepts:
                    concept_pages[concept] = self.concept_keywords[concept]
                
                return {
                    "type": "concept_reference",
                    "message": f"The concept(s) '{', '.join(question_concepts)}' appear in your notes but I couldn't find a direct answer to your question.",
                    "concepts": concept_pages
                }
            else:
                return {
                    "type": "not_found",
                    "message": "This concept was not found in the lecture notes. Please try a different question or check your spelling."
                }
        
        response = {
            "type": "answer",
            "answer": answer_result['answer'],
            "confidence": answer_result['score'],
            "page": page,
            "context": context[:300] + "..." if len(context) > 300 else context
        }
        
        return response
    
    def get_concept_references(self, concept: str):
        """Get all references to a specific concept"""
        if concept in self.concept_keywords:
            return {
                "type": "concept_reference",
                "concept": concept,
                "pages": self.concept_keywords[concept]
            }
        else:
            return {
                "type": "not_found",
                "message": f"The concept '{concept}' was not found in the lecture notes."
            }

# Initialize the chatbot
chatbot = ImprovedLectureNotesChatbot()