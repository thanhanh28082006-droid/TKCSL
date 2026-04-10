import streamlit as st
import itertools

# ==========================================
# PHẦN 0: KHỞI TẠO CẤU HÌNH TRANG
# ==========================================
st.set_page_config(page_title="CSDL Normalization App", layout="wide", page_icon="")

# ==========================================
# PHẦN 1: TẤT CẢ CÁC THUẬT TOÁN (CORE LÕI)
# ==========================================

def parse_input(u_str, f_str):
    """Hàm tách chuỗi thành Set và List cho máy tính hiểu"""
    U = set(u_str.replace(" ", "").replace(",", "")) if u_str else set()
    F = []
    if f_str:
        deps = f_str.replace(" ", "").split(',')
        for dep in deps:
            if '->' in dep:
                lhs, rhs = dep.split('->')
                F.append((set(lhs.strip()), set(rhs.strip())))
    return U, F

def get_closure(X, F):
    """Thuật toán: Tính Bao Đóng"""
    closure = set(X)
    changed = True
    while changed:
        changed = False
        for lhs, rhs in F:
            if lhs.issubset(closure) and not rhs.issubset(closure):
                closure.update(rhs)
                changed = True
    return closure

def find_all_keys(U, F):
    """Thuật toán: Tìm Tất Cả Các Khóa (Nhị Phân)"""
    lhs_all = set()
    rhs_all = set()
    for lhs, rhs in F:
        lhs_all.update(lhs)
        rhs_all.update(rhs)

    TN = U - rhs_all
    TG = lhs_all.intersection(rhs_all)
    
    if get_closure(TN, F) == U:
        return [TN]

    keys = []
    TG_list = list(TG)
    n = len(TG_list)
    
    for combo in itertools.product([0, 1], repeat=n):
        Xi = set(TG_list[i] for i in range(n) if combo[i] == 1)
        K_candidate = TN.union(Xi)
        
        if get_closure(K_candidate, F) == U:
            is_minimal = True
            for k in keys:
                if k.issubset(K_candidate):
                    is_minimal = False
                    break
            if is_minimal:
                keys.append(K_candidate)
    return keys

def check_normal_forms(U, F, keys):
    """Thuật toán: Biện luận Dạng Chuẩn 1NF, 2NF, 3NF"""
    prime_attrs = set().union(*keys)
    non_prime_attrs = U - prime_attrs
    steps_log = []
    
    steps_log.append("✅ **Bước 1:** Lược đồ mặc định đạt **1NF**.")
    
    # Check 2NF
    for lhs, rhs in F:
        rhs_non_prime = rhs - prime_attrs
        if rhs_non_prime:
            for k in keys:
                if lhs.issubset(k) and lhs != k:
                    violator = f"{''.join(sorted(lhs))} -> {''.join(sorted(rhs))}"
                    steps_log.append(f"❌ **Bước 2 (Kiểm tra 2NF):** Lược đồ KHÔNG đạt 2NF.")
                    steps_log.append(f"> Tồn tại `{violator}`: Thuộc tính không khóa `{''.join(sorted(rhs_non_prime))}` phụ thuộc vào một phần của khóa `{''.join(sorted(k))}`.")
                    return "1NF", prime_attrs, non_prime_attrs, steps_log
    
    steps_log.append("✅ **Bước 2:** Lược đồ đạt **2NF** (Không có phụ thuộc từng phần).")
    
    # Check 3NF
    for lhs, rhs in F:
        if rhs.issubset(lhs):
            continue
        is_superkey = any(k.issubset(lhs) for k in keys)
        is_rhs_prime = rhs.issubset(prime_attrs)
        
        if not is_superkey and not is_rhs_prime:
            violator = f"{''.join(sorted(lhs))} -> {''.join(sorted(rhs))}"
            steps_log.append(f"❌ **Bước 3 (Kiểm tra 3NF):** Lược đồ KHÔNG đạt 3NF.")
            steps_log.append(f"> Tồn tại `{violator}`: Vế trái không phải siêu khóa, vế phải không phải thuộc tính khóa.")
            return "2NF", prime_attrs, non_prime_attrs, steps_log
            
    steps_log.append("✅ **Bước 3:** Lược đồ đạt **3NF** (Không có phụ thuộc bắc cầu).")
    return "3NF", prime_attrs, non_prime_attrs, steps_log


# ==========================================
# PHẦN 2: ĐIỀU HƯỚNG TRANG (CĂN GIỮA MÀN HÌNH)
# ==========================================

st.markdown("<h1 style='text-align: center;'>🗄️ Test TKCSDLHT</h1>", unsafe_allow_html=True)

# Dùng 3 cột để ép Menu Radio vào giữa màn hình
col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])

with col_nav2:
    page = st.radio(
        "Điều hướng:",
        ["🧮 Phần 1: Demo Thuật Toán", "📚 Phần 2: Thư Viện Test Case "],
        horizontal=True, # Hiển thị nút bấm theo chiều ngang
        label_visibility="collapsed" # Ẩn chữ "Điều hướng:" đi cho đẹp
    )

st.markdown("---")


# ==========================================
# PHẦN 3: GIAO DIỆN TỪNG TRANG
# ==========================================

