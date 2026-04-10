import streamlit as st
import itertools

# ==========================================
# PHẦN 1: CÁC HÀM XỬ LÝ LÕI (ALGORITHMS)
# ==========================================

def parse_input(u_str, f_str):
    # Lọc bỏ dấu phẩy và khoảng trắng để lấy các chữ cái
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
    prime_attrs = set().union(*keys)
    non_prime_attrs = U - prime_attrs
    steps_log = []
    
    steps_log.append("✅ **1NF:** Mặc định Lược đồ đạt 1NF.")
    
    # Kiểm tra 2NF
    for lhs, rhs in F:
        rhs_non_prime = rhs - prime_attrs
        if rhs_non_prime:
            for k in keys:
                if lhs.issubset(k) and lhs != k:
                    violator = f"{''.join(sorted(lhs))} -> {''.join(sorted(rhs))}"
                    steps_log.append(f"❌ **2NF:** KHÔNG đạt 2NF.")
                    steps_log.append(f"> Thuộc tính không khóa `{''.join(sorted(rhs_non_prime))}` phụ thuộc vào một phần của khóa (`{violator}`).")
                    return "1NF", prime_attrs, non_prime_attrs, steps_log
    
    steps_log.append("✅ **2NF:** Lược đồ đạt 2NF (Không có phụ thuộc từng phần).")
    
    # Kiểm tra 3NF
    for lhs, rhs in F:
        if rhs.issubset(lhs):
            continue
        is_superkey = any(k.issubset(lhs) for k in keys)
        is_rhs_prime = rhs.issubset(prime_attrs)
        
        if not is_superkey and not is_rhs_prime:
            violator = f"{''.join(sorted(lhs))} -> {''.join(sorted(rhs))}"
            steps_log.append(f"❌ **3NF:** KHÔNG đạt 3NF.")
            steps_log.append(f"> Vế trái không phải siêu khóa, vế phải không phải thuộc tính khóa (`{violator}`).")
            return "2NF", prime_attrs, non_prime_attrs, steps_log
            
    steps_log.append("✅ **3NF:** Lược đồ đạt 3NF (Không có phụ thuộc bắc cầu).")
    return "3NF", prime_attrs, non_prime_attrs, steps_log


# ==========================================
# PHẦN 2: GIAO DIỆN (UI CHIA 2 BÊN CỐ ĐỊNH)
# ==========================================

st.set_page_config(page_title="CSDL Lab", layout="wide", page_icon="🗄️")
st.title("🗄️ CSDL Lab: Lý Thuyết & Thực Hành")
st.markdown("---")

# TẠO LAYOUT CHIA 2 CỘT (Tỷ lệ 4:6)
col_lib, col_gap, col_test = st.columns([4, 0.2, 6])

# ---------------------------------------------------------
# BÊN TRÁI: THƯ VIỆN SÁCH (HIỂN THỊ TẤT CẢ LÝ THUYẾT)
# ---------------------------------------------------------
with col_lib:
    st.header("📚 Thư Viện Sách")
    # Sử dụng container có height để tạo thanh cuộn độc lập cho cuốn sách
    with st.container(height=800):
        st.markdown("""
        ### 1. Tính Bao Đóng ($X^+$)
        Bao đóng của $X$ (ký hiệu $X^+$) là tập hợp TẤT CẢ các thuộc tính có thể được suy dẫn logic từ $X$ thông qua tập phụ thuộc hàm $F$.
        * **Ứng dụng:** Dùng để kiểm tra xem một phụ thuộc hàm có được suy dẫn từ F hay không.
        
        ---
        ### 2. Tìm Khóa Của Lược Đồ
        Một tập thuộc tính $K$ được gọi là **Khóa** nếu thỏa mãn:
        1. **Tính xác định duy nhất:** $K^+ = U$ (K đẻ ra được tất cả).
        2. **Tính tối thiểu:** Bất kỳ tập con thực sự nào của $K$ cũng không thể đẻ ra được $U$. 
        * **Thuật toán áp dụng:** Phương pháp phân loại thuộc tính (Tập nguồn, Tập trung gian, Tập đích) kết hợp lập bảng đường chạy nhị phân.
        
        ---
        ### 3. Chuẩn Hóa Lược Đồ (Normal Forms)
        * **Dạng chuẩn 1 (1NF):** Mọi giá trị đều là nguyên tử (không chứa đa trị). Mặc định luôn đạt.
        * **Dạng chuẩn 2 (2NF):** Đạt 1NF và **Không có phụ thuộc từng phần**. Thuộc tính không khóa không được phép "ăn bám" vào một mảnh vỡ của khóa chính ghép.
        * **Dạng chuẩn 3 (3NF):** Đạt 2NF và **Không có phụ thuộc bắc cầu** ($A \\rightarrow B \\rightarrow C$). Điều kiện kiểm tra: Mọi phụ thuộc hàm $X \\rightarrow Y$, hoặc $X$ là siêu khóa, hoặc $Y$ là thuộc tính khóa.
        """)

