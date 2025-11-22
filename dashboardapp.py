# dashboard2.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime
from collections import defaultdict
from typing import List, Dict, Any

# --- NOTE ---
# This module is UI-only. It expects two DB helper functions:
#   - run_query(sql, params=None, fetch=True) -> list of rows
#   - run_exec(sql, params=None, fetch=False) -> None
# For now we assume they exist in db_utils. If you don't have them,
# replace with your own DB calls.
try:
    from db_utils import run_query, run_exec
except Exception:
    # Fallback stubs (UI-local). Replace these with real implementations.
    def run_query(sql: str, params=None, fetch=True):
        # Simple fake responses for UI rendering; extend as needed.
        if "FROM procwh.m_item" in sql:
            return [("ITM0001", "Jet Cleaner", "UNIT"), ("ITM0016", "Timbangan Sonic", "UNIT")]
        if "FROM procwh.m_vendor" in sql:
            return [("946b489e-52b2-4d79-9404-152ffa316e0b", "CV Sumbermas MO"),
                    ("f294946b-6c53-410b-b534-90ec756bd217", "Tokopedia")]
        if "FROM procwh.t_pr_header" in sql:
            # sample approved PRs
            return [("PR-202511-00009", 1, date.today(), "APPROVED", "Test PR", datetime.now(), datetime.now())]
        if "FROM procwh.t_pr_detail" in sql:
            return [
                (1, "PR-202511-00009", "ITM0001", "Jet Cleaner Laguna 70", 3, "UNIT", 1500000, 4500000, None),
                (2, "PR-202511-00009", "ITM0016", "Timbangan Sonic", 1, "UNIT", 3500000, 3500000, None),
            ]
        if "FROM procwh.t_po_header" in sql:
            return []
        if "FROM procwh.m_stock" in sql:
            return []
        return []
    def run_exec(sql: str, params=None, fetch=False):
        # no-op stub
        return None

# ---------------------------
# App config and style
# ---------------------------
st.set_page_config(page_title="Sistem Logistik - UI", layout="wide")
st.markdown("""
<style>
/* minimal styling to keep UI pleasant */
.stApp { background-color: #f7fafc; }
.metric-card { background:#111827; color:#fff; padding:16px; border-radius:8px; }
</style>
""", unsafe_allow_html=True)


# ---------------------------
# Session initialization
# ---------------------------
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"
if "pr_items_ui" not in st.session_state:
    st.session_state.pr_items_ui = []
if "po_candidates" not in st.session_state:
    st.session_state.po_candidates = []  # produced from approved PRs
if "stock_history_ui" not in st.session_state:
    st.session_state.stock_history_ui = []  # local copy of stock movement entries


# ---------------------------
# Helper functions
# ---------------------------
def fetch_master_items() -> List:
    try:
        rows = run_query("SELECT item_id, name, base_uom_id FROM procwh.m_item")
        return rows
    except Exception as e:
        st.warning(f"Master items fetch failed: {e}")
        return []

def fetch_master_vendors() -> List:
    try:
        rows = run_query("SELECT vendor_id, name FROM procwh.m_vendor")
        return rows
    except Exception as e:
        st.warning(f"Master vendors fetch failed: {e}")
        return []

def fetch_approved_prs() -> List:
    try:
        rows = run_query("SELECT pr_id, employee_id, pr_date, status, remarks, created_at, updated_at FROM procwh.t_pr_header WHERE status = 'APPROVED'")
        return rows
    except Exception:
        return []

def fetch_pr_details(pr_id: str) -> List:
    try:
        rows = run_query("SELECT pr_detail_id, pr_id, item_id, description, qty_request, uom_id, unit_price, total_amour, vendor_id FROM procwh.t_pr_detail WHERE pr_id = %s", (pr_id,))
        return rows
    except Exception:
        return []

def fetch_pos_draft_for_pr(pr_id: str) -> List:
    try:
        rows = run_query("SELECT po_id, vendor_id, status FROM procwh.t_po_header WHERE pr_id = %s", (pr_id,))
        return rows
    except Exception:
        return []

def create_po_header(po_id: str, pr_id: str, vendor_id: str):
    sql = "INSERT INTO procwh.t_po_header (po_id, pr_id, vendor_id, status, created_at, updated_at) VALUES (%s,%s,%s,%s,NOW(),NOW())"
    run_exec(sql, (po_id, pr_id, vendor_id, "DRAFT"))

