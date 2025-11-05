import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
import chromadb

# 환경 변수 로드
load_dotenv()

# Gemini API 키 설정
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

GEMINI_MODEL_NAME = os.getenv('GEMINI_MODEL_NAME', 'gemini-2.5-flash')
GEMINI_TEMPERATURE = float(os.getenv('GEMINI_TEMPERATURE', 0.2))
GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv('GEMINI_MAX_OUTPUT_TOKENS', 1024))

class CareerChatbot:
    def __init__(self, db_path=None):
        self.db_path = db_path or Path(__file__).parent / "career_guidance.db"
        self.chroma_path = Path(__file__).parent / "chroma_db"
        
        # ChromaDB 존재 여부 확인
        if not self.chroma_path.exists():
            raise FileNotFoundError(
                "ChromaDB embeddings not found. Please run create_embeddings.py first to create the embeddings."
            )
        
        # ChromaDB 클라이언트 연결
        self.chroma_client = chromadb.PersistentClient(path=str(self.chroma_path))
        
        try:
            self.collection = self.chroma_client.get_collection("counselling_data")
        except:
            raise ValueError(
                "Counselling data collection not found in ChromaDB. Please run create_embeddings.py first."
            )

    def get_similar_cases(self, query, n_results=3):
        # 질문과 유사한 사례 검색
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results

    def generate_response(self, query):
        """AI 기반 응답 생성"""
        try:
            # 먼저 유사 사례 검색
            similar_cases = self.get_similar_cases(query)
            
            model = genai.GenerativeModel(
                GEMINI_MODEL_NAME,
                generation_config=genai.types.GenerationConfig(
                    temperature=GEMINI_TEMPERATURE,
                    max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
                )
            )
            
            # 유사 사례를 문맥으로 활용
            context = ""
            if similar_cases and similar_cases['documents'] and similar_cases['documents'][0]:
                context = "\n참고할 유사 사례들:\n"
                for i, doc in enumerate(similar_cases['documents'][0][:3], 1):
                    context += f"{i}. {doc}\n"
            
            prompt = f"""
            당신은 전문 진로 상담사입니다. 학생의 질문에 대해 따뜻하고 구체적인 조언을 제공해주세요.
            
            학생의 질문: {query}
            
            {context}
            
            위 사례를 참고하여 다음 형식으로 답변해주세요:
            1. 상황 분석
            2. 진로 방향 제안
            3. 구체적 행동 계획
            
            친근하고 도움이 되는 톤으로 작성해주세요.
            """
            
            response = model.generate_content(prompt)
            
            if response.candidates and response.candidates[0].content.parts:
                return response.text
            else:
                return "죄송합니다. 응답을 생성할 수 없습니다. 다시 시도해주세요."
                
        except Exception as e:
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"

def main():
    chatbot = CareerChatbot()
    
    # 테스트 질문
    test_query = "저는 고등학생인데 경제에 관심이 많고 한국은행에서 일하고 싶어요. 어떤 준비를 해야 할까요?"
    
    # 답변 생성 (내부에서 유사 사례 검색 자동 실행)
    response = chatbot.generate_response(test_query)
    print("=== 챗봇 답변 ===")
    print(response)

if __name__ == "__main__":
    main()
