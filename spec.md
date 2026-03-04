# POS 시스템 - 요구사항 명세서 (Specification)

## 1. 프로젝트 개요
- **프로젝트명**: POS SaaS 시스템
- **목적**: 다양한 업종의 소매점에서 사용 가능한 클라우드 기반 POS 서비스
- **서비스 형태**: SaaS (멀티테넌트)
- **대상 사용자**: 소규모 소매점 사장님 및 직원
- **플랫폼**: 웹 애플리케이션 (PC, 태블릿, 모바일 브라우저)

## 2. 기술 스택

| 구분 | 기술 |
|------|------|
| 백엔드 | Django 5 + Django REST Framework + PostgreSQL |
| 프론트엔드 | Next.js 14 (React) + TypeScript + Tailwind CSS |
| 인증 | JWT (access + refresh) + 아이디/비밀번호 + SMS 인증(가입 시) |
| 호스팅 | Railway/Render (백엔드), Vercel (프론트엔드) |
| 통신 | REST API (JSON) |
| 에러 모니터링 | Sentry (백엔드 + 프론트엔드) |
| CI/CD | GitHub Actions (자동 테스트 + 자동 배포) |

## 3. 핵심 기능 요구사항

### 3.1 회원가입 / 인증
- **회원가입**: 이름 + 아이디(직접 입력) + 비밀번호 + 전화번호 SMS 인증
- **로그인**: 아이디 + 비밀번호
- JWT 토큰 기반 인증 (access + refresh)
- 로그인 유지 (refresh token으로 자동 갱신)
- 전화번호 인증은 가입 시 1회만 (본인 확인용)
- **로그인 보안**: 5회 연속 실패 시 30분 계정 잠금 (자동 해제)

### 3.2 가게(Store) 관리
- **다점포 지원**: 1계정으로 여러 가게 운영 가능
- 가게 생성 시: 가게명 + 지점명 + 업종 선택 + 사업자등록번호(선택)
  - 가게명: "홍카페" (브랜드명)
  - 지점명: "강남점", "1호점" 등 (자유 입력)
  - 표시: "홍카페 강남점"
- 업종별 카테고리 프리셋 자동 생성 (10개 업종)
- 가게 간 전환 기능 (드롭다운 또는 대시보드)
- 가게별 독립된 데이터 (상품, 판매, 통계)

### 3.3 직원(Staff) 관리
- **역할 2단계**: 사장(owner), 직원(staff)
- 사장이 직원 계정 생성/삭제/권한 관리
- 직원도 아이디+비밀번호로 로그인 (사장이 계정 생성)
- **직원 권한 범위**:
  - 판매(체크아웃): 기본 허용
  - 상품 등록/수정: 사장이 허용/차단 설정
  - 매출 통계 조회: 사장이 허용/차단 설정
  - 환불 처리: 사장이 허용/차단 설정
  - 설정 변경: 사장만 가능
  - 직원 관리: 사장만 가능

### 3.4 판매/결제 (Checkout)
- 상품 검색 (이름, 바코드)
- USB 바코드 스캐너 지원
- 장바구니 관리 (추가, 수량 변경, 삭제)
- 도매가 자동 적용 (수량 기준)
- 결제 처리 (현금, 카드, 혼합)
- 거스름돈 자동 계산
- 키보드 단축키 지원
- **결제 완료 후**: 영수증 발행 / 거래명세서 발행 각각 선택 가능 (둘 다, 하나만, 안 함)
- **현금영수증**: 현금 결제 시 소비자 요청으로 발급 (전화번호 또는 카드번호 입력)
- **이중결제 방지**: 거래 고유번호(transaction_id)로 중복 요청 차단 + 결제 상태 추적(pending/approved/failed) + 타임아웃 처리

### 3.5 상품 관리
- 상품 등록/수정/삭제 (소프트 삭제)
- 카테고리 분류
- 단위 유형: 개, 잔, 인분, 병, 팩, 박스, 통, 포, m, kg, L, 롤, 장, 세트 (14종)
- 도매가 설정 (기준 수량 + 도매 단가)
- 재고 수량 관리
- 재고 부족 경고 (최소 재고 설정)
- 바코드 지원

