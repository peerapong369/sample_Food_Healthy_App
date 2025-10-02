import streamlit as st
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any, Tuple
import uuid, datetime, io

st.set_page_config(page_title="Food Healthy App", page_icon="🥗", layout="wide")

# ----------------------------
# ชุดข้อมูลตัวอย่าง (ค่าประมาณ ต่อหนึ่งเสิร์ฟ)
#  columns: id,name_th,name_en,price,calories,protein_g,fat_g,carb_g,sugar_g,image_url,notes
# หมายเหตุ: ตัวเลขเป็นค่าเฉลี่ยโดยประมาณ อาจต่างกันตามสูตร/ร้าน
# ----------------------------
# ----------------------------
# ชุดข้อมูลตัวอย่าง (15 เมนูสุขภาพสำหรับคนออกกำลังกาย)
# ----------------------------
SAMPLE_ROWS = [
    {
        "id":"1","name_th":"อกไก่นึ่ง + ข้าวกล้อง","name_en":"Steamed Chicken Breast with Brown Rice","price":79,
        "calories":420,"protein_g":40,"fat_g":5,"carb_g":50,"sugar_g":2,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/6/6b/Chicken_rice.jpg",
        "notes":"เมนูมาตรฐานของสายฟิตเนส"
    },
    {
        "id":"2","name_th":"แซลมอนย่าง + สลัดผัก","name_en":"Grilled Salmon with Salad","price":159,
        "calories":480,"protein_g":36,"fat_g":24,"carb_g":18,"sugar_g":3,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/2/2e/Grilled_Salmon.jpg",
        "notes":"ไขมันดีจากโอเมก้า-3"
    },
    {
        "id":"3","name_th":"ผัดผักรวมเต้าหู้","name_en":"Stir-fried Mixed Veggies with Tofu","price":69,
        "calories":300,"protein_g":18,"fat_g":8,"carb_g":30,"sugar_g":6,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/6/6f/Stir_fry_tofu_and_vegetables.jpg",
        "notes":"โปรตีนจากพืช เหมาะมังสวิรัติ"
    },
    {
        "id":"4","name_th":"โจ๊กข้าวโอ๊ตอกไก่","name_en":"Oatmeal Porridge with Chicken","price":85,
        "calories":350,"protein_g":25,"fat_g":6,"carb_g":40,"sugar_g":2,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/5/5f/Oatmeal_poridge.jpg",
        "notes":"ย่อยง่าย เหมาะเป็นอาหารเช้า"
    },
    {
        "id":"5","name_th":"ไข่ขาวต้ม + มันหวานญี่ปุ่น","name_en":"Boiled Egg Whites with Sweet Potato","price":59,
        "calories":280,"protein_g":22,"fat_g":2,"carb_g":45,"sugar_g":10,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/0/0b/Steamed_Sweet_potato.jpg",
        "notes":"คาร์บเชิงซ้อน + โปรตีนสูง"
    },
    {
        "id":"6","name_th":"ข้าวไรซ์เบอร์รี่ + อกไก่ย่าง","name_en":"Riceberry with Grilled Chicken","price":89,
        "calories":450,"protein_g":38,"fat_g":6,"carb_g":55,"sugar_g":3,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/b/b0/Riceberry.jpg",
        "notes":"ดัชนีน้ำตาลต่ำ"
    },
    {
        "id":"7","name_th":"สลัดทูน่า (ไม่ใส่มายองเนส)","name_en":"Tuna Salad (No Mayo)","price":75,
        "calories":260,"protein_g":30,"fat_g":7,"carb_g":15,"sugar_g":2,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/e/e2/Tuna_salad.jpg",
        "notes":"แคลอรีต่ำ โปรตีนสูง"
    },
    {
        "id":"8","name_th":"สเต็กอกไก่พริกไทยดำ","name_en":"Chicken Steak with Black Pepper","price":99,
        "calories":380,"protein_g":42,"fat_g":9,"carb_g":18,"sugar_g":1,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/4/44/Grilled_chicken_steak.jpg",
        "notes":"รสจัดจ้าน กินอิ่ม"
    },
    {
        "id":"9","name_th":"ข้าวต้มปลา","name_en":"Fish Rice Soup","price":69,
        "calories":320,"protein_g":28,"fat_g":5,"carb_g":40,"sugar_g":2,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/5/59/Fish_soup.jpg",
        "notes":"ย่อยง่าย เหมาะหลังออกกำลัง"
    },
    {
        "id":"10","name_th":"สลัดโรลไก่","name_en":"Chicken Salad Rolls","price":65,
        "calories":270,"protein_g":22,"fat_g":6,"carb_g":32,"sugar_g":5,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/3/32/Fresh_spring_rolls.jpg",
        "notes":"เมนูพกพาง่าย"
    },
    {
        "id":"11","name_th":"โยเกิร์ตไขมันต่ำ + เบอร์รี่","name_en":"Low-fat Yogurt with Berries","price":59,
        "calories":200,"protein_g":12,"fat_g":3,"carb_g":30,"sugar_g":15,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/3/3e/Yogurt_with_fruit.jpg",
        "notes":"โปรไบโอติกส์สูง"
    },
    {
        "id":"12","name_th":"สเต็กเนื้อไม่ติดมัน + ผักย่าง","name_en":"Lean Beef Steak with Grilled Veggies","price":149,
        "calories":480,"protein_g":40,"fat_g":20,"carb_g":20,"sugar_g":2,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/1/1a/Beef_steak.jpg",
        "notes":"โปรตีนคุณภาพสูง"
    },
    {
        "id":"13","name_th":"สลัดควินัว + อกไก่","name_en":"Quinoa Salad with Chicken","price":129,
        "calories":400,"protein_g":35,"fat_g":10,"carb_g":40,"sugar_g":5,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/8/80/Quinoa_salad.jpg",
        "notes":"ซูเปอร์ฟู้ด ใยอาหารสูง"
    },
    {
        "id":"14","name_th":"สลัดไข่ต้ม","name_en":"Boiled Egg Salad","price":59,
        "calories":280,"protein_g":20,"fat_g":10,"carb_g":18,"sugar_g":2,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/b/bc/Boiled_eggs_salad.jpg",
        "notes":"โปรตีนจากไข่ + ใยอาหาร"
    },
    {
        "id":"15","name_th":"ต้มยำกุ้ง (ไม่ใส่น้ำตาล)","name_en":"Tom Yum Goong (No Sugar)","price":95,
        "calories":190,"protein_g":24,"fat_g":7,"carb_g":8,"sugar_g":2,
        "image_url":"https://upload.wikimedia.org/wikipedia/commons/5/5e/Tom_yum_goong.jpg",
        "notes":"โปรตีนจากกุ้ง รสจัด เผาผลาญดี"
    },
]


