import streamlit as st
import requests
import os

# 1. إعدادات الصفحة الأساسية للتصميم
st.set_page_config(page_title="المساعد الدستوري الذكي", page_icon="⚖️", layout="wide")

# رابط السيرفر بتاعنا
BASE_URL = os.environ.get("BASE_URL", "http://backend:5000/api")

st.title("⚖️ المساعد الذكي للدستور المصري")
st.markdown("اسأل أي سؤال في الدستور، والذكاء الاصطناعي هيجاوبك من المواد الدستورية الموثقة.")

# -------------------------------------------------------------------
# القائمة الجانبية (Sidebar) للتحكم في الملفات وتجهيز البيانات
# -------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ لوحة التحكم")
    project_id = st.text_input("معرف المشروع:", value="law_project_1")
    
    # في القائمة الجانبية:
    st.subheader("🤖 محرك الذكاء الاصطناعي")
    selected_ai = st.selectbox(
        "اختر الموديل اللي هيجاوبك:",
        ["Gemini", "Groq"], # شيلنا OpenAI وحطينا Groq المجاني
        index=0
    )
    
    st.divider()
    
    # قسم رفع الملف
    st.subheader("1. رفع الدستور")
    uploaded_file = st.file_uploader("اختر ملف (PDF):", type=["pdf"])
    if st.button("رفع الملف 📤", use_container_width=True):
        if uploaded_file is not None:
            with st.spinner("جاري الرفع..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{BASE_URL}/data/upload/{project_id}", files=files)
                if response.status_code == 200:
                    st.success("تم رفع الملف بنجاح!")
                else:
                    st.error("حدث خطأ أثناء الرفع.")
        else:
            st.warning("الرجاء اختيار ملف أولاً.")

    # قسم التقطيع
    st.subheader("2. تقطيع المواد")
    if st.button("تقطيع وحفظ ✂️", use_container_width=True):
        if uploaded_file is not None:
            with st.spinner("جاري التقطيع..."):
                response = requests.post(f"{BASE_URL}/data/process/{project_id}?file_name={uploaded_file.name}")
                if response.status_code == 200:
                    st.success("تم التقطيع والحفظ في قاعدة البيانات!")
                else:
                    st.error("حدث خطأ أثناء التقطيع.")
        else:
            st.warning("الرجاء رفع الملف أولاً لمعرفة اسمه.")

    # قسم محرك البحث (Qdrant)
    st.subheader("3. تجهيز الذكاء الاصطناعي")
    if st.button("تحويل لأرقام (Index) 🧠", use_container_width=True):
        with st.spinner("جاري بناء محرك البحث..."):
            response = requests.post(f"{BASE_URL}/nlp/index/push/{project_id}")
            if response.status_code == 200:
                st.success("تم التجهيز بنجاح! جاهز للأسئلة.")
            else:
                st.error("حدث خطأ. تأكد من التقطيع أولاً.")

# -------------------------------------------------------------------
# واجهة الدردشة (Chat Interface)
# -------------------------------------------------------------------

# تهيئة ذاكرة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل القديمة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# صندوق إدخال السؤال
if prompt := st.chat_input("اكتب سؤالك هنا... (مثال: هل يجوز لرئيس الجمهورية الترشح لأكثر من فترة؟)"):
    
    # 1. طباعة سؤال المستخدم في الشاشة
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. التواصل مع السيرفر لطلب الإجابة
    with st.chat_message("assistant"):
        with st.spinner(f"ببحث في الدستور وبجهز الإجابة باستخدام {selected_ai}..."):
            
            # --- التعديل التاني هنا: ضفنا اختيار المستخدم في البيانات اللي رايحة للسيرفر ---
            payload = {
                "query": prompt, 
                "limit": 5,
                "provider": selected_ai.lower()
            }
            
            try:
                response = requests.post(f"{BASE_URL}/nlp/index/answer/{project_id}", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "لم أتمكن من إيجاد إجابة.")
                    sources = data.get("sources", [])
                    
                    # طباعة الإجابة
                    st.markdown(answer)
                    
                    # عرض المصادر
                    if sources:
                        with st.expander("📚 عرض المصادر الدستورية"):
                            for i, source in enumerate(sources):
                                st.info(f"**المصدر {i+1}:**\n{source}")
                    
                    # حفظ الإجابة في الذاكرة
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error("السيرفر واجه مشكلة في توليد الإجابة.")
            except Exception as e:
                st.error("تأكد إن سيرفر الـ FastAPI شغال في الخلفية.")