### 3.6 매출 통계
- 일별/월별 매출 현황 (차트)
- 인기 상품 분석 (판매량/매출액 기준)
- 카테고리별 매출 비율
- 현금/카드 결제 비율
- 기간별 필터링
- **DailySummary 기반**: 일별 요약 테이블에서 조회 (성능 최적화)

### 3.7 판매 이력
- 날짜 범위 필터링
- 거래 상세 조회
- **과거 거래에서도 영수증/거래명세서 발행 가능** (이력에서 선택)
- **환불 처리**:
  - 전체 환불: 전체 금액 환불 + 재고 복원
  - **부분 환불**: 특정 상품만 선택하여 환불 + 해당 상품 재고 복원 + 금액 재계산
  - 카드 결제 건: VAN 승인 취소 연동
  - 이중 환불 방지

### 3.8 대시보드
- 오늘 매출 합계 / 거래 건수
- 현금/카드 비율
- 재고 부족 알림
- 가게 전환 (다점포)

### 3.9 거래처 관리
- 거래처 등록/수정/삭제
- 거래처 정보: 상호명, 사업자등록번호, 대표자명, 주소, 전화번호, 메모
- 거래처 검색 (상호명, 사업자번호)

### 3.10 거래명세서
- 판매 완료 직후 또는 판매 이력에서 언제든 발행 가능
- 발행 시 거래처 선택 (등록된 거래처 목록에서)
- 거래명세서 내용:
  - 공급자: 내 가게 정보 (상호, 사업자번호, 대표자, 주소, 전화번호)
  - 공급받는 자: 거래처 정보 (상호, 사업자번호)
  - 거래일자, 거래명세서 번호 (자동 채번)
  - 품목: 품명, 규격/단위, 수량, 단가, 공급가액, 부가세
  - 합계: 공급가액, 부가세, 총합계
  - 비고/메모
- 거래명세서 인쇄 (브라우저 인쇄)
- 거래명세서 이력 조회 (날짜/거래처 필터)

### 3.11 설정
- 가게 이름/지점명 변경
- 사업자등록번호, 대표자명, 주소, 전화번호 설정 (거래명세서용)
- 카테고리 추가/삭제
- 직원 관리
- 데이터 내보내기 (Excel/CSV)

### 3.12 현금영수증
- 현금 결제 시 소비자 요청으로 발급
- 입력 방식: 전화번호 또는 현금영수증 카드번호
- 국세청 현금영수증 API 연동 (승인번호 발급)
- 발급 내역 저장 (Sale에 연결)
- 발급 이력 조회

### 3.13 일마감 / 시재 관리
- **영업 시작**: 시재(준비 현금) 금액 입력
- **영업 중**: 현금/카드 매출 자동 집계
- **일마감**:
  - 실제 현금 금액 입력 (직접 세서 입력)
  - 시스템 계산 현금 vs 실제 현금 비교 → 과부족 표시
  - 카드 매출 합계 확인
  - 일마감 확정 → DailySummary에 저장
- 일마감 이력 조회

### 3.14 활동 로그 (감사 추적)
- 자동 기록 대상:
  - 환불 처리 (누가, 언제, 어떤 거래)
  - 상품 가격 변경 (이전 가격 → 새 가격)
  - 직원 권한 변경
  - 상품 삭제 (소프트 삭제)
  - 일마감 처리
  - 설정 변경
- 로그 조회: 날짜/직원/활동 유형 필터
- 사장(owner)만 조회 가능

## 4. 부가세(VAT) 처리
- 가격 입력 시 **부가세 포함가** 기준 (소비자가)
- 영수증/통계에서 **공급가 / 부가세 / 합계** 분리 표시
- 공급가 = 합계 ÷ 1.1 (10% VAT 기준)
- 부가세 = 합계 - 공급가
- 영수증에 사업자등록번호 표시 (설정된 경우)

## 5. 결제 수단
- **현금**: 받은 금액 입력 → 거스름돈 자동 계산
- **카드**: VAN사 카드 단말기 연동 (실제 결제 처리)
- **혼합**: 현금 + 카드 분할 결제
- **현금영수증**: 현금 결제 시 국세청 API 연동 발급

