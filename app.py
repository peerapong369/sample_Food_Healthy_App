import streamlit as st
from dataclasses import dataclass, asdict
from typing import List, Dict
import uuid
import datetime

st.set_page_config(page_title="Food Healthy App", page_icon="🥗", layout="wide")

# ----------------------------
# โมเดลข้อมูล
# ----------------------------
@dataclass
class MenuItem:
    id: str
    name_th: str
    name_en: str
    price: float
    macros: Dict[str, str]  # โปรตีน/ไขมัน/น้ำตาล: "ต่ำ","กลาง","สูง"
    calories: int
    note: str = ""

# ตัวอย่างเมนู (สามารถเชื่อมต่อ DB จริงภายหลังได้)
MENU_DB: List[MenuItem] = [
    MenuItem(id="1", name_th="อกไก่ย่างสลัด", name_en="Grilled Chicken Salad",
             price=89, macros={"โปรตีน":"สูง","ไขมัน":"ต่ำ","น้ำตาล":"ต่ำ"}, calories=320,
             note="น้ำสลัดงาญี่ปุ่น"),
    MenuItem(id="2", name_th="ข้าวอกไก่ลวกจิ้ม", name_en="Chicken Breast Rice",
             price=79, macros={"โปรตีน":"สูง","ไขมัน":"ต่ำ","น้ำตาล":"กลาง"}, calories=450,
             note="ข้าวหอมมะลิ"),
    MenuItem(id="3", name_th="แซลมอนย่างมะนาว", name_en="Grilled Salmon",
             price=159, macros={"โปรตีน":"สูง","ไขมัน":"กลาง","น้ำตาล":"ต่ำ"}, calories=520,
             note="ไขมันดีจากปลา"),
    MenuItem(id="4", name_th="ผัดผักรวมเต้าหู้", name_en="Stir-fried Veggies with Tofu",
             price=69, macros={"โปรตีน":"กลาง","ไขมัน":"ต่ำ","น้ำตาล":"ต่ำ"}, calories=300,
             note="ใช้น้ำมันรำข้าว"),
    MenuItem(id="5", name_th="ข้าวกะเพราอกไก่ไม่ใส่น้ำตาล", name_en="Basil Chicken (no sugar)",
             price=75, macros={"โปรตีน":"สูง","ไขมัน":"กลาง","น้ำตาล":"ต่ำ"}, calories=520,
             note="เผ็ดกลาง"),
    MenuItem(id="6", name_th="โยเกิร์ตผลไม้รวม", name_en="Yogurt with Fruits",
             price=59, macros={"โปรตีน":"กลาง","ไขมัน":"ต่ำ","น้ำตาล":"กลาง"}, calories=280,
             note="น้ำตาลธรรมชาติจากผลไม้"),
    MenuItem(id="7", name_th="สเต็กหมูซอสพริกไทยดำ", name_en="Pork Steak",
             price=139, macros={"โปรตีน":"สูง","ไขมัน":"สูง","น้ำตาล":"ต่ำ"}, calories=610,
             note="เสิร์ฟกับสลัด"),
    MenuItem(id="8", name_th="ชาข้าวบาร์เล่ไม่หวาน", name_en="Unsweetened Barley Tea",
             price=25, macros={"โปรตีน":"ต่ำ","ไขมัน":"ต่ำ","น้ำตาล":"ต่ำ"}, calories=5,
             note="เครื่องดื่ม"),
]

MACRO_KEYS = ["โปรตีน", "ไขมัน", "น้ำตาล"]
LEVELS = ["ต่ำ", "กลาง", "สูง"]

# ----------------------------
# ฟังก์ชันช่วยเหลือ
# ----------------------------
def filter_menu(selected_macros: Dict[str, List[str]]) -> List[MenuItem]:
    """
    คัดกรองเมนูตามระดับสารอาหารที่เลือก
    - หากผู้ใช้ไม่ได้เลือกในหมวดใดเลย ให้ถือว่าหมวดนั้น 'ไม่จำกัด'
    - เงื่อนไขเป็น AND ระหว่างหมวด (ต้องผ่านทุกหมวดที่มีการเลือก)
    """
    results = []
    for item in MENU_DB:
        ok = True
        for macro_key, selected_levels in selected_macros.items():
            if selected_levels:  # มีการกำหนดระดับที่ต้องการ
                if item.macros.get(macro_key) not in selected_levels:
                    ok = False
                    break
        if ok:
            results.append(item)
    return results

def add_to_cart(item: MenuItem, qty: int = 1):
    if "cart" not in st.session_state:
        st.session_state.cart = {}
    if item.id not in st.session_state.cart:
        st.session_state.cart[item.id] = {"item": item, "qty": 0}
    st.session_state.cart[item.id]["qty"] += qty

def remove_from_cart(item_id: str):
    if "cart" in st.session_state and item_id in st.session_state.cart:
        del st.session_state.cart[item_id]

