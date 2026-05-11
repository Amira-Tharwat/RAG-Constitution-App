from .BaseController import BaseController
from models.ChunkModel import ChunkModel
from stores.llm.LLMFactory import LLMFactory
from stores.vectordb.VectorDBFactory import VectorDBFactory

class NlpController(BaseController):
    def __init__(self):
        super().__init__()
        # 1. الاتصال بقاعدة بيانات MongoDB
        self.chunk_model = ChunkModel()
        
        # 2. استدعاء مصانع الذكاء الاصطناعي الثابتة (التقطيع وقاعدة البيانات)
        self.embedder = LLMFactory.get_embedding_provider("local")
        self.vectordb = VectorDBFactory.get_vectordb("qdrant")
        
        # لاحظي: مفيش هنا self.llm لأننا هنصنعه ديناميكياً مع كل سؤال

    async def push_data_to_index(self, project_id: str) -> bool:
        """جلب المواد الدستورية من MongoDB وتحويلها لأرقام وحفظها في Qdrant"""
        # 1. جلب البيانات من MongoDB
        chunks = await self.chunk_model.get_chunks_by_project_id(project_id)
        if not chunks:
            return False

        # اسم الجدول في Qdrant هيكون مرتبط باسم المشروع
        collection_name = f"collection_{project_id}"

        # 2. إنشاء الـ Collection
        self.vectordb.create_collection(collection_name)

        # 3. تجهيز النصوص وتحويلها لأرقام
        chunks_dicts = [chunk.model_dump(by_alias=True) for chunk in chunks]
        
        embeddings = []
        for chunk in chunks_dicts:
            emb = self.embedder.embed_text(chunk["chunk_text"])
            embeddings.append(emb)

        # 4. الحفظ في Qdrant
        self.vectordb.add_documents(collection_name, chunks_dicts, embeddings)
        return True

    def search_by_vector(self, project_id: str, query: str, limit: int = 5) -> list:
        """تحويل السؤال لأرقام والبحث عن أقرب مواد دستورية"""
        collection_name = f"collection_{project_id}"
        
        query_vector = self.embedder.embed_text(query)
        results = self.vectordb.search_by_vector(collection_name, query_vector, limit)
        return results

    # التعديل الأهم: ضفنا provider هنا عشان نستقبله من الواجهة
    def answer_rag_question(self, project_id: str, query: str, provider: str = "gemini", limit: int = 5) -> dict:
        """العقل المدبر: يبحث، يجهز الـ Prompt، ويخلي الموديل يجاوب"""
        # 1. جلب المواد المشابهة للسؤال
        search_results = self.search_by_vector(project_id, query, limit)
        
        if not search_results:
            return {"answer": "لم أجد معلومات متعلقة بسؤالك في الدستور.", "sources": []}

        # 2. تجميع النصوص في نص واحد كبير (Context)
        context_text = ""
        sources = []
        for i, doc in enumerate(search_results):
            context_text += f"\n--- مادة رقم {i+1} ---\n{doc.text}\n"
            sources.append(doc.text)

        # 3. بناء الـ Prompt
        prompt = f"""إليك جزء من دستور جمهورية مصر العربية:
        {context_text}
        
        بناءً على هذا النص ، أجب على السؤال التالي باللغة العربية:
        السؤال:  {query}
        الإجابة:"""

        # 4. السحر هنا: بنصنع الموديل بناءً على اختيار المستخدم (Factory Pattern)
        llm_instance = LLMFactory.get_llm(provider)
        
        # 5. إرسال الـ Prompt للـ LLM لتوليد الإجابة
        answer = llm_instance.generate_response(prompt)
        
        # بنرجع الإجابة والمصادر
        return {
            "answer": answer,
            "sources": sources
        }