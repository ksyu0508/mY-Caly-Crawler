import json
import asyncio
from groq import Groq
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from datetime import datetime

from app.config import Config
from app.database.models import Post, Information, Image
from app.database.db import AsyncSessionLocal

GROQ_API_KEY = Config.GROQ_API_KEY

class LLM:
    def __init__(self, model_name, api_key):
        self.model_name = model_name.lower()
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.client = Groq(api_key=self.api_key)

    async def ask_llama(self, prompt, past_messages):
        llama_messages = past_messages.copy()
        llama_messages.append({"role": "user", "content": prompt})

        # Run the Groq API call in a separate thread to avoid blocking
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                messages=llama_messages,
                model="llama3-70b-8192",
                # model="llama-3.2-90b-text-preview",
                temperature=0.1,
            )
            return response.choices[0].message.content
        except Exception as e:
            print("Error with LLM response:", e)
            return "Sorry, I encountered an issue while processing your request."


# Instantiate the LLM agent
agent = LLM("GROQ_LLM", GROQ_API_KEY)

system_prompt = '''
You are tasked with categorizing and extracting necessary information from the provided document. Follow these rules strictly:
1.Type Classification:
Select the type only from the following categories:
[학사일정, 장학금, 인턴, 채용, 행사, 대학원, 대외활동, 동아리, 기타]
Do not create or modify the values in the list. Only choose from the list as-is.
2.Tags Classification:
Identify and select all relevant tags from the following list. If no tags apply, return an empty list ([])
[공공서비스, 전문직, 경영·기획·컨설팅, 금융·회계, 통상·무역, 교육, 인사·경영지원, 광고·마케팅, 영업, 법률·법무, IT, 디자인, 의약·보건, 생산관리/품질관리, 전기·전자·반도체, 재료·신소재, 에너지·환경, 기계·로봇·자동화, 화학·화공·섬유, 바이오·식품, 토목·건설·환경]
Do not create, modify, or use any values outside the provided list. Only select from the list as-is.
3.Period Extraction:
If the document specifies an application period, extract the start and end times of the application period.
If no application period is specified but other periods are mentioned, select the most important period.
If multiple periods are mentioned, prioritize the application period.
If no periods are specified, leave the "period" field empty.
If only dates (without times) are provided, assume:
Datetime format must follows 2024-11-11T00:00:00 shape
Start time: 00:00:00
End time: 23:59:59
4.Output Structure:
You must respond only in JSON format. Do not include any additional text, explanations, or comments. The output must strictly follow this structure:
{
  "type": "<selected_type>",
  "tags": [<list_of_selected_tags>],
  "startAt": "<start_datetime>",
  "endAt": "<end_datetime>"
}
Replace `<selected_type>` with the appropriate type, `<list_of_selected_tags>` with a list of relevant tags, `<start_datetime>` with the start datetime, and `<end_datetime>` with the end datetime.
You must respond strictly in JSON format. Here is an example:
{
  "type": "교육",
  "tags": ["IT", "디자인"],
  "startAt": "2024-11-11T00:00:00",
  "endAt": "2024-11-12T23:59:59"
}
'''

messages = [
    {
        "role": "system",
        "content": system_prompt,
    }
]

async def perform_llm(question: str, createdAt: str=''):
    if createdAt:
        question = f'document created at {createdAt}' + question
    answer = await agent.ask_llama(question, messages)
    try:
        answer = json.loads(answer)
        if answer['startAt']:
            answer['startAt'] = datetime.fromisoformat(answer['startAt'])
        else:
            answer['startAt'] = None
        if answer['endAt']:
            answer['endAt'] = datetime.fromisoformat(answer['endAt'])
        else:
            answer['endAt'] = None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    return answer

