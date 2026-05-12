from .BaseController import BaseController
from models.ChunkModel import ChunkModel
from stores.llm.LLMFactory import LLMFactory
from stores.vectordb.VectorDBFactory import VectorDBFactory

class NlpController(BaseController):
    def __init__(self):
        super().__init__()
        self.chunk_model = ChunkModel()
        
        self.embedder = LLMFactory.get_embedding_provider("local")
        self.vectordb = VectorDBFactory.get_vectordb("qdrant")
        

    async def push_data_to_index(self, project_id: str) -> bool:
        """نجيب المواد  من MongoDB ونحويلها لأرقام ونحفظها في Qdrant"""
        chunks = await self.chunk_model.get_chunks_by_project_id(project_id)
        if not chunks:
            return False

        collection_name = f"collection_{project_id}"

        self.vectordb.create_collection(collection_name)

        # 3. نجهز ال chunks وتحويلها لأرقام
        chunks_dicts = [chunk.model_dump(by_alias=True) for chunk in chunks]
        
        embeddings = []
        for chunk in chunks_dicts:
            emb = self.embedder.embed_text(chunk["chunk_text"])
            embeddings.append(emb)

        # 4. نحفظها في Qdrant
        self.vectordb.add_documents(collection_name, chunks_dicts, embeddings)
        return True

    def search_by_vector(self, project_id: str, query: str, limit: int = 5) -> list:
        collection_name = f"collection_{project_id}"
        
        query_vector = self.embedder.embed_text(query)
        results = self.vectordb.search_by_vector(collection_name, query_vector, limit)
        return results

    def answer_rag_question(self, project_id: str, query: str, provider: str = "gemini", limit: int = 5) -> dict:
        search_results = self.search_by_vector(project_id, query, limit)
        
        if not search_results:
            return {"answer": "لم أجد معلومات متعلقة بسؤالك في الدستور.", "sources": []}

        context_text = ""
        sources = []
        for i, doc in enumerate(search_results):
            context_text += f"\n--- مادة رقم {i+1} ---\n{doc.text}\n"
            sources.append(doc.text)

        # 3.  الـ Prompt
        prompt = f"""إليك جزء من دستور جمهورية مصر العربية:
        {context_text}
        
        بناءً على هذا النص ، أجب على السؤال التالي باللغة العربية:
        السؤال:  {query}
        الإجابة:"""

        llm_instance = LLMFactory.get_llm(provider)
        
        answer = llm_instance.generate_response(prompt)
        
        # بنرجع الإجابة والمصادر
        return {
            "answer": answer,
            "sources": sources
        }