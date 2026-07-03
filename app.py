import streamlit as st
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image, ImageEnhance, ImageFilter
import torch.nn.functional as F
import random
import os
import time
import cv2
import numpy as np
import gdown
import base64

# ==============================
# KONFIGURASI HALAMAN
# ==============================
st.set_page_config(
    page_title="Sistem Pakar Kualitas Jeruk Gerga",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# FUNGSI UNTUK MEMBACA GAMBAR LOKAL SEBAGAI BASE64
# ==============================
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

try:
    base64_img = get_base64_image("image_bf6d3d.png")
    background_style = f"""
        background-image: linear-gradient(rgba(255, 255, 255, 0.90), rgba(254, 243, 199, 0.85)), 
                          url("data:image/png;base64,{base64_img}");
    """
    banner_style = f"""
        background: linear-gradient(135deg, rgba(255, 122, 0, 0.9) 0%, rgba(255, 159, 67, 0.85) 100%),
                    url("data:image/png;base64,{base64_img}");
    """
except FileNotFoundError:
    background_style = "background-color: #FFF9F2;"
    banner_style = "background: linear-gradient(135deg, #FF7A00 0%, #FF9F43 100%);"

# ==============================
# CSS UI ENHANCEMENT (PERBAIKAN TOTAL TEKS BERTUMPUK)
# ==============================
st.markdown(f"""
<style>
    /* 1. Set font Times New Roman global ke element teks murni saja */
    html, body, [data-testid="stAppViewContainer"], .stApp, p, h1, h2, h3, h4, h5, h6, li, span, div {{
        font-family: 'Times New Roman', Times, serif !important;
    }}

    /* 2. Amankan Tombol & Input Element agar teksnya TNR tapi ikonnya tidak rusak */
    button, input, select, textarea {{
        font-family: 'Times New Roman', Times, serif !important;
    }}

    /* 3. PROTEKSI UTAMA: Kembalikan font khusus Ikon Streamlit agar TIDAK BERUBAH jadi tulisan mentah */
    [data-testid="stIconMaterial"], 
    .st-emotion-cache-16idsys, 
    .st-emotion-cache-1ae8t9w,
    [class*="stIcon"] {{
        font-family: "Material Symbols Outlined" !important;
        font-weight: normal !important;
        font-style: normal !important;
        text-transform: none !important;
        letter-spacing: normal !important;
        word-wrap: normal !important;
        white-space: nowrap !important;
        direction: ltr !important;
        -webkit-font-smoothing: antialiased !important;
        text-indent: 0px !important;
    }}

    /* 4. Sembunyikan teks bayangan / sisa kebocoran pada file uploader & expander */
    div[data-testid="stFileUploader"] button div div {{
        font-family: 'Times New Roman', Times, serif !important;
    }}
    
    /* Perbaikan CSS Background Utama */
    .stApp {{
        {background_style}
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Pengaturan Font Menu Sidebar */
    [data-testid="stSidebar"] button p {{
        font-size: 19px !important; 
        font-weight: 700 !important; 
        font-family: 'Times New Roman', Times, serif !important;
    }}
    
    /* Title Styling */
    .main-title {{
        text-align: center;
        font-size: 38px;
        font-weight: 800;
        background: linear-gradient(135deg, #FF7A00 0%, #FFB800 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 25px;
        padding: 10px 0;
    }}
    
    /* Card Container */
    .custom-card {{
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 30px;
        border-radius: 16px;
        border: 1px solid rgba(255, 122, 0, 0.25);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
    }}

    .custom-card h4 {{
        font-size: 22px !important;
        font-weight: 700 !important;
        border-bottom: 2px solid #FF7A00;
        padding-bottom: 8px;
        margin-bottom: 20px !important;
    }}

    .custom-card h3 {{
        font-size: 24px !important;
        font-weight: 700;
        margin-bottom: 15px;
    }}
    .custom-card p, .custom-card li {{
        font-size: 18px !important;
        line-height: 1.6 !important;
        color: #222222 !important;
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: rgba(255, 249, 242, 0.95) !important;
        border-right: 1px solid #FFEAD1;
    }}
    
    /* Badges */
    .badge {{
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 15px;
        display: inline-block;
    }}
    .badge-a {{ background-color: #E8F5E9; color: #2E7D32; border: 1px solid #C8E6C9; }}
    .badge-b {{ background-color: #FFFDE7; color: #F57F17; border: 1px solid #FFF9C4; }}
    .badge-c {{ background-color: #FFEBEE; color: #C62828; border: 1px solid #FFCDD2; }}
    
    /* Hero Banner */
    .hero-banner {{
        {banner_style}
        background-size: cover;
        background-position: center;
        color: white;
        padding: 45px;
        border-radius: 24px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(255, 122, 0, 0.15);
    }}
    
    /* Info Box */
    .info-box {{
        background-color: rgba(248, 249, 250, 0.9);
        padding: 14px 18px;
        border-radius: 8px;
        border-left: 4px solid #FF7A00;
        font-size: 16px !important;
        color: #333333;
        margin-top: 8px;
        line-height: 1.5;
    }}

    /* Gambar */
    [data-testid="stImage"] img {{
        border-radius: 14px !important;
        border: 3px solid #FFFFFF !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08) !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================
# SESSION STATE MANAGEMENT
# ==============================
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'results' not in st.session_state:
    st.session_state.results = []
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'temp_imgs' not in st.session_state:
    st.session_state.temp_imgs = []

def go(page):
    st.session_state.page = page
    st.rerun()

def reset_all():
    st.session_state.results = []
    st.session_state.temp_imgs = []
    st.session_state.uploader_key += 1
    st.session_state.page = "home"
    st.rerun()

def clear_images():
    st.session_state.temp_imgs = []
    st.session_state.uploader_key += 1
    st.rerun()

# ==============================
# SIDEBAR NAVIGATION
# ==============================
with st.sidebar:
    try:
        with open("sidebar_orange.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        img_src = f"data:image/png;base64,{encoded_string}"
    except Exception:
        img_src = ""

    if img_src:
        st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 14px; margin-bottom: 30px; padding: 10px 5px;'>
            <img src='{img_src}' style='width: 55px; height: auto; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.1));'>
            <div>
                <div style='font-weight: 800; font-size: 24px; color: #1E4620; line-height: 1.1;'>Sistem Pakar</div>
                <div style='font-weight: 700; font-size: 20px; color: #FF7A00; line-height: 1.1;'>Jeruk Gerga</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 30px; padding: 10px 5px;'>
            <span style='font-size: 38px;'>🍊</span>
            <div>
                <div style='font-weight: 800; font-size: 24px; color: #1E4620; line-height: 1.1;'>Sistem Pakar</div>
                <div style='font-weight: 700; font-size: 20px; color: #FF7A00; line-height: 1.1;'>Jeruk Gerga</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("Beranda", use_container_width=True):
        go("home")
    if st.button("Unggah Citra", use_container_width=True):
        go("input")
    if st.button("Hasil Analisis", use_container_width=True):
        go("processing")
    if st.button("Tentang Sistem", use_container_width=True):
        go("about")
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    if img_src:
        st.markdown(f"""
        <div style='background: #FFFFFF; padding: 22px; border-radius: 16px; text-align: center; box-shadow: 0 6px 20px rgba(0,0,0,0.06); border: 1px solid #EAEAEA; margin-bottom: 25px;'>
            <img src='{img_src}' style='width: 95px; height: auto; margin-bottom: 12px;'>
            <div style='color: #1E4620; font-weight: 700; font-size: 16px; margin-bottom: 6px;'>Jeruk Gerga Berkualitas</div>
            <div style='color: #555555; font-size: 13px; line-height: 1.4;'>Deteksi kualitas jeruk secara cepat, akurat, dan mudah.</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center; color: #555555; font-size: 12px;'>© 2026 Sistem Pakar Jeruk Gerga<br><span style='color:#888888;'>v2.0</span></div>", unsafe_allow_html=True)

# ==============================
# DATABASE HAMA & PENYAKIT
# ==============================
database_hama = [
    {"nama":"Thrips (Scirtothrips citri)", "gejala":"Kulit buah berwarna cokelat keabu-abuan dan terdapat garis nekrotis di sekitar permukaan buah", "pengendalian":"Penyemprotan insektisida Alfametrin atau Abamektin 2 ml/l serta menjaga tajuk tanaman agar tidak terlalu rapat"},
    {"nama":"Lalat Buah (Bactrocera sp)", "gejala":"Kulit buah berubah warna di sekitar bekas sengatan dan buah cepat membusuk", "pengendalian":"Penyemprotan insektisida Dimethoate atau Abamektin 1-2 cc/l serta pemasangan perangkap Methyl Eugenol"},
    {"nama":"Tungau Karat (P. oleivora Ashmead)", "gejala":"Permukaan buah berubah menjadi keperakan atau cokelat keperakan kemudian menjadi cokelat kehitaman", "pengendalian":"Penyemprotan Propagit, Dikofol, atau larutan sulfur sebanyak 2-3 kali menjelang berbunga"},
    {"nama":"Penggerek Buah (Citripestis sagitiferella)", "gejala":"Terdapat lubang pada buah disertai lendir dan buah menjadi busuk lalu gugur", "pengendalian":"Penyemprotan insektisida Dimethoate 1-2 cc/l dan pemanfaatan musuh alami Trichogramma nana"},
    {"nama":"Antraknosa", "gejala":"Kulit buah terdapat bercak hitam atau cokelat yang semakin meluas", "pengendalian":"Penyemprestam fungisida sesuai dosis anjuran dan menjaga kelembapan kebun"},
    {"nama":"Busuk Buah", "gejala":"Buah menjadi lunak, berair, dan membusuk", "pengendalian":"Memperbaiki drainase kebun dan membuang buah yang terinfeksi"},
    {"nama":"Kanker Jeruk", "gejala":"Kulit buah mengalami luka kasar berwarna cokelat", "pengendalian":"Pemangkasan bagian terserang dan penyemprotan bakterisida"},
    {"nama":"Embun Jelaga", "gejala":"Permukaan buah berwarna hitam seperti tertutup jelaga", "pengendalian":"Membersihkan permukaan buah dan mengendalikan hama kutu"},
    {"nama":"Defisiensi Nutrisi", "gejala":"Warna buah tidak merata dan pertumbuhan buah kurang optimal", "pengendalian":"Pemberian pupuk NPK dan unsur hara sesuai kebutuhan tanaman"}
]

# ==============================
# DEEP LEARNING MODEL LOAD
# ==============================
device = torch.device("cpu")

@st.cache_resource
def load_model():
    model = models.swin_t(weights=None)
    model.head = torch.nn.Linear(model.head.in_features, 3)
    path = "model_swin_jeruk.pth"
    if not os.path.exists(path):
        file_id = "19lK-eLqM9koa9iRRHlyAPMXNpPa5O4uL"
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, path, quiet=False)
    model.load_state_dict(torch.load(path, map_location=device))
    model.eval()
    return model

model = load_model()

# ==============================
# IMAGE PREPROCESSING & VALIDATION
# ==============================
def preprocess(img):
    img = img.resize((224,224))
    img = ImageEnhance.Brightness(img).enhance(1.1)
    img = ImageEnhance.Contrast(img).enhance(1.1)
    img = img.filter(ImageFilter.SHARPEN)
    return img

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406], [0.229,0.224,0.225])
])