# Title: 2024학년도 동절기 난방시행계획 안내(신촌, 국제캠퍼스)신촌/국제시설처, Contents: 1. 에너지 소비절약에 협조하여 주셔서 감사를 드립니다.2. 2024학년도 동절기 난방시행계획을 다음과 같이 안내하오니 에너지의 이용합리화에 적극 협조하여 주시기 바랍니다.가. 난방계획기간 : 2024. 11. 11.(월) ~ 2025. 4. 4.(금)까지* 2024. 11. 4.(월) ~ 11. 8.(금)까지 건물별로 시운전을 겸하여 난방시행나. 난방기준온도 : 실내온도 20o℃* 에너지 이용합리화법 시행규칙 제31조의2(냉난방온도의 제한온도 기준)3. 행사 장소의 난방 지원가. 교내 행사 장소의 난방 지원은 주 52시간 근무제 시행에 따른 근무자의 배치를 위해 사용부서의7일전 요청 공문에 의하여 난방을 시행하며, 난방계획기간 전, 후에도 온도 상황에 따라 지원 할 예정입니다.나. 주 52시간 근무제의 원활한 정착을 위하여야간, 주말 및 휴일행사를 최소화하여 주시기 바랍니다.4. 협조 의뢰 사항가. 난방 실시 중에는 건물구조나 실의 위치에 따라 자동으로 난방이 균일하게 조절되지 못하여 실내온도의 차이가 발생하므로 규정온도 이상일 경우에는 창문을 열지 말고,방열기의 밸브를 잠그거나, FCU(냉난방기)의 경우 난방스위치를 꺼서난방을 조절하시기 바랍니다.나. 지나친 난방은 고혈압, 심장병, 뇌졸증을 유발하여 건강에 해로우므로난방 적정온도인 20℃를 유지하여 주시기 바랍니다.다. 난방온도를1℃ 낮추면 7%가 절약됩니다.라. 난방 시 커튼이나 블라인드로 차단하면 10% 절감효과가 있습니다.마. 난방 시 창문이나 출입문을 꼭 닫고, 환기휀을 꺼 주시기 바랍니다.바. 중식시간, 퇴근시간30분~1시간 전에 난방기를 꺼도연속적인 난방 효과가 있습니다.사. 난방기를 사용하지 않는 시간 또는 퇴근 시에는 메인전원을 꺼서 대기전력을 절감하고, 화재를 예방하시기 바랍니다.아. 대학사무실에서는 각 대학 건물 내에 있는 실험실, 연구실, 동아리방 등의 개별 난방기기의 안전한 사용을 지속적으로 확인하여 주시기 바랍니다.
# Title: 연세대학교 신촌/국제캠퍼스 강사 공개채용, Contents: 2025학년도 1학기~2025학년도 2학기연세대학교 신촌/국제캠퍼스 강사 공개채용 공고연세대학교 신촌/국제캠퍼스에서 2025학년도 1학기~2025학년도 2학기 개설 교과목을 담당할 강사를 다음과 같이 공개채용하고자 공고합니다.1. 지원기간: 2024. 11. 6.(수) 10:00 ~2024. 11. 11.(월)15:002. 지원방법가.지원서 접수는 인터넷으로 진행하며진학프로 교원채용(https://www.jinhakpro.com)에 접속하여 지원함.나.제출서류는 PDF 파일로 업로드함(온라인으로만 지원할 수 있으며, 별도의 오프라인 서류제출은 없음).다. 접수기간 내 지원서 작성 및 제출서류 첨부하여접수 완료된 지원자에 한해 평가가 진행되며, 접수기간 종료 후 지원 불가함.라.온라인 지원시스템 관련 문의처(회원가입 및 접수 절차 등) : ㈜진학어플라이 1544-77153. 지원자격 및 임용기간:  붙임 강사 공개채용 안내[요강] 참고※ 특히, 선발직위가 학문후속세대강사인 경우, 자격 요건에 해당되는지 확인 후 지원하시기 바랍니다.4. 지원서류(온라인으로 작성 및 업로드)가.지원서: 지원교과목, 인적사항, 주요학력사항, 경력사항, 주요연구실적, 자격사항 등 입력※ 지원서 상에 입력한 모든 학력/경력/연구실적/자격사항에 대한 증빙을 PDF 형식으로 업로드하여야 함.나.자기소개서: 지원 교과목 관련 지원자 이력 등 입력다.PDF 형식 업로드 자료※ 강의계획서 및 학위/성적증명서는 공통 필수 제출 서류이며, 지원 교과목 관련 강의/연구/실무 경력 또는 자격증 등을 기재한해당자에 한해 다음의 연구실적/경력/재직/자격증 등의 증빙서류를 함께 업로드 하시기 바랍니다.1)강의계획서(본교 소정양식)각 1부.: 지원 교과목별로 각각 강의계획서 작성 후 1개의 PDF 파일로 병합하여 업로드2)학위증명서 및 성적증명서각 1부.: 지원서 학력사항에 기재된 모든 학위별 학위증 및 성적증명서를 1개의 PDF 파일로 병합하여 업로드(학사>석사>박사 순)※ 지원 시점에 재학 중인 학력 포함하며, 각 학위별 졸업, 수료, 재학 중 최종 상태의 증명서 제출3)주요 연구실적 및 자격사항(연구실적 및 자격증 사본)각 1부.: 지원서 상의 대표업적(최대 3건)에 대한 표지(예: 논문 첫페이지, 공연포스터 등) 및 자격증 등을 1개의 PDF 파일로 병합하여 업로드4)경력(재직)증명서각 1부.: 지원서 상의 강의 경력 포함 재직/경력증명서를 1개의 PDF 파일로 병합하여 업로드5. 안내(요강) 및 모집교과목/채용분야 전 목록, 서식 등: 공고 상단의 첨부파일 참조※ 지원 교과목/채용분야 관련 문의사항 등 자세한 사항은 모집 교과목/채용분야 목록에 표기된 선발기관(각 대학(원) 행정팀)으로 문의바랍니다.※ 지원 교과목/채용분야별로 자격요건 및 우대사항이 다를 수 있으니, 반드시 해당 비고란을 확인하시기 바랍니다.2024. 11.연세대학교 교무처장

async def process_posts():
    """
    Fetches unprocessed posts, performs LLM operation, and updates the database.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Post).where(Post.organized == False).order_by(Post.id)
        )
        posts = result.scalars().all()

    for post in posts:
        async with AsyncSessionLocal() as session:
            async with session.begin():  # Begin a transaction
                # Fetch posts with organized=False, ordered by id
                try:
                    # Perform LLM processing
                    result = await session.execute(
                        select(Image).where(Image.post_id == post.id)
                    )
                    images = result.scalars().all()
                    question = post.contents
                    for image in images:
                        question += image.img_contents
                    llm_response = await perform_llm(question, post.createdAt)

                    print(llm_response)
                    # Parse the LLM response
                    tags = llm_response.get("tags", [])
                    selected_type = llm_response.get("type", "")
                    start_at = llm_response.get("startAt", None)
                    end_at = llm_response.get("endAt", None)

                    # Add data to Information table
                    info = Information(
                        post_id=post.id,
                        tags=tags,
                        type=selected_type,
                        startAt=start_at,
                        endAt=end_at,
                    )
                    session.add(info)

                    # Mark the post as organized
                    await session.execute(
                        update(Post)
                        .where(Post.id == post.id)
                        .values(organized=True)
                    )
                    # Commit the transaction
                    await session.commit()
                except Exception as e:
                    await session.rollback()
                    print(f"Error occurred: {e}")

            await asyncio.sleep(20)