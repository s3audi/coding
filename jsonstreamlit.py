import streamlit as st
import os
import json
from pathlib import Path
import zipfile
import io

# --- Proje JSON dosyası yolu ---
PROJECTS_JSON_PATH = "projeler.json"

def load_projects():
    if os.path.exists(PROJECTS_JSON_PATH):
        with open(PROJECTS_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Varsayılan projeler (ilk açılış için)
        return {
            # ...buraya varsayılan projelerinizin içeriğini ekleyin...
        }

def save_projects(projects):
    with open(PROJECTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

def update_and_save_projects():
    save_projects(st.session_state.projects)

# Sayfa yapılandırması
st.set_page_config(
    page_title="🚀 Streamlit Kodlama Arayüzü",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stilleri
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .project-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .file-content {
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown("""
<div class="main-header">
    <h1 style="color: white; margin: 0;">🚀 Streamlit Kodlama Arayüzü</h1>
    <p style="color: white; margin: 0; opacity: 0.8;">Tab geçişli proje yönetimi ve kod editörü</p>
</div>
""", unsafe_allow_html=True)

# Projeleri yükle
if 'projects' not in st.session_state:
    st.session_state.projects = load_projects()
    # Eğer hiç proje yoksa, örnek bir proje oluştur
    if not st.session_state.projects:
        st.session_state.projects = {
            "ornek_proje": {
                "name": "Örnek Proje",
                "files": {
                    "main.py": "# Bu bir örnek projedir.\nprint('Merhaba Dünya!')"
                }
            }
        }
        save_projects(st.session_state.projects)

# Session state başlatma
if 'active_project' not in st.session_state:
    # Eğer hiç proje yoksa None, varsa ilk projeyi seç
    if st.session_state.projects:
        st.session_state.active_project = list(st.session_state.projects.keys())[0]
    else:
        st.session_state.active_project = None

if 'active_file' not in st.session_state:
    if st.session_state.active_project:
        st.session_state.active_file = list(st.session_state.projects[st.session_state.active_project]['files'].keys())[0]
    else:
        st.session_state.active_file = None

# Sidebar - Proje Yöneticisi
with st.sidebar:
    st.header("📁 Proje Yöneticisi")
    
    # Proje seçimi
    project_names = {k: v['name'] for k, v in st.session_state.projects.items()}
    project_keys = list(project_names.keys())
    if st.session_state.active_project not in project_keys:
        st.session_state.active_project = project_keys[0]

    selected_project = st.selectbox(
        "Aktif Proje",
        options=project_keys,
        format_func=lambda x: project_names[x],
        index=project_keys.index(st.session_state.active_project)
    )
    
    if selected_project != st.session_state.active_project:
        st.session_state.active_project = selected_project
        st.session_state.active_file = list(st.session_state.projects[selected_project]['files'].keys())[0]
        st.rerun()
    
    # Yeni proje ekleme
    st.subheader("➕ Yeni Proje")
    new_project_name = st.text_input("Proje adı")
    if st.button("Proje Oluştur") and new_project_name:
        project_key = new_project_name.lower().replace(' ', '_')
        st.session_state.projects[project_key] = {
            'name': new_project_name,
            'files': {
                'main.py': f'''import streamlit as st

st.title('{new_project_name}')

st.write("🚀 Yeni proje başlatıldı!")

# Buraya kodunuzu yazın
st.success("Proje hazır!")'''
            }
        }
        st.session_state.active_project = project_key
        st.session_state.active_file = 'main.py'
        st.success(f"✅ {new_project_name} projesi oluşturuldu!")
        update_and_save_projects()
        st.rerun()
    
    st.divider()
    
    # Dosya yöneticisi
    st.subheader("📄 Dosyalar")
    current_project = st.session_state.projects[st.session_state.active_project]
    
    # Dosya seçimi
    selected_file = st.selectbox(
        "Aktif Dosya",
        options=list(current_project['files'].keys()),
        index=list(current_project['files'].keys()).index(st.session_state.active_file)
    )
    
    if selected_file != st.session_state.active_file:
        st.session_state.active_file = selected_file
        st.rerun()
    
    # Yeni dosya ekleme
    col_add, col_del = st.columns([2, 1])

    with col_add:
        new_file_name = st.text_input("Yeni dosya adı (örn: utils.py)")
        if st.button("Dosya Ekle") and new_file_name:
            if not new_file_name.endswith('.py'):
                new_file_name += '.py'
            st.session_state.projects[st.session_state.active_project]['files'][new_file_name] = f'''# {new_file_name}

# Yeni dosya içeriği buraya yazılacak
'''
            st.session_state.active_file = new_file_name
            st.success(f"✅ {new_file_name} dosyası eklendi!")
            update_and_save_projects()
            st.rerun()

    with col_del:
        # Silme modunu kontrol et
        if 'delete_confirm' not in st.session_state:
            st.session_state.delete_confirm = False

        if not st.session_state.delete_confirm:
            if st.button("🗑️ Dosya Sil"):
                files = list(st.session_state.projects[st.session_state.active_project]['files'].keys())
                if len(files) > 1:
                    st.session_state.delete_confirm = True
                else:
                    st.warning("⚠️ En az bir dosya kalmalı!")
        else:
            if st.checkbox("Silmek istediğinize emin misiniz?"):
                if st.button("Evet, Sil"):
                    del st.session_state.projects[st.session_state.active_project]['files'][st.session_state.active_file]
                    st.session_state.active_file = list(st.session_state.projects[st.session_state.active_project]['files'].keys())[0]
                    st.success("✅ Dosya silindi!")
                    update_and_save_projects()
                    st.session_state.delete_confirm = False
                    st.rerun()
            if st.button("Vazgeç"):
                st.session_state.delete_confirm = False
    
    st.divider()
    
    # Proje işlemleri
    st.subheader("🔧 Proje İşlemleri")
    
    # Proje export
    if st.button("📦 Projeyi Export Et"):
        project_data = st.session_state.projects[st.session_state.active_project]
        json_data = json.dumps(project_data, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="💾 JSON olarak indir",
            data=json_data,
            file_name=f"{st.session_state.active_project}.json",
            mime="application/json"
        )
    
    st.divider()
    
    # Proje import
    st.subheader("📥 Proje İmport")
    
    # JSON dosyası yükleme
    uploaded_json = st.file_uploader(
        "JSON proje dosyası yükle",
        type=['json'],
        help="Daha önce export ettiğiniz proje dosyasını yükleyin"
    )
    
    if uploaded_json is not None:
        try:
            # JSON dosyasını oku
            json_data = json.loads(uploaded_json.read().decode('utf-8'))
            
            # Proje adını al
            import_project_name = st.text_input(
                "İmport edilecek proje adı",
                value=uploaded_json.name.replace('.json', '')
            )
            
            if st.button("📥 JSON Projesini İmport Et") and import_project_name:
                project_key = import_project_name.lower().replace(' ', '_').replace('-', '_')
                if project_key in st.session_state.projects:
                    st.warning("⚠️ Bu isimde bir proje zaten var!")
                else:
                    st.session_state.projects[project_key] = {
                        'name': import_project_name,
                        'files': json_data.get('files', {})
                    }
                    st.session_state.active_project = project_key
                    st.session_state.active_file = list(json_data.get('files', {}).keys())[0]
                    st.success(f"✅ {import_project_name} projesi başarıyla import edildi!")
                    update_and_save_projects()  # <-- Bunu ekle!
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ JSON dosyası okuma hatası: {str(e)}")
    
    # Python dosyası yükleme
    st.subheader("📄 Python Dosyası Yükle")
    uploaded_py = st.file_uploader(
        "Python dosyası yükle",
        type=['py'],
        help="Mevcut projeye Python dosyası ekleyin"
    )
    
    if uploaded_py is not None:
        try:
            # Python dosyasını oku
            file_content = uploaded_py.read().decode('utf-8')
            file_name = uploaded_py.name
            
            if st.button(f"📥 {file_name} dosyasını ekle"):
                # Dosya var mı kontrol et
                if file_name in st.session_state.projects[st.session_state.active_project]['files']:
                    if st.checkbox(f"⚠️ {file_name} zaten var. Üzerine yaz?"):
                        st.session_state.projects[st.session_state.active_project]['files'][file_name] = file_content
                        st.session_state.active_file = file_name
                        st.success(f"✅ {file_name} dosyası güncellendi!")
                        update_and_save_projects()
                        st.rerun()
                else:
                    st.session_state.projects[st.session_state.active_project]['files'][file_name] = file_content
                    st.session_state.active_file = file_name
                    st.success(f"✅ {file_name} dosyası eklendi!")
                    update_and_save_projects()
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Python dosyası okuma hatası: {str(e)}")
    
    # Toplu proje import
    st.subheader("📦 Toplu İmport")
    uploaded_zip = st.file_uploader(
        "ZIP dosyası yükle",
        type=['zip'],
        help="Birden fazla Python dosyası içeren ZIP dosyası yükleyin"
    )
    
    if uploaded_zip is not None:
        try:
            with zipfile.ZipFile(uploaded_zip, 'r') as zip_file:
                python_files = [f for f in zip_file.namelist() if f.endswith('.py')]
                
                if python_files:
                    st.write(f"📄 Bulunan Python dosyaları: {len(python_files)}")
                    for py_file in python_files:
                        st.write(f"• {py_file}")
                    
                    zip_project_name = st.text_input(
                        "ZIP projesi adı",
                        value=uploaded_zip.name.replace('.zip', '')
                    )
                    
                    if st.button("📥 ZIP Projesini İmport Et") and zip_project_name:
                        project_key = zip_project_name.lower().replace(' ', '_').replace('-', '_')
                        if project_key in st.session_state.projects:
                            st.warning("⚠️ Bu isimde bir proje zaten var!")
                        else:
                            # Yeni proje oluştur
                            new_project_files = {}
                            
                            for py_file in python_files:
                                file_content = zip_file.read(py_file).decode('utf-8')
                                file_name = os.path.basename(py_file)  # Sadece dosya adını al
                                new_project_files[file_name] = file_content
                            
                            st.session_state.projects[project_key] = {
                                'name': zip_project_name,
                                'files': new_project_files
                            }
                            st.session_state.active_project = project_key
                            st.session_state.active_file = list(new_project_files.keys())[0]
                            st.success(f"✅ {zip_project_name} projesi ({len(python_files)} dosya) başarıyla import edildi!")
                            update_and_save_projects()  # <-- Bunu ekle!
                            st.rerun()
                else:
                    st.warning("⚠️ ZIP dosyasında Python dosyası bulunamadı!")
                    
        except Exception as e:
            st.error(f"❌ ZIP dosyası okuma hatası: {str(e)}")

# Ana içerik alanı
current_project = st.session_state.projects[st.session_state.active_project]
current_file_content = current_project['files'][st.session_state.active_file]

# Proje bilgileri
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(f"### 📁 {current_project['name']}")
with col2:
    st.markdown(f"**📄 Dosya:** `{st.session_state.active_file}`")
with col3:
    if st.button("🔄 Sayfayı Yenile"):
        st.rerun()

# Tab'lar
tab1, tab2, tab3 = st.tabs(["✏️ Kod Editörü", "👁️ Önizleme", "📊 Analiz"])

with tab1:
    st.subheader(f"📝 {st.session_state.active_file} - Kod Editörü")
    
    # Kod editörü
    edited_code = st.text_area(
        "Kod",
        value=current_file_content,
        height=500,
        help="Python kodunuzu buraya yazın",
        label_visibility="collapsed"
    )
    
    # Kod güncelleme
    if edited_code != current_file_content:
        if st.button("💾 Değişiklikleri Kaydet"):
            st.session_state.projects[st.session_state.active_project]['files'][st.session_state.active_file] = edited_code
            update_and_save_projects()
            st.success("✅ Kod başarıyla kaydedildi!")
            st.rerun()
    
    # Kod kopyalama
    st.code(current_file_content, language='python')
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Kodu Kopyala"):
            st.code(current_file_content, language='python')
            st.info("💡 Yukarıdaki kod bloğundan kopyalayabilirsiniz")
    
    with col2:
        # Dosya indirme
        st.download_button(
            label="📁 Dosyayı İndir",
            data=current_file_content,
            file_name=st.session_state.active_file,
            mime="text/plain"
        )

with tab2:
    st.subheader("👁️ Kod Önizlemesi")
    
    st.markdown("""
    <div class="success-box">
        <h4>🚀 Streamlit'te Çalıştırma Talimatları:</h4>
        <ol>
            <li>Kodu kopyalayın veya dosyayı indirin</li>
            <li>Yeni bir .py dosyası oluşturup yapıştırın</li>
            <li><code>streamlit run dosya_adi.py</code> komutu ile çalıştırın</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Kod syntax highlighting
    st.code(current_file_content, language='python')

with tab3:
    st.subheader("📊 Kod Analizi")
    
    # Kod istatistikleri
    lines = current_file_content.split('\n')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📏 Toplam Satır", len(lines))
    
    with col2:
        non_empty_lines = len([line for line in lines if line.strip()])
        st.metric("📝 Kod Satırları", non_empty_lines)
    
    with col3:
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        st.metric("💬 Yorum Satırları", comment_lines)
    
    with col4:
        import_lines = len([line for line in lines if line.strip().startswith(('import ', 'from '))])
        st.metric("📦 Import Satırları", import_lines)
    
    # Import analizi
    imports = [line.strip() for line in lines if line.strip().startswith(('import ', 'from '))]
    if imports:
        st.subheader("📦 Kullanılan Kütüphaneler")
        for imp in imports:
            st.code(imp, language='python')

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🚀 <strong>Streamlit Kodlama Arayüzü</strong> | Tab geçişli proje yönetimi</p>
    <p>💡 Projelerinizi organize edin, kodlayın ve test edin!</p>
</div>
""", unsafe_allow_html=True)

st.subheader("🔧 Proje İşlemleri")

if 'project_delete_confirm' not in st.session_state:
    st.session_state.project_delete_confirm = False

if not st.session_state.project_delete_confirm:
    if st.button("🗑️ Projeyi Sil"):
        if len(st.session_state.projects) > 1:
            st.session_state.project_delete_confirm = True
        else:
            st.warning("⚠️ En az bir proje kalmalı!")
else:
    if st.checkbox("Projeyi silmek istediğinize emin misiniz?"):
        if st.button("Evet, Projeyi Sil"):
            projeler = st.session_state.projects
            aktif = st.session_state.active_project
            # Projeyi sil
            del projeler[aktif]
            # Yeni aktif proje ata
            yeni_aktif = list(projeler.keys())[0]
            st.session_state.active_project = yeni_aktif
            st.session_state.active_file = list(projeler[yeni_aktif]['files'].keys())[0]
            st.success("✅ Proje silindi!")
            update_and_save_projects()
            st.session_state.project_delete_confirm = False
            st.rerun()
    if st.button("Vazgeç", key="projeyi_sil_vazgec"):
        st.session_state.project_delete_confirm = False