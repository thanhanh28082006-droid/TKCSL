import streamlit as st
import itertools

# ==========================================
# PHẦN 1: TẤT CẢ CÁC THUẬT TOÁN (CORE ALGORITHMS)
# ==========================================

def parse_input(u_str, f_str):
    """Chuyển đổi chuỗi nhập thành Set và List."""
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
    """Thuật toán tính Bao đóng (X+)"""
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
    """Thuật toán tìm tất cả các khóa (Nhị phân)"""
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
    """Thuật toán kiểm tra Lược đồ đạt dạng chuẩn nào (1NF, 2NF, 3NF)"""
    prime_attrs = set().union(*keys)
    non_prime_attrs = U - prime_attrs
    steps_log = []
    
    steps_log.append("✅ **Kiểm tra 1NF:** Mặc định Lược đồ đạt 1NF.")
    
    # Kiểm tra 2NF
    for lhs, rhs in F:
        rhs_non_prime = rhs - prime_attrs
        if rhs_non_prime:
            for k in keys:
                if lhs.issubset(k) and lhs != k:
                    violator = f"{''.join(sorted(lhs))} -> {''.join(sorted(rhs))}"
                    steps_log.append(f"❌ **Kiểm tra 2NF:** Lược đồ KHÔNG đạt 2NF.")
                    steps_log.append(f"> Tồn tại phụ thuộc hàm `{violator}` vi phạm: Thuộc tính không khóa `{''.join(sorted(rhs_non_prime))}` phụ thuộc vào một phần của khóa `{''.join(sorted(k))}`.")
                    return "1NF", prime_attrs, non_prime_attrs, steps_log
    
    steps_log.append("✅ **Kiểm tra 2NF:** Lược đồ đạt 2NF (Không có phụ thuộc từng phần).")
    
    # Kiểm tra 3NF
    for lhs, rhs in F:
        if rhs.issubset(lhs):
            continue
        is_superkey = any(k.issubset(lhs) for k in keys)
        is_rhs_prime = rhs.issubset(prime_attrs)
        
        if not is_superkey and not is_rhs_prime:
            violator = f"{''.join(sorted(lhs))} -> {''.join(sorted(rhs))}"
            steps_log.append(f"❌ **Kiểm tra 3NF:** Lược đồ KHÔNG đạt 3NF.")
            steps_log.append(f"> Tồn tại phụ thuộc hàm `{violator}` vi phạm: Vế trái không phải siêu khóa, vế phải không phải thuộc tính khóa.")
            return "2NF", prime_attrs, non_prime_attrs, steps_log
            
    steps_log.append("✅ **Kiểm tra 3NF:** Lược đồ đạt 3NF (Không có phụ thuộc bắc cầu).")
    return "3NF", prime_attrs, non_prime_attrs, steps_log


# ==========================================
# PHẦN 2: DỮ LIỆU GIẢ LẬP (MOCK DATA)
# ==========================================
db_mock_data = {
    "Bài 1: Slide Thầy": {
        "desc": "Bài kiểm tra Q không đạt 2NF",
        "u_data": "A, B, C, D",
        "f_data": "AB->D, C->D"
    },
    "Bài 2: Test 3NF": {
        "desc": "Bài có 3 khóa, test xem đạt dạng chuẩn mấy",
        "u_data": "A, B, C, D, E",
        "f_data": "AB->C, CD->E, DE->B"
    },
    "Bài 3: Lược đồ lớn": {
        "desc": "Đề thi: Tìm khóa lược đồ 6 thuộc tính",
        "u_data": "A, B, C, D, E, G",
        "f_data": "AB->C, AC->D, D->EG, G->B, A->D, CG->A"
    },
    "Tự nhập dữ liệu...": {
        "desc": "Khu vực tự do gõ đề bài mới",
        "u_data": "",
        "f_data": ""
    }
}


# ==========================================
# PHẦN 3: GIAO DIỆN (UI CHIA 2 BÊN)
# ==========================================

