from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "diagrams"


def svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs>',
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        '<path d="M0,0 L0,6 L9,3 z" fill="#475569"/>',
        '</marker>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#172033} .title{font-size:26px;font-weight:700} .label{font-size:15px} .small{font-size:13px;fill:#475569} .box{stroke:#334155;stroke-width:2;rx:12} .line{stroke:#64748b;stroke-width:2;fill:none;marker-end:url(#arrow)}</style>',
        '</defs>',
        f'<text x="40" y="42" class="title">{escape(title)}</text>',
    ]


def add_box(lines: list[str], x: int, y: int, w: int, h: int, heading: str, details: list[str], fill: str) -> None:
    lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" class="box"/>')
    lines.append(f'<text x="{x + 16}" y="{y + 30}" class="label" font-weight="700">{escape(heading)}</text>')
    for index, detail in enumerate(details):
        lines.append(f'<text x="{x + 16}" y="{y + 56 + index * 21}" class="small">{escape(detail)}</text>')


def add_line(lines: list[str], x1: int, y1: int, x2: int, y2: int, label: str | None = None) -> None:
    lines.append(f'<path d="M{x1},{y1} L{x2},{y2}" class="line"/>')
    if label:
        lines.append(f'<text x="{(x1 + x2) // 2}" y="{(y1 + y2) // 2 - 6}" text-anchor="middle" class="small">{escape(label)}</text>')


def render_c4() -> None:
    lines = svg_header(1200, 700, "C4 Container Diagram — Flower Shop Information System")
    add_box(lines, 50, 180, 240, 120, "Client", ["Web browser", "catalog and bouquet builder"], "#dbeafe")
    add_box(lines, 50, 430, 240, 120, "Staff", ["Web browser", "manager, stockkeeper, florist"], "#dbeafe")
    add_box(lines, 430, 260, 320, 180, "Backend API", ["FastAPI modular monolith", "Auth, Catalog, Bouquet", "Order, Inventory, Admin"], "#dcfce7")
    add_box(lines, 900, 100, 240, 130, "PostgreSQL", ["catalog", "orders and users", "inventory and audit"], "#fef3c7")
    add_box(lines, 900, 290, 240, 110, "Redis", ["cache", "short reservations"], "#fef3c7")
    add_box(lines, 900, 460, 240, 110, "Notification Provider", ["email / SMS / messenger"], "#fef3c7")
    add_box(lines, 900, 610, 240, 70, "Object Storage", ["product images"], "#fef3c7")
    add_line(lines, 290, 240, 430, 320, "HTTPS REST/JSON")
    add_line(lines, 290, 490, 430, 390, "HTTPS REST/JSON")
    add_line(lines, 750, 300, 900, 180, "SQL transactions")
    add_line(lines, 750, 350, 900, 345, "TTL and cache")
    add_line(lines, 750, 400, 900, 515, "events")
    add_line(lines, 750, 430, 900, 640, "images")
    lines.append('</svg>')
    (OUT / "c4-container.svg").write_text("\n".join(lines), encoding="utf-8")


def render_erd() -> None:
    lines = svg_header(1740, 1160, "ER Diagram — Flower Shop Information System")
    boxes = [
        (40, 80, 350, 220, "users", ["PK id uuid", "UQ email", "password_hash", "full_name", "is_active", "created_at"], "#dbeafe"),
        (450, 80, 280, 150, "roles", ["PK id", "UQ code", "name"], "#dbeafe"),
        (40, 380, 350, 240, "products", ["PK id", "FK category_id", "UQ sku", "name", "product_type", "unit", "price", "min/max_quantity"], "#dcfce7"),
        (450, 380, 280, 150, "categories", ["PK id", "UQ name"], "#dcfce7"),
        (850, 80, 300, 160, "warehouses", ["PK id", "name", "address", "is_active"], "#fef3c7"),
        (850, 300, 370, 210, "stock_balances", ["PK/FK warehouse_id", "PK/FK product_id", "on_hand", "reserved", "updated_at"], "#fef3c7"),
        (1280, 300, 400, 230, "stock_movements", ["PK id", "FK warehouse_id", "FK product_id", "FK order_id", "movement_type", "quantity", "created_by"], "#fef3c7"),
        (40, 760, 350, 170, "bouquet_recipes", ["PK id", "name", "description", "is_active"], "#fce7f3"),
        (450, 730, 300, 190, "recipe_items", ["PK/FK recipe_id", "PK/FK product_id", "quantity", "is_required"], "#fce7f3"),
        (850, 610, 370, 250, "orders", ["PK id", "UQ number", "FK customer_id", "status", "fulfillment_type", "scheduled_at", "total"], "#ede9fe"),
        (1280, 620, 400, 230, "order_items", ["PK id", "FK order_id", "FK product_id", "name_snapshot", "price_snapshot", "quantity", "line_total"], "#ede9fe"),
        (850, 940, 370, 170, "reservations", ["PK id", "FK order_id", "FK warehouse_id", "FK product_id", "quantity", "expires_at"], "#fee2e2"),
        (1280, 920, 400, 190, "order_status_history", ["PK id", "FK order_id", "FK changed_by", "from/to_status", "comment", "created_at"], "#fee2e2"),
    ]
    for x, y, w, h, heading, details, fill in boxes:
        add_box(lines, x, y, w, h, heading, details, fill)
    add_line(lines, 390, 140, 450, 140, "user_roles")
    add_line(lines, 390, 460, 450, 460, "category")
    add_line(lines, 730, 460, 850, 395, "stock")
    add_line(lines, 730, 165, 850, 160, "warehouse")
    add_line(lines, 1150, 390, 1280, 390, "movement")
    add_line(lines, 390, 820, 450, 820, "recipe")
    add_line(lines, 750, 820, 850, 730, "order")
    add_line(lines, 1220, 730, 1280, 730, "items")
    add_line(lines, 1035, 860, 1035, 940, "reserve")
    add_line(lines, 1220, 750, 1280, 1010, "history")
    lines.append('<text x="40" y="1140" class="small">PK — primary key, FK — foreign key, UQ — unique constraint. Detailed source: erd.dbml</text>')
    lines.append('</svg>')
    (OUT / "erd.svg").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    render_c4()
    render_erd()