def cart_total():
    if "cart" not in st.session_state or not st.session_state.cart:
        return 0.0
    return sum(v["item"].price * v["qty"] for v in st.session_state.cart.values())

def pay_now(method: str) -> Dict:
    """
    จำลองการชำระเงิน: คืนค่าใบเสร็จ/สถานะออเดอร์
    """
    order_id = str(uuid.uuid4())[:8].upper()
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    items = []
    for v in st.session_state.cart.values():
        items.append({
            "id": v["item"].id,
            "name": v["item"].name_th,
            "qty": v["qty"],
            "unit_price": v["item"].price,
            "subtotal": v["item"].price * v["qty"],
        })
    receipt = {
        "order_id": order_id,
        "paid_at": ts,
        "method": method,
        "items": items,
        "total": cart_total()
    }
    # ล้างตะกร้าหลังชำระ
    st.session_state.cart = {}
    return receipt

# ----------------------------
# UI
# ----------------------------
st.title("🥗 Food Healthy App")
st.caption("เลือกสารอาหาร → ดูเมนูที่ตรง → ใส่ตะกร้า → จ่ายเงิน")

with st.sidebar:
    st.header("🧪 เลือกสารอาหารที่ต้องการ")
    selected_macros = {}
    for k in MACRO_KEYS:
        selected_levels = st.multiselect(
            f"{k} (เลือกได้หลายระดับ)",
            LEVELS,
            default=[],
            key=f"macro_{k}"
        )
        selected_macros[k] = selected_levels

    st.markdown("---")
    st.subheader("🛒 ตะกร้าสินค้า")
    if "cart" not in st.session_state:
        st.session_state.cart = {}

    if st.session_state.cart:
        for item_id, data in list(st.session_state.cart.items()):
            item = data["item"]
            qty = data["qty"]
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{item.name_th}**")
                st.caption(item.name_en)
            with col2:
                st.write(f"x {qty}")
            with col3:
                if st.button("ลบ", key=f"rm_{item_id}"):
                    remove_from_cart(item_id)
        st.info(f"รวมทั้งหมด: {cart_total():,.2f} บาท")
    else:
        st.write("ตะกร้าของคุณยังว่าง")

# Section 1–2: Filter + แสดงเมนู
st.subheader("🍽️ เมนูที่แนะนำตามสารอาหารที่เลือก")
filtered = filter_menu(selected_macros)
if not filtered:
    st.warning("ไม่พบเมนูที่ตรงกับเงื่อนไข ลองปรับระดับสารอาหารดูนะครับ")
else:
    # แสดงเป็นการ์ด
    cols = st.columns(3)
    for i, item in enumerate(filtered):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{item.name_th}**")
                st.caption(item.name_en)
                st.write(f"แคลอรี: {item.calories} kcal")
                st.write(
                    f"โปรตีน: {item.macros['โปรตีน']} | "
                    f"ไขมัน: {item.macros['ไขมัน']} | "
                    f"น้ำตาล: {item.macros['น้ำตาล']}"
                )
                if item.note:
                    st.caption(f"หมายเหตุ: {item.note}")
                st.write(f"ราคา: **{item.price:,.2f} บาท**")

                qty = st.number_input("จำนวน", min_value=1, max_value=20, value=1, key=f"qty_{item.id}")
                if st.button("ใส่ตะกร้า", key=f"add_{item.id}"):
                    add_to_cart(item, qty)
                    st.success(f"เพิ่ม {item.name_th} x{qty} ลงตะกร้าแล้ว")

st.markdown("---")

# Section 3–4: Checkout + Payment
st.subheader("💳 ชำระเงิน")
left, right = st.columns([2, 1], gap="large")

with left:
    st.write("ตรวจสอบออเดอร์ก่อนชำระ:")
    if st.session_state.cart:
        for v in st.session_state.cart.values():
            st.write(f"- {v['item'].name_th} x {v['qty']} = {v['item'].price * v['qty']:,.2f} บาท")
        st.info(f"รวมสุทธิ: **{cart_total():,.2f} บาท**")
    else:
        st.caption("ยังไม่มีรายการในตะกร้า")

with right:
    pay_method = st.selectbox("วิธีชำระเงิน", ["PromptPay", "บัตรเครดิต/เดบิต", "เงินสดเมื่อรับของ"])
    if st.button("ชำระเงินตอนนี้", type="primary", disabled=(cart_total() == 0)):
        receipt = pay_now(pay_method)
        st.success(f"ชำระเงินสำเร็จ! หมายเลขออเดอร์: {receipt['order_id']}")
        with st.expander("ดูใบเสร็จ"):
            st.json(receipt)

# Footer
st.markdown("---")
st.caption("ตัวอย่างเดโม: สามารถต่อฐานข้อมูลจริง/เกตเวย์ชำระเงินจริง (เช่น Omise/Stripe/PromptPay QR) ได้ภายหลัง")
