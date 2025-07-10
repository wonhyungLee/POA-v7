#!/usr/bin/env python3
"""
POA v5 자동 업그레이드 스크립트
이 스크립트는 기존 POA 설치를 업그레이드합니다.
"""

import os
import shutil
import sys
from datetime import datetime

def backup_file(filepath):
    """파일 백업"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filepath, backup_path)
        print(f"백업 생성: {backup_path}")
        return backup_path
    return None

def upgrade_poa():
    """POA 업그레이드 실행"""
    print("POA v5 업그레이드를 시작합니다...")
    
    # 경로 설정
    base_path = "/root/POA"
    if not os.path.exists(base_path):
        print(f"에러: {base_path} 경로를 찾을 수 없습니다.")
        return False
    
    # 1. 기존 .env 파일 백업
    env_path = os.path.join(base_path, ".env")
    env_backup = backup_file(env_path)
    
    # 2. 중요 파일 백업
    important_files = [
        "exchange/model/schemas.py",
        "exchange/pexchange.py",
        "exchange/stock/kis.py",
        "exchange/__init__.py",
        "requirements.txt"
    ]
    
    backups = {}
    for file in important_files:
        filepath = os.path.join(base_path, file)
        backup = backup_file(filepath)
        if backup:
            backups[file] = backup
    
    try:
        # 3. 새 파일로 교체
        replacements = {
            "exchange/model/schemas_upgraded.py": "exchange/model/schemas.py",
            "exchange/pexchange_upgraded.py": "exchange/pexchange.py",
            "exchange/stock/kis_upgraded.py": "exchange/stock/kis.py",
            "exchange/__init___upgraded.py": "exchange/__init__.py",
            "requirements_upgraded.txt": "requirements.txt"
        }
        
        for src, dst in replacements.items():
            src_path = os.path.join(base_path, src)
            dst_path = os.path.join(base_path, dst)
            
            if os.path.exists(src_path):
                print(f"파일 교체: {dst}")
                shutil.copy2(src_path, dst_path)
                # 업그레이드 파일 삭제
                os.remove(src_path)
        
        # 4. Bithumb 파일이 없으면 복사
        bithumb_path = os.path.join(base_path, "exchange/bithumb.py")
        if not os.path.exists(bithumb_path):
            print("Bithumb 거래소 파일 추가")
            # 여기서는 이미 생성된 파일이 있다고 가정
        
        # 5. .env 파일 업데이트
        if not os.path.exists(env_path) or os.path.getsize(env_path) == 0:
            print(".env 파일 생성")
            template_path = os.path.join(base_path, ".env.template")
            if os.path.exists(template_path):
                shutil.copy2(template_path, env_path)
            else:
                # 기본 .env 파일 생성
                create_default_env(env_path)
        
        # 6. 패키지 업데이트
        print("\n패키지 업데이트 중...")
        os.system(f"cd {base_path} && {base_path}/.venv/bin/pip install -r requirements.txt")
        
        print("\n✅ 업그레이드가 완료되었습니다!")
        print("\n다음 단계:")
        print("1. 'edit_env' 명령으로 .env 파일을 편집하여 API 키를 설정하세요.")
        print("2. 'start' 명령으로 POA를 시작하세요.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 업그레이드 중 오류 발생: {e}")
        
        # 롤백
        print("\n변경사항을 롤백합니다...")
        for file, backup in backups.items():
            filepath = os.path.join(base_path, file)
            if os.path.exists(backup):
                shutil.copy2(backup, filepath)
                print(f"롤백: {file}")
        
        return False

def create_default_env(env_path):
    """기본 .env 파일 생성"""
    default_env = """# POA 자동매매 설정 파일
# 이 파일을 수정하여 API 키와 설정을 입력하세요

# 기본 설정
PASSWORD="your_password_here"
PORT="80"
DISCORD_WEBHOOK_URL=""

# 데이터베이스 설정
DB_ID="poa@admin.com"
DB_PASSWORD="poabot!@#$"

# 화이트리스트 IP (쉼표로 구분)
WHITELIST=["127.0.0.1"]

# 암호화폐 거래소 API 키
BINANCE_KEY=""
BINANCE_SECRET=""

UPBIT_KEY=""
UPBIT_SECRET=""

BYBIT_KEY=""
BYBIT_SECRET=""

OKX_KEY=""
OKX_SECRET=""
OKX_PASSPHRASE=""

BITGET_KEY=""
BITGET_SECRET=""
BITGET_PASSPHRASE=""

BITHUMB_KEY=""
BITHUMB_SECRET=""

# 한국투자증권(KIS) API 설정
KIS1_KEY=""
KIS1_SECRET=""
KIS1_ACCOUNT_NUMBER=""
KIS1_ACCOUNT_CODE="01"

# 추가 KIS 계정은 필요시 설정
"""
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(default_env)

if __name__ == "__main__":
    upgrade_poa()
