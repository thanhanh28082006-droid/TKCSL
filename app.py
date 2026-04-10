import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# ==========================================
# 1. TẦNG DATABASE (THIẾT KẾ VẬT LÝ)
# ==========================================
def init_db():
    """Tự động tạo CSDL SQLite với đầy đủ Ràng buộc (Constraints) và Khóa ngoại"""
    conn = sqlite3.connect('thuvien_hoanhtrang.db')
    c = conn.cursor()
    
    # Bảng SÁCH
    c.execute('''
        CREATE TABLE IF NOT EXISTS SACH (
            MaSach TEXT PRIMARY KEY,
            TenSach TEXT NOT NULL,
            TacGia TEXT,
            TheLoai TEXT,
            SoLuongTong INTEGER CHECK(SoLuongTong >= 0),
            SoLuongHienTai INTEGER CHECK(SoLuongHienTai >= 0)
        )
    ''')
    
    # Bảng ĐỘC GIẢ
    c.execute('''
        CREATE TABLE IF NOT EXISTS DOCGIA (
            MaDG TEXT PRIMARY KEY,
            TenDG TEXT NOT NULL,
            SoDienThoai TEXT UNIQUE
        )
    ''')
    
    # Bảng PHIẾU MƯỢN (Bảng trung gian N-N)
    c.execute('''
        CREATE TABLE IF NOT EXISTS PHIEUMUON (
            MaPhieu INTEGER PRIMARY KEY AUTOINCREMENT,
            MaDG TEXT,
            MaSach TEXT,
            NgayMuon DATE,
            TrangThai TEXT DEFAULT 'Đang mượn',
            FOREIGN KEY(MaDG) REFERENCES DOCGIA(MaDG),
            FOREIGN KEY(MaSach) REFERENCES SACH(MaSach)
        )
    ''')
    conn.commit()
    return conn

conn = init_db()

# ==========================================
# 2. TẦNG NGHIỆP VỤ (LẬP TRÌNH OOP & CRUD)
# ==========================================
def execute_query(query, params=()):
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()

def fetch_data(query, params=()):
    return pd.read_sql_query(query, conn, params=params)

def them_sach(ma, ten, tacgia, theloai, soluong):
    try:
        execute_query(
            "INSERT INTO SACH VALUES (?, ?, ?, ?, ?, ?)", 
            (ma, ten, tacgia, theloai, soluong, soluong)
        )
        return True
    except sqlite3.IntegrityError:
        return False # Lỗi trùng mã sách

def muon_sach(ma_dg, ma_sach):
    c = conn.cursor()
    # Kiểm tra sách còn không
    c.execute("SELECT SoLuongHienTai FROM SACH WHERE MaSach=?", (ma_sach,))
    result = c.fetchone()
    
    if result and result[0] > 0:
        # Tạo phiếu mượn
        c.execute("INSERT INTO PHIEUMUON (MaDG, MaSach, NgayMuon) VALUES (?, ?, ?)", 
                 (ma_dg, ma_sach, date.today()))
        # Trừ số lượng sách
        c.execute("UPDATE SACH SET SoLuongHienTai = SoLuongHienTai - 1 WHERE MaSach=?", (ma_sach,))
        conn.commit()
        return "Thành công"
    return "Sách đã hết hoặc không tồn tại"

# ==========================================
# 3. TẦNG GIAO DIỆN (STREAMLIT UI)
# ==========================================
st.set_page_config(page_title="Hệ Thống Quản Lý Thư Viện", layout="wide")
st.sidebar.title("📚 MENU ĐIỀU HƯỚNG")
menu = st.sidebar.radio("Chọn chức năng:", ["1. Tổng quan", "2. Quản lý Sách", "3. Quản lý Độc giả", "4. Nghiệp vụ Mượn/Trả"])

if menu == "1. Tổng quan":
    st.title("📊 Tổng Quan Hệ Thống")
    col1, col2, col3 = st.columns(3)
    sach_df = fetch_data("SELECT SUM(SoLuongTong) as Tong, SUM(SoLuongHienTai) as HienTai FROM SACH")
    dg_df = fetch_data("SELECT COUNT(*) as TongDG FROM DOCGIA")
    
    with col1:
        st.metric("Tổng số sách trong kho", f"{sach_df['Tong'][0] or 0} quyển")
    with col2:
        st.metric("Sách đang sẵn sàng", f"{sach_df['HienTai'][0] or 0} quyển")
    with col3:
        st.metric("Tổng số Độc giả", f"{dg_df['TongDG'][0] or 0} người")

elif menu == "2. Quản lý Sách":
    st.title("📖 Quản Lý Danh Mục Sách")
    
    # Form Thêm Sách
    with st.expander("➕ Thêm sách mới"):
        with st.form("form_them_sach"):
            col1, col2 = st.columns(2)
            ma_sach = col1.text_input("Mã Sách (VD: S001)")
            ten_sach = col2.text_input("Tên Sách")
            tac_gia = col1.text_input("Tác giả")
            the_loai = col2.selectbox("Thể loại", ["CNTT", "Văn học", "Kinh tế", "Khoa học"])
            so_luong = st.number_input("Số lượng", min_value=1, value=5)
            
            if st.form_submit_button("Lưu dữ liệu"):
                if them_sach(ma_sach, ten_sach, tac_gia, the_loai, so_luong):
                    st.success("Đã thêm sách thành công!")
                else:
                    st.error("Lỗi: Mã sách đã tồn tại!")

    # Bảng Hiển Thị CSDL
    st.subheader("Danh sách hiện tại")
    df_sach = fetch_data("SELECT * FROM SACH")
    st.dataframe(df_sach, use_container_width=True)

elif menu == "3. Quản lý Độc giả":
    st.title("👥 Quản Lý Độc Giả")
    with st.form("form_them_dg"):
        ma_dg = st.text_input("Mã Độc Giả (VD: DG01)")
        ten_dg = st.text_input("Tên Độc Giả")
        sdt = st.text_input("Số điện thoại")
        if st.form_submit_button("Đăng ký thẻ"):
            try:
                execute_query("INSERT INTO DOCGIA VALUES (?, ?, ?)", (ma_dg, ten_dg, sdt))
                st.success("Đăng ký thành công!")
            except:
                st.error("Lỗi: Mã độc giả hoặc SĐT bị trùng!")
                
    st.dataframe(fetch_data("SELECT * FROM DOCGIA"), use_container_width=True)

elif menu == "4. Nghiệp vụ Mượn/Trả":
    st.title("🔄 Xử Lý Mượn Trả")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Lập Phiếu Mượn")
        ma_dg = st.text_input("Nhập Mã Độc Giả")
        ma_sach = st.text_input("Nhập Mã Sách Cần Mượn")
        if st.button("Xác nhận Mượn"):
            ket_qua = muon_sach(ma_dg, ma_sach)
            if ket_qua == "Thành công":
                st.success("Giao dịch thành công! Đã trừ số lượng sách.")
            else:
                st.error(ket_qua)
                
    with col2:
        st.subheader("Lịch sử Giao dịch")
        df_phieu = fetch_data("""
            SELECT P.MaPhieu, D.TenDG, S.TenSach, P.NgayMuon, P.TrangThai 
            FROM PHIEUMUON P
            JOIN DOCGIA D ON P.MaDG = D.MaDG
            JOIN SACH S ON P.MaSach = S.MaSach
        """)
        st.dataframe(df_phieu, use_container_width=True)