def insert_po_detail(po_id: str, pr_detail_id: int, item_id: str, qty:int, uom:str, unit_price:float):
    sql = "INSERT INTO procwh.t_po_detail (po_id, pr_detail_id, item_id, qty_ordered, uom_id, unit_price, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s,NOW(),NOW())"
    run_exec(sql, (po_id, pr_detail_id, item_id, qty, uom, unit_price))


def generate_po_id_stub():
    # lightweight generator for UI demo; replace with procwh.fn_next_po_id()
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"PO-UI-{ts}"


def generate_gr_id_stub():
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"GR-UI-{ts}"


def create_gr_from_po_ui(po_row: Dict[str, Any]) -> str:
    """
    UI-level function to demonstrate: when user triggers GR for a PO,
    create GR header + details and auto-generate stock movement records in session_state.
    This function does not write to DB unless you hook run_exec calls.
    """
    po_id = po_row.get("po_id")
    # For demo: fetch PO detail rows from DB (if available), else create sample
    try:
        po_details = run_query("SELECT po_detail_id, item_id, qty_ordered FROM procwh.t_po_detail WHERE po_id = %s", (po_id,))
    except Exception:
        po_details = [(1, "ITM0001", 3), (2, "ITM0016", 1)]

    gr_id = generate_gr_id_stub()
    created = datetime.now()
    # Insert GR header to DB (commented; implement if needed)
    # run_exec("INSERT INTO procwh.t_gr_header (gr_id, po_id, gr_date, created_at) VALUES (%s,%s,%s,NOW())", (gr_id, po_id, created))

    # For each po_detail, create gr_detail and stock movement entry in session_state
    for pd in po_details:
        po_detail_id, item_id, qty_ordered = pd[0], pd[1], pd[2]
        qty_received = qty_ordered  # assume full receive in demo
        # In DB: insert gr_detail
        # run_exec("INSERT INTO procwh.t_gr_detail (gr_id, po_detail_id, item_id, qty_received, qty_remaining, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,NOW(),NOW())", (gr_id, po_detail_id, item_id, qty_received, 0))

        # create stock movement entry (UI-only)
        st.session_state.stock_history_ui.append({
            "movement_id": f"SM-{len(st.session_state.stock_history_ui)+1}",
            "gr_id": gr_id,
            "po_id": po_id,
            "item_id": item_id,
            "qty": qty_received,
            "movement_type": "IN",
            "location_id": "MAIN-WAREHOUSE",
            "timestamp": created
        })

    return gr_id


# ---------------------------
# Sidebar navigation
# ---------------------------
menu = ["Dashboard", "PR Approval", "PO Approval", "GR / Receiving", "Inventory (m_stock)", "Stock Movement", "Settings"]
choice = st.sidebar.selectbox("Menu", menu, index=menu.index(st.session_state.active_page) if st.session_state.active_page in menu else 0)
st.session_state.active_page = choice

