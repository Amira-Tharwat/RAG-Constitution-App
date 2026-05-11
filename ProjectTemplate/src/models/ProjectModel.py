from .DataBaseModel import DataBaseModel
from .db_schemes.project import Project

class ProjectModel(DataBaseModel):
    def __init__(self):
        super().__init__()
        # اختيار الـ Collection (الجدول) اللي اسمه projects
        self.collection = self.db["projects"]

    async def create_project(self, project: Project) -> Project:
        """إنشاء مشروع جديد في الداتا بيز"""
        # تحويل الـ Pydantic object لـ Dictionary عشان MongoDB تفهمه
        project_dict = project.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(project_dict)
        
        # إضافة الـ ID اللي اتعمل في MongoDB للأوبجكت بتاعنا
        project.id = str(result.inserted_id)
        return project

    async def get_project_or_create_one(self, project_id: str) -> Project:
        """البحث عن مشروع، لو مش موجود بيعمله"""
        project_doc = await self.collection.find_one({"project_id": project_id})
        
        if project_doc:
            # تحويل الـ ObjectId لنص عشان Pydantic ميزعلش
            project_doc["_id"] = str(project_doc["_id"])
            return Project(**project_doc)
        
        # لو مش موجود، نعمل واحد جديد
        new_project = Project(project_id=project_id)
        return await self.create_project(new_project)