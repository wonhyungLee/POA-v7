from datetime import datetime
import asyncio
import httpx
from exchange.pexchange import get_bot
from exchange.utility import settings, log_message
from typing import Dict, List
import json
import traceback


class AssetMonitor:
    def __init__(self):
        self.webhook_url = settings.DISCORD_WEBHOOK_URL
        self.last_report_time = None
        
    async def get_crypto_assets(self) -> Dict[str, Dict]:
        """암호화폐 거래소 자산 조회"""
        assets = {}
        
        # Binance
        try:
            if settings.BINANCE_KEY:
                binance = get_bot("BINANCE")
                balance = binance.client.fetch_balance()
                assets["BINANCE"] = {
                    "total_usdt": balance.get("USDT", {}).get("total", 0),
                    "balances": {k: v for k, v in balance.get("total", {}).items() if v > 0}
                }
        except Exception as e:
            log_message(f"Binance 자산 조회 실패: {str(e)}")
            
        # Upbit
        try:
            if settings.UPBIT_KEY:
                upbit = get_bot("UPBIT")
                balance = upbit.client.fetch_balance()
                assets["UPBIT"] = {
                    "total_krw": balance.get("KRW", {}).get("total", 0),
                    "balances": {k: v for k, v in balance.get("total", {}).items() if v > 0}
                }
        except Exception as e:
            log_message(f"Upbit 자산 조회 실패: {str(e)}")
            
        # Bithumb
        try:
            if settings.BITHUMB_KEY:
                bithumb = get_bot("BITHUMB")
                balance = bithumb.get_balance()
                assets["BITHUMB"] = {
                    "total_krw": float(balance.get("total_krw", 0)),
                    "balances": {k.replace('total_', '').upper(): float(v) for k, v in balance.items() 
                               if k.startswith("total_") and float(v) > 0}
                }
        except Exception as e:
            log_message(f"Bithumb 자산 조회 실패: {str(e)}")
            
        # Bybit
        try:
            if settings.BYBIT_KEY:
                bybit = get_bot("BYBIT")
                balance = bybit.client.fetch_balance()
                assets["BYBIT"] = {
                    "total_usdt": balance.get("USDT", {}).get("total", 0),
                    "balances": {k: v for k, v in balance.get("total", {}).items() if v > 0}
                }
        except Exception as e:
            log_message(f"Bybit 자산 조회 실패: {str(e)}")
            
        # Bitget
        try:
            if settings.BITGET_KEY:
                bitget = get_bot("BITGET")
                balance = bitget.client.fetch_balance()
                assets["BITGET"] = {
                    "total_usdt": balance.get("USDT", {}).get("total", 0),
                    "balances": {k: v for k, v in balance.get("total", {}).items() if v > 0}
                }
        except Exception as e:
            log_message(f"Bitget 자산 조회 실패: {str(e)}")
            
        # OKX
        try:
            if settings.OKX_KEY:
                okx = get_bot("OKX")
                balance = okx.client.fetch_balance()
                assets["OKX"] = {
                    "total_usdt": balance.get("USDT", {}).get("total", 0),
                    "balances": {k: v for k, v in balance.get("total", {}).items() if v > 0}
                }
        except Exception as e:
            log_message(f"OKX 자산 조회 실패: {str(e)}")
            
        return assets
    
    async def get_stock_assets(self) -> Dict[str, Dict]:
        """주식 계좌 자산 조회"""
        assets = {}
        
        for kis_num in range(1, 51):  # KIS1부터 KIS50까지 확인
            try:
                kis_key = getattr(settings, f"KIS{kis_num}_KEY", None)
                if kis_key:
                    bot = get_bot("KRX", kis_number=kis_num) # KRX를 통해 KIS bot 로드
                    balance_info = bot.get_balance()
                    
                    assets[f"KIS{kis_num}"] = {
                        "total_krw": balance_info.get("total_krw", 0),
                        "stocks": balance_info.get("stocks", [])
                    }
            except Exception as e:
                log_message(f"KIS{kis_num} 자산 조회 실패: {str(e)}")
                
        return assets
    
    def format_asset_message(self, crypto_assets: Dict, stock_assets: Dict) -> Dict:
        """디스코드 메시지 포맷팅"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        embeds = [{
            "title": "💰 POA Bot 자산 현황",
            "description": f"조회 시간: {timestamp}",
            "color": 0x00ff00,
            "fields": []
        }]
        
        # 암호화폐 자산
        if crypto_assets:
            crypto_field = {
                "name": "🪙 암호화폐 거래소",
                "value": "",
                "inline": False
            }
            
            for exchange, data in crypto_assets.items():
                value_lines = [f"**{exchange}**"]
                
                if exchange in ["UPBIT", "BITHUMB"]:
                    total_krw = data.get("total_krw", 0)
                    value_lines.append(f"총 자산: {total_krw:,.0f} KRW")
                else:
                    total_usdt = data.get("total_usdt", 0)
                    value_lines.append(f"총 자산: {total_usdt:,.2f} USDT")
                
                # 주요 보유 자산 표시
                balances = data.get("balances", {})
                major_assets = sorted(
                    [(k, v) for k, v in balances.items() if v > 0],
                    key=lambda x: x[1],
                    reverse=True
                )[:5]  # 상위 5개만 표시
                
                if major_assets:
                    value_lines.append("주요 보유:")
                    for asset, amount in major_assets:
                        if asset not in ["KRW", "USDT", "total_krw"]:
                            value_lines.append(f"  • {asset}: {amount:.4f}")
                
                crypto_field["value"] += "\n".join(value_lines) + "\n\n"
            
            embeds[0]["fields"].append(crypto_field)
        
        # 주식 자산
        if stock_assets:
            stock_field = {
                "name": "📈 주식 계좌",
                "value": "",
                "inline": False
            }
            
            for account, data in stock_assets.items():
                total_krw = data.get("total_krw", 0)
                stock_field["value"] += f"**{account}**: {total_krw:,.0f} KRW\n"
                
                stocks = data.get("stocks", [])
                if stocks:
                    for stock in stocks[:5]: # 상위 5개 종목만 표시
                        stock_field["value"] += f"  • {stock['name']} ({stock['symbol']}): {stock['quantity']}주\n"
            
            embeds[0]["fields"].append(stock_field)
        
        return {
            "content": None,
            "embeds": embeds
        }
    
    async def send_discord_notification(self, message: Dict):
        """디스코드 웹훅으로 메시지 전송"""
        if not self.webhook_url:
            log_message("디스코드 웹훅 URL이 설정되지 않았습니다.")
            return
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=message)
                if response.status_code != 204:
                    log_message(f"디스코드 알림 전송 실패: {response.text}")
        except Exception as e:
            log_message(f"디스코드 알림 전송 오류: {str(e)}")
    
    async def report_assets(self):
        """자산 현황 리포트"""
        try:
            crypto_assets = await self.get_crypto_assets()
            stock_assets = await self.get_stock_assets()
            
            if crypto_assets or stock_assets:
                message = self.format_asset_message(crypto_assets, stock_assets)
                await self.send_discord_notification(message)
                log_message("자산 현황 리포트 전송 완료")
            else:
                log_message("조회된 자산이 없습니다.")
                
        except Exception as e:
            log_message(f"자산 리포트 오류: {traceback.format_exc()}")


# 정기 실행을 위한 스케줄러
async def run_periodic_asset_report(interval_hours: int = 6):
    """정기적으로 자산 리포트 실행"""
    monitor = AssetMonitor()
    
    while True:
        await monitor.report_assets()
        await asyncio.sleep(interval_hours * 3600)  # 시간을 초로 변환


# 단독 실행 테스트
if __name__ == "__main__":
    monitor = AssetMonitor()
    asyncio.run(monitor.report_assets())
