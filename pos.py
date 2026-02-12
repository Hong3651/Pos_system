"""
철물점 POS 시스템 (Hardware Store Point of Sale)
Usage: python pos.py
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import init_db, backup_db, yearly_backup
from models import (
    get_categories, get_products, get_product, search_products,
    create_product, update_product, delete_product,
    create_sale, get_sales, get_sale_detail, refund_sale,
    get_today_summary, get_daily_stats, get_monthly_stats,
    get_top_products, get_category_stats, get_low_stock_products
)
from config import Config, UNIT_TYPES
from datetime import date, datetime

app = Flask(__name__)
app.config.from_object(Config)
app.config['STORE_NAME'] = Config.STORE_NAME


# ── Jinja2 필터 ──────────────────────────────────────

@app.template_filter('number_format')
def number_format(value):
    try:
        return "{:,.0f}".format(float(value))
    except (ValueError, TypeError):
        return value


# ── 페이지 라우트 ────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html', config=Config)


@app.route('/checkout')
def checkout():
    categories = get_categories()
    return render_template('checkout.html', config=Config,
                           categories=categories, unit_types=UNIT_TYPES)


@app.route('/products')
def products_list():
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', type=int)
    page = request.args.get('page', 1, type=int)

    products, total = get_products(
        category_id=category_id, search=search or None,
        page=page, per_page=Config.ITEMS_PER_PAGE
    )
    total_pages = max(1, -(-total // Config.ITEMS_PER_PAGE))  # ceil division

    return render_template('products.html', config=Config,
                           products=products, categories=get_categories(),
                           unit_types=UNIT_TYPES, search=search,
                           category_id=category_id, page=page, total_pages=total_pages)


@app.route('/products/new', methods=['GET', 'POST'])
def product_new():
    if request.method == 'POST':
        data = _parse_product_form(request.form)
        create_product(data)
        return redirect(url_for('products_list'))

    return render_template('product_form.html', config=Config,
                           product=None, categories=get_categories(),
                           unit_types=UNIT_TYPES)


@app.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
def product_edit(product_id):
    product = get_product(product_id)
    if not product:
        return redirect(url_for('products_list'))

    if request.method == 'POST':
        data = _parse_product_form(request.form)
        update_product(product_id, data)
        return redirect(url_for('products_list'))

    return render_template('product_form.html', config=Config,
                           product=product, categories=get_categories(),
                           unit_types=UNIT_TYPES)


def _parse_product_form(form):
    return {
        'name': form['name'].strip(),
        'barcode': form.get('barcode', '').strip() or None,
        'category_id': int(form['category_id']) if form.get('category_id') else None,
        'unit_type': form.get('unit_type', 'piece'),
        'price': float(form['price']),
        'cost_price': float(form.get('cost_price') or 0),
        'stock_quantity': float(form.get('stock_quantity') or 0),
        'min_stock': float(form.get('min_stock') or 0),
        'bulk_threshold': int(form['bulk_threshold']) if form.get('bulk_threshold') else None,
        'bulk_price': float(form['bulk_price']) if form.get('bulk_price') else None,
        'memo': form.get('memo', '').strip(),
    }


@app.route('/sales')
def sales_list():
    today = date.today().isoformat()
    date_from = request.args.get('date_from', today)
    date_to = request.args.get('date_to', today)
    page = request.args.get('page', 1, type=int)

    sales, total = get_sales(date_from=date_from, date_to=date_to,
                             page=page, per_page=Config.ITEMS_PER_PAGE)
    total_pages = max(1, -(-total // Config.ITEMS_PER_PAGE))

    return render_template('sales_history.html', config=Config,
                           sales=sales, date_from=date_from, date_to=date_to,
                           page=page, total_pages=total_pages)


@app.route('/sales/<int:sale_id>')
def sale_detail(sale_id):
    sale, items = get_sale_detail(sale_id)
    if not sale:
        return redirect(url_for('sales_list'))
    return render_template('sale_detail.html', config=Config,
                           sale=sale, items=items, unit_types=UNIT_TYPES)


@app.route('/sales/<int:sale_id>/receipt')
def sale_receipt(sale_id):
    sale, items = get_sale_detail(sale_id)
    if not sale:
        return redirect(url_for('sales_list'))
    return render_template('receipt.html', sale=sale, items=items,
                           store_name=Config.STORE_NAME, unit_types=UNIT_TYPES)


@app.route('/statistics')
def statistics():
    now = datetime.now()
    years = list(range(now.year - 2, now.year + 1))
    return render_template('statistics.html', config=Config,
                           years=years, current_year=now.year,
                           current_month=now.month)


# ── API 엔드포인트 ───────────────────────────────────

@app.route('/api/products/search')
def api_search_products():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    results = search_products(q)
    return jsonify(results)


@app.route('/api/products/by-category')
def api_products_by_category():
    category_id = request.args.get('category_id', type=int)
    products, _ = get_products(category_id=category_id, per_page=200)
    return jsonify(products)


@app.route('/api/products', methods=['POST'])
def api_create_product():
    data = request.get_json()
    try:
        product_id = create_product(data)
        return jsonify({'success': True, 'id': product_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/products/<int:product_id>', methods=['PUT'])
def api_update_product(product_id):
    data = request.get_json()
    try:
        update_product(product_id, data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def api_delete_product(product_id):
    try:
        delete_product(product_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/products/low-stock')
def api_low_stock():
    products = get_low_stock_products()
    for p in products:
        ut = UNIT_TYPES.get(p.get('unit_type', ''), {})
        p['unit_label'] = ut.get('label', p.get('unit_type', ''))
    return jsonify(products)


@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    data = request.get_json()
    try:
        items = data['items']
        sale_id = create_sale(
            items=items,
            payment_method=data['payment_method'],
            cash_amount=data.get('cash_amount', 0),
            card_amount=data.get('card_amount', 0),
            change_amount=data.get('change_amount', 0),
            memo=data.get('memo', '')
        )
        return jsonify({'success': True, 'sale_id': sale_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/sales/<int:sale_id>/refund', methods=['POST'])
def api_refund(sale_id):
    result = refund_sale(sale_id)
    if result:
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': '환불할 수 없는 거래입니다'}), 400


@app.route('/api/stats/today')
def api_stats_today():
    return jsonify(get_today_summary())


@app.route('/api/stats/daily')
def api_stats_daily():
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)
    return jsonify(get_daily_stats(year, month))


@app.route('/api/stats/monthly')
def api_stats_monthly():
    year = request.args.get('year', date.today().year, type=int)
    return jsonify(get_monthly_stats(year))


@app.route('/api/stats/top-products')
def api_top_products():
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    order_by = request.args.get('order_by', 'quantity')
    limit = request.args.get('limit', 20, type=int)
    return jsonify(get_top_products(date_from, date_to, limit, order_by))


@app.route('/api/stats/categories')
def api_category_stats():
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    return jsonify(get_category_stats(date_from, date_to))


@app.route('/api/backup', methods=['POST'])
def api_backup():
    try:
        path = backup_db()
        return jsonify({'success': True, 'path': path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── 실행 ─────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    yearly_backup()
    print("=" * 50)
    print("  대왕철물 POS 시스템")
    print("  브라우저에서 http://localhost:5000 접속")
    print("  종료: Ctrl+C")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