# ---------------------------
# Dashboard
# ---------------------------
if choice == "Dashboard":
    st.title("📊 Dashboard - Sistem Logistik")
    col1, col2, col3 = st.columns(3)
    col1.metric("Approved PR", len(fetch_approved_prs()))
    col2.metric("Draft PO", len(run_query("SELECT 1 FROM procwh.t_po_header WHERE status='DRAFT'") or []))
    col3.metric("Stock Movements (UI)", len(st.session_state.stock_history_ui))

    # quick charts
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["PR","PO","GR"], y=[len(fetch_approved_prs()), 5, len(st.session_state.stock_history_ui)]))
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# PR Approval UI
# ---------------------------
elif choice == "PR Approval":
    st.title("📝 PR Approval")
    st.markdown("List PR yang membutuhkan approval or already approved. (UI - connect DB later)")

    prs = fetch_approved_prs()  # approved
    if not prs:
        st.info("No approved PRs available to process.")
    else:
        # show PR list
        pr_df = pd.DataFrame(prs, columns=["pr_id","employee_id","pr_date","status","remarks","created_at","updated_at"])
        st.dataframe(pr_df, use_container_width=True)

        # Choose PR to view details
        selected = st.selectbox("Pilih PR", pr_df["pr_id"].tolist())
        details = fetch_pr_details(selected)
        if details:
            det_df = pd.DataFrame(details, columns=["pr_detail_id","pr_id","item_id","description","qty_request","uom_id","unit_price","total_amount","vendor_id"])
            st.dataframe(det_df, use_container_width=True)
        else:
            st.info("No PR details found.")

        st.markdown("---")
        st.header("Simulate Approval (UI)")
        col1, col2 = st.columns(2)
        with col1:
            level = st.selectbox("Pilih level approval", [1,2])
            action_by = st.text_input("Action By (user id)", value="user_demo")
        with col2:
            action = st.selectbox("Action", ["APPROVE", "REJECT"])
            notes = st.text_area("Notes (optional)")

        if st.button("Submit PR Approval"):
            # In real: insert into t_pr_approval and let trigger update t_pr_header
            # UI: show message
            st.success(f"PR {selected} -> {action} by {action_by} (level {level}) recorded (UI-only).")
            # Optionally run insert query:
            # run_exec("INSERT INTO procwh.t_pr_approval (pr_id, action, action_by, action_at, notes, level) VALUES (%s,%s,%s,NOW(),%s,%s)", (selected, action, action_by, notes, level))


# ---------------------------
# PO Approval UI
# ---------------------------
elif choice == "PO Approval":
    st.title("📄 PO Approval (3-level)")
    st.markdown("List draft PO and perform approval steps (UI demonstration).")

    # fetch draft PO's (UI / DB)
    try:
        po_list = run_query("SELECT po_id, vendor_id, status FROM procwh.t_po_header WHERE status = 'DRAFT'")
    except Exception:
        po_list = [("PO-UI-1","946b489e-52b2-4d79-9404-152ffa316e0b","DRAFT")]

    if not po_list:
        st.info("No DRAFT POs available.")
    else:
        po_df = pd.DataFrame(po_list, columns=["po_id","vendor_id","status"])
        st.dataframe(po_df, use_container_width=True)

        selected_po = st.selectbox("Pilih PO untuk approve", po_df["po_id"].tolist())
        st.markdown("### PO Details (preview)")
        try:
            po_details = run_query("SELECT po_detail_id, item_id, qty_ordered, uom_id, unit_price FROM procwh.t_po_detail WHERE po_id = %s", (selected_po,))
        except Exception:
            po_details = [(1,"ITM0001",3,"UNIT",1500000)]
        st.dataframe(pd.DataFrame(po_details, columns=["po_detail_id","item_id","qty_ordered","uom_id","unit_price"]), use_container_width=True)

        st.markdown("---")
        st.header("Simulate PO Approval")
        col1, col2, col3 = st.columns(3)
        with col1:
            level = st.selectbox("Approval Level", [1,2,3])
            action_by = st.text_input("Action by", value="po_user")
        with col2:
            action = st.selectbox("Action", ["APPROVE","REJECT"])
            notes = st.text_input("Notes")
        with col3:
            if st.button("Submit PO Approval"):
                # Suggested behaviour:
                # - insert into t_po_approval
                # - trigger updates t_po_header.status based on level rules (REVIEWED -> VERIFIED -> APPROVED)
                st.success(f"PO {selected_po} {action} at level {level} by {action_by} (UI-only).")
                # Optionally: run_exec insert query

# ---------------------------
# GR / Receiving UI
# ---------------------------
elif choice == "GR / Receiving":
    st.title("📥 Goods Receipt (GR) & Receiving")
    st.markdown("Generate GR from PO and auto-create stock movement (UI-only).")

    # list POs that are APPROVED (or VERIFIED depending on your flow)
    try:
        approved_pos = run_query("SELECT po_id, vendor_id, status FROM procwh.t_po_header WHERE status IN ('APPROVED','VERIFIED','REVIEWED')")
    except Exception:
        # demo: list some POs created previously
        approved_pos = [("PO-UI-1", "946b489e-52b2-4d79-9404-152ffa316e0b", "APPROVED"),
                        ("PO-UI-2", "f294946b-6c53-410b-b534-90ec756bd217", "APPROVED")]

    if not approved_pos:
        st.info("No approved POs to receive.")
    else:
        ap_df = pd.DataFrame(approved_pos, columns=["po_id","vendor_id","status"])
        st.dataframe(ap_df, use_container_width=True)
        chosen = st.selectbox("Pilih PO untuk GR", ap_df["po_id"].tolist())
        if st.button("Generate GR & Create Stock Movement"):
            # call ui generate
            po_row = {"po_id": chosen}
            gr_id = create_gr_from_po_ui(po_row)
            st.success(f"GR {gr_id} created (UI-only). Stock movements appended to UI list.")

    st.markdown("---")
    st.subheader("Stock Movements (preview - UI)")
    sm_df = pd.DataFrame(st.session_state.stock_history_ui)
    if sm_df.empty:
        st.info("No stock movement yet.")
    else:
        st.dataframe(sm_df, use_container_width=True)


