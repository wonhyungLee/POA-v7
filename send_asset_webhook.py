#!/usr/bin/env python3
import sys
import os
import httpx
from datetime import datetime

# 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from exchange.stock.kis_improved import ImprovedKoreaInvestment, AssetInfo
from exchange.utility import settings

def format_discord_message(balance_data: dict, kis_number: int) -> dict:
    """디스코드 웹훅에 보낼 메시지 포맷 생성 (공식 문서 기반 최종 수정)"""
    
    domestic_data = balance_data.get("domestic_balance", {})
    overseas_data = balance_data.get("overseas_balance", {})
    exchange_rate = balance_data.get("exchange_rate")
    is_rate_fallback = balance_data.get("is_rate_fallback", False)

    dom_total_krw = domestic_data.get("total_krw", 0)
    dom_stocks = domestic_data.get("stocks", [])
    
    ovs_total_usd = overseas_data.get("total_usd", 0)
    ovs_stocks = overseas_data.get("stocks", [])
    
    # 총 자산 계산
    ovs_total_krw = 0
    if exchange_rate and ovs_total_usd > 0:
        ovs_total_krw = ovs_total_usd * exchange_rate
    
    grand_total_krw = dom_total_krw + ovs_total_krw
    
    # 총 평가금액에 (추정) 표시 추가
    total_label = "💰 총 평가 금액 (KRW)"
    if is_rate_fallback:
        total_label += " (추정)"

    embed = {
        "title": f"📈 KIS-{kis_number} 자산 현황",
        "description": f"조회 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "color": 0x4A90E2,
        "fields": [
            # --- 총 평가 금액 ---
            {
                "name": total_label,
                "value": f"**{grand_total_krw:,.0f} 원**",
                "inline": False
            },
            # --- 국내 주식 ---
            {
                "name": "🇰🇷 국내 주식 (KRW)",
                "value": f"**{dom_total_krw:,.0f} 원**",
                "inline": False
            }
        ],
        "footer": {
            "text": "Powered by POA-v7 Improved KIS"
        }
    }
    
    if not dom_stocks:
        embed["fields"].append({"name": " ", "value": "보유 종목 없음", "inline": True})
    else:
        # 국내 주식 표시 (기존과 동일)
        for stock in sorted(dom_stocks, key=lambda x: x.eval_amount, reverse=True)[:5]:
            embed["fields"].append({
                "name": f"ㄴ {stock.name} ({stock.symbol})",
                "value": f"{stock.eval_amount:,.0f} 원 ({stock.quantity}주)",
                "inline": True
            })

    # --- 해외 주식 ---
    ovs_value_str = f"**${ovs_total_usd:,.2f}**"
    if ovs_total_krw > 0:
        ovs_value_str += f" (약 {ovs_total_krw:,.0f} 원)"

    embed["fields"].append({
        "name": f"🇺🇸 해외 주식 (USD)",
        "value": ovs_value_str,
        "inline": False
    })

    if not ovs_stocks:
        embed["fields"].append({"name": " ", "value": "보유 종목 없음", "inline": True})
    else:
        for stock in sorted(ovs_stocks, key=lambda x: x.eval_amount_usd, reverse=True)[:5]:
            stock_value_str = f"${stock.eval_amount_usd:,.2f} ({stock.quantity}주)"
            if exchange_rate:
                stock_krw_value = stock.eval_amount_usd * exchange_rate
                stock_value_str += f"\n(약 {stock_krw_value:,.0f} 원)"

            embed["fields"].append({
                "name": f"ㄴ {stock.name} ({stock.symbol})",
                "value": stock_value_str,
                "inline": True
            })
            
    # 환율 정보 표시
    if exchange_rate:
        rate_label = "환율"
        if is_rate_fallback:
            rate_label += "(추정)"
        embed["footer"]["text"] += f" | {rate_label}: {exchange_rate:,.2f} KRW/USD"
            
    return {"embeds": [embed]}


def send_webhook(webhook_url: str, message: dict):
    """웹훅 전송"""
    try:
        with httpx.Client() as client:
            response = client.post(webhook_url, json=message)
            response.raise_for_status()
        print("✅ 디스코드 웹훅 전송 성공")
    except Exception as e:
        print(f"❌ 디스코드 웹훅 전송 실패: {e}")

def main():
    """메인 실행 함수"""
    
    kis_number = 1 # 요청에 따라 1로 변경
    
    kis_key = getattr(settings, f'KIS{kis_number}_KEY', None)
    kis_secret = getattr(settings, f'KIS{kis_number}_SECRET', None)
    kis_account = getattr(settings, f'KIS{kis_number}_ACCOUNT_NUMBER', None)
    kis_code = getattr(settings, f'KIS{kis_number}_ACCOUNT_CODE', '01')
    webhook_url = getattr(settings, 'DISCORD_WEBHOOK_URL', None)
    
    if not all([kis_key, kis_secret, kis_account, webhook_url]):
        print("❌ KIS 설정 또는 디스코드 웹훅 URL이 없습니다.")
        return
        
    print(f"⏳ KIS-{kis_number} 자산 정보 조회 중...")
    kis = ImprovedKoreaInvestment(
        key=kis_key,
        secret=kis_secret,
        account_number=kis_account,
        account_code=kis_code,
        kis_number=kis_number
    )
    
    balance_data = kis.get_balance()
    kis.close()
    
    if balance_data:
        print("✅ 자산 정보 조회 성공")
        message = format_discord_message(balance_data, kis_number)
        send_webhook(webhook_url, message)
    else:
        print("❌ 자산 정보 조회 실패")

if __name__ == "__main__":
    main()
