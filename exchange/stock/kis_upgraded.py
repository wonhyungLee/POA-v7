from datetime import datetime
import json
import httpx
from bs4 import BeautifulSoup
from exchange.stock.error import TokenExpired
from exchange.stock.schemas import *
from exchange.database import db
from pydantic import validate_arguments
import traceback
import copy
from exchange.model import MarketOrder
from devtools import debug


class KoreaInvestment:
    def __init__(
        self,
        key: str,
        secret: str,
        account_number: str,
        account_code: str,
        kis_number: int,
    ):
        self.key = key
        self.secret = secret
        self.kis_number = kis_number
        # 모든 계정은 실전투자 URL 사용 (모의투자 제거)
        self.base_url = BaseUrls.base_url.value
        self.is_auth = False
        self.account_number = account_number
        self.base_headers = {}
        self.session = httpx.Client()
        self.async_session = httpx.AsyncClient()
        self.auth()

        self.base_body = {}
        self.base_order_body = AccountInfo(
            CANO=account_number, ACNT_PRDT_CD=account_code
        )
        self.order_exchange_code = {
            "NASDAQ": ExchangeCode.NASDAQ,
            "NYSE": ExchangeCode.NYSE,
            "AMEX": ExchangeCode.AMEX,
        }
        self.query_exchange_code = {
            "NASDAQ": QueryExchangeCode.NASDAQ,
            "NYSE": QueryExchangeCode.NYSE,
            "AMEX": QueryExchangeCode.AMEX,
        }

    def init_info(self, order_info: MarketOrder):
        self.order_info = order_info

    def close_session(self):
        self.session.close()

    def get(self, endpoint: str, params: dict = None, headers: dict = None):
        url = f"{self.base_url}{endpoint}"
        # headers |= self.base_headers
        return self.session.get(url, params=params, headers=headers).json()

    def post_with_error_handling(
        self, endpoint: str, data: dict = None, headers: dict = None
    ):
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data, headers=headers).json()
        if "access_token" in response.keys() or response["rt_cd"] == "0":
            return response
        else:
            raise Exception(response)

    def post(self, endpoint: str, data: dict = None, headers: dict = None):
        return self.post_with_error_handling(endpoint, data, headers)

    def get_hashkey(self, data) -> str:
        headers = {"appKey": self.key, "appSecret": self.secret}
        endpoint = "/uapi/hashkey"
        url = f"{self.base_url}{endpoint}"
        return self.session.post(url, json=data, headers=headers).json()["HASH"]

    def open_auth(self):
        return self.open_json("auth.json")

    def write_auth(self, auth):
        self.write_json("auth.json", auth)

    def check_auth(self, auth, key, secret, kis_number):
        if auth is None:
            return False
        access_token, access_token_token_expired = auth
        try:
            if access_token == "nothing":
                return False
            else:
                if not self.is_auth:
                    response = self.session.get(
                        "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-ccnl",
                        headers={
                            "authorization": f"BEARER {access_token}",
                            "appkey": key,
                            "appsecret": secret,
                            "custtype": "P",
                            "tr_id": "FHKST01010300",
                        },
                        params={
                            "FID_COND_MRKT_DIV_CODE": "J",
                            "FID_INPUT_ISCD": "005930",
                        },
                    ).json()
                    if response["msg_cd"] == "EGW00123":
                        return False

            access_token_token_expired = datetime.strptime(
                access_token_token_expired, "%Y-%m-%d %H:%M:%S"
            )
            diff = access_token_token_expired - datetime.now()
            total_seconds = diff.total_seconds()
            if total_seconds < 60 * 60:
                return False
            else:
                return True

        except Exception as e:
            print(traceback.format_exc())

    def create_auth(self, key: str, secret: str):
        data = {"grant_type": "client_credentials", "appkey": key, "appsecret": secret}
        base_url = BaseUrls.base_url.value
        endpoint = "/oauth2/tokenP"

        url = f"{base_url}{endpoint}"

        response = self.session.post(url, json=data).json()
        if "access_token" in response.keys() or response.get("rt_cd") == "0":
            return response["access_token"], response["access_token_token_expired"]
        else:
            raise Exception(response)

    def auth(self):
        auth_id = f"KIS{self.kis_number}"
        auth = db.get_auth(auth_id)
        if not self.check_auth(auth, self.key, self.secret, self.kis_number):
            auth = self.create_auth(self.key, self.secret)
            db.set_auth(auth_id, auth[0], auth[1])
        else:
            self.is_auth = True
        access_token = auth[0]
        self.base_headers = BaseHeaders(
            authorization=f"Bearer {access_token}",
            appkey=self.key,
            appsecret=self.secret,
            custtype="P",
        ).dict()
        return auth

    @validate_arguments
    def create_order(
        self,
        exchange: Literal["KRX", "NASDAQ", "NYSE", "AMEX"],
        ticker: str,
        order_type: Literal["limit", "market"],
        side: Literal["buy", "sell"],
        amount: int,
        price: int = 0,
        mintick=0.01,
    ):
        endpoint = (
            Endpoints.korea_order.value
            if exchange == "KRX"
            else Endpoints.usa_order.value
        )
        body = self.base_order_body.dict()
        headers = copy.deepcopy(self.base_headers)
        price = str(price)

        amount = str(int(amount))

        if exchange == "KRX":
            headers |= (
                KoreaBuyOrderHeaders(**headers).dict()
                if side == "buy"
                else KoreaSellOrderHeaders(**headers).dict()
            )

            if order_type == "market":
                body |= KoreaMarketOrderBody(**body, PDNO=ticker, ORD_QTY=amount).dict()
            elif order_type == "limit":
                body |= KoreaOrderBody(
                    **body,
                    PDNO=ticker,
                    ORD_DVSN=KoreaOrderType.limit,
                    ORD_QTY=amount,
                    ORD_UNPR=price,
                ).dict()
        elif exchange in ("NASDAQ", "NYSE", "AMEX"):
            exchange_code = self.order_exchange_code.get(exchange)
            current_price = self.fetch_current_price(exchange, ticker)
            price = (
                current_price + mintick * 50
                if side == "buy"
                else current_price - mintick * 50
            )
            if price < 1:
                price = 1.0
            price = float("{:.2f}".format(price))
            
            headers |= (
                UsaBuyOrderHeaders(**headers).dict()
                if side == "buy"
                else UsaSellOrderHeaders(**headers).dict()
            )

            if order_type == "market":
                body |= UsaOrderBody(
                    **body,
                    PDNO=ticker,
                    ORD_DVSN=UsaOrderType.limit.value,
                    ORD_QTY=amount,
                    OVRS_ORD_UNPR=price,
                    OVRS_EXCG_CD=exchange_code,
                ).dict()
            elif order_type == "limit":
                body |= UsaOrderBody(
                    **body,
                    PDNO=ticker,
                    ORD_DVSN=UsaOrderType.limit.value,
                    ORD_QTY=amount,
                    OVRS_ORD_UNPR=price,
                    OVRS_EXCG_CD=exchange_code,
                ).dict()
        return self.post(endpoint, body, headers)

    def create_market_buy_order(
        self,
        exchange: Literal["KRX", "NASDAQ", "NYSE", "AMEX"],
        ticker: str,
        amount: int,
        price: int = 0,
    ):
        if exchange == "KRX":
            return self.create_order(exchange, ticker, "market", "buy", amount)
        elif exchange == "usa":
            return self.create_order(exchange, ticker, "market", "buy", amount, price)

    def create_market_sell_order(
        self,
        exchange: Literal["KRX", "NASDAQ", "NYSE", "AMEX"],
        ticker: str,
        amount: int,
        price: int = 0,
    ):
        if exchange == "KRX":
            return self.create_order(exchange, ticker, "market", "sell", amount)
        elif exchange == "usa":
            return self.create_order(exchange, ticker, "market", "buy", amount, price)

    def create_korea_market_buy_order(self, ticker: str, amount: int):
        return self.create_market_buy_order("KRX", ticker, amount)

    def create_korea_market_sell_order(self, ticker: str, amount: int):
        return self.create_market_sell_order("KRX", ticker, amount)

    def create_usa_market_buy_order(self, ticker: str, amount: int, price: int):
        return self.create_market_buy_order("usa", ticker, amount, price)

    def fetch_ticker(
        self, exchange: Literal["KRX", "NASDAQ", "NYSE", "AMEX"], ticker: str
    ):
        if exchange == "KRX":
            endpoint = Endpoints.korea_ticker.value
            headers = KoreaTickerHeaders(**self.base_headers).dict()
            query = KoreaTickerQuery(FID_INPUT_ISCD=ticker).dict()
        elif exchange in ("NASDAQ", "NYSE", "AMEX"):
            exchange_code = self.query_exchange_code.get(exchange)
            endpoint = Endpoints.usa_ticker.value
            headers = UsaTickerHeaders(**self.base_headers).dict()
            query = UsaTickerQuery(EXCD=exchange_code, SYMB=ticker).dict()
        ticker = self.get(endpoint, query, headers)
        return ticker.get("output")

    def fetch_current_price(self, exchange, ticker: str):
        try:
            if exchange == "KRX":
                return float(self.fetch_ticker(exchange, ticker)["stck_prpr"])
            elif exchange in ("NASDAQ", "NYSE", "AMEX"):
                return float(self.fetch_ticker(exchange, ticker)["last"])

        except KeyError:
            print(traceback.format_exc())
            return None

    def get_exchange_rate(self):
        """USD/KRW 환율 조회 (다중 소스 백업)"""
        # 1순위: 한국수출입은행 API
        try:
            # 참고: API 키 발급이 필요합니다. https://www.koreaexim.go.kr/site/program/openapi/openApiView?menuid=001003002002&apino=2&viewtype=C
            # 정식 서비스에서는 'YOUR_KEY_HERE'를 발급받은 키로 교체해야 합니다.
            auth_key = "YOUR_KEY_HERE" 
            search_date = datetime.now().strftime('%Y%m%d')
            url = f"https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey={auth_key}&searchdate={search_date}&data=AP01"
            
            response = httpx.get(url)
            response.raise_for_status()
            data = response.json()
            
            for item in data:
                if item.get('cur_unit') == 'USD':
                    exchange_rate_str = item.get('tts', item.get('deal_bas_r', '0')).replace(',', '')
                    if float(exchange_rate_str) > 0:
                        return float(exchange_rate_str)
            raise ValueError("USD exchange rate not found in Eximbank API response")

        except Exception as e:
            print(f"한국수출입은행 API 조회 실패: {e}. 다음 단계로 진행합니다.")
            # 2순위: 네이버 금융 크롤링
            try:
                url = "https://finance.naver.com/marketindex/"
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = httpx.get(url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                exchange_rate_str = soup.select_one("#exchangeList > li.on > a.head.usd > div > span.value").text.replace(',', '')
                return float(exchange_rate_str)
            except Exception as e:
                print(f"네이버 금융 크롤링 실패: {e}. 다음 단계로 진행합니다.")
                # 3순위: 고정 환율
                print("모든 환율 조회 실패, 고정 환율 1350.0 적용")
                return 1350.0

    def get_balance(self):
        """국내 및 해외 주식 잔고 조회 통합 메서드"""
        try:
            # 국내주식 잔고 조회
            domestic_result = self._get_domestic_balance()
            
            # 해외주식 잔고 조회  
            overseas_result = self._get_overseas_balance()
            
            # 결과 통합
            total_krw = domestic_result.get('total_krw', 0) + overseas_result.get('total_krw', 0)
            all_stocks = domestic_result.get('stocks', []) + overseas_result.get('stocks', [])
            
            return {
                'total_krw': total_krw,
                'stocks': all_stocks
            }
        except Exception as e:
            from exchange.utility import log_message
            log_message(f'KIS 자산 조회 실패: {str(e)}')
            return {'total_krw': 0, 'stocks': []}
        
    def _get_domestic_balance(self):
        """국내 주식 잔고 조회"""
        endpoint = '/uapi/domestic-stock/v1/trading/inquire-balance'
        headers = self.base_headers.copy()
        headers['tr_id'] = 'TTTC8434R'
        
        params = {
            'CANO': self.account_number,
            'ACNT_PRDT_CD': '01',
            'AFHR_FLNG_YN': 'N',
            'OFL_YN': '',
            'INQR_DVSN': '02',
            'UNPR_DVSN': '01', 
            'FUND_STTL_ICLD_YN': 'N',
            'FNCG_AMT_AUTO_RDPT_YN': 'N',
            'PRCS_DVSN': '01',
            'CTX_AREA_FK100': '',
            'CTX_AREA_NK100': ''
        }
        
        try:
            response = self.get(endpoint, params=params, headers=headers)
            if response and response.get('rt_cd') == '0':
                output1 = response.get('output1', [])
                output2 = response.get('output2', [])
                
                total_krw = 0
                if output2:
                    total_krw = int(output2[0].get('tot_evlu_amt', 0))
                    
                stocks = []
                for item in output1:
                    if int(item.get('hldg_qty', 0)) > 0:
                        stocks.append({
                            'symbol': item.get('pdno', ''),
                            'name': item.get('prdt_name', ''),
                            'quantity': int(item.get('hldg_qty', 0)),
                            'average_price': float(item.get('pchs_avg_pric', 0)),
                            'current_price': float(item.get('prpr', 0)),
                            'eval_amount': int(item.get('evlu_amt', 0))
                        })
                
                return {'total_krw': total_krw, 'stocks': stocks}
        except Exception as e:
            from exchange.utility import log_message
            log_message(f'KIS 국내 잔고 조회 실패: {str(e)}')
            
        return {'total_krw': 0, 'stocks': []}
    
    def _get_overseas_balance(self):
        """해외 주식 잔고 조회 (TTTS3012R)"""
        endpoint = "/uapi/overseas-stock/v1/trading/inquire-balance"
        headers = self.base_headers.copy()
        headers["tr_id"] = "TTTS3012R"
        
        params = {
            "CANO": self.account_number,
            "ACNT_PRDT_CD": "01",
            "OVRS_EXCG_CD": "NYS", # NYS, NAS, AMS 등, 전체 조회를 위해 특정 시장 지정
            "TR_CRCY_CD": "USD",
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": ""
        }
        
        exchange_rate = self.get_exchange_rate()
        
        total_eval_usd = 0
        all_stocks = []

        # 주요 해외 시장에 대해 반복 조회
        for exch_code in ["NYS", "NAS", "AMS"]:
            params["OVRS_EXCG_CD"] = exch_code
            try:
                res = self.get(endpoint, params=params, headers=headers)
                if res and res.get('rt_cd') == '0' and res.get('output1'):
                    for item in res.get('output1', []):
                        if int(item.get('ovrs_cblc_qty', 0)) > 0:
                            eval_usd = float(item.get('frcr_evlu_amt', 0))
                            total_eval_usd += eval_usd
                            all_stocks.append({
                                "symbol": item['ovrs_pdno'],
                                "name": item['ovrs_item_name'],
                                "quantity": int(item['ovrs_cblc_qty']),
                                "average_price": float(item['pchs_avg_pric']),
                                "current_price": float(item['now_pric1']),
                                "eval_amount": eval_usd * exchange_rate # KRW로 변환
                            })
            except Exception as e:
                from exchange.utility import log_message
                log_message(f"KIS 해외 잔고 조회 실패 ({exch_code}): {e}")

        total_krw = total_eval_usd * exchange_rate
        return {"total_krw": total_krw, "stocks": all_stocks}

    def open_json(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def write_json(self, path, data):
        with open(path, "w") as f:
            json.dump(data, f)


if __name__ == "__main__":
    pass