### 카드 단말기 연동
- **VAN사**: NICE정보통신 / KIS정보통신 / KSNET (설정에서 선택)
- **통신 흐름**: 웹 POS → 로컬 에이전트(localhost) → 카드 단말기 → VAN사 → 카드사
- **로컬 에이전트**: VAN사 제공 프로그램을 PC에 설치 필요
- **기능**:
  - 승인 요청 (결제 금액 전송 → 단말기 카드 투입/터치 대기 → 승인 결과 수신)
  - 승인 취소 (환불 시 — 전체/부분)
  - 승인번호, 카드사명, 카드번호(마스킹) 저장
- **이중결제 방지**:
  - 거래별 고유 transaction_id 생성
  - 결제 상태 추적: pending → approved / failed
  - 타임아웃 시 자동 승인 조회
- **오프라인 대응**: 에이전트 미연결 시 금액 기록만 (수동 모드)

## 6. 업종 프리셋 (10종)
| 업종 | 카테고리 예시 |
|------|--------------|
| 일반 소매점 | 식품, 음료, 생활용품, 문구/사무, 의류/잡화, 전자기기 |
| 카페/음료 | 커피(HOT), 커피(ICE), 음료, 스무디, 디저트, 티/차 |
| 음식점 | 메인 메뉴, 사이드 메뉴, 음료, 주류, 세트 메뉴 |
| 편의점/마트 | 식품, 음료, 과자/빵, 유제품, 냉동식품, 생활용품 |
| 베이커리/제과 | 빵, 케이크, 쿠키/과자, 음료, 선물세트 |
| 철물점 | 나사/볼트, 파이프, 전선, 페인트, 수공구, 전동공구 |
| 의류/패션 | 상의, 하의, 원피스, 아우터, 신발, 가방, 액세서리 |
| 약국/건강 | 일반의약품, 건강기능식품, 의료기기, 위생용품 |
| 문구/사무 | 필기구, 노트/종이, 사무용품, 학용품 |
| 직접 설정 | 사용자가 카테고리 수동 입력 |

## 7. 멀티테넌트 데이터 구조

### 핵심 모델
```
User (사용자)
├── username (아이디, 고유)
├── password (해싱 저장)
├── phone (전화번호, 고유)
├── name
├── failed_login_count (로그인 실패 횟수)
├── locked_until (잠금 해제 시각)
└── created_at

Store (가게)
├── owner → User (사장)
├── name (가게명: "홍카페")
├── branch_name (지점명: "강남점", "1호점" 등)
├── business_type (업종)
├── business_number (사업자등록번호, 선택)
├── representative (대표자명)
├── address, phone (거래명세서용)
├── van_provider (VAN사: nice/kis/ksnet, 선택)
├── van_terminal_id (단말기 ID)
└── created_at

StoreStaff (직원 매핑)
├── store → Store
├── user → User
├── role: owner | staff
├── permissions (JSON: checkout, products, stats, refund)
└── is_active

Category (카테고리)
├── store → Store
├── name
└── sort_order

Product (상품)
├── store → Store
├── barcode, name, category → Category
├── unit_type, price, cost_price
├── stock_quantity, min_stock
├── bulk_threshold, bulk_price
├── is_active (소프트 삭제)
└── memo

Client (거래처)
├── store → Store
├── company_name (상호명)
├── business_number (사업자등록번호)
├── representative (대표자명)
├── address, phone
└── memo

Sale (판매)
├── store → Store
├── staff → User (판매한 직원)
├── client → Client (거래처, 선택 — 거래명세서용)
├── transaction_id (거래 고유번호, UUID — 이중결제 방지)
├── status (pending / approved / failed)
├── total_amount, supply_amount, vat_amount
├── payment_method, cash_amount, card_amount, change_amount
├── card_approval_no (카드 승인번호)
├── card_company (카드사명)
├── card_number (카드번호, 마스킹: ****-****-****-1234)
├── cash_receipt_number (현금영수증 승인번호)
├── cash_receipt_type (소득공제 / 지출증빙)
├── is_refunded (전체 환불 여부)
├── refunded_amount (부분 환불 누적 금액)
└── memo

SaleItem (판매 항목)
├── sale → Sale
├── product → Product
├── product_name, unit_type (스냅샷)
├── quantity, unit_price, subtotal
├── supply_amount, vat_amount
├── is_bulk
├── refunded_quantity (부분 환불된 수량)
└── is_refunded (이 항목 전체 환불 여부)

Invoice (거래명세서)
├── sale → Sale
├── store → Store
├── client → Client (거래처)
├── invoice_number (자동 채번)
├── issued_date
└── memo

DailySummary (일별 매출 요약)
├── store → Store
├── date (날짜, store+date 유니크)
├── total_sales, total_refunds
├── cash_sales, card_sales
├── supply_amount, vat_amount
├── transaction_count
├── opening_cash (시재 — 영업 시작 현금)
├── expected_cash (시스템 계산 현금)
├── actual_cash (실제 현금 — 일마감 시 입력)
├── cash_difference (과부족)
├── is_closed (일마감 여부)
└── closed_by → User (마감 처리자)

ActivityLog (활동 로그)
├── store → Store
├── user → User (행위자)
├── action_type (refund / price_change / permission_change / product_delete / daily_close / setting_change)
├── target_type (Sale / Product / StoreStaff 등)
├── target_id
├── detail (JSON: 변경 전/후 데이터)
└── created_at
```

