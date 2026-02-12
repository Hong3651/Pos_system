"""데이터베이스 초기화 및 연결 관리"""
import sqlite3
import shutil
import os
from datetime import datetime
from config import Config, DEFAULT_CATEGORIES


def get_db():
    """데이터베이스 연결을 반환한다."""
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """테이블이 없으면 생성하고 기본 카테고리를 삽입한다."""
    db = get_db()
    try:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS categories (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL UNIQUE,
                description TEXT DEFAULT '',
                created_at  TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS products (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode         TEXT UNIQUE,
                name            TEXT NOT NULL,
                category_id     INTEGER REFERENCES categories(id),
                unit_type       TEXT NOT NULL DEFAULT 'piece',
                price           REAL NOT NULL,
                cost_price      REAL DEFAULT 0,
                stock_quantity  REAL DEFAULT 0,
                min_stock       REAL DEFAULT 0,
                bulk_threshold  INTEGER DEFAULT NULL,
                bulk_price      REAL DEFAULT NULL,
                is_active       INTEGER DEFAULT 1,
                memo            TEXT DEFAULT '',
                created_at      TEXT DEFAULT (datetime('now','localtime')),
                updated_at      TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
            CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
            CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);

            CREATE TABLE IF NOT EXISTS sales (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_date       TEXT DEFAULT (datetime('now','localtime')),
                total_amount    REAL NOT NULL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                payment_method  TEXT NOT NULL DEFAULT 'cash',
                cash_amount     REAL DEFAULT 0,
                card_amount     REAL DEFAULT 0,
                change_amount   REAL DEFAULT 0,
                memo            TEXT DEFAULT '',
                is_refunded     INTEGER DEFAULT 0,
                created_at      TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);

            CREATE TABLE IF NOT EXISTS sale_items (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id     INTEGER NOT NULL REFERENCES sales(id),
                product_id  INTEGER NOT NULL REFERENCES products(id),
                product_name TEXT NOT NULL,
                unit_type   TEXT NOT NULL,
                quantity    REAL NOT NULL,
                unit_price  REAL NOT NULL,
                subtotal    REAL NOT NULL,
                is_bulk     INTEGER DEFAULT 0,
                created_at  TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id);
            CREATE INDEX IF NOT EXISTS idx_sale_items_product ON sale_items(product_id);

            CREATE TABLE IF NOT EXISTS daily_summary (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                summary_date      TEXT NOT NULL UNIQUE,
                total_sales       REAL DEFAULT 0,
                total_cash        REAL DEFAULT 0,
                total_card        REAL DEFAULT 0,
                total_refunds     REAL DEFAULT 0,
                transaction_count INTEGER DEFAULT 0,
                memo              TEXT DEFAULT '',
                created_at        TEXT DEFAULT (datetime('now','localtime'))
            );
        """)

        # 기본 카테고리 삽입
        for cat_name in DEFAULT_CATEGORIES:
            db.execute(
                "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                (cat_name,)
            )
        db.commit()
    finally:
        db.close()


def backup_db():
    """데이터베이스 파일을 backups 폴더에 복사한다."""
    if not os.path.exists(Config.DB_PATH):
        return None
    os.makedirs(Config.BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(Config.BACKUP_DIR, f'pos_data_{timestamp}.db')
    shutil.copy2(Config.DB_PATH, backup_path)
    return backup_path


def yearly_backup():
    """올해 연도 백업이 없으면 자동으로 생성한다. 서버 시작 시 호출."""
    if not os.path.exists(Config.DB_PATH):
        return None
    os.makedirs(Config.BACKUP_DIR, exist_ok=True)

    year = datetime.now().strftime('%Y')
    yearly_name = f'pos_data_yearly_{year}.db'
    yearly_path = os.path.join(Config.BACKUP_DIR, yearly_name)

    # 올해 백업이 이미 있으면 스킵
    if os.path.exists(yearly_path):
        return None

    # 작년 이하 연도 백업 확인 → 없으면 첫 해이므로 스킵
    import glob
    existing = glob.glob(os.path.join(Config.BACKUP_DIR, 'pos_data_yearly_*.db'))
    if not existing:
        # 첫 실행: 올해 기준점 백업 생성
        shutil.copy2(Config.DB_PATH, yearly_path)
        print(f"[백업] 첫 연간 백업 생성: {yearly_name}")
        return yearly_path

    # 새해가 되었으므로 자동 백업
    shutil.copy2(Config.DB_PATH, yearly_path)
    print(f"[백업] {year}년 연간 백업 생성: {yearly_name}")
    return yearly_path
