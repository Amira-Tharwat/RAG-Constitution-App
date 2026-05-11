from fastapi import APIRouter, HTTPException
from controllers.NlpController import NlpController
from .schema.nlp import SearchRequest

nlp_router = APIRouter(prefix="/api/nlp", tags=["NLP"])

@nlp_router.post("/index/push/{project_id}")
async def push_to_index(project_id: str):
    nlp_controller = NlpController()
    success = await nlp_controller.push_data_to_index(project_id)
    if not success:
        raise HTTPException(status_code=400, detail="فشل رفع البيانات لقاعدة بيانات المتجهات. تأكد من تقطيع الملف أولاً.")
    return {"message": "تم تحويل المواد لأرقام ورفعها إلى Qdrant بنجاح"}

@nlp_router.post("/index/search/{project_id}")
async def search(project_id: str, request: SearchRequest):
    nlp_controller = NlpController()
    results = nlp_controller.search_by_vector(project_id, request.query, request.limit)
    return {"results": results}

@nlp_router.post("/index/answer/{project_id}")
async def answer_question(project_id: str, request: SearchRequest):
    nlp_controller = NlpController()
    # تم إضافة request.provider هنا لإرسال اختيار المستخدم إلى العقل المدبر
    response = nlp_controller.answer_rag_question(project_id, request.query, request.provider, request.limit)
    return response