### 데이터 격리 원칙
- 모든 가게 데이터 쿼리에 `store_id` 필터 필수
- API에서 현재 사용자의 가게 소속 여부 검증
- 다른 가게 데이터 접근 불가

### DB 인덱스 전략
- Sale: `store_id` + `created_at` (판매 이력 조회)
- Sale: `transaction_id` (이중결제 방지, UNIQUE)
- Product: `store_id` + `name` (상품 검색)
- Product: `store_id` + `barcode` (바코드 검색)
- DailySummary: `store_id` + `date` (UNIQUE, 통계 조회)
- ActivityLog: `store_id` + `created_at` (로그 조회)
- SaleItem: `sale_id` (판매 상세)

## 8. API 구조 (주요 엔드포인트)

### 인증
- `POST /api/auth/register` — 회원가입 (이름, 아이디, 비밀번호, 전화번호, 인증코드)
- `POST /api/auth/send-code` — SMS 인증코드 발송 (가입 시)
- `POST /api/auth/login` — 로그인 (아이디 + 비밀번호 → JWT 발급)
- `POST /api/auth/refresh` — 토큰 갱신
- `POST /api/auth/logout` — 로그아웃

### 가게
- `POST /api/stores` — 가게 생성
- `GET /api/stores` — 내 가게 목록
- `PUT /api/stores/:id` — 가게 정보 수정
- `GET /api/stores/:id` — 가게 상세

### 직원
- `POST /api/stores/:id/staff` — 직원 추가 (전화번호로)
- `GET /api/stores/:id/staff` — 직원 목록
- `PUT /api/stores/:id/staff/:userId` — 권한 변경
- `DELETE /api/stores/:id/staff/:userId` — 직원 제거

### 카테고리
- `GET /api/stores/:id/categories` — 카테고리 목록
- `POST /api/stores/:id/categories` — 카테고리 추가
- `PUT /api/stores/:id/categories/:catId` — 카테고리 수정
- `DELETE /api/stores/:id/categories/:catId` — 카테고리 삭제

### 상품
- `GET /api/stores/:id/products` — 상품 목록 (필터/페이징)
- `GET /api/stores/:id/products/search?q=` — 상품 검색
- `POST /api/stores/:id/products` — 상품 등록
- `PUT /api/stores/:id/products/:prodId` — 상품 수정
- `DELETE /api/stores/:id/products/:prodId` — 상품 삭제 (소프트)
- `GET /api/stores/:id/products/low-stock` — 재고 부족 상품

### 판매
- `POST /api/stores/:id/sales` — 판매 처리 (체크아웃)
- `GET /api/stores/:id/sales` — 판매 이력 (필터/페이징)
- `GET /api/stores/:id/sales/:saleId` — 판매 상세
- `POST /api/stores/:id/sales/:saleId/refund` — 환불 (전체)
- `POST /api/stores/:id/sales/:saleId/partial-refund` — 부분 환불 (항목 선택)

