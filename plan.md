# 철물점 POS 시스템 - 개발 계획 (Plan)

## 아키텍처

```
[브라우저] <--HTTP--> [Flask 서버 (pos.py)] <--SQL--> [SQLite DB (pos_data.db)]
                           │
                    ┌──────┼──────┐
                    │      │      │
              config.py  database.py  models.py
```

## 데이터베이스 테이블
- `categories` - 상품 카테고리
- `products` - 상품 정보 (바코드, 가격, 단위, 재고, 도매가)
- `sales` - 판매 거래 헤더
- `sale_items` - 판매 상세 항목
- `daily_summary` - 일일 마감 집계

## 구현 단계

### Phase 1: Foundation
- [x] 프로젝트 구조 생성
- [x] 문서 파일 작성 (spec/plan/tasks/progress/finding)
- [ ] config.py - 설정 상수
- [ ] database.py - DB 스키마 및 연결
- [ ] models.py - 데이터 액세스 함수
- [ ] requirements.txt + pip install

### Phase 2: 기본 UI
- [ ] base.html - 공통 레이아웃 (Bootstrap 5)
- [ ] pos.css - POS 전용 스타일
- [ ] index.html - 대시보드

### Phase 3: 상품 관리
- [ ] 상품 목록 페이지
- [ ] 상품 등록/수정 폼
- [ ] 상품 API (CRUD)
- [ ] 샘플 데이터 스크립트

### Phase 4: 체크아웃 (핵심)
- [ ] checkout.html - 판매 화면
- [ ] pos_checkout.js - 장바구니 로직
- [ ] 상품 검색 API
- [ ] 결제 처리 API
- [ ] 바코드 스캐너 지원
- [ ] 키보드 단축키

### Phase 5: 통계 및 이력
- [ ] 판매 이력 페이지
- [ ] 영수증 페이지
- [ ] 통계 페이지 + Chart.js
- [ ] 통계 API

### Phase 6: 마무리
- [ ] 대시보드 완성
- [ ] 설정 페이지
- [ ] DB 백업 기능
- [ ] 전체 테스트

## 실행 방법
```bash
pip install flask
python pos.py
# 브라우저에서 http://localhost:5000 접속
```
