#!/usr/bin/env python
"""
POA Bot 환경 설정 테스트 스크립트
서버 시작 전에 환경 설정이 올바른지 확인합니다.
"""

import os
import sys

def check_env():
    print("🔍 POA Bot 환경 설정 확인")
    print("=" * 50)
    
    # .env 파일 확인
    if not os.path.exists(".env"):
        print("❌ .env 파일이 없습니다!")
        print("   해결: cp .env.template .env")
        return False
    else:
        print("✅ .env 파일 존재")
    
    # .env 파일 읽기
    try:
        with open(".env", "r", encoding="utf-8") as f:
            env_content = f.read()
            
        # PASSWORD 확인
        if "PASSWORD=" not in env_content:
            print("❌ PASSWORD 설정이 없습니다!")
            return False
        
        # PASSWORD 값 확인
        for line in env_content.split("\n"):
            if line.startswith("PASSWORD="):
                password_value = line.split("=", 1)[1].strip()
                if not password_value or password_value == "your_password_here":
                    print("❌ PASSWORD가 기본값입니다. 실제 비밀번호를 설정하세요!")
                    return False
                else:
                    print(f"✅ PASSWORD 설정됨 (길이: {len(password_value)})")
                break
        
        # 설정된 거래소 확인
        print("\n📊 설정된 거래소:")
        exchanges = ["UPBIT", "BINANCE", "BYBIT", "BITGET", "OKX"]
        configured = []
        
        for exchange in exchanges:
            if f"{exchange}_KEY=" in env_content:
                for line in env_content.split("\n"):
                    if line.startswith(f"{exchange}_KEY="):
                        key_value = line.split("=", 1)[1].strip()
                        if key_value:
                            configured.append(exchange)
                            print(f"   ✅ {exchange}")
                        break
        
        if not configured:
            print("   ⚠️  거래소 API가 설정되지 않았습니다")
        
        # KIS 계좌 확인
        print("\n📈 KIS 계좌:")
        for i in range(1, 51):
            if f"KIS{i}_KEY=" in env_content:
                for line in env_content.split("\n"):
                    if line.startswith(f"KIS{i}_KEY="):
                        key_value = line.split("=", 1)[1].strip()
                        if key_value:
                            print(f"   ✅ KIS{i}")
                        break
        
        # 디스코드 웹훅 확인
        print("\n🔔 알림 설정:")
        if "DISCORD_WEBHOOK_URL=" in env_content:
            for line in env_content.split("\n"):
                if line.startswith("DISCORD_WEBHOOK_URL="):
                    webhook_value = line.split("=", 1)[1].strip()
                    if webhook_value and webhook_value.startswith("https://discord.com"):
                        print("   ✅ 디스코드 웹훅 설정됨")
                    break
        else:
            print("   ⚠️  디스코드 웹훅 미설정")
        
        print("\n" + "=" * 50)
        print("✅ 환경 설정 확인 완료!")
        return True
        
    except Exception as e:
        print(f"❌ .env 파일 읽기 오류: {e}")
        return False

def test_import():
    print("\n📦 모듈 임포트 테스트")
    print("=" * 50)
    
    try:
        print("설정 모듈 로드 중...")
        from exchange.utility import settings
        print("✅ 설정 로드 성공")
        print(f"   포트: {settings.PORT or 8000}")
        
        print("\n메인 앱 로드 중...")
        from main import app
        print("✅ 앱 로드 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 모듈 로드 실패: {e}")
        print("\n필요한 패키지가 설치되지 않았을 수 있습니다.")
        print("해결: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    print("\n🚀 POA Bot 환경 테스트\n")
    
    env_ok = check_env()
    
    if env_ok:
        import_ok = test_import()
        
        if import_ok:
            print("\n✅ 모든 테스트 통과! 서버를 시작할 수 있습니다.")
            print("   실행: python run.py")
        else:
            print("\n❌ 모듈 로드 문제가 있습니다.")
            sys.exit(1)
    else:
        print("\n❌ 환경 설정을 먼저 완료하세요.")
        sys.exit(1)
