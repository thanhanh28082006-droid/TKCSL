import streamlit as st
import itertools


# ==========================================
# PHẦN 1: CÁC HÀM XỬ LÝ LÕI (ALGORITHMS)
# ==========================================

def parse_input(u_str, f_str):
    """Chuyển đổi chuỗi nhập thành Set và List. Giả định mỗi thuộc tính là 1 chữ cái viết hoa."""
    U = set(u_str.replace(" ", "").replace(",", "")) if u_str else set()
    F = []
    if f_str:
        deps = f_str.replace(" ", "").split(',')
        for dep in deps:
            if '->' in dep:
                lhs, rhs = dep.split('->')
                F.append((set(lhs), set(rhs)))
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
    """Thuật toán tìm tất cả các khóa (Dùng phương pháp Nhị phân)"""
    lhs_all = set()
    rhs_all = set()
    for lhs, rhs in F:
        lhs_all.update(lhs)
        rhs_all.update(rhs)

    TN = U - rhs_all  # Tập nguồn
    TG = lhs_all.intersection(rhs_all)  # Tập trung gian

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
    # Tìm thuộc tính khóa và không khóa
    prime_attrs = set().union(*keys)
    non_prime_attrs = U - prime_attrs

    steps_log = []

    # Mặc định đạt 1NF
    steps_log.append("✅ **Kiểm tra 1NF:** Mặc định Lược đồ đạt 1NF (các thuộc tính đều đơn trị).")

    # Kiểm tra 2NF
    is_2nf = True
    for lhs, rhs in F:
        # Lấy các thuộc tính nằm ở vế phải nhưng KHÔNG phải thuộc tính khóa
        rhs_non_prime = rhs - prime_attrs
        if rhs_non_prime:  # Nếu có thuộc tính không khóa bị phụ thuộc
            for k in keys:
                # Nếu vế trái là một tập con thực sự của bất kỳ khóa nào -> Phụ thuộc từng phần!
                if lhs.issubset(k) and lhs != k:
                    violator = f"{''.join(sorted(lhs))} -> {''.join(sorted(rhs))}"
                    steps_log.append(f"❌ **Kiểm tra 2NF:** Lược đồ KHÔNG đạt 2NF.")
                    steps_log.append(
                        f"> Tồn tại phụ thuộc hàm `{violator}` vi phạm: Thuộc tính không khóa `{''.join(sorted(rhs_non_prime))}` phụ thuộc vào `{''.join(sorted(lhs))}` (là một phần của khóa `{''.join(sorted(k))}`).")
                    is_2nf = False
                    return "1NF", prime_attrs, non_prime_attrs, steps_log

    steps_log.append("✅ **Kiểm tra 2NF:** Lược đồ đạt 2NF (Không có phụ thuộc từng phần).")

    # Kiểm tra 3NF
    is_3nf = True
    for lhs, rhs in F:
        # Bỏ qua các phụ thuộc hàm tầm thường (vế phải nằm trong vế trái)
        if rhs.issubset(lhs):
            continue

        # Điều kiện 1: Vế trái phải là Siêu khóa
        is_superkey = False
        for k in keys:
            if k.issubset(lhs):
                is_superkey = True
                break

        # Điều kiện 2: Vế phải phải là thuộc tính khóa
        is_rhs_prime = rhs.issubset(prime_attrs)

        # Nếu vi phạm CẢ 2 điều kiện -> Vi phạm 3NF
        if not is_superkey and not is_rhs_prime:
            violator = f"{''.join(sorted(lhs))} -> {''.join(sorted(rhs))}"
            steps_log.append(f"❌ **Kiểm tra 3NF:** Lược đồ KHÔNG đạt 3NF.")
            steps_log.append(
                f"> Tồn tại phụ thuộc hàm `{violator}` vi phạm: Vế trái `{''.join(sorted(lhs))}` không phải siêu khóa, và vế phải `{''.join(sorted(rhs - prime_attrs))}` không phải thuộc tính khóa.")
            is_3nf = False
            return "2NF", prime_attrs, non_prime_attrs, steps_log

    steps_log.append("✅ **Kiểm tra 3NF:** Lược đồ đạt 3NF (Không có phụ thuộc bắc cầu).")
    return "3NF", prime_attrs, non_prime_attrs, steps_log


# ==========================================
# PHẦN 2: GIAO DIỆN STREAMLIT (UI)
# ==========================================

st.set_page_config(page_title="Công cụ Thiết kế CSDL", layout="wide", page_icon="🗄️")

st.sidebar.title("🗄️ Menu Chức Năng")
menu = st.sidebar.radio("", ["📖 Lý thuyết Dạng Chuẩn", "🧮 Tính Toán & Tìm Khóa", "🔍 Phân Tích Dạng Chuẩn"])

