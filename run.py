import uvicorn
import fire
import sys
import os

def start_server(host="0.0.0.0", port=8000):
    try:
        # 환경 확인
        if not os.path.exists(".env"):
            print("\n[오류] .env 파일이 없습니다!")
            print("\n해결 방법:")
            print("1. cp .env.template .env")
            print("2. nano .env (또는 vi .env)")
            print("3. 필요한 설정 입력 후 저장")
            print("\n최소한 PASSWORD는 반드시 설정해야 합니다.\n")
            sys.exit(1)
            
        # 설정 로드 시도
        from exchange.utility import settings
        
        # 포트 설정
        if settings.PORT is not None:
            port = settings.PORT
            
        print(f"\n✨ POA Bot 서버 시작")
        print(f"   호스트: {host}")
        print(f"   포트: {port}")
        print(f"   URL: http://{host}:{port}")
        print(f"\n테스트: http://{host}:{port}/hi\n")
        
        from main import app
        app.state.port = port
        uvicorn.run("main:app", host=host, port=port, reload=False)
        
    except Exception as e:
        print(f"\n[서버 시작 실패] {str(e)}")
        print("\n오류 해결 방법:")
        print("1. .env 파일이 올바른지 확인")
        print("2. PASSWORD 필드가 설정되어 있는지 확인")
        print("3. 필요한 패키지 설치: pip install -r requirements.txt\n")
        raise


if __name__ == "__main__":
    fire.Fire(start_server)