def sample_df() -> pd.DataFrame:
    return pd.DataFrame(SAMPLE_ROWS)

# ----------------------------
# Utilities
# ----------------------------
def filter_numeric(
    df: pd.DataFrame,
    ranges: Dict[str, Tuple[float, float]]
) -> pd.DataFrame:
    out = df.copy()
    for k, (lo, hi) in ranges.items():
        out = out[(out[k] >= lo) & (out[k] <= hi)]
    return out

def ensure_cart():
    if "cart" not in st.session_state:
        st.session_state.cart = {}

def add_to_cart(row: pd.Series, qty: int):
    ensure_cart()
    item_id = str(row["id"])
    if item_id not in st.session_state.cart:
        st.session_state.cart[item_id] = {"row": row.to_dict(), "qty": 0}
    st.session_state.cart[item_id]["qty"] += qty
    st.rerun()  # <-- สำคัญ: rerun หลังอัปเดต

def remove_from_cart(item_id: str):
    ensure_cart()
    if item_id in st.session_state.cart:
        del st.session_state.cart[item_id]
        st.rerun()  # <-- rerun หลังลบ


def cart_total() -> float:
    ensure_cart()
    return sum(v["row"]["price"] * v["qty"] for v in st.session_state.cart.values())

def pay_now(method: str):
    order_id = str(uuid.uuid4())[:8].upper()
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    items = [
        {
            "id": k,
            "name": v["row"]["name_th"],
            "qty": v["qty"],
            "unit_price": v["row"]["price"],
            "subtotal": v["row"]["price"] * v["qty"],
        }
        for k, v in st.session_state.cart.items()
    ]
    receipt = {
        "order_id": order_id,
        "paid_at": ts,
        "method": method,
        "items": items,
        "total": cart_total()
    }
    st.session_state.cart = {}
    return receipt