# ---------------------------------------------------------
# BÊN PHẢI: KHU VỰC TEST (HIỂN THỊ TẤT CẢ CHỨC NĂNG)
# ---------------------------------------------------------
with col_test:
    st.header("⚙️ Khu Vực Test Thuật Toán")
    
    # 1. Box nhập liệu dùng chung cho mọi chức năng
    with st.container(border=True):
        st.markdown("##### 📥 1. Nhập Dữ Liệu Đầu Vào")
        c1, c2 = st.columns(2)
        with c1:
            u_input = st.text_input("Tập Thuộc Tính U:", "A, B, C, D, E")
        with c2:
            f_input = st.text_input("Tập Phụ Thuộc Hàm F:", "AB->C, CD->E, DE->B")
            
        U, F = parse_input(u_input, f_input)

    st.markdown("<br>", unsafe_allow_html=True) # Khoảng trắng

    if not U or not F:
        st.warning("👈 Vui lòng nhập U và F ở trên để bắt đầu test!")
    else:
        # 2. Box tính Bao Đóng
        with st.container(border=True):
            st.markdown("##### 🧩 2. Tính Bao Đóng ($X^+$)")
            x_input = st.text_input("Nhập tập X cần tính (VD: AD):", "A, D")
            if st.button("▶ Tính Bao Đóng", type="primary"):
                X = set(x_input.replace(" ", "").replace(",", ""))
                res = get_closure(X, F)
                st.success(f"**Kết quả:** $({x_input})^+ = \{{ {', '.join(sorted(res))} \}}$")
                
        # 3. Box Tìm Khóa
        with st.container(border=True):
            st.markdown("##### 🔑 3. Tìm Tất Cả Các Khóa")
            if st.button("▶ Chạy Thuật Toán Tìm Khóa", type="primary"):
                all_keys = find_all_keys(U, F)
                st.success(f"**Lược đồ có {len(all_keys)} khóa:**")
                for i, k in enumerate(all_keys):
                    st.write(f"- Khóa $K_{i+1} = \{{ { ''.join(sorted(k)) } \}}$")

        # 4. Box Dạng Chuẩn
        with st.container(border=True):
            st.markdown("##### 🔍 4. Phân Tích Dạng Chuẩn")
            if st.button("▶ Bắt đầu Kiểm Tra", type="primary"):
                keys = find_all_keys(U, F)
                key_strs = ["{" + "".join(sorted(k)) + "}" for k in keys]
                st.write(f"**🔑 Khóa của lược đồ:** {', '.join(key_strs)}")
                
                highest_nf, prime, non_prime, logs = check_normal_forms(U, F, keys)
                
                # In log từng bước
                for log in logs:
                    st.write(log)
                        
                st.success(f"🏆 **KẾT LUẬN: Lược đồ đạt dạng chuẩn {highest_nf}**")
