"""
AI 진로 상담 챗봇 GUI
"""
import os
import gradio as gr
from pathlib import Path
from dotenv import load_dotenv
from career_chatbot import CareerChatbot
import logging

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CareerGUI:
    def __init__(self):
        """GUI 초기화"""
        try:
            # CareerChatbot 인스턴스 생성
            self.chatbot = CareerChatbot()
            self.use_real_chatbot = True
            logger.info("CareerChatbot을 성공적으로 초기화했습니다.")
        except Exception as e:
            logger.warning(f"CareerChatbot 초기화 실패: {e}")
            logger.info("모의 응답 모드로 실행합니다.")
            self.use_real_chatbot = False

    def chat_response(self, message, history):
        """
        채팅 응답 생성
        
        Args:
            message (str): 사용자 메시지
            history (list): 채팅 히스토리
        
        Returns:
            str: 응답 메시지
        """
        if not message.strip():
            return "안녕하세요! 진로에 관한 궁금한 점을 언제든 물어보세요."
        
        if self.use_real_chatbot:
            try:
                # CareerChatbot을 사용한 실제 응답 생성
                response = self.chatbot.generate_response(message)
                return response
                
            except Exception as e:
                logger.error(f"CareerChatbot 응답 생성 중 오류: {e}")
                logger.info("모의 응답으로 전환합니다.")
                # 오류 시 모의 응답으로 fallback
                pass
        
        # 모의 응답 생성
        return self.get_mock_response(message)

    def get_mock_response(self, query):
        """모의 응답 생성 (API 할당량 문제 해결용)"""
        # 키워드 기반 간단한 응답 생성
        if "경제" in query or "한국은행" in query:
            return """
안녕하세요! 경제학과 한국은행에 관심을 가지고 계시는군요. 훌륭한 목표입니다! 

**1. 질문자의 상황 분석**
고등학생으로서 경제학에 관심을 가지고 있고, 한국은행이라는 구체적인 목표 기관이 있어서 매우 좋습니다. 이는 명확한 진로 방향성을 보여줍니다.

**2. 추천하는 진로 방향**
- 경제학과 진학을 목표로 하세요
- 통계학, 수학 등 관련 학과도 고려해볼 수 있습니다
- 한국은행 외에도 금융권 전반에 대해 알아보세요

**3. 구체적인 행동 제안**
- 수학과 사회 과목을 열심히 공부하세요
- 경제 관련 책을 읽어보세요 (맨큐의 경제학 원리 등)
- 한국은행 홈페이지를 방문해서 채용 정보를 확인해보세요
- 경제학과가 있는 대학들을 알아보고 입시 준비를 하세요

화이팅하세요! 여러분의 꿈을 응원합니다! 🎓📈
            """
        elif "의사" in query:
            return """
의사가 되고 싶다는 꿈을 가지고 계시는군요! 

**1. 질문자의 상황 분석**
의료진이 되려는 목표는 사회에 기여할 수 있는 훌륭한 꿈입니다.

**2. 추천하는 진로 방향**
- 의예과 진학을 목표로 하세요
- 생물, 화학, 물리 등 자연과학 공부가 중요합니다

**3. 구체적인 행동 제안**
- 과학 과목을 열심히 공부하세요
- 병원 봉사활동을 해보세요
- 의대 입시 정보를 알아보세요
- 다양한 의료 분야에 대해 조사해보세요

꿈을 향해 열심히 노력하세요! 🏥👩‍⚕️
            """
        elif "컴퓨터" in query or "프로그래밍" in query or "게임" in query:
            return """
컴퓨터와 프로그래밍에 관심이 있으시는군요!

**1. 질문자의 상황 분석**
IT 분야는 현재와 미래에 매우 유망한 분야입니다.

**2. 추천하는 진로 방향**
- 컴퓨터공학과, 소프트웨어학과 진학
- 게임 개발, 웹 개발, 앱 개발 등 다양한 분야 탐색

**3. 구체적인 행동 제안**
- Python, Scratch 등으로 프로그래밍을 시작해보세요
- 온라인 코딩 강의를 들어보세요
- 간단한 게임이나 앱을 만들어보세요
- 수학과 영어 실력을 키우세요

코딩의 세계로 오신 것을 환영합니다! 💻🎮
            """
        else:
            return """
진로에 대해 고민하고 계시는군요!

**1. 질문자의 상황 분석**
자신의 미래에 대해 생각하고 있다는 것이 매우 좋습니다.

**2. 추천하는 진로 방향**
- 자신의 관심사와 재능을 파악해보세요
- 다양한 직업에 대해 알아보세요
- 체험 활동을 통해 경험을 쌓아보세요

**3. 구체적인 행동 제안**
- 진로 적성 검사를 받아보세요
- 관심 있는 분야의 전문가와 대화해보세요
- 독서와 체험 활동을 늘려보세요
- 학교 진로 상담 선생님과 상담해보세요

천천히 자신만의 길을 찾아가세요! 🌟
            """

    def create_interface(self):
        """Gradio 인터페이스 생성"""
        chat_interface = gr.ChatInterface(
            self.chat_response,
            title="AI 진로 상담 챗봇 🎓",
            description="""
            이 챗봇은 실제 진로상담 데이터를 기반으로 학습되었습니다.
            - 학교급별 상담 데이터 (초등/중등/고등)
            - 직업 카테고리별 상담 데이터 (기술/서비스/생산/사무)
            - 전문가 의견
            을 바탕으로 맞춤형 진로 상담을 제공합니다.
            
            **현재는 데모 버전으로 운영 중입니다.**
            """,
            examples=[
                "저는 고등학생인데 경제에 관심이 많고 한국은행에서 일하고 싶어요. 어떤 준비를 해야 할까요?",
                "중학생인데 의사가 되고 싶어요. 어떤 과목을 잘해야 하나요?",
                "컴퓨터나 게임 만드는 것에 관심이 있는 초등학생입니다. 어떤 직업이 좋을까요?",
                "고등학생인데 진로를 아직 못 정했어요. 어떻게 찾아야 할까요?"
            ],
            theme=gr.themes.Soft(),
            analytics_enabled=False
        )
        
        return chat_interface

    def launch(self, debug=False):
        """웹 인터페이스 실행"""
        interface = self.create_interface()
        
        interface.launch(
            debug=debug,
            share=False,
            server_name="127.0.0.1",
            server_port=7860,
            show_error=True,
            quiet=False
        )

def main():
    """메인 실행 함수"""
    logger.info("AI 진로 상담 챗봇을 시작합니다...")
    
    gui = CareerGUI()
    gui.launch(debug=True)

if __name__ == "__main__":
    main()