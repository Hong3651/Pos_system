# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# 절대 규칙
모든 의사결정은 사용자인 주인님한테 물어본다

## 프로젝트 개요
SaaS 멀티테넌트 POS 시스템. 기술 스택과 요구사항은 spec.md, 구현 계획은 plan.md 참조.

## 핵심 규칙 (코드 작성 시 반드시 준수)

### 멀티테넌트 데이터 격리
- Row-Level 격리: 모든 테이블에 `store_id` FK
- 모든 쿼리에 store 필터 필수
- API에서 사용자의 가게 소속 여부 검증

### 금액 처리
- DB: DecimalField (정수, 원 단위). **float 사용 금지.**
- 프론트: 천 단위 콤마 + ₩ 기호
- 수량: DecimalField (소수점 허용 — m, kg, L 등)

### VAT
- 소비자가(부가세 포함) 기준 입력
- 공급가 = 합계 ÷ 1.1, 부가세 = 합계 - 공급가
- sale_items에 supply_amount, vat_amount 저장

### 인증 플로우
- **회원가입**: 이름 + 아이디 + 비밀번호 + 전화번호 SMS 인증 → POST /api/auth/register
- **로그인**: 아이디 + 비밀번호 → POST /api/auth/login → JWT 발급
- 전화번호 인증은 가입 시 1회만 (본인 확인용)
- **로그인 보안**: 5회 연속 실패 시 30분 잠금

### 권한 체계
- **사장(owner)**: 모든 기능 접근
- **직원(staff)**: 사장이 설정한 권한만 (판매, 상품관리, 통계, 환불)
- DRF Permission 클래스로 구현

### 도매가 처리
- bulk_threshold 이상 구매 시 bulk_price 적용
- **3곳 동기화**: 백엔드 판매 API, 프론트 장바구니 계산, 영수증 표시

### 소프트 삭제
- 상품: is_active=False (실제 삭제 아님)
- 모든 상품 조회에서 is_active=True 필터

### 이중결제 방지
- 모든 판매에 transaction_id (UUID) 생성
- 결제 상태 추적: pending → approved / failed
- 동일 transaction_id 중복 요청 차단

### 환불
- 전체 환불 + 부분 환불 (항목 선택) 지원
- 환불 시 해당 상품 재고 복원
- 카드 결제 건: VAN 승인 취소 연동

### 활동 로그
- 환불, 가격 변경, 권한 변경, 삭제, 일마감 등 주요 활동 자동 기록
- ActivityLog 모델에 저장

### 테스트
- 매 Phase 완료 시 해당 기능 테스트 작성
- 금액/VAT/도매가/재고/환불 로직은 반드시 테스트 포함

## UI 언어
모든 UI 텍스트는 한국어(Korean). 코드 주석도 한국어 권장.

## 현재 상태
v3.0 SaaS 전환 작업 중. 기존 코드 삭제 완료, 문서 4개만 남은 상태 (Phase 1 시작 전).
