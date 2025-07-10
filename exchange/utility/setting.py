from exchange.model import Settings
from functools import lru_cache
import sys


@lru_cache()
def get_settings():
    try:
        return Settings()
    except Exception as e:
        print(f"설정 로드 실패: {str(e)}", file=sys.stderr)
        print("다음 사항을 확인하세요:", file=sys.stderr)
        print("1. .env 파일이 존재하는지", file=sys.stderr)
        print("2. PASSWORD 필드가 설정되어 있는지", file=sys.stderr)
        raise


settings = get_settings()