# -----------------------------------------------------
# GIAO DIỆN TRANG 1: DEMO THUẬT TOÁN (PLAYGROUND)
# -----------------------------------------------------
if page == "🧮 Phần 1: Demo Thuật Toán":
    st.subheader("🧮 Chạy các thuật toán ")
    st.markdown("Nhập dữ liệu để test nhé.")
    
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            u_input = st.text_input("Tập Thuộc Tính U:", "A, B, C, D, E")
        with c2:
            f_input = st.text_input("Tập Phụ Thuộc Hàm F:", "AB->C, CD->E, DE->B")
            
    U, F = parse_input(u_input, f_input)
    
    if U and F:
        st.divider()
        # Dùng Tab để hiển thị 3 thuật toán gọn gàng
        t1, t2, t3 = st.tabs(["🧩 1. Bao Đóng", "🔑 2. Tìm Khóa", "🔍 3. Dạng Chuẩn"])
        
        with t1:
            x_in = st.text_input("Nhập tập X cần tính Bao Đóng (VD: AB):")
            if st.button("Tính Bao Đóng", type="primary"):
                X = set(x_in.replace(" ", "").replace(",", ""))
                res = get_closure(X, F)
                st.success(f"**Kết quả:** $({x_in})^+ = \{{ {', '.join(sorted(res))} \}}$")
                
        with t2:
            if st.button("Chạy Thuật Toán Tìm Khóa", type="primary"):
                keys = find_all_keys(U, F)
                st.success(f"**Lược đồ có {len(keys)} khóa:**")
                for i, k in enumerate(keys):
                    st.write(f"- Khóa $K_{i+1} = \{{ { ''.join(sorted(k)) } \}}$")
                    
        with t3:
            if st.button("Kiểm Tra Chuẩn Hóa", type="primary"):
                keys = find_all_keys(U, F)
                highest_nf, prime, non_prime, logs = check_normal_forms(U, F, keys)
                for log in logs:
                    st.write(log)
                st.success(f"🏆 **KẾT LUẬN: Lược đồ đạt {highest_nf}**")

# -----------------------------------------------------
# GIAO DIỆN TRANG 2: THƯ VIỆN TEST CASE
# -----------------------------------------------------
elif page == "📚 Phần 2: Thư Viện Test Case":
    st.subheader("📚 Thư Viện Bài Tập Mẫu")
    
    # 1. Database giả lập (Đã đổi thành tên Bài Tập chung chung)
    db = {
        "Bài Tập 1 (Test 2NF)": {
            "u": "A, B, C, D", "f": "AB->D, C->D", "note": "Bài này Q không đạt 2NF"
        },
        "Bài Tập 2 (Nhiều Khóa)": {
            "u": "A, B, C, D, E", "f": "AB->C, CD->E, DE->B", "note": "Bài khó, có tận 3 khóa"
        },
        "Bài Tập 3 (Lược đồ 6 thuộc tính)": {
            "u": "A, B, C, D, E, G", "f": "AB->C, AC->D, D->EG, G->B, A->D, CG->A", "note": "Đề thi phức tạp, cần test cẩn thận"
        },
        "Bài Tập 4 (Tìm 1 Khóa)": {
            "u": "A, B, C, D, E", "f": "DE->A, B->C, E->AD", "note": "Lược đồ cơ bản chỉ có 1 khóa duy nhất"
        }
    }
    
    # 2. Chia layout trang 2 thành 2 cột: Danh sách bên trái, Thao tác bên phải
    col_list, col_action = st.columns([3, 7])
    
    with col_list:
        st.markdown("#### 📁 Chọn Bài Tập")
        selected_case = st.radio("Danh sách Bài Tập:", options=list(db.keys()), label_visibility="collapsed")
        st.info(f"**Ghi chú:** {db[selected_case]['note']}")
        
    with col_action:
        st.markdown(f"#### ⚙️ Đang Test: `{selected_case}`")
        
        # Nạp dữ liệu tự động từ DB vào Form
        u_val = db[selected_case]['u']
        f_val = db[selected_case]['f']
        
        c1, c2 = st.columns(2)
        with c1:
            u_in = st.text_input("Tập U:", value=u_val, key="u2")
        with c2:
            f_in = st.text_input("Tập F:", value=f_val, key="f2")
            
        U2, F2 = parse_input(u_in, f_in)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🚀 Bảng Điều Khiển Thực Thi")
        
        # Các nút bấm chạy thẳng thuật toán
        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button("🔑 TÌM KHÓA AUTO", use_container_width=True):
                keys = find_all_keys(U2, F2)
                st.write(f"Tìm thấy {len(keys)} khóa:")
                for k in keys:
                    st.code("{" + "".join(sorted(k)) + "}")
                    
        with btn2:
            if st.button("🔍 CHECK DẠNG CHUẨN AUTO", use_container_width=True):
                keys = find_all_keys(U2, F2)
                highest_nf, _, _, logs = check_normal_forms(U2, F2, keys)
                with st.expander("Xem chi tiết biện luận", expanded=True):
                    for log in logs:
                        st.write(log)
                st.success(f"**Kết Quả Cuối:** {highest_nf}")