st.sidebar.divider()
st.sidebar.info(
    "💡 **Mẹo:** Nhập thuộc tính bằng các chữ cái viết hoa liên tiếp (VD: ABC). Phụ thuộc hàm cách nhau bởi dấu phẩy (VD: AB->C, C->D).")

# ----------------- TAB 1: LÝ THUYẾT -----------------
if menu == "📖 Lý thuyết Dạng Chuẩn":
    st.title("📚 Lý thuyết Chuẩn Hóa Cơ Sở Dữ Liệu")

    st.markdown("""
    ### 1. Dạng chuẩn 1 (1NF)
    * Mọi thuộc tính của bảng đều là **nguyên tử** (không chứa đa trị, không chứa tập hợp).
    * *Trong lý thuyết tính toán, mọi lược đồ mặc định đạt 1NF.*

    ### 2. Dạng chuẩn 2 (2NF)
    * Phải đạt 1NF.
    * **KHÔNG có phụ thuộc từng phần:** Mọi thuộc tính không khóa phải phụ thuộc đầy đủ vào toàn bộ Khóa chính. 
    * *(Nghĩa là: Nếu khóa gồm 2 chữ $AB$, không được phép có thuộc tính nào chỉ phụ thuộc vào riêng $A$ hoặc riêng $B$).*

    ### 3. Dạng chuẩn 3 (3NF)
    * Phải đạt 2NF.
    * **KHÔNG có phụ thuộc bắc cầu:** Thuộc tính không khóa không được phụ thuộc vào một thuộc tính không khóa khác.
    * *(Thuật toán kiểm tra: Mọi phụ thuộc hàm $X \\rightarrow Y$, hoặc $X$ là siêu khóa, hoặc $Y$ là thuộc tính khóa).*
    """)

# ----------------- TAB 2 & 3: SETUP INPUT CHUNG -----------------
else:
    if menu == "🧮 Tính Toán & Tìm Khóa":
        st.title("🧮 Bao Đóng & Tìm Khóa Lược Đồ")
    else:
        st.title("🔍 Phân Tích Dạng Chuẩn (1NF, 2NF, 3NF)")

    # Form nhập liệu luôn hiện ở trên
    with st.expander("⚙️ NHẬP LƯỢC ĐỒ (Bấm để mở rộng)", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            u_input = st.text_input("Tập thuộc tính U:", "A, B, C, D")
        with col2:
            f_input = st.text_input("Tập Phụ thuộc hàm F:", "AB->D, C->D")

    U, F = parse_input(u_input, f_input)

    if not U or not F:
        st.warning("Vui lòng nhập đầy đủ U và F để bắt đầu tính toán!")
        st.stop()

    # ----------------- TAB 2: TÍNH TOÁN -----------------
    if menu == "🧮 Tính Toán & Tìm Khóa":
        st.subheader("1. Tính Bao Đóng")
        x_input = st.text_input("Nhập tập X cần tính:")
        if st.button("Tính X⁺"):
            X = set(x_input.replace(" ", "").replace(",", ""))
            res = get_closure(X, F)
            st.success(f"Kết quả: $({x_input})^+ = \{{ {', '.join(sorted(res))} \}}$")

        st.divider()
        st.subheader("2. Tất Cả Các Khóa")
        if st.button("Chạy Thuật Toán Tìm Khóa"):
            all_keys = find_all_keys(U, F)
            st.success(f"**Lược đồ có {len(all_keys)} khóa:**")
            for i, k in enumerate(all_keys):
                st.write(f"- Khóa $K_{i + 1} = \{{ {''.join(sorted(k))} \}}$")

    # ----------------- TAB 3: DẠNG CHUẨN -----------------
    elif menu == "🔍 Phân Tích Dạng Chuẩn":
        if st.button("Kiểm tra Lược Đồ Đạt Dạng Chuẩn Mấy?", type="primary"):
            # Bắt buộc phải tìm khóa trước
            keys = find_all_keys(U, F)

            # Hiển thị Khóa
            key_strs = ["{" + "".join(sorted(k)) + "}" for k in keys]
            st.markdown(f"**🔑 Khóa của lược đồ:** {', '.join(key_strs)}")

            # Chạy thuật toán chuẩn hóa
            highest_nf, prime, non_prime, logs = check_normal_forms(U, F, keys)

            # Hiển thị phân loại thuộc tính
            c1, c2 = st.columns(2)
            c1.info(f"**Thuộc tính khóa (Prime):** {', '.join(sorted(prime)) if prime else '∅'}")
            c2.warning(f"**Thuộc tính không khóa (Non-prime):** {', '.join(sorted(non_prime)) if non_prime else '∅'}")

            st.divider()
            st.subheader("BƯỚC BIỆN LUẬN CHI TIẾT:")

            # In từng bước biện luận y như bài giảng
            for log in logs:
                st.write(log)

            st.divider()
            st.success(f"🏆 **KẾT LUẬN CUỐI CÙNG: Lược đồ đạt dạng chuẩn {highest_nf}**")