# ----------------------------
# UI: Header & Data source
# ----------------------------
st.title("🥗 Food Healthy App — โภชนาการแบบตัวเลข + รูปภาพ")
st.caption("เลือกช่วงตัวเลขสารอาหาร (กรัม) → ดูเมนูรูปภาพที่ตรง → ใส่ตะกร้า → ชำระเงิน (จำลอง)")

with st.expander("📥 อัปโหลดข้อมูลเมนูของคุณเอง (CSV) หรือดาวน์โหลดเทมเพลต"):
    template = pd.DataFrame({
        "id":[""],"name_th":[""],"name_en":[""],"price":[0],
        "calories":[0],"protein_g":[0],"fat_g":[0],"carb_g":[0],"sugar_g":[0],
        "image_url":[""],"notes":[""]
    })
    buf = io.StringIO()
    template.to_csv(buf, index=False, encoding="utf-8")
    st.download_button("ดาวน์โหลดเทมเพลต CSV", buf.getvalue(), file_name="menu_template.csv", mime="text/csv")
    uploaded = st.file_uploader("อัปโหลดไฟล์ CSV (UTF-8, header ตามเทมเพลต)", type=["csv"])

# โหลดข้อมูล
if uploaded:
    try:
        df = pd.read_csv(uploaded)
        required_cols = {"id","name_th","name_en","price","calories","protein_g","fat_g","carb_g","sugar_g","image_url","notes"}
        missing = required_cols - set(df.columns)
        if missing:
            st.error(f"คอลัมน์หายไป: {', '.join(missing)}")
            st.stop()
    except Exception as e:
        st.error(f"อ่านไฟล์ไม่สำเร็จ: {e}")
        st.stop()
else:
    df = sample_df()

# ----------------------------
# Sidebar: ตะกร้า
# ----------------------------
with st.sidebar:
    st.header("🛒 ตะกร้าของคุณ")
    ensure_cart()
    if st.session_state.cart:
        for k, v in list(st.session_state.cart.items()):
            row = v["row"]
            col1, col2, col3 = st.columns([4,2,2])
            with col1:
                st.write(f"**{row['name_th']}**")
                st.caption(row["name_en"])
            with col2:
                st.write(f"x {v['qty']}")
            with col3:
                if st.button("ลบ", key=f"rm_{k}"):
                    remove_from_cart(k)
        st.info(f"รวมทั้งหมด: {cart_total():,.2f} บาท")
    else:
        st.caption("ยังไม่มีรายการ")

# ----------------------------
# Filters: Numeric ranges
# ----------------------------
st.subheader("🧪 เลือกช่วงสารอาหาร (กรัม ต่อหนึ่งเสิร์ฟ)")
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    cal_min, cal_max = st.slider("แคลอรี (kcal)", 0, 1200, (0, 800))
with c2:
    pro_min, pro_max = st.slider("โปรตีน (g)", 0, 100, (0, 50))
with c3:
    fat_min, fat_max = st.slider("ไขมัน (g)", 0, 100, (0, 30))
with c4:
    carb_min, carb_max = st.slider("คาร์บ (g)", 0, 150, (0, 80))
with c5:
    sug_min, sug_max = st.slider("น้ำตาล (g)", 0, 100, (0, 15))

