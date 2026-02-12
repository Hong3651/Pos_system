# 철물점 POS 시스템 - 작업 목록 (Tasks)

## 진행 상태 범례
- [ ] 미시작
- [~] 진행 중
- [x] 완료

---

## Task 1: 프로젝트 문서 작성
- [x] spec.md 작성
- [x] plan.md 작성
- [x] tasks.md 작성
- [x] progress.md 작성
- [x] finding.md 작성

## Task 2: Foundation 구축
- [x] config.py 작성
- [x] database.py 작성 (스키마 정의)
- [x] models.py 작성 (CRUD 함수)
- [x] requirements.txt 작성
- [x] Flask 설치 (pip install)

## Task 3: 정적 파일 및 기본 템플릿
- [x] Bootstrap 5 CSS/JS 다운로드 (오프라인용)
- [x] Chart.js 다운로드 (오프라인용)
- [x] pos.css 작성 (POS 전용 스타일)
- [x] base.html 작성 (공통 레이아웃)
- [x] index.html 작성 (대시보드)

## Task 4: 상품 관리 기능
- [x] products.html (상품 목록)
- [x] product_form.html (등록/수정 폼)
- [x] pos.py에 상품 라우트 추가
- [x] pos.py에 상품 API 추가
- [x] setup_sample_data.py (샘플 데이터 50개)

## Task 5: 체크아웃(판매/결제) 기능
- [x] checkout.html (판매 화면 - 2단 레이아웃)
- [x] 장바구니 JS 로직 (checkout.html 내장)
- [x] 상품 검색 API (/api/products/search)
- [x] 카테고리별 상품 API (/api/products/by-category)
- [x] 결제 처리 API (/api/checkout)
- [x] 바코드 스캐너 입력 처리
- [x] 키보드 단축키 (F1/F2/F4/Esc)
- [x] 결제 모달 (현금/카드/혼합)
- [x] 빠른 금액 버튼 + 거스름돈 자동 계산
- [x] 도매가 자동 적용
- [x] 결제 완료 모달 + 영수증 인쇄 연동

## Task 6: 매출 통계 및 판매 이력
- [x] sales_history.html (판매 이력 + 날짜 필터)
- [x] sale_detail.html (거래 상세)
- [x] receipt.html (영수증 인쇄 - 80mm 열전사)
- [x] statistics.html (매출 통계)
- [x] Chart.js 차트 (일별/월별/인기상품/카테고리/결제비율)
- [x] 통계 API (/api/stats/today, daily, monthly, top-products, categories)
- [x] 환불 기능 (/api/sales/<id>/refund)

## Task 7: 마무리
- [x] 대시보드 데이터 연동 (오늘 매출 + 재고 부족)
- [x] DB 백업 API (/api/backup)
- [x] 전체 플로우 테스트 (모든 페이지 200 OK)
- [x] CLAUDE.md 작성
- [ ] 설정 페이지 (향후 구현 예정)
