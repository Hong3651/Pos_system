"""데이터 액세스 함수 (CRUD)"""
from database import get_db
from datetime import datetime, date


# ── 카테고리 ──────────────────────────────────────────

def get_categories():
    db = get_db()
    try:
        rows = db.execute("SELECT * FROM categories ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


# ── 상품 ──────────────────────────────────────────────

def get_products(category_id=None, search=None, page=1, per_page=50, active_only=True):
    db = get_db()
    try:
        query = "SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON p.category_id = c.id"
        conditions = []
        params = []

        if active_only:
            conditions.append("p.is_active = 1")
        if category_id:
            conditions.append("p.category_id = ?")
            params.append(category_id)
        if search:
            conditions.append("(p.name LIKE ? OR p.barcode LIKE ?)")
            params.extend([f'%{search}%', f'%{search}%'])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY p.name"

        # 전체 개수
        count_query = query.replace("SELECT p.*, c.name as category_name", "SELECT COUNT(*)")
        total = db.execute(count_query, params).fetchone()[0]

        # 페이징
        query += " LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])

        rows = db.execute(query, params).fetchall()
        return [dict(r) for r in rows], total
    finally:
        db.close()


def get_product(product_id):
    db = get_db()
    try:
        row = db.execute(
            "SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE p.id = ?",
            (product_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        db.close()


def search_products(query, limit=20):
    """체크아웃 자동완성용 상품 검색"""
    db = get_db()
    try:
        if query.isdigit() and len(query) >= 8:
            rows = db.execute(
                "SELECT * FROM products WHERE barcode = ? AND is_active = 1",
                (query,)
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM products WHERE name LIKE ? AND is_active = 1 ORDER BY name LIMIT ?",
                (f'%{query}%', limit)
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def create_product(data):
    db = get_db()
    try:
        cursor = db.execute(
            """INSERT INTO products (barcode, name, category_id, unit_type, price, cost_price,
               stock_quantity, min_stock, bulk_threshold, bulk_price, memo)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data.get('barcode') or None,
                data['name'],
                data.get('category_id'),
                data.get('unit_type', 'piece'),
                data['price'],
                data.get('cost_price', 0),
                data.get('stock_quantity', 0),
                data.get('min_stock', 0),
                data.get('bulk_threshold') or None,
                data.get('bulk_price') or None,
                data.get('memo', ''),
            )
        )
        db.commit()
        return cursor.lastrowid
    finally:
        db.close()


def update_product(product_id, data):
    db = get_db()
    try:
        db.execute(
            """UPDATE products SET barcode=?, name=?, category_id=?, unit_type=?, price=?,
               cost_price=?, stock_quantity=?, min_stock=?, bulk_threshold=?, bulk_price=?,
               memo=?, updated_at=datetime('now','localtime')
               WHERE id=?""",
            (
                data.get('barcode') or None,
                data['name'],
                data.get('category_id'),
                data.get('unit_type', 'piece'),
                data['price'],
                data.get('cost_price', 0),
                data.get('stock_quantity', 0),
                data.get('min_stock', 0),
                data.get('bulk_threshold') or None,
                data.get('bulk_price') or None,
                data.get('memo', ''),
                product_id,
            )
        )
        db.commit()
    finally:
        db.close()


def delete_product(product_id):
    """소프트 삭제"""
    db = get_db()
    try:
        db.execute("UPDATE products SET is_active = 0 WHERE id = ?", (product_id,))
        db.commit()
    finally:
        db.close()


# ── 판매 ──────────────────────────────────────────────

def create_sale(items, payment_method, cash_amount, card_amount, change_amount, memo=''):
    """판매 거래를 처리한다. 실패 시 롤백."""
    db = get_db()
    try:
        total = sum(item['subtotal'] for item in items)
        cursor = db.execute(
            """INSERT INTO sales (total_amount, payment_method, cash_amount,
               card_amount, change_amount, memo)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (total, payment_method, cash_amount, card_amount, change_amount, memo)
        )
        sale_id = cursor.lastrowid

        for item in items:
            db.execute(
                """INSERT INTO sale_items (sale_id, product_id, product_name,
                   unit_type, quantity, unit_price, subtotal, is_bulk)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (sale_id, item['product_id'], item['product_name'],
                 item['unit_type'], item['quantity'], item['unit_price'],
                 item['subtotal'], item.get('is_bulk', 0))
            )
            # 재고 차감
            db.execute(
                "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                (item['quantity'], item['product_id'])
            )

        db.commit()
        return sale_id
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_sales(date_from=None, date_to=None, page=1, per_page=50):
    db = get_db()
    try:
        query = "SELECT * FROM sales"
        conditions = []
        params = []

        if date_from:
            conditions.append("date(sale_date) >= ?")
            params.append(date_from)
        if date_to:
            conditions.append("date(sale_date) <= ?")
            params.append(date_to)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        total = db.execute(count_query, params).fetchone()[0]

        query += " ORDER BY sale_date DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])

        rows = db.execute(query, params).fetchall()
        return [dict(r) for r in rows], total
    finally:
        db.close()


def get_sale_detail(sale_id):
    db = get_db()
    try:
        sale = db.execute("SELECT * FROM sales WHERE id = ?", (sale_id,)).fetchone()
        if not sale:
            return None, []
        items = db.execute(
            "SELECT * FROM sale_items WHERE sale_id = ? ORDER BY id", (sale_id,)
        ).fetchall()
        return dict(sale), [dict(i) for i in items]
    finally:
        db.close()


def refund_sale(sale_id):
    """판매를 환불 처리하고 재고를 복구한다."""
    db = get_db()
    try:
        sale = db.execute("SELECT * FROM sales WHERE id = ?", (sale_id,)).fetchone()
        if not sale or sale['is_refunded']:
            return False

        items = db.execute("SELECT * FROM sale_items WHERE sale_id = ?", (sale_id,)).fetchall()
        for item in items:
            db.execute(
                "UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?",
                (item['quantity'], item['product_id'])
            )

        db.execute("UPDATE sales SET is_refunded = 1 WHERE id = ?", (sale_id,))
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── 통계 ──────────────────────────────────────────────

def get_today_summary():
    db = get_db()
    try:
        today = date.today().isoformat()
        row = db.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN is_refunded = 0 THEN total_amount ELSE 0 END), 0) as total_sales,
                COALESCE(SUM(CASE WHEN is_refunded = 0 THEN cash_amount ELSE 0 END), 0) as total_cash,
                COALESCE(SUM(CASE WHEN is_refunded = 0 THEN card_amount ELSE 0 END), 0) as total_card,
                SUM(CASE WHEN is_refunded = 0 THEN 1 ELSE 0 END) as transaction_count,
                COALESCE(SUM(CASE WHEN is_refunded = 1 THEN total_amount ELSE 0 END), 0) as total_refunds
            FROM sales
            WHERE date(sale_date) = ?
        """, (today,)).fetchone()
        return dict(row)
    finally:
        db.close()


def get_daily_stats(year, month):
    db = get_db()
    try:
        rows = db.execute("""
            SELECT date(sale_date) as day,
                   SUM(total_amount) as total,
                   SUM(cash_amount) as cash,
                   SUM(card_amount) as card,
                   COUNT(*) as count
            FROM sales
            WHERE strftime('%Y', sale_date) = ? AND strftime('%m', sale_date) = ?
                  AND is_refunded = 0
            GROUP BY date(sale_date)
            ORDER BY day
        """, (str(year), str(month).zfill(2))).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def get_monthly_stats(year):
    db = get_db()
    try:
        rows = db.execute("""
            SELECT strftime('%m', sale_date) as month,
                   SUM(total_amount) as total,
                   SUM(cash_amount) as cash,
                   SUM(card_amount) as card,
                   COUNT(*) as count
            FROM sales
            WHERE strftime('%Y', sale_date) = ? AND is_refunded = 0
            GROUP BY strftime('%m', sale_date)
            ORDER BY month
        """, (str(year),)).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def get_top_products(date_from=None, date_to=None, limit=20, order_by='quantity'):
    db = get_db()
    try:
        query = """
            SELECT si.product_id, si.product_name,
                   SUM(si.quantity) as total_qty,
                   SUM(si.subtotal) as total_revenue
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            WHERE s.is_refunded = 0
        """
        params = []
        if date_from:
            query += " AND date(s.sale_date) >= ?"
            params.append(date_from)
        if date_to:
            query += " AND date(s.sale_date) <= ?"
            params.append(date_to)

        query += " GROUP BY si.product_id, si.product_name"

        if order_by == 'revenue':
            query += " ORDER BY total_revenue DESC"
        else:
            query += " ORDER BY total_qty DESC"

        query += " LIMIT ?"
        params.append(limit)

        rows = db.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def get_category_stats(date_from=None, date_to=None):
    db = get_db()
    try:
        query = """
            SELECT c.name as category_name,
                   SUM(si.subtotal) as total_revenue
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN products p ON si.product_id = p.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE s.is_refunded = 0
        """
        params = []
        if date_from:
            query += " AND date(s.sale_date) >= ?"
            params.append(date_from)
        if date_to:
            query += " AND date(s.sale_date) <= ?"
            params.append(date_to)

        query += " GROUP BY c.name ORDER BY total_revenue DESC"
        rows = db.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()


def get_low_stock_products(limit=20):
    db = get_db()
    try:
        rows = db.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = 1 AND p.min_stock > 0 AND p.stock_quantity <= p.min_stock
            ORDER BY (p.stock_quantity - p.min_stock) ASC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        db.close()