ranges = {
    "calories": (cal_min, cal_max),
    "protein_g": (pro_min, pro_max),
    "fat_g": (fat_min, fat_max),
    "carb_g": (carb_min, carb_max),
    "sugar_g": (sug_min, sug_max),
}

# ตัวเลือกจัดเรียง
st.markdown("")
sort_col = st.selectbox("จัดเรียงผลลัพธ์ตาม", ["แนะนำ", "โปรตีนมาก→น้อย", "แคลอรีน้อย→มาก", "น้ำตาลน้อย→มาก", "ราคา น้อย→มาก"])
filtered = filter_numeric(df, ranges)

if sort_col == "โปรตีนมาก→น้อย":
    filtered = filtered.sort_values("protein_g", ascending=False)
elif sort_col == "แคลอรีน้อย→มาก":
    filtered = filtered.sort_values("calories", ascending=True)
elif sort_col == "น้ำตาลน้อย→มาก":
    filtered = filtered.sort_values("sugar_g", ascending=True)
elif sort_col == "ราคา น้อย→มาก":
    filtered = filtered.sort_values("price", ascending=True)

# ----------------------------
# Results: cards with image
# ----------------------------
st.subheader("🍽️ เมนูที่ตรงกับเงื่อนไข")
if filtered.empty:
    st.warning("ไม่พบเมนูที่ตรงกับช่วงสารอาหารที่เลือก ลองขยายช่วงตัวเลขดูนะครับ")
else:
    cols = st.columns(3)
    for i, row in filtered.reset_index(drop=True).iterrows():
        with cols[i % 3]:
            with st.container(border=True):
                if isinstance(row["image_url"], str) and row["image_url"]:
                    st.image(row["image_url"], use_container_width=True)
                st.markdown(f"**{row['name_th']}**")
                st.caption(row["name_en"])
                st.write(
                    f"พลังงาน: {int(row['calories'])} kcal | "
                    f"โปรตีน: {row['protein_g']} g | ไขมัน: {row['fat_g']} g | "
                    f"คาร์บ: {row['carb_g']} g | น้ำตาล: {row['sugar_g']} g"
                )
                st.write(f"ราคา: **{row['price']:,.2f} บาท**")
                if isinstance(row.get("notes",""), str) and row["notes"]:
                    st.caption(f"หมายเหตุ: {row['notes']}")
                qty = st.number_input("จำนวน", 1, 20, 1, key=f"qty_{row['id']}")
                if st.button("ใส่ตะกร้า", key=f"add_{row['id']}"):
                    add_to_cart(row, qty)
                    st.success(f"เพิ่ม {row['name_th']} x{qty} ลงตะกร้าแล้ว")

st.markdown("---")

# ----------------------------
# Checkout
# ----------------------------
st.subheader("💳 ชำระเงิน")
left, right = st.columns([2,1])
with left:
    ensure_cart()
    if st.session_state.cart:
        for v in st.session_state.cart.values():
            r = v["row"]
            st.write(f"- {r['name_th']} x {v['qty']} = {r['price'] * v['qty']:,.2f} บาท")
        st.info(f"รวมสุทธิ: **{cart_total():,.2f} บาท**")
    else:
        st.caption("ยังไม่มีรายการในตะกร้า")

with right:
    pay_method = st.selectbox("วิธีชำระเงิน", ["PromptPay (QR)", "บัตรเครดิต/เดบิต", "เงินสดเมื่อรับของ"])
    pay_btn = st.button("ชำระเงินตอนนี้", type="primary", disabled=(cart_total()==0))
    if pay_btn:
        receipt = pay_now(pay_method)
        st.success(f"ชำระเงินสำเร็จ! หมายเลขออเดอร์: {receipt['order_id']}")
        with st.expander("ดูใบเสร็จ"):
            st.json(receipt)

st.caption("หมายเหตุ: การจ่ายเงินเป็นการจำลอง สามารถต่อเกตเวย์จริง (เช่น PromptPay QR หรือ Stripe) ได้ภายหลัง")
