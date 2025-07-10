# POA Bot v7 - 빠른 시작 가이드

## 🚀 오라클 클라우드 서버에서 설치 및 실행

### 1. 코드 다운로드
```bash
git clone [repository-url]
cd poa-v7
```

### 2. 환경 설정
```bash
# .env 템플릿 복사
cp .env.template .env

# .env 파일 편집 (nano 또는 vi 사용)
nano .env

# 또는
vi .env
```

### 3. .env 파일 작성 방법
**중요: 따옴표 없이 = 다음에 바로 값을 입력합니다**

```bash
# 올바른 예시
PASSWORD=mypassword123
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/abcdefghijk
UPBIT_KEY=your_upbit_api_key_here
UPBIT_SECRET=your_upbit_secret_here

# 잘못된 예시 (따옴표 사용 X)
PASSWORD="mypassword123"  # ❌ 따옴표 사용하지 마세요

# 빈 값을 남길 때
BINANCE_KEY=
BINANCE_SECRET=
```

### 4. 필수 설정
최소한 다음 항목은 반드시 설정해야 합니다:
- `PASSWORD`: POA Bot 접근 비밀번호

### 5. 패키지 설치
```bash
pip install -r requirements.txt
```

### 6. 서버 실행
```bash
python run.py
```

### 7. 서버 접속 테스트
브라우저에서 다음 주소로 접속:
```
http://서버IP:8000/hi
```

## 🔧 문제 해결

### 서버가 시작되지 않을 때

1. **.env 파일 확인**
   ```bash
   # .env 파일이 있는지 확인
   ls -la .env
   
   # 없다면 템플릿에서 복사
   cp .env.template .env
   ```

2. **PASSWORD 설정 확인**
   ```bash
   # .env 파일에서 PASSWORD 확인
   grep PASSWORD .env
   ```

3. **Python 패키지 확인**
   ```bash
   # 필요한 패키지 재설치
   pip install -r requirements.txt --upgrade
   ```

4. **방화벽 설정**
   ```bash
   # 오라클 클라우드에서 8000번 포트 열기
   sudo firewall-cmd --permanent --zone=public --add-port=8000/tcp
   sudo firewall-cmd --reload
   ```

### 자산 모니터링 활성화

1. **.env에서 설정**
   ```bash
   # 디스코드 웹훅 URL 설정 (필수)
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   
   # 자산 모니터링 활성화
   ENABLE_ASSET_MONITOR=true
   
   # 리포트 간격 (시간 단위)
   ASSET_REPORT_INTERVAL_HOURS=6
   ```

2. **즉시 자산 확인**
   ```
   # 자산 조회
   GET http://서버IP:8000/assets
   
   # 디스코드로 리포트 전송
   POST http://서버IP:8000/assets/report
   ```

## 📝 주요 변경사항

1. **KIS4 실전투자**: 모든 KIS 계좌(1-4)가 실전투자로 설정됨
2. **Upbit 정상 작동**: UPBIT_KEY, UPBIT_SECRET 설정으로 사용 가능
3. **자산 모니터링**: 정기적으로 전체 자산을 디스코드로 알림

## 🆘 도움말

문제가 계속되면 다음을 확인하세요:
- Python 버전: 3.8 이상
- 서버 로그: `python run.py` 실행 시 출력되는 메시지
- .env 파일 권한: `chmod 600 .env` (보안을 위해)