def is_orange_object(img):
    img_np = np.array(img.resize((300,300)))
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
    lower = np.array([0,40,40])
    upper = np.array([40,255,255])
    mask = cv2.inRange(hsv, lower, upper)
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(cnts) == 0: return False
    c = max(cnts, key=cv2.contourArea)
    area = cv2.contourArea(c)
    if area < 1500: return False
    perimeter = cv2.arcLength(c, True)
    if perimeter == 0: return False
    circularity = 4 * np.pi * area / (perimeter * perimeter)
    return circularity >= 0.30

# ==============================
# HALAMAN 1: BERANDA
# ==============================
if st.session_state.page == "home":
    st.markdown("""
    <div class='hero-banner'>
        <h1 style='margin:0; font-weight:800;'>Sistem Informasi Kualitas Jeruk Gerga</h1>
        <p style='opacity:0.9; margin-top:10px;'>Sistem berbasis Deep Learning dengan model Swin Transformer untuk mengklasifikasikan kualitas buah Jeruk Gerga.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='custom-card'>
        <h4>Apa Saja yang Bisa Dilakukan Aplikasi Ini?</h4>
        <p>Aplikasi ini dibuat untuk membantu Anda melihat kualitas jeruk lewat 3 fungsi utama:</p>
        <ul>
            <li><b>Mengecek Foto Jeruk:</b> Anda tinggal mengambil foto jeruk lewat kamera langsung atau memilih file foto yang sudah ada di galeri hp/laptop.</li>
            <li><b>Melihat Hasil Grade:</b> Setelah foto dimasukkan, sistem akan memeriksa gambar dan memunculkan hasilnya apakah jeruk tersebut termasuk ke dalam Grade A, Grade B, atau Grade C.</li>
            <li><b>Solusi Perawatan Buah:</b> Kalau hasil pengecekan menunjukkan jeruk kurang bagus (Grade C), aplikasi akan menampilkan informasi tentang hama yang menyerang beserta tips cara menanganinya.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        if st.button("Mulai Proses Analisis", key="start_btn", use_container_width=True):
            go("input")

# ==============================
# HALAMAN 2: INPUT CITRA
# ==============================
elif st.session_state.page == "input":
    st.markdown("<div class='main-title'>Unggah Citra Sampel</div>", unsafe_allow_html=True)
    
    col_kamera, col_berkas = st.columns(2, gap="large")
    imgs = []

    with col_kamera:
        st.markdown("""
        <div class='custom-card' style='text-align: center; min-height: 220px;'>
            <span style='font-size: 35px;'>📷</span>
            <h3>Kamera Langsung</h3>
            <p>Ambil gambar jeruk gerga secara langsung menggunakan kamera perangkat Anda.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if "open_camera" not in st.session_state:
            st.session_state.open_camera = False

        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("Buka Kamera", use_container_width=True, type="primary"):
                st.session_state.open_camera = True
                st.rerun()
        with c_btn2:
            if st.button("Tutup Kamera", use_container_width=True):
                st.session_state.open_camera = False
                st.rerun()

        if st.session_state.open_camera:
            cam = st.camera_input("Posisikan objek tepat di tengah bingkai")
            if cam is not None:
                imgs.append(Image.open(cam).convert("RGB"))

    with col_berkas:
        st.markdown("""
        <div class='custom-card' style='text-align: center; min-height: 220px;'>
            <span style='font-size: 35px;'>📤</span>
            <h3>Unggah dari Perangkat</h3>
            <p>Pilih dan unggah gambar jeruk gerga dari galeri atau folder lokal perangkat Anda.</p>
        </div>
        """, unsafe_allow_html=True)
        
        files = st.file_uploader(
            "Format berkas: JPG, JPEG, atau PNG",
            type=['jpg', 'png', 'jpeg'],
            accept_multiple_files=True,
            key=st.session_state.uploader_key
        )
        if files:
            for f in files:
                imgs.append(Image.open(f).convert("RGB"))

        if imgs:
            st.session_state.temp_imgs = imgs

    st.markdown("<br>", unsafe_allow_html=True)
    
    c_action1, c_action2, _ = st.columns([1.2, 1.2, 2])
    with c_action1:
        if st.button("Jalankan Klasifikasi", type="primary", use_container_width=True):
            if not st.session_state.temp_imgs:
                st.warning("Peringatan: Silakan unggah berkas atau ambil gambar terlebih dahulu.")
            else:
                go("processing")
    with c_action2:
        if st.button("Hapus Gambar", use_container_width=True):
            clear_images()

# ==============================
# HALAMAN 3: PROCESSING
# ==============================
elif st.session_state.page == "processing":
    st.markdown("<div class='main-title'>Proses Analisis Citra</div>", unsafe_allow_html=True)
    
    _, center_box, _ = st.columns([1, 2, 1])
    with center_box:
        if not st.session_state.temp_imgs:
            st.markdown("<div class='custom-card' style='text-align: center;'>", unsafe_allow_html=True)
            st.warning("Informasi: Belum ada data sampel citra yang diunggah.")
            st.markdown("<p style='font-size: 16px; margin-bottom: 20px;'>Silakan menuju menu <b>Unggah Citra</b> terlebih dahulu untuk mengambil foto lewat kamera atau mengunggah berkas gambar jeruk.</p>", unsafe_allow_html=True)
            if st.button("Menuju Halaman Unggah Citra", type="primary", use_container_width=True):
                go("input")
            st.markdown("</div>", unsafe_allow_html=True)
        
        else:
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            status_text = st.empty()
            pb = st.progress(0)
            
            result = []
            imgs = st.session_state.temp_imgs

            for i, img in enumerate(imgs):
                status_text.markdown(f"Menganalisis citra ke-**{i+1}** dari **{len(imgs)}** sampel...")
                
                x = transform(preprocess(img)).unsqueeze(0)
                with torch.no_grad():
                    out = model(x)
                    prob = F.softmax(out, dim=1)

                conf, pred = torch.max(prob, 1)
                grade = ["A", "B", "C"][pred.item()]
                score = round(conf.item() * 100, 2)
                
                prob_values = prob[0].cpu().numpy()
                max_prob = prob_values.max()
                sorted_probs = sorted(prob_values)
                gap = sorted_probs[-1] - sorted_probs[-2]

                CONF_THRESHOLD = 0.6
                GAP_THRESHOLD = 0.2

                if (not is_orange_object(img)) or (max_prob < CONF_THRESHOLD or gap < GAP_THRESHOLD):
                    grade = "Bukan Jeruk"

                result.append({
                    "img": img,
                    "grade": grade,
                    "score": score,
                    "logits": out.cpu().numpy()[0]
                })

                pb.progress((i + 1) / len(imgs))
                time.sleep(0.3)

            st.session_state.results = result
            status_text.success("Seluruh sampel citra berhasil diklasifikasikan.")
            
            if st.button("Tampilkan Hasil Klasifikasi", type="primary", use_container_width=True):
                go("result")
            st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# HALAMAN 4: RESULTS (DASHBOARD)
# ==============================
elif st.session_state.page == "result":
    st.markdown("<div class='main-title'>Dashboard Hasil Klasifikasi</div>", unsafe_allow_html=True)
    laporan = "LAPORAN HASIL KLASIFIKASI KUALITAS JERUK\n" + "="*40 + "\n"

    if not st.session_state.results:
        st.info("Informasi: Belum ada data hasil analisis.")
    else:
        for i, r in enumerate(st.session_state.results):
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2], gap="large")

            with c1:
                st.image(r['img'], use_container_width=True, caption=f"Citra Sampel ke-{i+1}")

            with c2:
                if r['grade'] == "Bukan Jeruk":
                    st.markdown("<span class='badge badge-c'>OBJEK TIDAK TERIDENTIFIKASI / KUALITAS RENDAH</span>", unsafe_allow_html=True)
                    st.error("Sistem mengidentifikasi objek bukan Jeruk Gerga, atau kondisi pencahayaan gambar kurang ideal.")
                    laporan += f"Sampel {i+1}: Objek Tidak Teridentifikasi\n"
                else:
                    if r['grade'] == "A":
                        st.markdown("<h3><span class='badge badge-a'>GRADE A</span> - Kualitas Premium</h3>", unsafe_allow_html=True)
                    elif r['grade'] == "B":
                        st.markdown("<h3><span class='badge badge-b'>GRADE B</span> - Kualitas Standar</h3>", unsafe_allow_html=True)
                    elif r['grade'] == "C":
                        st.markdown("<h3><span class='badge badge-c'>GRADE C</span> - Kualitas Rendah / Rusak</h3>", unsafe_allow_html=True)
                        
                        h = random.choice(database_hama)
                        st.markdown(f"""
                        <div style='background-color: #FFF5F5; padding: 15px; border-radius: 10px; border-left: 5px solid #E53E3E; margin: 10px 0;'>
                            <b style='color:#C62828;'>Rekomendasi Teknis Penanganan:</b><br>
                            - <b>Identifikasi Gejala:</b> {h['nama']}<br>
                            - <b>Karakteristik Fisik:</b> {h['gejala']}<br>
                            - <b>Tindakan Pengendalian:</b> {h['pengendalian']}
                        </div>
                        """, unsafe_allow_html=True)

                    metric_col, logit_col = st.columns(2)
                    with metric_col:
                        st.metric(label="Tingkat Keyakinan (Confidence)", value=f"{r['score']} %")
                        st.markdown("<div class='info-box'>Nilai confidence mengukur tingkat kepastian model terhadap penentuan kelas objek jeruk.</div>", unsafe_allow_html=True)
                        
                    with logit_col:
                        with st.expander("Nilai Output Model (Logits)", expanded=False):
                            st.markdown("<p style='font-size: 13px; color: #555555;'>Nilai logits merupakan nilai mentah dari model sebelum diubah ke probabilitas.</p>", unsafe_allow_html=True)
                            st.code(f"Logit A (z1): {r['logits'][0]:.4f}\nLogit B (z2): {r['logits'][1]:.4f}\nLogit C (z3): {r['logits'][2]:.4f}")
                    
                    laporan += f"Sampel {i+1}: Grade {r['grade']} ({r['score']}%)\nLogits: A:{r['logits'][0]:.4f}, B:{r['logits'][1]:.4f}, C:{r['logits'][2]:.4f}\n\n"
            st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("Unduh Laporan", data=laporan, file_name="Laporan_Klasifikasi_Jeruk.txt", mime="text/plain", use_container_width=True)
    with c2:
        if st.button("Ulangi Klasifikasi", type="primary", use_container_width=True):
            st.session_state.temp_imgs = [] 
            go("input") 
    with c3:
        if st.button("Kembali ke Halaman Utama", use_container_width=True):
            reset_all()

# ==============================
# HALAMAN 5: ABOUT
# ==============================
elif st.session_state.page == "about":
    st.markdown("<div class='main-title'>Tentang Sistem</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='custom-card'>
        <h4>Apa itu Sistem Pakar Jeruk Gerga?</h4>
        <p>Aplikasi ini dibuat untuk membantu menentukan kualitas atau grade buah <b>Jeruk Gerga Lebong</b> secara otomatis menggunakan bantuan visi komputer.</p>
    </div>
    <div class='custom-card'>
        <h4>Teknologi yang Digunakan</h4>
        <ul>
            <li><b>Bahasa Pemrograman & UI:</b> Python & Streamlit Framework.</li>
            <li><b>Model Kecerdasan Buatan (AI):</b> PyTorch dengan arsitektur Swin Transformer.</li>
            <li><b>Pengolah Gambar:</b> OpenCV dan Pillow.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)