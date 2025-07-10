# POA v5 웹훅 요청 샘플

## 암호화폐 거래소 샘플

### 1. Binance 현물 매수
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

### 2. Binance 선물 진입 (롱)
```json
{
  "password": "your_password_here",
  "exchange": "BINANCE",
  "base": "BTC",
  "quote": "USDT.P",
  "side": "entry/buy",
  "amount": 0.01,
  "leverage": 10
}
```

### 3. Binance 선물 진입 (숏)
```json
{
  "password": "your_password_here",
  "exchange": "BINANCE",
  "base": "BTC",
  "quote": "USDT.P",
  "side": "entry/sell",
  "amount": 0.01,
  "leverage": 10
}
```

### 4. Binance 선물 청산
```json
{
  "password": "your_password_here",
  "exchange": "BINANCE",
  "base": "BTC",
  "quote": "USDT.P",
  "side": "close/buy",
  "amount": 0.01
}
```

### 5. Upbit 현물 매수 (원화 기준)
```json
{
  "password": "your_password_here",
  "exchange": "UPBIT",
  "base": "BTC",
  "quote": "KRW",
  "side": "buy",
  "cost": 100000
}
```

### 6. Upbit 현물 매도
```json
{
  "password": "your_password_here",
  "exchange": "UPBIT",
  "base": "BTC",
  "quote": "KRW",
  "side": "sell",
  "amount": 0.001
}
```

### 7. Bithumb 현물 매수 (신규)
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

### 8. Bithumb 현물 매도 (신규)
```json
{
  "password": "your_password_here",
  "exchange": "BITHUMB",
  "base": "ETH",
  "quote": "KRW",
  "side": "sell",
  "amount": 0.1
}
```

### 9. Bybit 선물 진입
```json
{
  "password": "your_password_here",
  "exchange": "BYBIT",
  "base": "BTC",
  "quote": "USDT.P",
  "side": "entry/buy",
  "amount": 0.01,
  "leverage": 5
}
```

### 10. Bitget 선물 진입
```json
{
  "password": "your_password_here",
  "exchange": "BITGET",
  "base": "ETH",
  "quote": "USDT.P",
  "side": "entry/sell",
  "amount": 0.1,
  "leverage": 20
}
```

## 주식 거래소 샘플

### 11. KRX (한국거래소) 매수
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

### 12. KRX 매도
```json
{
  "password": "your_password_here",
  "exchange": "KRX",
  "base": "005930",
  "quote": "KRW",
  "side": "sell",
  "amount": 10,
  "kis_number": 1
}
```

### 13. NASDAQ 매수
```json
{
  "password": "your_password_here",
  "exchange": "NASDAQ",
  "base": "AAPL",
  "quote": "USD",
  "side": "buy",
  "amount": 5,
  "kis_number": 2
}
```

### 14. NYSE 매도
```json
{
  "password": "your_password_here",
  "exchange": "NYSE",
  "base": "MSFT",
  "quote": "USD",
  "side": "sell",
  "amount": 3,
  "kis_number": 3
}
```

### 15. 다중 KIS 계정 사용 예시
```json
{
  "password": "your_password_here",
  "exchange": "KRX",
  "base": "035720",
  "quote": "KRW",
  "side": "buy",
  "amount": 100,
  "kis_number": 25
}
```

## 헤지 거래 샘플

### 16. 김프 헤지 시작
```json
{
  "password": "your_password_here",
  "exchange": "BINANCE",
  "base": "BTC",
  "quote": "USDT.P",
  "amount": 0.01,
  "leverage": 1,
  "hedge": "ON"
}
```

### 17. 김프 헤지 종료
```json
{
  "password": "your_password_here",
  "exchange": "BINANCE",
  "base": "BTC",
  "quote": "USDT.P",
  "hedge": "OFF"
}
```

## 특수 주문 샘플

### 18. 퍼센트 기반 주문
```json
{
  "password": "your_password_here",
  "exchange": "BINANCE",
  "base": "ETH",
  "quote": "USDT",
  "side": "buy",
  "percent": 50,
  "order_name": "ETH 50% 매수"
}
```

### 19. 전체 포지션 청산
```json
{
  "password": "your_password_here",
  "exchange": "BINANCE",
  "base": "BTC",
  "quote": "USDT.P",
  "side": "close/buy",
  "is_total": true,
  "order_name": "BTC 전체 청산"
}
```

## 주의사항

1. **password**: 반드시 .env 파일의 PASSWORD와 일치해야 함
2. **kis_number**: KIS 계정 사용 시 1-50 사이의 숫자 지정
3. **amount vs cost**: 
   - amount: 구매할 코인/주식 수량
   - cost: 구매에 사용할 원화/달러 금액
4. **quote 표기**:
   - 현물: USDT, KRW, USD
   - 선물: USDT.P, USD.P
5. **side 표기**:
   - 현물: buy, sell
   - 선물 진입: entry/buy (롱), entry/sell (숏)
   - 선물 청산: close/buy (숏청산), close/sell (롱청산)

## 테스트 방법

1. Postman 또는 curl을 사용하여 테스트:
```bash
curl -X POST http://your-server-ip/order \
  -H "Content-Type: application/json" \
  -d '{
    "password": "your_password_here",
    "exchange": "BINANCE",
    "base": "BTC",
    "quote": "USDT",
    "side": "buy",
    "amount": 0.001
  }'
```

2. TradingView Alert에서 웹훅 URL 설정:
   - URL: http://your-server-ip/order
   - 메시지에 JSON 형식 입력