# ---------------------------
# Inventory (m_stock) UI
# ---------------------------
elif choice == "Inventory (m_stock)":
    st.title("📦 Inventory (m_stock) - Real Time view (UI)")
    st.markdown("This page reads from your `m_stock` master if connected, otherwise shows a UI-aggregated balance from stock movements.")

    # Try to read m_stock table
    try:
        mstock_rows = run_query("SELECT item_id, location_id, current_qty, last_updated FROM procwh.m_stock")
    except Exception:
        mstock_rows = []

    if mstock_rows:
        df = pd.DataFrame(mstock_rows, columns=["item_id","location_id","current_qty","last_updated"])
        st.dataframe(df, use_container_width=True)
    else:
        # derive from UI stock movements
        balance = defaultdict(lambda: defaultdict(float))
        for mv in st.session_state.stock_history_ui:
            item = mv["item_id"]
            loc = mv.get("location_id","MAIN-WAREHOUSE")
            qty = mv["qty"]
            balance[item][loc] += qty

        rows = []
        for item, locs in balance.items():
            for loc, qty in locs.items():
                rows.append({"item_id":item, "location_id":loc, "current_qty":qty, "last_updated": datetime.now()})
        df = pd.DataFrame(rows)
        if df.empty:
            st.info("No stock data available (m_stock empty and no UI movements).")
        else:
            st.dataframe(df, use_container_width=True)


# ---------------------------
# Stock Movement (read-only)
# ---------------------------
elif choice == "Stock Movement":
    st.title("📑 Stock Movement (Read-only)")
    st.markdown("Read-only list of stock movements (from t_stock_movement).")

    # Try real table read
    try:
        sm_rows = run_query("SELECT movement_id, gr_id, po_id, item_id, qty, movement_type, location_id, created_at FROM procwh.t_stock_movement ORDER BY created_at DESC LIMIT 200")
    except Exception:
        sm_rows = []  # fallback to UI session list

    if not sm_rows:
        if st.session_state.stock_history_ui:
            st.dataframe(pd.DataFrame(st.session_state.stock_history_ui), use_container_width=True)
        else:
            st.info("No stock movement data available.")
    else:
        st.dataframe(pd.DataFrame(sm_rows, columns=["movement_id","gr_id","po_id","item_id","qty","movement_type","location_id","created_at"]), use_container_width=True)


# ---------------------------
# Settings (master data quick)
# ---------------------------
elif choice == "Settings":
    st.title("⚙️ Settings (Master Data quick edits)")
    st.markdown("Add/edit master suppliers or categories (UI-only).")
    vendors = [v[1] for v in fetch_master_vendors()]
    if not vendors:
        vendors = st.session_state.get("master_suppliers", ["PT Pakan Jaya", "CV Kimia Air"])
    st.write("Suppliers")
    v_df = pd.DataFrame({"name": vendors})
    st.dataframe(v_df, use_container_width=True)
    with st.form("add_supplier"):
        newv = st.text_input("New supplier name")
        if st.form_submit_button("Add supplier"):
            st.session_state.master_suppliers.append(newv)
            st.success(f"Supplier '{newv}' added (UI-only).")

    st.markdown("---")
    st.write("Master items (preview)")
    items = fetch_master_items()
    if items:
        st.dataframe(pd.DataFrame(items, columns=["item_id","name","uom"]), use_container_width=True)
    else:
        st.info("No items fetched (DB offline).")

# End of file
