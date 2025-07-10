# POA v5 업그레이드 요약

## 완료된 작업

### 1. 보안 개선
✅ 모든 API 키와 민감한 정보를 .env 파일로 분리
✅ cloud-init에서 하드코딩된 API 키 제거
✅ .env.template 파일 제공으로 쉬운 설정 가능

### 2. Bithumb 거래소 지원 추가
✅ `exchange/bithumb.py` 파일 생성
✅ Bithumb API 인증 및 거래 기능 구현
✅ KRW 마켓 시장가/지정가 주문 지원

### 3. KIS(한국투자증권) 확장
✅ 모의투자 제거, 실전투자만 지원
✅ KIS 1-50번 계정 지원 추가
✅ `schemas.py`에 KIS 1-50 설정 추가
✅ `pexchange.py`에서 다중 KIS 계정 관리

### 4. 생성된 파일 목록
- `.env.template` - 환경변수 템플릿
- `exchange/bithumb.py` - Bithumb 거래소 지원
- `exchange/model/schemas_upgraded.py` - 업그레이드된 스키마
- `exchange/pexchange_upgraded.py` - 업그레이드된 거래소 관리
- `exchange/stock/kis_upgraded.py` - 업그레이드된 KIS
- `exchange/__init___upgraded.py` - 업그레이드된 초기화 파일
- `requirements_upgraded.txt` - 업데이트된 패키지 목록
- `cloud-init-upgraded.yaml` - 업그레이드된 클라우드 초기화 스크립트
- `upgrade_poa.py` - 자동 업그레이드 스크립트
- `UPGRADE_GUIDE.md` - 업그레이드 가이드
- `WEBHOOK_SAMPLES.md` - 웹훅 요청 샘플
- `upgrade_windows.bat` - Windows 테스트용 배치 파일

## 적용 방법

### Oracle Cloud (Ubuntu) 환경
1. SSH로 서버 접속
2. 업그레이드 스크립트 실행:
   ```bash
   cd /root/POA
   python3 upgrade_poa.py
   ```

### Windows 테스트 환경
1. `upgrade_windows.bat` 실행
2. `.env.template`을 `.env`로 복사 후 편집
3. Python 가상환경에서 패키지 설치:
   ```cmd
   pip install -r requirements.txt
   ```

## 주요 변경사항

### API 변경
- Bithumb 거래소 추가로 `EXCHANGE_LITERAL`에 "BITHUMB" 추가
- `CRYPTO_EXCHANGES` 튜플에 "BITHUMB" 추가
- `COST_BASED_ORDER_EXCHANGES`에 "BITHUMB" 추가

### 설정 변경
- Settings 클래스에 BITHUMB_KEY, BITHUMB_SECRET 추가
- KIS 1-50번 계정 설정 추가 (각각 KEY, SECRET, ACCOUNT_NUMBER, ACCOUNT_CODE)
- 모의투자 관련 코드 제거

### 기능 개선
- `get_bot()` 함수에서 KIS 1-50번 자동 선택
- Bithumb API 완전 통합
- 에러 처리 및 로깅 개선

## 테스트 체크리스트

- [ ] .env 파일 생성 및 API 키 설정
- [ ] Binance 현물/선물 주문 테스트
- [ ] Upbit 현물 주문 테스트
- [ ] Bithumb 현물 주문 테스트 (신규)
- [ ] KIS 1번 계정 주문 테스트
- [ ] KIS 25번 계정 주문 테스트
- [ ] Discord 웹훅 알림 테스트
- [ ] TradingView 웹훅 연동 테스트

## 주의사항

1. **백업**: 업그레이드 전 반드시 기존 파일 백업
2. **API 키**: .env 파일에 정확한 API 키 입력 필요
3. **테스트**: 실제 자금 사용 전 충분한 테스트 필요
4. **보안**: .env 파일은 절대 공개 저장소에 업로드 금지

## 문제 발생 시

1. 백업 파일로 롤백
2. 로그 확인: `pm2 logs`
3. Discord 또는 GitHub Issues로 문의

---

업그레이드가 성공적으로 완료되었습니다! 🎉
