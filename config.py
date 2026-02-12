"""철물점 POS 시스템 설정"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    STORE_NAME = '대왕철물'
    DB_PATH = os.path.join(BASE_DIR, 'pos_data.db')
    BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
    SECRET_KEY = 'pos-system-secret-key-change-in-production'
    TAX_RATE = 0.0  # 부가세율 (0이면 세금 미적용)
    CURRENCY = '₩'
    ITEMS_PER_PAGE = 50

# 단위 유형 정의
UNIT_TYPES = {
    'piece': {'label': '개', 'decimal': False, 'step': 1},
    'box':   {'label': '박스', 'decimal': False, 'step': 1},
    'can':   {'label': '통', 'decimal': False, 'step': 1},
    'bag':   {'label': '포', 'decimal': False, 'step': 1},
    'meter': {'label': 'm', 'decimal': True, 'step': 0.1},
    'kg':    {'label': 'kg', 'decimal': True, 'step': 0.1},
    'roll':  {'label': '롤', 'decimal': False, 'step': 1},
    'sheet': {'label': '장', 'decimal': False, 'step': 1},
    'set':   {'label': '세트', 'decimal': False, 'step': 1},
}

# 기본 카테고리
DEFAULT_CATEGORIES = [
    '나사/볼트/너트',
    '파이프/피팅',
    '전선/전기자재',
    '페인트/접착제',
    '시멘트/모래',
    '수공구',
    '전동공구',
    '배관자재',
    '철물/경첩',
    '안전용품',
    '기타',
]
