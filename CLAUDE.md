# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요
철물점 전용 웹 기반 POS(Point of Sale) 시스템. Flask + SQLite + Bootstrap 5로 구축.

## 실행 방법
```bash
pip install flask
python pos.py
# http://localhost:5000 접속
```

샘플 데이터 등록: `python setup_sample_data.py`

## 아키텍처
```
pos.py          ← Flask 앱 + 모든 라우트 (페이지 + API)
config.py       ← 설정 상수, 단위 유형, 기본 카테고리
database.py     ← SQLite 스키마 정의, get_db(), init_db(), backup_db()
models.py       ← 모든 데이터 액세스 함수 (ORM 없이 순수 SQL)
```

- **DB**: SQLite (`pos_data.db`), 테이블: categories, products, sales, sale_items, daily_summary
- **Frontend**: Jinja2 템플릿 + Bootstrap 5 (로컬 번들) + Chart.js
- **오프라인 동작**: 모든 정적 파일이 `static/`에 포함, CDN 의존 없음

## 핵심 패턴
- DB 연결은 함수마다 `get_db()` 호출 후 `finally: db.close()` (ORM 없음)
- 상품 삭제는 소프트 삭제 (`is_active = 0`)
- `sale_items`에 상품명/단가 스냅샷 저장 (비정규화)
- 수량은 REAL 타입 (미터/kg 소수점 지원)
- 도매가: `bulk_threshold` + `bulk_price` 두 필드로 처리

## 주요 라우트
- `/` 대시보드, `/checkout` 판매화면, `/products` 상품관리
- `/sales` 판매이력, `/statistics` 매출통계
- API: `/api/products/search`, `/api/checkout`, `/api/stats/*`

## 단위 유형 (`config.py UNIT_TYPES`)
piece(개), box(박스), can(통), bag(포), meter(m), kg, roll(롤), sheet(장), set(세트)

## UI 언어
모든 UI 텍스트는 한국어(Korean)