st.set_page_config(page_title="Hệ Thống Thiết Kế CSDL", layout="wide", page_icon="🗄️")
st.title("🗄️ Quản Lý Bài Tập CSDL (Normal Forms)")
st.markdown("---")

# CHIA LAYOUT (Trái 3 phần, Phải 7 phần)
col_list, col_gap, col_detail = st.columns([3, 0.5, 6.5])

# -----------------------------------------
# CỘT TRÁI: DANH SÁCH BÀI TẬP (MASTER)
# -----------------------------------------
with col_list:
    st.markdown("### 📚 Thư Viện Bài Tập")
    st.caption("Chọn một bài để load dữ liệu tự động:")
    
    # Dùng radio button để làm danh sách chọn
    selected_name = st.radio(
        "Danh sách Test Case:",
        options=list(db_mock_data.keys()),
        label_visibility="collapsed"
    )

# -----------------------------------------
# CỘT PHẢI: CHI TIẾT & KHU VỰC TEST (DETAIL)
# -----------------------------------------
with col_detail:
    user_info = db_mock_data[selected_name]
    
    # Header
    st.markdown(f"### 🎯 Đang thao tác: {selected_name}")
    st.caption(f"📝 Mô tả: {user_info['desc']}")
    
    st.divider()
    
    # Ô nhập liệu (có thể sửa được nếu muốn)
    st.markdown("#### ⚙️ Dữ Liệu Lược Đồ (U, F)")
    c1, c2 = st.columns(2)
    with c1:
        u_input = st.text_input("Tập Thuộc Tính U:", value=user_info['u_data'])
    with c2:
        f_input = st.text_input("Tập Phụ Thuộc Hàm F:", value=user_info['f_data'])
        
    U, F = parse_input(u_input, f_input)
    
    if not U or not F:
        st.warning("👈 Vui lòng nhập U và F để sử dụng các công cụ bên dưới!")
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # CÁC CÔNG CỤ TEST (Dùng Tabs cho gọn gàng)
        tab1, tab2, tab3 = st.tabs(["🧩 1. Tính Bao Đóng", "🔑 2. Tìm Khóa", "🔍 3. Dạng Chuẩn"])
        
        with tab1:
            st.markdown("**Thuật toán: Tính Bao Đóng ($X^+$)**")
            x_in = st.text_input("Nhập tập X cần tính (VD: AB):", key="x_input")
            if st.button("▶ Chạy Tính Bao Đóng", type="primary"):
                if x_in:
                    X = set(x_in.replace(" ", "").replace(",", ""))
                    res = get_closure(X, F)
                    st.success(f"**Kết quả:** $({x_in})^+ = \{{ {', '.join(sorted(res))} \}}$")
                else:
                    st.error("Vui lòng nhập X!")
                    
        with tab2:
            st.markdown("**Thuật toán: Tìm Tất cả các Khóa**")
            if st.button("▶ Chạy Tìm Khóa", type="primary"):
                all_keys = find_all_keys(U, F)
                st.success(f"**Lược đồ có {len(all_keys)} khóa:**")
                for i, k in enumerate(all_keys):
                    st.write(f"- Khóa $K_{i+1} = \{{ { ''.join(sorted(k)) } \}}$")

        with tab3:
            st.markdown("**Thuật toán: Phân tích 1NF, 2NF, 3NF**")
            if st.button("▶ Bắt đầu Kiểm Tra Chuẩn Hóa", type="primary"):
                keys = find_all_keys(U, F)
                key_strs = ["{" + "".join(sorted(k)) + "}" for k in keys]
                st.write(f"**🔑 Các khóa đã tìm được:** {', '.join(key_strs)}")
                
                highest_nf, prime, non_prime, logs = check_normal_forms(U, F, keys)
                
                with st.expander("Xem chi tiết các bước biện luận", expanded=True):
                    for log in logs:
                        st.write(log)
                        
                st.success(f"🏆 **KẾT LUẬN: Lược đồ đạt dạng chuẩn {highest_nf}**")
