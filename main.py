#!/usr/bin/env python3
import csv, argparse, os, datetime, collections
from typing import List, Dict, Optional

CSV = "expenses.csv"
HEADER = ["date", "category", "amount", "note"]  # YYYY-MM-DD

# ---------- Utilidades base ----------
def ensure_csv():
    if not os.path.exists(CSV):
        with open(CSV, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADER)

def load_rows() -> List[Dict[str, str]]:
    ensure_csv()
    with open(CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    # normaliza amount a float
    for r in rows:
        try:
            r["amount"] = float(r["amount"])
        except Exception:
            r["amount"] = 0.0
    return rows

def save_rows(rows: List[Dict[str, str]]):
    with open(CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        for r in rows:
            w.writerow({
                "date": r["date"],
                "category": r["category"],
                "amount": f'{float(r["amount"]):.2f}',
                "note": r.get("note", "")
            })

def is_valid_date(s: str) -> bool:
    try:
        datetime.date.fromisoformat(s)  # YYYY-MM-DD
        return True
    except ValueError:
        return False

def is_valid_month(s: str) -> bool:
    try:
        datetime.datetime.strptime(s, "%Y-%m")
        return True
    except ValueError:
        return False

def parse_amount(s: str) -> Optional[float]:
    try:
        v = float(s)
        return v if v > 0 else None
    except ValueError:
        return None

def filter_by_month(rows: List[Dict[str, str]], ym: str):
    return [r for r in rows if str(r["date"]).startswith(ym)]

def filter_by_range(rows: List[Dict[str, str]], d1: str, d2: str):
    return [r for r in rows if d1 <= r["date"] <= d2]

# ---------- Acciones ----------
def add(date: str, category: str, amount: str, note: str = ""):
    if not is_valid_date(date):
        print("❌ Fecha inválida. Usa YYYY-MM-DD (ej. 2025-08-24)."); return
    value = parse_amount(amount)
    if value is None:
        print("❌ Monto inválido. Debe ser numérico > 0 (ej. 12.50)."); return

    ensure_csv()
    with open(CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([date, category.strip(), f"{value:.2f}", note.strip()])
    print(f"✅ Gasto agregado: {date} | {category} | ${value:.2f} | {note}")

def list_cmd(limit: Optional[int]=None, month: Optional[str]=None, category: Optional[str]=None):
    rows = load_rows()
    if month:
        if not is_valid_month(month):
            print("❌ Mes inválido. Usa YYYY-MM (ej. 2025-08)."); return
        rows = filter_by_month(rows, month)
    if category:
        rows = [r for r in rows if r["category"].lower() == category.lower()]

    if not rows:
        print("🗒️  No hay registros para los filtros dados."); return

    total = 0.0
    print("Idx  Fecha        Categoría          Monto       Nota")
    print("---- ------------ ------------------ ----------- -----------------------------")
    for idx, r in enumerate(rows, start=1):
        total += r["amount"]
        print(f"{idx:>3}  {r['date']}  {r['category']:<18} ${r['amount']:>9.2f}  {r['note']}")
        if limit and idx >= limit:
            break
    print(f"\n📊 Total mostrado: ${total:.2f}")

def delete(index: int, month: Optional[str]=None, category: Optional[str]=None):
    """Elimina UNA fila por índice sobre el subconjunto filtrado (si hay filtros)."""
    if index <= 0:
        print("❌ Índice inválido (debe ser >= 1)."); return

    all_rows = load_rows()
    # construye la misma vista que list_cmd para mapear índice->fila
    view = all_rows
    if month:
        if not is_valid_month(month):
            print("❌ Mes inválido. Usa YYYY-MM."); return
        view = filter_by_month(view, month)
    if category:
        view = [r for r in view if r["category"].lower() == category.lower()]

    if not view or index > len(view):
        print("⚠️  Índice fuera de rango para los filtros dados."); return

    target = view[index - 1]  # dict
    # elimina la PRIMERA ocurrencia equivalente en all_rows
    removed = False
    for i, r in enumerate(all_rows):
        if r is target:  # misma referencia si no se copiaron dicts
            all_rows.pop(i); removed = True; break
        # por seguridad: comparación de campos
        if (r["date"] == target["date"] and
            r["category"] == target["category"] and
            abs(r["amount"] - target["amount"]) < 1e-9 and
            r["note"] == target["note"]):
            all_rows.pop(i); removed = True; break

    if not removed:
        print("⚠️  No se pudo eliminar (no encontrado)."); return

    save_rows(all_rows)
    print(f"🗑️  Eliminado índice {index}.")

def edit(index: int, date: Optional[str], category: Optional[str], amount: Optional[str], note: Optional[str],
         month: Optional[str]=None, category_filter: Optional[str]=None):
    """Edita una fila por índice en la vista filtrada."""
    if index <= 0:
        print("❌ Índice inválido (>=1)."); return

    all_rows = load_rows()
    view = all_rows
    if month:
        if not is_valid_month(month):
            print("❌ Mes inválido. Usa YYYY-MM."); return
        view = filter_by_month(view, month)
    if category_filter:
        view = [r for r in view if r["category"].lower() == category_filter.lower()]

    if not view or index > len(view):
        print("⚠️  Índice fuera de rango para los filtros dados."); return

    target = view[index - 1]

    # Validaciones de nuevos valores
    if date is not None and not is_valid_date(date):
        print("❌ Fecha inválida. Usa YYYY-MM-DD."); return
    if amount is not None:
        val = parse_amount(amount)
        if val is None:
            print("❌ Monto inválido (>0)."); return
    # Aplicar cambios
    if date is not None: target["date"] = date
    if category is not None: target["category"] = category.strip()
    if amount is not None: target["amount"] = float(amount)
    if note is not None: target["note"] = note.strip()

    save_rows(all_rows)
    print(f"✏️  Editado índice {index}.")

def report_month(ym: str, export: Optional[str]=None):
    if not is_valid_month(ym):
        print("❌ Mes inválido. Usa YYYY-MM (ej. 2025-08)."); return
    rows = filter_by_month(load_rows(), ym)
    total = 0.0
    print(f"📆 Reporte del mes {ym}\n")
    for r in rows:
        total += r["amount"]
        print(f'{r["date"]}  {r["category"]:<15} ${r["amount"]:>8.2f}  {r["note"]}')
    print(f"\nTOTAL {ym}: ${total:.2f}")

    if export:
        with open(export, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=HEADER)
            w.writeheader()
            for r in rows:
                w.writerow({
                    "date": r["date"],
                    "category": r["category"],
                    "amount": f'{r["amount"]:.2f}',
                    "note": r["note"]
                })
        print(f"💾 Exportado a {export}")

def report_category():
    rows = load_rows()
    agg = collections.defaultdict(float)
    for r in rows:
        agg[r["category"]] += r["amount"]
    print("📊 Total por categoría\n")
    for cat, amt in sorted(agg.items(), key=lambda x: -x[1]):
        print(f"{cat:<20} ${amt:>10.2f}")

def report_overview():
    rows = load_rows()
    by_month = collections.defaultdict(float)
    for r in rows:
        ym = str(r["date"])[:7]
        by_month[ym] += r["amount"]
    print("🧾 Resumen por mes\n")
    for ym, amt in sorted(by_month.items()):
        print(f"{ym}: ${amt:.2f}")

def report_range(d1: str, d2: str):
    if not (is_valid_date(d1) and is_valid_date(d2)) or d1 > d2:
        print("❌ Rango inválido. Usa YYYY-MM-DD YYYY-MM-DD y d1<=d2."); return
    rows = filter_by_range(load_rows(), d1, d2)
    total = 0.0
    print(f"📅 Reporte por rango {d1} → {d2}\n")
    for r in rows:
        total += r["amount"]
        print(f'{r["date"]}  {r["category"]:<15} ${r["amount"]:>8.2f}  {r["note"]}')
    print(f"\nTOTAL {d1}..{d2}: ${total:.2f}")

# ---------- CLI ----------
if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Budget Tracker CSV (mejorado)")
    sub = p.add_subparsers(dest="cmd")

    # add
    a = sub.add_parser("add", help="Agregar gasto")
    a.add_argument("date", help="YYYY-MM-DD")
    a.add_argument("category")
    a.add_argument("amount")
    a.add_argument("note", nargs="?", default="")

    # list
    l = sub.add_parser("list", help="Listar (con índice) y totales")
    l.add_argument("--limit", type=int)
    l.add_argument("--month", help="YYYY-MM")
    l.add_argument("--category")

    # delete
    d = sub.add_parser("delete", help="Eliminar por índice (con mismos filtros que list)")
    d.add_argument("index", type=int)
    d.add_argument("--month", help="YYYY-MM")
    d.add_argument("--category")

    # edit
    e = sub.add_parser("edit", help="Editar por índice")
    e.add_argument("index", type=int)
    e.add_argument("--date")
    e.add_argument("--category")
    e.add_argument("--amount")
    e.add_argument("--note")
    e.add_argument("--month", help="YYYY-MM (filtro)")
    e.add_argument("--category-filter", help="filtro de categoría")

    # report
    r = sub.add_parser("report", help="Reportes")
    r.add_argument("type", choices=["month", "category", "overview", "range"])
    r.add_argument("value1", nargs="?")
    r.add_argument("value2", nargs="?")
    r.add_argument("--export", help="Ruta CSV para exportar (solo month)")

    args = p.parse_args()

    if args.cmd == "add":
        add(args.date, args.category, args.amount, args.note)

    elif args.cmd == "list":
        list_cmd(limit=args.limit, month=args.month, category=args.category)

    elif args.cmd == "delete":
        delete(args.index, month=args.month, category=args.category)

    elif args.cmd == "edit":
        edit(args.index, args.date, args.category, args.amount, args.note,
             month=args.month, category_filter=args.category_filter)

    elif args.cmd == "report":
        if args.type == "month":
            if not args.value1:
                print("❌ Falta el mes (YYYY-MM).");
            else:
                report_month(args.value1, export=args.export)
        elif args.type == "category":
            report_category()
        elif args.type == "overview":
            report_overview()
        elif args.type == "range":
            if not (args.value1 and args.value2):
                print("❌ Falta rango: YYYY-MM-DD YYYY-MM-DD.");
            else:
                report_range(args.value1, args.value2)
    else:
        p.print_help()
