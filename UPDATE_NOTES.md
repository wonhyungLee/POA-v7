# POA-v7 업데이트 내역

## 주요 변경사항

### 1. .env 템플릿 파일 추가
- `.env.template` 파일을 생성하여 환경 설정을 쉽게 할 수 있도록 개선
- 오라클 클라우드 서버에서 `git clone` 후 `.env.template`을 `.env`로 복사하여 사용
```bash
cp .env.template .env
# 이후 .env 파일을 편집하여 실제 값 입력
```

### 2. KIS4 실전투자 계좌 인식 수정
- 기존: KIS4가 모의투자 계좌로 인식되는 문제
- 수정: KIS1, KIS2, KIS3, KIS4 모두 실전투자 계좌로 인식되도록 변경
- `exchange/stock/kis.py` 파일에서 `paper_base_url` 사용 조건 제거

### 3. Bithumb 거래소 지원 추가
- `BITHUMB` 거래소가 지원 목록에 추가됨
- `exchange/bithumb.py` 파일에 Bithumb API 구현
- 환경변수: `BITHUMB_KEY`, `BITHUMB_SECRET` 설정 필요

### 4. 자산 모니터링 기능 추가
- 정기적으로 전체 거래소와 주식 계좌의 자산 현황을 디스코드로 알림
- 새로운 파일: `asset_monitor.py`
- 환경변수 설정:
  - `ENABLE_ASSET_MONITOR`: 자산 모니터링 활성화 (true/false)
  - `ASSET_REPORT_INTERVAL_HOURS`: 리포트 전송 간격 (기본값: 6시간)

#### 새로운 API 엔드포인트:
- `GET /assets`: 현재 자산 현황 즉시 조회
- `POST /assets/report`: 자산 현황 리포트를 디스코드로 즉시 전송

## 사용 방법

### 1. 환경 설정
```bash
# .env 파일 생성
cp .env.template .env

# .env 파일 편집하여 필요한 값 입력
nano .env
```

### 2. 자산 모니터링 활성화
`.env` 파일에서:
```
# 디스코드 웹훅 URL 설정 (필수)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# 자산 모니터링 활성화
ENABLE_ASSET_MONITOR=true

# 리포트 간격 설정 (시간 단위)
ASSET_REPORT_INTERVAL_HOURS=6
```

### 3. 서버 실행
```bash
python run.py
```

## 주의사항

1. **Bithumb 사용 시**: 
   - `BITHUMB_KEY`와 `BITHUMB_SECRET` 설정 필수
   - Bithumb은 KRW 마켓만 지원

2. **자산 모니터링**:
   - 디스코드 웹훅 URL이 설정되어 있어야 함
   - 각 거래소의 API 키가 올바르게 설정되어 있어야 자산 조회 가능

3. **KIS 계좌**:
   - KIS1~KIS4 모두 실전투자 계좌로 처리됨
   - 모의투자가 필요한 경우 별도 설정 필요

## 문제 해결

### 거래소 연결 오류
- API 키와 시크릿이 올바르게 설정되었는지 확인
- 화이트리스트에 서버 IP가 추가되었는지 확인

### 자산 모니터링이 작동하지 않을 때
1. `ENABLE_ASSET_MONITOR=true` 확인
2. `DISCORD_WEBHOOK_URL` 설정 확인
3. 로그에서 오류 메시지 확인

### Bithumb 연결 문제
- Bithumb API는 IP 화이트리스트 설정이 필요할 수 있음
- API 키 권한 확인 (잔고 조회, 주문 권한 필요)
