import streamlit as st
import time
import itertools
import graphviz

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="App Thiết kế CSDL", page_icon="🗄️", layout="wide")

# Mẹo làm đẹp giao diện (CSS tùy chỉnh)
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1, h2, h3 {color: #2c3e50;}
    .stButton>button {background-color: #3498db; color: white; border-radius: 5px;}
    .stButton>button:hover {background-color: #2980b9;}
    .success-box {padding: 15px; border-radius: 5px; background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; margin-top:10px;}
    </style>
""", unsafe_allow_html=True)

st.title("🗄️ Ứng Dụng Hỗ Trợ Thiết Kế Cơ Sở Dữ Liệu")
st.markdown("Đồ án môn học: Quản lý Thư viện | Tích hợp thuật toán Dạng chuẩn")

# --- TẠO 3 TABS CHÍNH ---
tab1, tab2, tab3 = st.tabs(["🟦 1. Thiết kế Khái niệm", "🟧 2. Thiết kế Logic (Core)", "🟩 3. Thiết kế Vật lý"])

# ==========================================
# TAB 1: THIẾT KẾ KHÁI NIỆM (ERD)
# ==========================================
with tab1:
    st.header("Thiết kế mức Khái niệm (Conceptual Design)")
    st.write("Tại bước này, chúng ta xác định các Thực thể (Entity) và Mối quan hệ (Relationship) của hệ thống Quản lý thư viện.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Mô hình Thực thể - Mối kết hợp (ERD)")
        # Sử dụng Graphviz để vẽ sơ đồ trực tiếp
        graph = graphviz.Digraph()
        graph.attr(rankdir='LR')
        graph.node('DG', 'ĐỘC GIẢ\n(MaDG, TenDG)', shape='box', style='filled', fillcolor='lightblue')
        graph.node('M', 'MƯỢN\n(NgayMuon)', shape='diamond', style='filled', fillcolor='lightgreen')
        graph.node('S', 'SÁCH\n(MaSach, TenSach)', shape='box', style='filled', fillcolor='lightblue')
        
        graph.edge('DG', 'M', label='1')
        graph.edge('M', 'S', label='N')
        
        st.graphviz_chart(graph)
        
    with col2:
        st.subheader("Các thành phần chính:")
        st.markdown("""
        * **Thực thể (Hình chữ nhật):** Độc giả, Sách, Thẻ thư viện, Nhân viên...
        * **Thuộc tính (Hình oval):** Tên sách, Tác giả, Ngày sinh...
        * **Mối quan hệ (Hình thoi):** * `1 - 1`: 1 Độc giả sở hữu 1 Thẻ thư viện.
            * `1 - N`: 1 Độc giả lập nhiều Phiếu mượn.
            * `N - N`: Nhiều Độc giả có thể mượn Nhiều Sách (thông qua bảng trung gian).
        """)

# ==========================================
# THUẬT TOÁN CHO TAB 2 (LOGIC)
# ==========================================
def parse_fds(fd_string):
    """Hàm phân tích chuỗi Phụ thuộc hàm sang dạng List[Tuple[Set, Set]]"""
    fds = []
    lines = fd_string.strip().split('\n')
    for line in lines:
        if '->' in line:
            left, right = line.split('->')
            # Cắt các thuộc tính bằng dấu phẩy và xóa khoảng trắng
            left_attrs = set([x.strip() for x in left.split(',') if x.strip()])
            right_attrs = set([x.strip() for x in right.split(',') if x.strip()])
            if left_attrs and right_attrs:
                fds.append((left_attrs, right_attrs))
    return fds

def compute_closure(X, fds):
    """Thuật toán tính Bao đóng X+"""
    closure = set(X)
    changed = True
    while changed:
        changed = False
        for left, right in fds:
            # Nếu vế trái là tập con của bao đóng hiện tại, và vế phải chưa nằm trong bao đóng
            if left.issubset(closure) and not right.issubset(closure):
                closure.update(right)
                changed = True
    return sorted(list(closure))

def find_candidate_keys(R, fds):
    """Thuật toán tìm Khóa ứng viên (Candidate Keys)"""
    R_set = set(R)
    keys = []
    
    # Duyệt từ tập hợp có 1 thuộc tính, đến n thuộc tính
    for i in range(1, len(R) + 1):
        for subset in itertools.combinations(R, i):
            subset_set = set(subset)
            
            # Kiểm tra xem nó có chứa một khóa nào đã tìm thấy trước đó không (Tối ưu hóa)
            is_superset = any(set(k).issubset(subset_set) for k in keys)
            if not is_superset:
                closure = compute_closure(subset_set, fds)
                # Nếu bao đóng của nó bằng đúng tập R -> Nó là Khóa
                if set(closure) == R_set:
                    keys.append(sorted(list(subset_set)))
    return keys

# ==========================================
# TAB 2: THIẾT KẾ LOGIC
# ==========================================
with tab2:
    st.header("Thiết kế mức Logic: Công cụ tính toán Phụ thuộc hàm")
    st.write("Nhập tập thuộc tính và tập phụ thuộc hàm (FD) để hệ thống tự động tính toán Bao đóng và Khóa ứng viên.")
    
    col_input, col_result = st.columns([1, 1])
    
    with col_input:
        st.subheader("Nhập dữ liệu")
        # Nhập Tập R
        R_input = st.text_input("Tập thuộc tính R (Cách nhau bằng dấu phẩy):", "A, B, C, D")
        R = [x.strip() for x in R_input.split(',') if x.strip()]
        
        # Nhập Tập F
        st.write("Tập phụ thuộc hàm F (Mỗi dòng 1 luật, dùng '->'):")
        F_input = st.text_area("Ví dụ: A -> B, C", "A -> B\nB -> C\nC -> D")
        fds = parse_fds(F_input)
        
        # Nút Tìm Khóa
        btn_find_key = st.button("🗝️ Tìm Khóa Ứng Viên")
        
        st.markdown("---")
        # Tính Bao đóng tùy chỉnh
        st.write("Tính bao đóng của một tập con cụ thể:")
        X_input = st.text_input("Tập X (Cách nhau bằng dấu phẩy):", "A")
        X = [x.strip() for x in X_input.split(',') if x.strip()]
        btn_closure = st.button("🧮 Tính Bao Đóng X⁺")

    with col_result:
        st.subheader("Kết quả thuật toán")
        
        if btn_find_key:
            if not R or not fds:
                st.warning("Vui lòng nhập đủ Tập R và Tập F!")
            else:
                with st.spinner('Đang tính toán khóa...'):
                    keys = find_candidate_keys(R, fds)
                    time.sleep(0.5) # Tạo cảm giác tính toán cho ngầu
                    
                st.markdown(f"**Tập thuộc tính R:** `{{{', '.join(R)}}}`")
                st.markdown("**Các Khóa Ứng Viên tìm được:**")
                if keys:
                    for idx, k in enumerate(keys):
                        st.markdown(f"<div class='success-box'>Khóa K{idx+1}: <b>{'{' + ', '.join(k) + '}'}</b></div>", unsafe_allow_html=True)
                else:
                    st.error("Không tìm thấy khóa nào với cấu hình hiện tại.")
                    
        if btn_closure:
            if not X:
                st.warning("Vui lòng nhập tập X cần tính!")
            else:
                closure = compute_closure(X, fds)
                st.markdown(f"**Bao đóng của X = `{{{', '.join(X)}}}` là:**")
                st.markdown(f"<div class='success-box'>X⁺ = <b>{'{' + ', '.join(closure) + '}'}</b></div>", unsafe_allow_html=True)

# ==========================================
# TAB 3: THIẾT KẾ VẬT LÝ
# ==========================================
with tab3:
    st.header("Thiết kế mức Vật lý: Mô phỏng Indexing")
    st.write("Tại sao chúng ta cần tạo `INDEX` trong SQL? Chạy mô phỏng truy vấn tìm kiếm một thẻ thư viện trong 1.000.000 dòng dữ liệu để xem sự khác biệt.")
    
    if st.button("🚀 Chạy Mô Phỏng Truy Vấn (1 Triệu dòng)"):
        col_no_index, col_index = st.columns(2)
        
        with col_no_index:
            st.error("❌ Truy vấn KHÔNG có Index (Table Scan)")
            progress_bar_no_index = st.progress(0)
            status_text_no_index = st.empty()
            
            # Mô phỏng chậm
            for i in range(100):
                time.sleep(0.04) # Chậm
                progress_bar_no_index.progress(i + 1)
                status_text_no_index.text(f"Đang quét từng dòng... {i+1}%")
            status_text_no_index.markdown("**Hoàn thành trong: 4.12 giây** 🐢")
            
        with col_index:
            st.success("✅ Truy vấn CÓ Index (Index Seek - B-Tree)")
            progress_bar_index = st.progress(0)
            status_text_index = st.empty()
            
            # Mô phỏng cực nhanh
            for i in range(100):
                time.sleep(0.002) # Rất nhanh
                progress_bar_index.progress(i + 1)
                status_text_index.text(f"Đang duyệt cây B-Tree... {i+1}%")
            status_text_index.markdown("**Hoàn thành trong: 0.05 giây** ⚡ (Nhanh hơn ~80 lần)")
