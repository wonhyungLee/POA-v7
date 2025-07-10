#!/bin/bash
# POA Bot 빠른 시작 스크립트

echo ""
echo "🚀 POA Bot 서버 시작 스크립트"
echo "========================="
echo ""

# Python 버전 확인
echo "🐍 Python 버전 확인..."
python3 --version
echo ""

# .env 파일 확인
if [ ! -f .env ]; then
    echo "❌ .env 파일이 없습니다!"
    echo ""
    echo "📄 .env.template에서 복사합니다..."
    cp .env.template .env
    echo "✅ .env 파일이 생성되었습니다."
    echo ""
    echo "📝 이제 설정을 입력해주세요:"
    echo "   nano .env"
    echo ""
    echo "최소한 PASSWORD는 반드시 설정해야 합니다!"
    echo ""
    exit 1
fi

# 환경 테스트 실행
echo "🔍 환경 설정 테스트..."
python3 test_env.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 환경 설정에 문제가 있습니다."
    echo "위의 오류 메시지를 확인하고 해결해주세요."
    exit 1
fi

# 필수 패키지 설치 확인
echo ""
echo "📦 필수 패키지 확인..."
pip install -r requirements.txt -q

# 서버 시작
echo ""
echo "✨ 서버를 시작합니다..."
echo ""
python3 run.py