### 현금영수증
- `POST /api/stores/:id/sales/:saleId/cash-receipt` — 현금영수증 발급
- `GET /api/stores/:id/cash-receipts` — 현금영수증 발급 이력

### 통계
- `GET /api/stores/:id/stats/today` — 오늘 요약
- `GET /api/stores/:id/stats/daily?year=&month=` — 일별 통계
- `GET /api/stores/:id/stats/monthly?year=` — 월별 통계
- `GET /api/stores/:id/stats/top-products` — 인기 상품
- `GET /api/stores/:id/stats/categories` — 카테고리별 매출

### 일마감
- `POST /api/stores/:id/daily-close/open` — 영업 시작 (시재 입력)
- `GET /api/stores/:id/daily-close/current` — 현재 영업 현황 (실시간 집계)
- `POST /api/stores/:id/daily-close/close` — 일마감 처리 (실제 현금 입력)
- `GET /api/stores/:id/daily-close/history` — 일마감 이력

### 거래처
- `GET /api/stores/:id/clients` — 거래처 목록 (검색)
- `POST /api/stores/:id/clients` — 거래처 등록
- `PUT /api/stores/:id/clients/:clientId` — 거래처 수정
- `DELETE /api/stores/:id/clients/:clientId` — 거래처 삭제

### 거래명세서
- `POST /api/stores/:id/invoices` — 거래명세서 발행 (sale_id + client_id)
- `GET /api/stores/:id/invoices` — 거래명세서 목록 (날짜/거래처 필터)
- `GET /api/stores/:id/invoices/:invoiceId` — 거래명세서 상세

### 활동 로그
- `GET /api/stores/:id/activity-logs` — 활동 로그 조회 (날짜/직원/유형 필터)

### 설정
- `GET /api/stores/:id/settings` — 가게 설정 조회
- `PUT /api/stores/:id/settings` — 가게 설정 변경

## 9. 보안 요구사항
- 비밀번호 정책:
  - 8자 이상
  - 숫자, 특수문자, 영문 중 2가지 이상 포함
  - 아이디와 동일 불가
  - 아이디와 3글자 이상 연속 겹침 불가
- 비밀번호 저장: Django 기본 해싱 (PBKDF2)
- **로그인 보안**: 5회 연속 실패 시 30분 계정 잠금 (자동 해제)
- SMS 인증코드: 6자리 숫자, 5분 유효, 5회 시도 제한 (가입 시에만)
- JWT: access token 30분, refresh token 7일
- 모든 API: 인증 필수 (토큰 검증)
- 가게 데이터: store_id + 소속 검증 (다른 가게 접근 차단)
- HTTPS 필수 (호스팅 환경에서 자동 적용)
- CORS 설정 (프론트엔드 도메인만 허용)
- **이중결제 방지**: transaction_id 유니크 제약 + 결제 상태 추적

## 10. 금액 처리 원칙
- DB에서 금액은 **정수** (원 단위, DECIMAL 또는 INTEGER)
- float 사용 금지 (부동소수점 오차 방지)
- 프론트엔드 표시 시 천 단위 콤마 + ₩ 기호
- 수량은 소수점 허용 (DECIMAL) — meter, kg, liter 등

## 11. 비기능 요구사항
- 응답 시간: API 평균 200ms 이하
- 동시 사용자: 초기 100명 이상
- 데이터 백업: 자동 (호스팅 환경 DB 백업 활용)
- 한국어 UI
- 반응형 디자인 (PC + 태블릿 + 모바일)
- **PWA 지원**: 오프라인 모드 (인터넷 끊겨도 판매 가능, 복구 시 서버 동기화)
- **에러 모니터링**: Sentry 연동 (백엔드 API 에러 + 프론트엔드 에러 자동 수집)
- **CI/CD**: GitHub Actions (push → 자동 테스트 → 통과 시 자동 배포)
- **테스트**: Phase별 단위/API 테스트 작성

## 12. 향후 확장 고려사항 (현재 미구현)
- 요금제/결제 시스템
- 바코드 라벨 출력
- 재고 입출고 이력
- Excel 일괄 상품 등록
- 알림 (재고 부족, 매출 리포트)
- 감열 프린터 연동 (ESC/POS)
- 할인/쿠폰 기능
