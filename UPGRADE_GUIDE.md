# POA v5 업그레이드 가이드

## 개요
이 문서는 POA v5 자동매매 프로그램의 업그레이드 버전에 대한 설치 및 설정 가이드입니다.

## 주요 변경사항

### 1. 보안 강화
- 모든 API 키와 민감한 정보를 `.env` 파일로 분리
- cloud-init에서 하드코딩된 정보 제거
- `.env` 파일은 서버에서 직접 편집 가능

### 2. Bithumb 거래소 지원 추가
- Bithumb API 통합
- KRW 마켓 자동매매 지원
- 시장가/지정가 주문 지원

### 3. KIS(한국투자증권) 확장
- 모의투자 제거, 실전투자만 지원
- KIS 1번부터 50번까지 계정 지원
- 다중 계정 동시 운영 가능

## 설치 방법

### 1. Oracle Cloud 인스턴스 생성
1. Oracle Cloud에서 Ubuntu 20.04 또는 22.04 인스턴스 생성
2. 인스턴스 생성 시 "Advanced options" 클릭
3. "Cloud-init script" 섹션에 `cloud-init-upgraded.yaml` 내용 붙여넣기
4. 인스턴스 생성 완료

### 2. 초기 설정
1. 인스턴스가 재시작된 후 SSH로 접속:
   ```bash
   ssh ubuntu@<your-instance-ip>
   sudo su -
   ```

2. API 키 설정:
   ```bash
   edit_env
   ```
   
3. `.env` 파일 편집:
   - PASSWORD: TradingView 웹훅 비밀번호
   - DISCORD_WEBHOOK_URL: Discord 알림 URL
   - 각 거래소별 API 키와 시크릿
   - KIS 계정 정보 (사용할 계정만 입력)

### 3. 프로그램 시작
```bash
start
```

## 사용 가능한 명령어

- `start` - POA 프로그램 시작
- `quit` - POA 프로그램 중지
- `monitor` - 실시간 로그 확인
- `list` - 실행 중인 프로세스 확인
- `edit_env` - 환경 변수 편집
- `update` - 프로그램 업데이트
- `reinstall` - 프로그램 재설치

## TradingView 웹훅 설정

### 1. 기본 주문 형식
```json
{
  "password": "your_password_here",
  "exchange": "BINANCE",
  "base": "BTC",
  "quote": "USDT",
  "side": "buy",
  "amount": 0.001
}
```

### 2. KIS(한국투자증권) 주문 형식
```json
{
  "password": "your_password_here",
  "exchange": "KRX",
  "base": "005930",
  "quote": "KRW",
  "side": "buy",
  "amount": 10,
  "kis_number": 1
}
```

### 3. Bithumb 주문 형식
```json
{
  "password": "your_password_here",
  "exchange": "BITHUMB",
  "base": "BTC",
  "quote": "KRW",
  "side": "buy",
  "cost": 100000
}
```

## 지원 거래소

### 암호화폐 거래소
- BINANCE (현물/선물)
- UPBIT (현물)
- BYBIT (현물/선물)
- BITGET (현물/선물)
- OKX (현물/선물)
- BITHUMB (현물) - **신규**

### 주식 거래소
- KRX (한국거래소)
- NASDAQ
- NYSE
- AMEX

## 파일 구조

```
/root/POA/
├── .env                    # API 키 및 설정 파일
├── run.py                  # 메인 실행 파일
├── main.py                 # FastAPI 애플리케이션
├── exchange/
│   ├── binance.py         # Binance API
│   ├── upbit.py           # Upbit API
│   ├── bithumb.py         # Bithumb API (신규)
│   ├── bybit.py           # Bybit API
│   ├── bitget.py          # Bitget API
│   ├── okx.py             # OKX API
│   ├── stock/
│   │   └── kis.py         # 한국투자증권 API (업그레이드)
│   └── model/
│       └── schemas.py     # 데이터 모델 (업그레이드)
└── requirements.txt       # Python 패키지 목록
```

## 보안 주의사항

1. `.env` 파일은 절대 공개 저장소에 업로드하지 마세요
2. API 키는 필요한 권한만 부여하세요 (거래, 잔고 조회)
3. 출금 권한은 부여하지 마세요
4. 정기적으로 API 키를 재발급하세요
5. 화이트리스트 IP를 설정하여 접근을 제한하세요

## 문제 해결

### 프로그램이 시작되지 않는 경우
```bash
# 로그 확인
monitor

# 프로세스 상태 확인
list

# 재시작
quit
start
```

### API 키 오류
1. `.env` 파일의 API 키가 올바른지 확인
2. 거래소에서 API 권한 확인
3. IP 화이트리스트 설정 확인

### 웹훅이 작동하지 않는 경우
1. 비밀번호가 일치하는지 확인
2. JSON 형식이 올바른지 확인
3. 방화벽 설정 확인 (포트 80 또는 설정된 포트)

## 업데이트 방법

```bash
# 자동 업데이트
update

# 수동 업데이트
cd /root/POA
git pull --rebase
start
```

## 지원 및 문의

- GitHub Issues: https://github.com/jangdokang/POA-v5/issues
- Discord 커뮤니티: [Discord 링크]

---

**주의**: 이 프로그램은 실제 자금을 사용하는 자동매매 시스템입니다. 사용 전 충분한 테스트를 진행하고, 손실에 대한 책임은 사용자에게 있습니다.
