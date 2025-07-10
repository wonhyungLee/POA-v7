from exchange.binance import Binance
from exchange.upbit import Upbit
from exchange.bybit import Bybit
from exchange.bitget import Bitget
from exchange.okx import Okx
from exchange.bithumb import Bithumb
from exchange.stock.kis import KoreaInvestment
from exchange.utility import settings
from exchange.database import db
from typing import Dict
import threading

CRYPTO_EXCHANGES = {
    "BINANCE": None,
    "UPBIT": None,
    "BYBIT": None,
    "BITGET": None,
    "OKX": None,
    "BITHUMB": None,
}

KIS_EXCHANGES = {}

# 전역 락 객체
exchange_lock = threading.Lock()


def initialize_kis_exchanges():
    """KIS 거래소 1-50번 초기화"""
    for i in range(1, 51):
        key = getattr(settings, f"KIS{i}_KEY", None)
        secret = getattr(settings, f"KIS{i}_SECRET", None)
        account_number = getattr(settings, f"KIS{i}_ACCOUNT_NUMBER", None)
        account_code = getattr(settings, f"KIS{i}_ACCOUNT_CODE", None)
        
        if key and secret and account_number and account_code:
            try:
                kis_exchange = KoreaInvestment(
                    key=key,
                    secret=secret,
                    account_number=account_number,
                    account_code=account_code,
                    kis_number=i
                )
                KIS_EXCHANGES[f"KIS{i}"] = kis_exchange
            except Exception as e:
                print(f"KIS{i} 초기화 실패: {e}")
                KIS_EXCHANGES[f"KIS{i}"] = None
        else:
            KIS_EXCHANGES[f"KIS{i}"] = None


# KIS 거래소 초기화
initialize_kis_exchanges()


def initialize_exchange(exchange_name: str):
    """거래소 객체를 초기화합니다."""
    try:
        if exchange_name == "BINANCE":
            if settings.BINANCE_KEY and settings.BINANCE_SECRET:
                return Binance()
        elif exchange_name == "UPBIT":
            if settings.UPBIT_KEY and settings.UPBIT_SECRET:
                return Upbit()
        elif exchange_name == "BYBIT":
            if settings.BYBIT_KEY and settings.BYBIT_SECRET:
                return Bybit()
        elif exchange_name == "BITGET":
            if settings.BITGET_KEY and settings.BITGET_SECRET and settings.BITGET_PASSPHRASE:
                return Bitget()
        elif exchange_name == "OKX":
            if settings.OKX_KEY and settings.OKX_SECRET and settings.OKX_PASSPHRASE:
                return Okx()
        elif exchange_name == "BITHUMB":
            if settings.BITHUMB_KEY and settings.BITHUMB_SECRET:
                return Bithumb()
    except Exception as e:
        print(f"{exchange_name} 초기화 실패: {e}")
    
    return None


def get_exchange(exchange_name: str = None) -> Dict:
    """거래소 객체를 반환합니다."""
    with exchange_lock:
        # 암호화폐 거래소
        if exchange_name in CRYPTO_EXCHANGES:
            if CRYPTO_EXCHANGES[exchange_name] is None:
                CRYPTO_EXCHANGES[exchange_name] = initialize_exchange(exchange_name)
            return CRYPTO_EXCHANGES
        
        # KIS 거래소
        if exchange_name and exchange_name.startswith("KIS"):
            if exchange_name in KIS_EXCHANGES:
                return {exchange_name: KIS_EXCHANGES[exchange_name]}
        
        # 전체 거래소 반환
        if exchange_name is None:
            all_exchanges = CRYPTO_EXCHANGES.copy()
            all_exchanges.update(KIS_EXCHANGES)
            return all_exchanges
        
        raise ValueError(f"지원하지 않는 거래소: {exchange_name}")


def get_bot(exchange_name: str, kis_number: int = 1):
    """거래 봇 객체를 반환합니다."""
    if exchange_name in ["KRX", "NASDAQ", "NYSE", "AMEX"]:
        # 주식 거래인 경우 KIS 번호로 거래소 선택
        kis_key = f"KIS{kis_number}"
        if kis_key in KIS_EXCHANGES and KIS_EXCHANGES[kis_key] is not None:
            return KIS_EXCHANGES[kis_key]
        else:
            raise ValueError(f"{kis_key} 거래소가 설정되지 않았습니다.")
    else:
        # 암호화폐 거래소
        with exchange_lock:
            if exchange_name not in CRYPTO_EXCHANGES:
                raise ValueError(f"지원하지 않는 거래소: {exchange_name}")
            
            if CRYPTO_EXCHANGES[exchange_name] is None:
                CRYPTO_EXCHANGES[exchange_name] = initialize_exchange(exchange_name)
            
            if CRYPTO_EXCHANGES[exchange_name] is None:
                raise ValueError(f"{exchange_name} 거래소가 설정되지 않았습니다.")
            
            return CRYPTO_EXCHANGES[exchange_name]


# 기존 호환성을 위한 exports
__all__ = ['get_exchange', 'get_bot', 'CRYPTO_EXCHANGES', 'KIS_EXCHANGES']
