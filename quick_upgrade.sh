#!/bin/bash
# POA v5 빠른 업그레이드 스크립트

echo "==================================="
echo "POA v5 업그레이드 스크립트"
echo "==================================="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# POA 경로 확인
POA_PATH="/root/POA"
if [ ! -d "$POA_PATH" ]; then
    echo -e "${RED}❌ 에러: POA가 설치되지 않았습니다.${NC}"
    echo "먼저 POA를 설치해주세요."
    exit 1
fi

cd $POA_PATH

# 현재 실행 중인 POA 중지
echo -e "${YELLOW}1. 현재 실행 중인 POA 중지...${NC}"
pm2 delete POA > /dev/null 2>&1

# 백업 디렉토리 생성
BACKUP_DIR="$POA_PATH/backup_$(date +%Y%m%d_%H%M%S)"
echo -e "${YELLOW}2. 백업 생성: $BACKUP_DIR${NC}"
mkdir -p $BACKUP_DIR

# 중요 파일 백업
cp -f .env $BACKUP_DIR/ 2>/dev/null
cp -f exchange/model/schemas.py $BACKUP_DIR/
cp -f exchange/pexchange.py $BACKUP_DIR/
cp -f exchange/stock/kis.py $BACKUP_DIR/
cp -f exchange/__init__.py $BACKUP_DIR/
cp -f requirements.txt $BACKUP_DIR/

# Git에서 최신 버전 가져오기
echo -e "${YELLOW}3. 최신 버전 다운로드...${NC}"
git fetch origin
git reset --hard origin/main

# 백업한 .env 파일 복원
if [ -f "$BACKUP_DIR/.env" ]; then
    echo -e "${YELLOW}4. .env 파일 복원...${NC}"
    cp -f $BACKUP_DIR/.env .
else
    echo -e "${YELLOW}4. .env 파일 생성...${NC}"
    cat > .env << 'EOF'
# POA 자동매매 설정 파일
PASSWORD="your_password_here"
PORT="80"
DISCORD_WEBHOOK_URL=""
DB_ID="poa@admin.com"
DB_PASSWORD="poabot!@#$"
WHITELIST=["127.0.0.1"]

# 거래소 API 키는 edit_env 명령으로 설정하세요
BINANCE_KEY=""
BINANCE_SECRET=""
UPBIT_KEY=""
UPBIT_SECRET=""
BITHUMB_KEY=""
BITHUMB_SECRET=""
# ... 나머지 설정
EOF
fi

# 패키지 업데이트
echo -e "${YELLOW}5. Python 패키지 업데이트...${NC}"
/root/POA/.venv/bin/pip install -r requirements.txt --quiet

# 설정 파일 권한 설정
chmod 600 .env

echo ""
echo -e "${GREEN}✅ 업그레이드 완료!${NC}"
echo ""
echo "다음 단계:"
echo "1. edit_env 명령으로 API 키 설정"
echo "2. start 명령으로 POA 시작"
echo ""
echo "백업 위치: $BACKUP_DIR"
echo ""
