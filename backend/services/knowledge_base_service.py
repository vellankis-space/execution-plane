import uuid
import os
import aiohttp
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader, WebBaseLoader
from langchain_core.documents import Document
from bs4 import BeautifulSoup
import requests
from ollama import Client as OllamaClient

from models.knowledge_base import KnowledgeBase, KnowledgeDocument, KnowledgeSourceType, ProcessingStatus
from schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeDocumentCreate, KnowledgeBaseQuery, KnowledgeBaseQueryResult

# Singleton QdrantClient to prevent lock conflicts
# Qdrant local mode only allows one client instance at a time
_qdrant_client = None

def get_qdrant_client():
    """Get or create singleton QdrantClient instance"""
    global _qdrant_client
    if _qdrant_client is None:
        # Use separate path from mem0's /tmp/qdrant to avoid lock conflicts
        _qdrant_client = QdrantClient(path="/tmp/qdrant_kb")
    return _qdrant_client


class KnowledgeBaseService:
    def __init__(self, db: Session):
        self.db = db
        self.qdrant_client = get_qdrant_client()  # Use singleton instance
        self.ollama_client = OllamaClient(host="http://localhost:11434")
        self.upload_dir = "/tmp/knowledge_base_uploads"
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def _generate_collection_name(self, agent_id: str, kb_name: str) -> str:
        sanitized_name = kb_name.lower().replace(" ", "_").replace("-", "_")
        return f"kb_{agent_id[:8]}_{sanitized_name}_{uuid.uuid4().hex[:8]}"
    
    def _get_embeddings(self, texts: List[str], model: str = "qwen3-embedding:0.6b") -> List[List[float]]:
        """Generate embeddings with error handling and timeout"""
        embeddings = []
        try:
            for text in texts:
                # Truncate text to prevent embedding timeouts
                truncated_text = text[:8000] if len(text) > 8000 else text
                response = self.ollama_client.embeddings(model=model, prompt=truncated_text)
                embeddings.append(response['embedding'])
            return embeddings
        except Exception as e:
            error_msg = str(e).lower()
            if "connection" in error_msg or "refused" in error_msg:
                raise Exception("Ollama server is not running. Please start Ollama: 'ollama serve'")
            elif "not found" in error_msg or "pull" in error_msg:
                raise Exception(f"Embedding model '{model}' not found. Please pull it: 'ollama pull {model}'")
            else:
                raise Exception(f"Failed to generate embeddings: {str(e)}")
    
    async def create_knowledge_base(self, kb_data: KnowledgeBaseCreate) -> KnowledgeBase:
        kb_id = str(uuid.uuid4())
        collection_name = self._generate_collection_name(kb_data.agent_id, kb_data.name)
        
        try:
            embedding_dim = len(self._get_embeddings(["test"], kb_data.embedding_model)[0])
        except:
            embedding_dim = 1024
        
        self.qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE)
        )
        
        db_kb = KnowledgeBase(
            kb_id=kb_id,
            agent_id=kb_data.agent_id,
            name=kb_data.name,
            description=kb_data.description,
            collection_name=collection_name,
            embedding_model=kb_data.embedding_model,
            chunk_size=kb_data.chunk_size,
            chunk_overlap=kb_data.chunk_overlap
        )
        
        self.db.add(db_kb)
        self.db.commit()
        self.db.refresh(db_kb)
        return db_kb
    
    async def get_knowledge_base(self, kb_id: str) -> Optional[KnowledgeBase]:
        return self.db.query(KnowledgeBase).filter(KnowledgeBase.kb_id == kb_id).first()
    
    async def get_knowledge_bases_by_agent(self, agent_id: str) -> List[KnowledgeBase]:
        return self.db.query(KnowledgeBase).filter(KnowledgeBase.agent_id == agent_id).all()
    
    async def delete_knowledge_base(self, kb_id: str) -> bool:
        kb = await self.get_knowledge_base(kb_id)
        if not kb:
            return False
        
        try:
            self.qdrant_client.delete_collection(collection_name=kb.collection_name)
        except:
            pass
        
        self.db.query(KnowledgeDocument).filter(KnowledgeDocument.kb_id == kb_id).delete()
        self.db.delete(kb)
        self.db.commit()
        return True
    
    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_text(text)
    
    async def _fetch_url_content(self, url: str) -> str:
        """Fetch and extract readable text from a URL.
        Strategy:
        1) Try LangChain's WebBaseLoader (async) for robust HTML parsing.
        2) Fallback to aiohttp + BeautifulSoup with proper headers, timeouts, and redirects.
        """
        # 1) Try WebBaseLoader (async)
        try:
            loader = WebBaseLoader([url])
            # Be a good citizen; also avoids burst blocks
            loader.requests_per_second = 1
            docs = await loader.aload()
            text = "\n\n".join([d.page_content for d in docs]) if docs else ""
            if text and len(text.strip()) >= 50:
                return text
        except Exception as e:
            # Fall through to aiohttp fallback
            print(f"WebBaseLoader failed for {url}: {e}")

        # 2) Fallback: aiohttp with headers, timeout, redirects
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }
        timeout = aiohttp.ClientTimeout(total=25)
        try:
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(url, allow_redirects=True) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to fetch URL: {response.status}")
                    content_type = response.headers.get("Content-Type", "")
                    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                        # Not HTML-like; skip
                        html = await response.text(errors="ignore")
                    else:
                        html = await response.text(errors="ignore")
                    soup = BeautifulSoup(html, 'html.parser')
                    for el in soup(["script", "style", "noscript", "template"]):
                        el.decompose()
                    text = soup.get_text(separator='\n', strip=True)
                    if not text or len(text.strip()) < 10:
                        raise Exception("Extracted empty content from page")
                    return text
        except Exception as e:
            # Retry once disabling SSL verification as a last resort
            try:
                async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                    async with session.get(url, allow_redirects=True, ssl=False) as response:
                        if response.status != 200:
                            raise Exception(f"Failed to fetch URL (no-ssl): {response.status}")
                        html = await response.text(errors="ignore")
                        soup = BeautifulSoup(html, 'html.parser')
                        for el in soup(["script", "style", "noscript", "template"]):
                            el.decompose()
                        text = soup.get_text(separator='\n', strip=True)
                        if not text or len(text.strip()) < 10:
                            raise Exception("Extracted empty content from page (no-ssl)")
                        return text
            except Exception as e2:
                raise Exception(f"Failed to fetch URL content after retries: {e2}")
    
    async def add_document(self, doc_data: KnowledgeDocumentCreate, process_immediately: bool = True) -> KnowledgeDocument:
        kb = await self.get_knowledge_base(doc_data.kb_id)
        if not kb:
            raise ValueError("Knowledge base not found")
        
        doc_id = str(uuid.uuid4())
        db_doc = KnowledgeDocument(
            doc_id=doc_id,
            kb_id=doc_data.kb_id,
            source_type=doc_data.source_type,
            source_content=doc_data.source_content,
            source_url=doc_data.source_url,
            file_name=doc_data.file_name,
            status=ProcessingStatus.PENDING
        )
        
        self.db.add(db_doc)
        self.db.commit()
        self.db.refresh(db_doc)
        
        # For file uploads, the file_path may be set after this call by the API route.
        # In that case, processing should be triggered explicitly later.
        if process_immediately:
            await self._process_document(db_doc, kb)
        
        return db_doc
    
    async def _process_document(self, doc: KnowledgeDocument, kb: KnowledgeBase):
        try:
            doc.status = ProcessingStatus.PROCESSING
            self.db.commit()
            
            if doc.source_type == KnowledgeSourceType.TEXT:
                content = doc.source_content
            elif doc.source_type == KnowledgeSourceType.URL:
                content = await self._fetch_url_content(doc.source_url)
                doc.source_content = content[:1000]
            elif doc.source_type == KnowledgeSourceType.FILE:
                content = self._load_file_content(doc.file_path)
            else:
                raise ValueError(f"Unsupported source type: {doc.source_type}")
            
            chunks = self._chunk_text(content, kb.chunk_size, kb.chunk_overlap)
            embeddings = self._get_embeddings(chunks, kb.embedding_model)
            
            points = []
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                points.append(
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            "text": chunk,
                            "doc_id": doc.doc_id,
                            "kb_id": kb.kb_id,
                            "agent_id": kb.agent_id,
                            "chunk_index": idx,
                            "source_type": doc.source_type.value,
                            "source_url": doc.source_url,
                            "file_name": doc.file_name
                        }
                    )
                )
            
            self.qdrant_client.upsert(
                collection_name=kb.collection_name,
                points=points
            )
            
            doc.chunk_count = len(chunks)
            doc.status = ProcessingStatus.COMPLETED
            self.db.commit()
            
        except Exception as e:
            doc.status = ProcessingStatus.FAILED
            doc.error_message = str(e)
            self.db.commit()
            raise e
    
    def _load_file_content(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            return "\n\n".join([doc.page_content for doc in docs])
        elif ext == '.docx':
            loader = Docx2txtLoader(file_path)
            docs = loader.load()
            return "\n\n".join([doc.page_content for doc in docs])
        elif ext in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.json':
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert JSON to readable text format
                return json.dumps(data, indent=2, ensure_ascii=False)
        elif ext in ['.html', '.htm']:
            loader = UnstructuredHTMLLoader(file_path)
            docs = loader.load()
            return "\n\n".join([doc.page_content for doc in docs])
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    async def query_knowledge_base(self, kb_id: str, query_data: KnowledgeBaseQuery) -> List[KnowledgeBaseQueryResult]:
        kb = await self.get_knowledge_base(kb_id)
        if not kb:
            raise ValueError("Knowledge base not found")
        
        query_embedding = self._get_embeddings([query_data.query], kb.embedding_model)[0]
        
        search_results = self.qdrant_client.search(
            collection_name=kb.collection_name,
            query_vector=query_embedding,
            limit=query_data.top_k,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="kb_id",
                        match=MatchValue(value=kb_id)
                    )
                ]
            )
        )
        
        results = []
        for result in search_results:
            results.append(
                KnowledgeBaseQueryResult(
                    content=result.payload.get("text", ""),
                    score=result.score,
                    metadata={
                        "doc_id": result.payload.get("doc_id"),
                        "chunk_index": result.payload.get("chunk_index"),
                        "source_type": result.payload.get("source_type"),
                        "source_url": result.payload.get("source_url"),
                        "file_name": result.payload.get("file_name")
                    }
                )
            )
        
        return results
    
    async def query_agent_knowledge(self, agent_id: str, query: str, top_k: int = 5) -> str:
        """Query knowledge bases for an agent with error handling"""
        try:
            knowledge_bases = await self.get_knowledge_bases_by_agent(agent_id)
            
            if not knowledge_bases:
                return ""
            
            all_results = []
            for kb in knowledge_bases:
                try:
                    query_data = KnowledgeBaseQuery(query=query, top_k=top_k)
                    results = await self.query_knowledge_base(kb.kb_id, query_data)
                    all_results.extend(results)
                except Exception as kb_error:
                    # Log error but continue with other knowledge bases
                    print(f"Error querying knowledge base {kb.kb_id}: {str(kb_error)}")
                    continue
            
            if not all_results:
                return ""
            
            all_results.sort(key=lambda x: x.score, reverse=True)
            top_results = all_results[:top_k]
            
            if not top_results:
                return ""
            
            context = "Relevant information from knowledge base:\n\n"
            for idx, result in enumerate(top_results, 1):
                context += f"{idx}. {result.content}\n\n"
            
            return context
        except Exception as e:
            # Log error and return empty context to allow agent to continue without KB
            print(f"Error querying agent knowledge: {str(e)}")
            import traceback
            traceback.print_exc()
            return ""
    
    async def get_documents(self, kb_id: str) -> List[KnowledgeDocument]:
        return self.db.query(KnowledgeDocument).filter(KnowledgeDocument.kb_id == kb_id).all()
    
    async def delete_document(self, doc_id: str) -> bool:
        doc = self.db.query(KnowledgeDocument).filter(KnowledgeDocument.doc_id == doc_id).first()
        if not doc:
            return False
        
        kb = await self.get_knowledge_base(doc.kb_id)
        if kb:
            try:
                self.qdrant_client.delete(
                    collection_name=kb.collection_name,
                    points_selector=Filter(
                        must=[
                            FieldCondition(
                                key="doc_id",
                                match=MatchValue(value=doc_id)
                            )
                        ]
                    )
                )
            except:
                pass
        
        self.db.delete(doc)
        self.db.commit()
        return True
