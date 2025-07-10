import base64
import hashlib
import hmac
import json
import time
import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

import httpx
from pydantic import BaseModel, Field
from exchange.model import MarketOrder
from exchange.utility import settings
from devtools import debug


class BithumbAuth:
    """Bithumb API 인증 클래스"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        
    def _get_nonce(self) -> str:
        """현재 시간을 마이크로초로 반환"""
        return str(int(time.time() * 1000))
    
    def _create_signature(self, endpoint: str, params: Dict[str, Any], nonce: str) -> str:
        """API 서명 생성"""
        # 파라미터를 URL 인코딩
        query_string = urllib.parse.urlencode(params)
        
        # 서명할 문자열 생성
        str_data = f"{endpoint}\0{query_string}\0{nonce}"
        
        # HMAC-SHA512로 서명
        h = hmac.new(self.api_secret.encode('utf-8'), str_data.encode('utf-8'), hashlib.sha512)
        signature = base64.b64encode(h.hexdigest().encode('utf-8')).decode('utf-8')
        
        return signature
    
    def get_headers(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, str]:
        """API 요청을 위한 헤더 생성"""
        nonce = self._get_nonce()
        params['endpoint'] = endpoint
        signature = self._create_signature(endpoint, params, nonce)
        
        return {
            'Api-Key': self.api_key,
            'Api-Sign': signature,
            'Api-Nonce': nonce,
            'Content-Type': 'application/x-www-form-urlencoded'
        }


class Bithumb:
    """Bithumb 거래소 API 클래스"""
    
    def __init__(self):
        self.base_url = "https://api.bithumb.com"
        self.api_key = settings.BITHUMB_KEY
        self.api_secret = settings.BITHUMB_SECRET
        
        if not self.api_key or not self.api_secret:
            raise ValueError("BITHUMB_KEY와 BITHUMB_SECRET이 설정되어 있지 않습니다.")
        
        self.auth = BithumbAuth(self.api_key, self.api_secret)
        self.session = httpx.Client(timeout=30.0)
        
    def init_info(self, order_info: MarketOrder):
        self.order_info = order_info
        
    def close_session(self):
        """세션 종료"""
        self.session.close()
        
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """API 응답 처리"""
        try:
            result = response.json()
            
            if result.get('status') == '0000':
                return result.get('data', {})
            else:
                error_msg = result.get('message', 'Unknown error')
                raise Exception(f"Bithumb API Error: {error_msg}")
                
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response: {response.text}")
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """현재가 정보 조회"""
        endpoint = f"/public/ticker/{symbol}_KRW"
        url = f"{self.base_url}{endpoint}"
        
        response = self.session.get(url)
        return self._handle_response(response)
    
    def fetch_price(self, base: str, quote: str) -> float:
        """현재가 조회"""
        if quote != "KRW":
            raise ValueError("Bithumb은 KRW 마켓만 지원합니다.")
            
        ticker_data = self.get_ticker(base)
        return float(ticker_data.get('closing_price', 0))
    
    def get_balance(self, currency: str = "ALL") -> Dict[str, Any]:
        """잔고 조회"""
        endpoint = "/info/balance"
        params = {
            'currency': currency
        }
        
        headers = self.auth.get_headers(endpoint, params)
        url = f"{self.base_url}{endpoint}"
        
        response = self.session.post(url, headers=headers, data=params)
        return self._handle_response(response)
    
    def create_order(self, symbol: str, side: str, amount: float, 
                    price: Optional[float] = None, order_type: str = "market") -> Dict[str, Any]:
        """주문 생성"""
        endpoint = "/trade/place"
        
        # Bithumb은 시장가 주문시에도 가격을 입력해야 함
        if order_type == "market" and not price:
            current_price = self.fetch_price(symbol, "KRW")
            if side == "buy":
                price = current_price * 1.1  # 시장가 매수는 현재가의 110%
            else:
                price = current_price * 0.9  # 시장가 매도는 현재가의 90%
        
        params = {
            'order_currency': symbol,
            'payment_currency': 'KRW',
            'units': str(amount),
            'price': str(int(price)),
            'type': 'bid' if side == 'buy' else 'ask'
        }
        
        headers = self.auth.get_headers(endpoint, params)
        url = f"{self.base_url}{endpoint}"
        
        response = self.session.post(url, headers=headers, data=params)
        result = self._handle_response(response)
        
        # 주문 결과 포맷 통일
        return {
            'id': result.get('order_id'),
            'symbol': f"{symbol}/KRW",
            'side': side,
            'amount': amount,
            'price': price,
            'status': 'open',
            'exchange': 'BITHUMB',
            'timestamp': datetime.now().isoformat()
        }
    
    def market_buy(self, order_info: MarketOrder) -> Dict[str, Any]:
        """시장가 매수"""
        # Bithumb은 원화 기준으로 주문하므로 amount 대신 cost 사용
        if order_info.cost:
            # cost를 현재가로 나누어 수량 계산
            current_price = self.fetch_price(order_info.base, "KRW")
            amount = order_info.cost / current_price
        else:
            amount = order_info.amount
            
        return self.create_order(
            symbol=order_info.base,
            side="buy",
            amount=amount,
            order_type="market"
        )
    
    def market_sell(self, order_info: MarketOrder) -> Dict[str, Any]:
        """시장가 매도"""
        return self.create_order(
            symbol=order_info.base,
            side="sell",
            amount=order_info.amount,
            order_type="market"
        )
    
    def cancel_order(self, order_id: str, symbol: str, side: str) -> Dict[str, Any]:
        """주문 취소"""
        endpoint = "/trade/cancel"
        
        params = {
            'order_id': order_id,
            'type': 'bid' if side == 'buy' else 'ask',
            'order_currency': symbol,
            'payment_currency': 'KRW'
        }
        
        headers = self.auth.get_headers(endpoint, params)
        url = f"{self.base_url}{endpoint}"
        
        response = self.session.post(url, headers=headers, data=params)
        return self._handle_response(response)
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """주문 정보 조회"""
        endpoint = "/info/order_detail"
        
        params = {
            'order_id': order_id,
            'order_currency': 'BTC',  # 실제로는 모든 통화에 대해 조회 가능
            'payment_currency': 'KRW'
        }
        
        headers = self.auth.get_headers(endpoint, params)
        url = f"{self.base_url}{endpoint}"
        
        response = self.session.post(url, headers=headers, data=params)
        result = self._handle_response(response)
        
        # 주문 정보 포맷 통일
        order_data = result.get('data', {})
        return {
            'id': order_id,
            'symbol': f"{order_data.get('order_currency')}/KRW",
            'side': 'buy' if order_data.get('type') == 'bid' else 'sell',
            'amount': float(order_data.get('units', 0)),
            'filled': float(order_data.get('units_traded', 0)),
            'remaining': float(order_data.get('units_remaining', 0)),
            'price': float(order_data.get('price', 0)),
            'status': order_data.get('order_status', 'unknown'),
            'exchange': 'BITHUMB'
        }
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """미체결 주문 조회"""
        endpoint = "/info/orders"
        
        params = {
            'order_id': '',
            'type': 'bid',  # 매수/매도 모두 조회하려면 별도 요청 필요
            'count': 100,
            'after': 0,
            'order_currency': symbol if symbol else 'BTC',
            'payment_currency': 'KRW'
        }
        
        orders = []
        
        # 매수 주문 조회
        params['type'] = 'bid'
        headers = self.auth.get_headers(endpoint, params)
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, headers=headers, data=params)
        buy_orders = self._handle_response(response)
        
        if isinstance(buy_orders, list):
            orders.extend(buy_orders)
        
        # 매도 주문 조회
        params['type'] = 'ask'
        headers = self.auth.get_headers(endpoint, params)
        response = self.session.post(url, headers=headers, data=params)
        sell_orders = self._handle_response(response)
        
        if isinstance(sell_orders, list):
            orders.extend(sell_orders)
        
        return orders
    
    def get_trading_fee(self, symbol: str) -> Dict[str, float]:
        """거래 수수료 조회"""
        endpoint = "/info/account"
        
        params = {
            'order_currency': symbol,
            'payment_currency': 'KRW'
        }
        
        headers = self.auth.get_headers(endpoint, params)
        url = f"{self.base_url}{endpoint}"
        
        response = self.session.post(url, headers=headers, data=params)
        result = self._handle_response(response)
        
        return {
            'maker': float(result.get('trade_fee', 0.15)) / 100,  # 퍼센트를 비율로 변환
            'taker': float(result.get('trade_fee', 0.15)) / 100
        }


# 사용 예시
if __name__ == "__main__":
    # 테스트 코드
    try:
        bithumb = Bithumb()
        
        # 잔고 조회
        balance = bithumb.get_balance()
        print("Balance:", balance)
        
        # 현재가 조회
        price = bithumb.fetch_price("BTC", "KRW")
        print("BTC/KRW Price:", price)
        
    except Exception as e:
        print(f"Error: {e}")
