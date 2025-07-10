# 한국투자증권(KIS) API 연동 가이드

## API 키 발급 방법

### 1. 한국투자증권 홈페이지 접속
- https://www.koreainvestment.com
- 로그인 후 마이페이지 → API 서비스 신청

### 2. API 서비스 신청
- 실전투자 API 신청
- 서비스 약관 동의
- API Key, Secret 발급

### 3. 계좌 정보 확인
- 계좌번호: 8자리 숫자
- 계좌 상품코드: 보통 "01" (종합계좌)

## KIS API 주요 엔드포인트

### 국내주식
- **주문**: `/uapi/domestic-stock/v1/trading/order-cash`
- **현재가 조회**: `/uapi/domestic-stock/v1/quotations/inquire-price`
- **잔고 조회**: `/uapi/domestic-stock/v1/trading/inquire-balance`

### 해외주식
- **주문**: `/uapi/overseas-stock/v1/trading/order`
- **현재가 조회**: `/uapi/overseas-stock/v1/quotations/price`
- **잔고 조회**: `/uapi/overseas-stock/v1/trading/inquire-balance`

## POA에서 KIS 설정 예시

### .env 파일 설정
```env
# KIS 1번 계정 (국내주식 전용)
KIS1_KEY="PSxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
KIS1_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
KIS1_ACCOUNT_NUMBER="12345678"
KIS1_ACCOUNT_CODE="01"

# KIS 2번 계정 (해외주식 전용)
KIS2_KEY="PSyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
KIS2_SECRET="yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
KIS2_ACCOUNT_NUMBER="87654321"
KIS2_ACCOUNT_CODE="01"

# KIS 3-50번 계정도 동일한 형식으로 추가 가능
```

## 주문 예시

### 국내주식 (KRX)
```json
{
  "password": "your_password",
  "exchange": "KRX",
  "base": "005930",  // 삼성전자 종목코드
  "quote": "KRW",
  "side": "buy",
  "amount": 10,      // 10주
  "kis_number": 1    // KIS1 계정 사용
}
```

### 미국주식 (NASDAQ)
```json
{
  "password": "your_password",
  "exchange": "NASDAQ",
  "base": "AAPL",    // Apple 티커
  "quote": "USD",
  "side": "buy",
  "amount": 5,       // 5주
  "kis_number": 2    // KIS2 계정 사용
}
```

## 주요 종목코드

### 국내주식 (6자리)
- 삼성전자: 005930
- SK하이닉스: 000660
- NAVER: 035420
- 카카오: 035720
- LG에너지솔루션: 373220

### 미국주식 (티커)
- Apple: AAPL (NASDAQ)
- Microsoft: MSFT (NASDAQ)
- Amazon: AMZN (NASDAQ)
- Tesla: TSLA (NASDAQ)
- Google: GOOGL (NASDAQ)

## 거래 시간

### 국내주식
- 정규장: 09:00 ~ 15:30 (한국시간)
- 시간외 단일가: 16:00 ~ 18:00

### 미국주식
- 정규장: 23:30 ~ 06:00 (한국시간, 서머타임 22:30 ~ 05:00)
- 프리마켓: 18:00 ~ 23:30
- 애프터마켓: 06:00 ~ 10:00

## 주의사항

1. **API 제한**
   - 초당 20회 요청 제한
   - 1분당 1000회 요청 제한

2. **주문 수량**
   - 국내주식: 1주 단위
   - 미국주식: 1주 단위 (소수점 주문 불가)

3. **수수료**
   - 국내주식: 약 0.015% ~ 0.35%
   - 미국주식: 약 0.25% + $0.00396/주

4. **세금**
   - 국내주식: 거래세 0.23% (코스피), 0.25% (코스닥)
   - 미국주식: 양도소득세 22% (250만원 공제)

## 에러 코드

- `EGW00123`: 인증 토큰 만료
- `EGW00201`: 잔고 부족
- `EGW00202`: 주문 수량 초과
- `EGW00203`: 호가 범위 초과

## 디버깅 팁

1. **토큰 확인**
   ```python
   # kis.py에서 auth 확인
   print(f"Token: {self.base_headers['authorization']}")
   ```

2. **주문 응답 확인**
   ```python
   # 주문 후 응답 출력
   result = kis.create_order(...)
   print(f"Order result: {result}")
   ```

3. **잔고 확인**
   - 주문 전 계좌 잔고 확인
   - 보유 종목 수량 확인

## 추가 리소스

- [한국투자증권 API 문서](https://apiportal.koreainvestment.com)
- [KIS Developers 커뮤니티](https://forum.koreainvestment.com)
- [API 테스트 도구](https://apiportal.koreainvestment.com/apiservice/oauth2#L_5c87ba63-740a-4166-93ac-803510bb9c02)
