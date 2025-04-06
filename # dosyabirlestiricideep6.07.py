# dosyabirlestiricigrk6.07.py
# 2025 Nisan 05 - Gelişmiş Dosya Birleştirici GRK+deepseek6.07
# Tüm hata yönetimleri, testler ve optimizasyonlar ile tam sürüm
# Geliştirici: GRK+deepseek: zuhtu mete Dinler
# zmetedinler@gmail.com
# github: /metedinler/dosyabirlestirici

import os
import sys
import re
import subprocess
import logging
import csv
import shutil
import math
from datetime import datetime
from multiprocessing import Pool, cpu_count
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import importlib.util
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import json
import argparse

# Gerekli modülleri kontrol et ve yükle
def install_packages():
    required_modules = [
        "autopep8", "black", "flake8", "pylint", "pydeps", "pyan", 
        "graphviz", "chardet", "python-dotenv", "coverage"
    ]
    for mod in required_modules:
        if importlib.util.find_spec(mod) is None:
            print(f"{mod} bulunamadı, yükleniyor...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", mod])
                print(f"{mod} başarıyla yüklendi.")
            except subprocess.CalledProcessError as e:
                print(f"{mod} yüklenemedi: {e}")
        else:
            print(f"{mod} zaten yüklü.")

install_packages()
import chardet
from ast import parse, FunctionDef, ClassDef, Import, ImportFrom, If, For, While, Try, Expr, Str
from dotenv import load_dotenv, set_key

# Sabitler
DEFAULT_OUTPUT = "combined_content.txt"
DEFAULT_LIST = "file_list.txt"
DEFAULT_EXT = [".py"]
ENCODING_OPTIONS = {
    "1": ("utf-8", "Unicode (UTF-8)"),
    "2": ("windows-1254", "Windows Türkçe (Windows-1254)"),
    "3": ("ascii", "İngilizce (ASCII)"),
    "4": ("latin-1", "Latin-1"),
    "5": ("utf-8", "BOM'suz UTF-8"),  # Varsayılan
    "6": ("utf-8-sig", "UTF-8-SIG")
}
LOG_FILE_TEMPLATE = "{}_analysis_log_{}.txt"
ERROR_LOG_TEMPLATE = "{}_hata_raporu.txt"
TEST_RESULTS_FILE = "test_results.json"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
# Sabitler kısmına son kullanılan ayarları saklamak için dosya adı ekleyelim
CONFIG_FILE = "dosyabirlestirici_config.json"

### 0. Argüman İşleme Modülü ###
def arg_parser():
    
    #Komut satırı argümanlarını işler ve config dosyasını yönetir
    # Config dosyası varsa yükle
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Config dosyası okunamadı: {e}")
    
    p = argparse.ArgumentParser(description="Gelişmiş Dosya Birleştirici GRK-deep 6.07 - Dosya analizi ve birleştirme aracı")
    p.add_argument("folder", nargs="?", help="İşlenecek klasör tam yolu")
    p.add_argument("-l", "--list", default=DEFAULT_LIST, help="Dosya listesi adı")
    p.add_argument("-o", "--output", default=DEFAULT_OUTPUT, help="Birleştirilmiş dosya adı")
    p.add_argument("-e", "--ext", nargs="*", default=DEFAULT_EXT, help="Filtrelenecek uzantılar")
    p.add_argument("-n", "--nosubdirs", action="store_true", help="Alt klasörleri tarama")
    p.add_argument("-a", "--append", action="store_true", help="Dosyalara ekle")
    p.add_argument("-f", "--fixcode", action="store_true", help="Kod formatlama")
    p.add_argument("-ft", "--fixtool", choices=["autopep8", "black"], default="black", help="Format aracı")
    p.add_argument("-lt", "--linttool", choices=["flake8", "pylint"], default="flake8", help="Lint aracı")
    p.add_argument("-d", "--depmap", action="store_true", help="Bağımlılık analizi")
    p.add_argument("-dt", "--deptool", choices=["pydeps", "pyan"], default="pydeps", help="Bağımlılık aracı")
    p.add_argument("-mb", "--maxbacon", type=int, help="pydeps max bacon")
    p.add_argument("-pu", "--pyanuses", action="store_true", help="pyan --uses")
    p.add_argument("-pd", "--pyandefines", action="store_true", help="pyan --defines")
    p.add_argument("-pc", "--pyancolored", action="store_true", help="pyan --colored")
    p.add_argument("-ob", "--openbrowser", action="store_true", help="Grafiği tarayıcıda aç")
    p.add_argument("-eb", "--envbul", action="store_true", help="env_bulucu12.py çalıştır")
    p.add_argument("-mx", "--mbaix", action="store_true", help="mbaix4.py çalıştır")
    p.add_argument("-m", "--mp", action="store_true", help="Multiprocessing kullan")
    p.add_argument("-t", "--thread", action="store_true", help="Threading kullan")
    p.add_argument("-enc", "--encoding", default="5", help="Kodlama seçimi (1-6)")
    p.add_argument("-bl", "--blackline", type=int, default=120, help="Black satır uzunluğu")
    p.add_argument("-aa", "--autoagg", type=int, choices=[0, 1, 2], default=1, help="Autopep8 agresiflik")
    p.add_argument("-fm", "--flakemax", type=int, default=120, help="Flake8 max satır uzunluğu")
    p.add_argument("-mp", "--mbaxpath", default=None, help="mbaix4.py yolu")
    p.add_argument("-ep", "--envpath", default=None, help="env_olusturucu12.py yolu")
    p.add_argument("-h2", "--help2", action="store_true", help="Detaylı yardım")
    
    args = p.parse_args()
    # Config dosyasını güncelle
    config.update({
        'folder': args.folder,
        'output': args.output,
        # Diğer ayarlar...
    })
    
    if args.help2:
        print("""
        Detaylı Yardım:
        - folder: İşlenecek klasörün tam yolu (örn: /path/to/folder)
        - -l, --list: Dosya listesi adı (varsayılan: file_list.txt)
        - -o, --output: Birleştirilmiş dosya adı (varsayılan: combined_content.txt)
        - -e, --ext: Filtrelenecek uzantılar (örn: .py .txt)
        - -n, --nosubdirs: Alt klasörleri tarama (kapalıysa tüm klasörler taranır)
        - -a, --append: Dosyalara ekle (varsayılan: üzerine yazar)
        - -f, --fixcode: Kod formatlama yap
        - -ft, --fixtool: Format aracı (autopep8 veya black)
        - -lt, --linttool: Lint aracı (flake8 veya pylint)
        - -d, --depmap: Bağımlılık analizi yap
        - -dt, --deptool: Bağımlılık aracı (pydeps veya pyan)
        - -mb, --maxbacon: pydeps için max bacon değeri
        - -pu, --pyanuses: pyan --uses seçeneği
        - -pd, --pyandefines: pyan --defines seçeneği
        - -pc, --pyancolored: pyan --colored seçeneği
        - -ob, --openbrowser: Grafiği tarayıcıda aç
        - -eb, --envbul: env_bulucu12.py çalıştır
        - -mx, --mbaix: mbaix4.py çalıştır
        - -m, --mp: Multiprocessing kullan
        - -t, --thread: Threading kullan
        - -enc, --encoding: Kodlama seçimi (1-6, varsayılan: 5)
        - -bl, --blackline: Black satır uzunluğu (varsayılan: 120)
        - -aa, --autoagg: Autopep8 agresiflik (0-2, varsayılan: 1)
        - -fm, --flakemax: Flake8 max satır uzunluğu (varsayılan: 120)
        - -mp, --mbaxpath: mbaix4.py tam yolu
        - -ep, --envpath: env_olusturucu12.py tam yolu
        Örnek: python dosyabirlestiricigrk6.py /path -l list.txt -o output.txt -e .py -m -t
        """)
        sys.exit(0)
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Config dosyası yazılamadı: {e}")
        
    return args

# Loglama ayarları
def setup_logging(folder_path):
    """Loglama sistemini başlatır ve log dosyalarını oluşturur"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(folder_path, "birlesikdosyalar")
        os.makedirs(output_dir, exist_ok=True)
        log_file = os.path.join(output_dir, LOG_FILE_TEMPLATE.format(os.path.basename(folder_path), timestamp))
        error_file = os.path.join(output_dir, ERROR_LOG_TEMPLATE.format(os.path.basename(folder_path)))
        
        # Loglamayı sıfırdan yapılandır
        logging.getLogger().handlers = []  # Eski handler'ları temizle
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler()  # Konsola da yaz
            ]
        )
        error_handler = logging.FileHandler(error_file, encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logging.getLogger().addHandler(error_handler)
        
        logging.info(f"Loglama başlatıldı: {log_file}")
        return log_file, error_file
    except Exception as e:
        print(f"Loglama kurulumu başarısız: {e}")
        return None, None

### 1. Kodlama Tespit Modülü ###
def detect_encoding(file_path):
    """Dosyanın kodlamasını tespit eder"""
    try:
        if not os.path.exists(file_path):
            logging.error(f"Dosya bulunamadı: {file_path}")
            return "utf-8"
            
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            logging.warning(f"Büyük dosya ({file_size/1024/1024:.2f}MB), kısmi okuma yapılıyor: {file_path}")
            with open(file_path, "rb") as f:
                rawdata = f.read(1024*1024)  # İlk 1MB'ı oku
        else:
            with open(file_path, "rb") as f:
                rawdata = f.read()
                
        result = chardet.detect(rawdata)
        encoding = result["encoding"] if result["encoding"] else "utf-8"
        confidence = result["confidence"] if "confidence" in result else 0
        logging.info(f"{file_path} için kodlama: {encoding} (güven: {confidence:.2%})")
        return encoding
    except PermissionError:
        logging.error(f"Dosya okuma izni reddedildi: {file_path}")
        return "utf-8"
    except Exception as e:
        logging.error(f"{file_path} kodlama tespiti başarısız: {e}")
        return "utf-8"

### 2. Dosya İşleme ve Analiz Modülü ###
def analyze_python_file(file_path, encoding):
    """Python dosyasını analiz ederek detaylı bilgiler çıkarır"""
    logging.info(f"{file_path} analiz ediliyor")
    try:
        # Dosya boyutu kontrolü
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            logging.warning(f"Büyük Python dosyası ({file_size/1024/1024:.2f}MB), analiz atlanabilir: {file_path}")
            return None

        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            content = f.read()
        
        lines = content.splitlines()
        comment_lines = sum(1 for line in lines if line.strip().startswith("#") or not line.strip())
        no_comment_lines = len(lines) - comment_lines
        
        try:
            tree = parse(content)
            classes = {
                node.name: [n.name for n in node.body if isinstance(n, FunctionDef)] 
                for node in tree.body if isinstance(node, ClassDef)
            }
            standalone_funcs = [node.name for node in tree.body if isinstance(node, FunctionDef)]
            module_name = os.path.basename(file_path).replace(".py", "")
            
            # Fonksiyon kodlarını topla
            func_codes = {}
            for node in tree.body:
                if isinstance(node, FunctionDef):
                    start_line = node.lineno - 1
                    end_line = node.end_lineno
                    func_codes[node.name] = "\n".join(lines[start_line:end_line])
                elif isinstance(node, ClassDef):
                    for sub_node in node.body:
                        if isinstance(sub_node, FunctionDef):
                            start_line = sub_node.lineno - 1
                            end_line = sub_node.end_lineno
                            func_codes[sub_node.name] = "\n".join(lines[start_line:end_line])
            
            # Import ifadelerini topla
            imports = []
            for node in tree.body:
                if isinstance(node, Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ImportFrom):
                    module = node.module if node.module else ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            # Ortam değişkenlerini ve DB bağlantılarını bul
            env_vars = []
            for i, line in enumerate(lines):
                if "os.environ" in line:
                    match = re.search(r'os\.environ\[["\']([^"\']+)["\']\]', line)
                    if match:
                        comment = line.split("#", 1)[1].strip() if "#" in line else ""
                        env_vars.append((match.group(1), comment))
            
            db_connections = re.findall(r'(?:mysql|postgresql|sqlite|oracle|mssql)://\S+', content)
            
            logging.info(f"{file_path} başarıyla analiz edildi")
            return (
                module_name, classes, standalone_funcs, comment_lines, 
                no_comment_lines, content, func_codes, imports, 
                env_vars, db_connections
            )
            
        except SyntaxError as e:
            logging.error(f"{file_path} sözdizimi hatası: {e}")
            return None
        except ValueError as e:
            logging.error(f"{file_path} değer hatası: {e}")
            return None
        except Exception as e:
            logging.error(f"{file_path} ayrıştırma hatası: {e}")
            return None
            
    except UnicodeDecodeError:
        logging.error(f"{file_path} kodlama hatası (kullanılan encoding: {encoding})")
        return None
    except PermissionError:
        logging.error(f"{file_path} okuma izni reddedildi")
        return None
    except Exception as e:
        logging.error(f"{file_path} okunamadı: {e}")
        return None

def process_single_file(file_path, extensions, encoding):
    """Tek bir dosyayı işler ve içeriğini döndürür"""
    try:
        if not isinstance(file_path, str) or not os.path.exists(file_path):
            logging.error(f"Geçersiz dosya yolu: {file_path}")
            return None, None
            
        if not any(file_path.endswith(ext) for ext in extensions):
            logging.info(f"{file_path} belirtilen uzantılarda değil, atlanıyor")
            return None, None
            
        detected_enc = detect_encoding(file_path)
        if not detected_enc:
            logging.warning(f"{file_path} için kodlama tespit edilemedi, varsayılan utf-8 kullanılıyor")
            detected_enc = "utf-8"
            
        with open(file_path, "r", encoding=detected_enc, errors="replace") as f:
            content = f.read()
            
        uncommented = remove_comments(content)
        if not isinstance(uncommented, str):
            logging.error(f"{file_path} için remove_comments string döndürmedi: {uncommented}")
            uncommented = ""
            
        logging.info(f"{file_path} başarıyla işlendi")
        return f"# {file_path}\n{content}\n", uncommented + "\n"
        
    except Exception as e:
        logging.error(f"{file_path} işlenirken hata: {e}")
        return None, None

def code_quality_analysis(file_path, encoding):
    """Kod kalitesi metriklerini hesaplar"""
    logging.info(f"{file_path} kalite analizi yapılıyor")
    try:
        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            content = f.read()
            lines = content.splitlines()
            total_lines = len(lines)
            comment_lines = sum(1 for line in lines if line.strip().startswith("#") or not line.strip())
            code_lines = total_lines - comment_lines
            comment_ratio = (comment_lines / total_lines * 100) if total_lines > 0 else 0

            tree = parse(content)
            classes = [node for node in tree.body if isinstance(node, ClassDef)]
            funcs = [node for node in tree.body if isinstance(node, FunctionDef)]
            imports = [node for node in tree.body if isinstance(node, (Import, ImportFrom))]
            try_blocks = sum(1 for node in tree.body if hasattr(node, "handlers") and node.handlers)

            complexity = 1  # Temel karmaşıklık
            for node in tree.body:
                if isinstance(node, (FunctionDef, ClassDef)):
                    complexity += sum(1 for n in node.body if isinstance(n, (If, For, While, Try)))
                    
            avg_lines_per_func = sum(node.end_lineno - node.lineno + 1 for node in funcs) / len(funcs) if funcs else 0
            docstring_count = sum(1 for node in funcs if node.body and isinstance(node.body[0], Expr) and isinstance(node.body[0].value, Str))
            test_funcs = sum(1 for node in funcs if node.name.startswith("test_"))

            # Tekrar eden satırları bul
            unique_lines = set(lines)
            duplication = sum(1 for line in unique_lines if lines.count(line) > 1) / total_lines if total_lines else 0
            
            # Bakım indeksi hesapla (171-5.2*ln(ort_satır)-0.23*karmaşıklık-16.2*ln(toplam_satır))
            maintainability = 171 - 5.2 * math.log(avg_lines_per_func or 1) - 0.23 * complexity - 16.2 * math.log(total_lines or 1)
            
            # Test kapsamı (basit bir yaklaşım)
            coverage = (docstring_count + test_funcs) / len(funcs) if funcs else 0

            logging.info(f"{file_path} kalite analizi tamamlandı")
            return {
                "total_lines": (total_lines, "Toplam kod satırı sayısı"),
                "comment_ratio": (comment_ratio, "Yorum oranı yüksekse kod daha okunabilir olur"),
                "class_count": (len(classes), "Sınıf sayısı, kodun nesne yönelimli yapısını gösterir"),
                "func_count": (len(funcs), "Fonksiyon sayısı, kodun modülerliğini belirtir"),
                "import_count": (len(imports), "Dış bağımlılıkların sayısı"),
                "try_blocks": (try_blocks, "Hata yönetimi yoğunluğu"),
                "complexity": (complexity, "Düşük karmaşıklık daha az hata riski demektir"),
                "duplication": (duplication, "Kod tekrarı az olmalı, bakım zorlaşır"),
                "maintainability": (maintainability, "Yüksek değer bakım kolaylığı sağlar"),
                "coverage": (coverage, "Test kapsayıcılığı yüksekse güvenilirlik artar")
            }
    except SyntaxError as e:
        logging.error(f"{file_path} sözdizimi hatası: {e}")
        return None
    except Exception as e:
        logging.error(f"{file_path} kalite analizi başarısız: {e}")
        return None

def process_files(folder_path, output_list_file, output_content_file, extensions, include_subdirs, overwrite_content, encoding, use_mp=False):
    """Tüm dosyaları işler ve çıktıları üretir"""
    logging.info(f"process_files başlıyor: {folder_path}")
    
    try:
        # Giriş doğrulama
        if not os.path.isdir(folder_path):
            raise ValueError(f"Geçersiz klasör yolu: {folder_path}")
            
        output_dir = os.path.join(folder_path, "birlesikdosyalar")
        os.makedirs(output_dir, exist_ok=True)
        log_file, error_file = setup_logging(folder_path)
        
        if not log_file or not error_file:
            raise RuntimeError("Log dosyaları oluşturulamadı")

        # Dosya listesini oluştur
        file_paths = []
        if include_subdirs:
            for root, _, files in os.walk(folder_path):
                for fn in files:
                    if any(fn.endswith(ext) for ext in extensions):
                        file_path = os.path.join(root, fn)
                        file_paths.append(file_path)
        else:
            for fn in os.listdir(folder_path):
                if os.path.isfile(os.path.join(folder_path, fn)) and any(fn.endswith(ext) for ext in extensions):
                    file_paths.append(os.path.join(folder_path, fn))
                    
        if not file_paths:
            logging.warning("İşlenecek dosya bulunamadı")
            return

        logging.info(f"İşlenecek {len(file_paths)} dosya bulundu")
        
        folder_name = os.path.basename(os.path.normpath(folder_path))
        analysis_data = {}
        quality_data = {}
        
        # Değişkenleri başlat
        commented_content = []
        uncommented_content = []
        
        # Çoklu işlem veya tekli işlem seçeneği
        if use_mp:
            with Pool(min(cpu_count(), 4)) as pool:  # Maksimum 4 çekirdek kullan
                # Python dosyalarını analiz et
                py_files = [fp for fp in file_paths if fp.endswith(".py")]
                if py_files:
                    analysis_results = pool.starmap(analyze_python_file, [(fp, encoding) for fp in py_files])
                    quality_results = pool.starmap(code_quality_analysis, [(fp, encoding) for fp in py_files])
                    
                    for fp, result in zip(py_files, analysis_results):
                        if result is not None:
                            analysis_data[fp] = result
                            
                    for fp, q_data in zip(py_files, quality_results):
                        if q_data is not None:
                            quality_data[fp] = q_data
                
                # Tüm dosyaları işle
                results = pool.starmap(process_single_file, [(fp, extensions, encoding) for fp in file_paths])
                for comm, uncomm in results:
                    if comm: commented_content.append(comm)
                    if uncomm: uncommented_content.append(uncomm)
        else:
            for fp in file_paths:
                if fp.endswith(".py"):
                    analysis_result = analyze_python_file(fp, encoding)
                    quality_result = code_quality_analysis(fp, encoding)
                    if analysis_result is not None:
                        analysis_data[fp] = analysis_result
                    if quality_result is not None:
                        quality_data[fp] = quality_result
                
                comm, uncomm = process_single_file(fp, extensions, encoding)
                if comm: commented_content.append(comm)
                if uncomm: uncommented_content.append(uncomm)

        # Dosya listesini yaz
        list_path = os.path.join(output_dir, f"{folder_name}_{output_list_file}")
        try:
            with open(list_path, "w", encoding=encoding) as fl:
                for fp in file_paths:
                    try:
                        size_kb = os.path.getsize(fp) / 1024
                        fl.write(f"{os.path.basename(fp)}\t\t{size_kb:.2f} KB\n")
                    except OSError as e:
                        logging.error(f"{fp} boyutu alınamadı: {e}")
                        fl.write(f"{os.path.basename(fp)}\t\tBoyut bilinmiyor\n")
        except IOError as e:
            logging.error(f"Dosya listesi yazılamadı: {e}")
            raise

        # İçerik dosyalarını yaz
        mode = "w" if overwrite_content else "a"
        for comment_state in ["yorumlu", "yorumsuz"]:
            for ext in [".txt", ".py"]:
                content_path = os.path.join(output_dir, f"{folder_name}_{output_content_file}_{comment_state}{ext}")
                try:
                    with open(content_path, mode, encoding=encoding) as fc:
                        if overwrite_content:
                            fc.write(f"# {folder_name} ({comment_state.capitalize()})\n\n")
                        content = commented_content if comment_state == "yorumlu" else uncommented_content
                        fc.write("\n".join(content))
                except IOError as e:
                    logging.error(f"{content_path} yazılamadı: {e}")
                    continue

        # Ek raporları oluştur
        generate_statistics(output_dir, folder_name, file_paths, analysis_data, quality_data, encoding)
        generate_csv(output_dir, folder_name, file_paths, analysis_data, quality_data, encoding)
        generate_dependency_map(folder_path)
        
        logging.info(f"Çıktılar '{output_dir}' altına kaydedildi.")
        
    except Exception as e:
        logging.error(f"process_files başarısız: {e}")
        raise

### 3. İstatistik ve Raporlama Modülü ###
def generate_statistics(output_dir, folder_name, file_paths, analysis_data, quality_data, encoding):
    """İstatistik raporları oluşturur"""
    logging.info("generate_statistics başlıyor")
    
    try:
        # Çıktı dosya yolları
        stats_file = os.path.join(output_dir, f"{folder_name}_istatistik.txt")
        req_file = os.path.join(output_dir, f"{folder_name}_gereksinim.txt")
        env_file = os.path.join(output_dir, f"{folder_name}_cevresel.txt")
        alpha_file = os.path.join(output_dir, f"{folder_name}_alfabetik.txt")
        func_detail_file = os.path.join(output_dir, f"{folder_name}_fonksiyon_detay.txt")
        complexity_file = os.path.join(output_dir, f"{folder_name}_karmasiklik_raporu.txt")
        func_lib_file = os.path.join(output_dir, f"{folder_name}_toplu_fonksiyonlar_kod_kutuphanesi.txt")
        func_alt_file = os.path.join(output_dir, f"{folder_name}_fonksiyon_kutuphanesi.txt")

        # Toplam istatistikleri hesapla
        total_stats = {
            "total_lines": 0, "comment_ratio": 0, "class_count": 0, 
            "func_count": 0, "import_count": 0, "try_blocks": 0,
            "complexity": 0, "duplication": 0, "maintainability": 0, 
            "coverage": 0
        }
        imports = set()
        env_vars = set()
        all_funcs = []
        py_file_count = 0

        for fp in file_paths:
            if fp.endswith(".py") and fp in analysis_data and fp in quality_data:
                py_file_count += 1
                data = analysis_data[fp]
                q = quality_data[fp]
                
                # İstatistikleri topla
                for k in total_stats:
                    value = q[k][0] if isinstance(q[k], tuple) else q[k]
                    total_stats[k] += value
                
                # Import ve env değişkenlerini topla
                imports.update(data[7])
                env_vars.update(f"{var} # {desc}" for var, desc in data[8])
                
                # Fonksiyon bilgilerini topla
                for cls, funcs in data[1].items():
                    all_funcs.extend(f"{data[0]}.{cls}.{func}" for func in funcs)
                all_funcs.extend(f"{data[0]}.{func}" for func in data[2])

        # Ortalamaları hesapla
        if py_file_count > 0:
            for k in total_stats:
                if k not in ["comment_ratio", "duplication", "maintainability", "coverage"]:
                    total_stats[k] = total_stats[k] / py_file_count

        # İstatistik dosyasını yaz
        try:
            with open(stats_file, "w", encoding=encoding) as f:
                f.write(f"# {folder_name} İstatistikleri\n\n")
                f.write(f"Analiz edilen Python dosyası sayısı: {py_file_count}\n")
                
                for k, v in total_stats.items():
                    desc = quality_data[next(iter(quality_data))][k][1] if quality_data and py_file_count > 0 else ""
                    if k == "comment_ratio":
                        f.write(f"Yorum satırı oranı: {v:.1f}% ({desc})\n")
                    elif k == "duplication":
                        f.write(f"Kod tekrar oranı: {v:.1%} ({desc})\n")
                    elif k == "maintainability":
                        f.write(f"Bakım indeksi: {v:.1f} ({desc})\n")
                    elif k == "coverage":
                        f.write(f"Test kapsamı: {v:.1%} ({desc})\n")
                    else:
                        f.write(f"{k.replace('_', ' ').title()}: {v:.1f} ({desc})\n")
                
                f.write("\n# Kod Optimizasyon Önerileri\n")
                if total_stats["complexity"] > 10: 
                    f.write("- Yüksek karmaşıklık tespit edildi, fonksiyonlar bölünebilir.\n")
                if total_stats["duplication"] > 0.1: 
                    f.write("- Kod tekrarı var, ortak fonksiyonlar oluşturulabilir.\n")
                if total_stats["maintainability"] < 65: 
                    f.write("- Bakım indeksi düşük, kod refaktör edilmeli.\n")
                if total_stats["coverage"] < 0.3: 
                    f.write("- Test kapsamı düşük, birim testleri eklenmeli.\n")
        except IOError as e:
            logging.error(f"İstatistik dosyası yazılamadı: {e}")

        # Diğer rapor dosyalarını yaz
        try:
            with open(req_file, "w", encoding=encoding) as f:
                f.write("\n".join(sorted(imports)))
        except IOError as e:
            logging.error(f"Gereksinim dosyası yazılamadı: {e}")

        try:
            with open(env_file, "w", encoding=encoding) as f:
                f.write("\n".join(sorted(env_vars)))
        except IOError as e:
            logging.error(f"Çevresel değişken dosyası yazılamadı: {e}")

        try:
            with open(alpha_file, "w", encoding=encoding) as f:
                all_modules = sorted(set(data[0] for data in analysis_data.values()))
                all_classes = sorted(set(cls for data in analysis_data.values() for cls in data[1]))
                unique_funcs = sorted(set(all_funcs))
                
                f.write("# Modüller\n")
                for i, mod in enumerate(all_modules, 1):
                    f.write(f"{i:02d}. {mod}\n")
                
                f.write("\n# Sınıflar\n")
                for i, cls in enumerate(all_classes, 1):
                    f.write(f"{i:02d}. {cls}\n")
                
                f.write("\n# Fonksiyonlar\n")
                for i, func in enumerate(unique_funcs, 1):
                    f.write(f"{i:03d}. {func}\n")
        except IOError as e:
            logging.error(f"Alfabetik liste dosyası yazılamadı: {e}")

        # Fonksiyon detay raporu
        try:
            with open(func_detail_file, "w", encoding=encoding) as f:
                for fp in file_paths:
                    if fp.endswith(".py") and fp in analysis_data and fp in quality_data:
                        q = quality_data[fp]
                        module_info = analysis_data[fp]
                        f.write(f"\n=== Dosya: {fp} ===\n")
                        
                        # Sınıf fonksiyonları
                        for cls, funcs in module_info[1].items():
                            for func in funcs:
                                func_code = module_info[6].get(func, "")
                                lines = len(func_code.splitlines()) if func_code else 0
                                complexity = q['complexity'][0]/q['func_count'][0] if q['func_count'][0] else 0
                                has_doc = '"""' in func_code.splitlines()[0] if func_code and len(func_code.splitlines()) > 0 else False
                                
                                f.write(f"{cls}.{func}:\n")
                                f.write(f"  Satır sayısı: {lines}\n")
                                f.write(f"  Karmaşıklık: {complexity:.2f}\n")
                                f.write(f"  Docstring: {'Var' if has_doc else 'Yok'}\n")
                                f.write(f"  Bakım indeksi: {q['maintainability'][0]:.1f}\n\n")
                        
                        # Bağımsız fonksiyonlar
                        for func in module_info[2]:
                            func_code = module_info[6].get(func, "")
                            lines = len(func_code.splitlines()) if func_code else 0
                            complexity = q['complexity'][0]/q['func_count'][0] if q['func_count'][0] else 0
                            has_doc = '"""' in func_code.splitlines()[0] if func_code and len(func_code.splitlines()) > 0 else False
                            
                            f.write(f"{func}:\n")
                            f.write(f"  Satır sayısı: {lines}\n")
                            f.write(f"  Karmaşıklık: {complexity:.2f}\n")
                            f.write(f"  Docstring: {'Var' if has_doc else 'Yok'}\n")
                            f.write(f"  Bakım indeksi: {q['maintainability'][0]:.1f}\n\n")
        except IOError as e:
            logging.error(f"Fonksiyon detay dosyası yazılamadı: {e}")

        # Karmaşıklık raporu
        try:
            with open(complexity_file, "w", encoding=encoding) as f:
                f.write("Kod Karmaşıklık Raporu\n")
                f.write("=====================\n\n")
                
                for fp in file_paths:
                    if fp.endswith(".py") and fp in quality_data:
                        q = quality_data[fp]
                        f.write(f"Dosya: {fp}\n")
                        f.write(f"  Toplam karmaşıklık: {q['complexity'][0]:.1f}\n")
                        f.write(f"  Fonksiyon başına ortalama: {q['complexity'][0]/q['func_count'][0] if q['func_count'][0] else 0:.2f}\n")
                        f.write(f"  Bakım indeksi: {q['maintainability'][0]:.1f}\n\n")
        except IOError as e:
            logging.error(f"Karmaşıklık raporu yazılamadı: {e}")

        # Fonksiyon kütüphanesi
        all_funcs_data = []
        for fp, data in analysis_data.items():
            for class_name, funcs in data[1].items():
                for func in funcs:
                    all_funcs_data.append((
                        func, class_name, data[0], folder_name, 
                        data[6].get(func, "")
                    ))
            for func in data[2]:
                all_funcs_data.append((
                    func, "", data[0], folder_name, 
                    data[6].get(func, "")
                ))
        
        all_funcs_data.sort()
        
        try:
            with open(func_lib_file, "w", encoding=encoding) as ff:
                for func_name, class_name, module_name, program_name, func_code in all_funcs_data:
                    ff.write(f"=== {func_name} ===\n")
                    ff.write(f"Modül: {module_name}\n")
                    ff.write(f"Sınıf: {class_name}\n")
                    ff.write(f"Program: {program_name}\n\n")
                    ff.write(f"{func_code}\n\n")
        except IOError as e:
            logging.error(f"Fonksiyon kütüphanesi yazılamadı: {e}")

        # Alternatif fonksiyon kütüphanesi (daha basit format)
        try:
            shutil.copy(func_lib_file, func_alt_file)
        except IOError as e:
            logging.error(f"Alternatif fonksiyon kütüphanesi oluşturulamadı: {e}")

        logging.info("generate_statistics tamamlandı")
        
    except Exception as e:
        logging.error(f"generate_statistics başarısız: {e}")
        raise

def generate_csv(output_dir, folder_name, file_paths, analysis_data, quality_data, encoding):
    """CSV formatında raporlar oluşturur"""
    logging.info("generate_csv başlıyor")
    
    try:
        simple_csv = os.path.join(output_dir, f"{folder_name}_tumfonk.tablo.csv")
        detailed_csv = os.path.join(output_dir, f"{folder_name}_detailed_analysis.csv")

        simple_data = [["Modül", "Sınıf", "Fonksiyon"]]
        detailed_data = [["Modül", "Sınıf", "Fonksiyon", "Bağımlılıklar", "Karmaşıklık", 
                         "Satır Sayısı", "Docstring", "Açıklama", "Bakım İndeksi"]]

        for fp in file_paths:
            if fp.endswith(".py") and fp in analysis_data and fp in quality_data:
                module_info = analysis_data[fp]
                q = quality_data[fp]
                module_name, classes, standalone_funcs, _, _, _, func_codes, imports, _, _ = module_info
                
                # Sınıf fonksiyonları
                for class_name, funcs in classes.items():
                    for func in funcs:
                        simple_data.append([module_name, class_name, func])
                        
                        func_code = func_codes.get(func, "")
                        lines = len(func_code.splitlines()) if func_code else 0
                        complexity = q['complexity'][0]/q['func_count'][0] if q['func_count'][0] else 0
                        has_doc = '"""' in func_code.splitlines()[0] if func_code and len(func_code.splitlines()) > 0 else False
                        
                        detailed_data.append([
                            module_name, class_name, func, 
                            ",".join(imports), f"{complexity:.2f}",
                            lines, "Var" if has_doc else "Yok", 
                            "Analiz edildi", f"{q['maintainability'][0]:.1f}"
                        ])
                
                # Bağımsız fonksiyonlar
                for func in standalone_funcs:
                    simple_data.append([module_name, "", func])
                    
                    func_code = func_codes.get(func, "")
                    lines = len(func_code.splitlines()) if func_code else 0
                    complexity = q['complexity'][0]/q['func_count'][0] if q['func_count'][0] else 0
                    has_doc = '"""' in func_code.splitlines()[0] if func_code and len(func_code.splitlines()) > 0 else False
                    
                    detailed_data.append([
                        module_name, "", func, 
                        ",".join(imports), f"{complexity:.2f}",
                        lines, "Var" if has_doc else "Yok", 
                        "Analiz edildi", f"{q['maintainability'][0]:.1f}"
                    ])

        # CSV dosyalarını yaz
        try:
            with open(simple_csv, "w", encoding=encoding, newline="") as f:
                writer = csv.writer(f)
                writer.writerows(simple_data)
        except IOError as e:
            logging.error(f"Basit CSV yazılamadı: {e}")

        try:
            with open(detailed_csv, "w", encoding=encoding, newline="") as f:
                writer = csv.writer(f)
                writer.writerows(detailed_data)
        except IOError as e:
            logging.error(f"Detaylı CSV yazılamadı: {e}")

        logging.info("generate_csv tamamlandı")
        
    except Exception as e:
        logging.error(f"generate_csv başarısız: {e}")
        raise

def generate_dependency_map(folder_path):
    """Bağımlılık haritası oluşturur"""
    logging.info("generate_dependency_map başlıyor")
    
    try:
        output_dir = os.path.join(folder_path, "birlesikdosyalar")
        os.makedirs(output_dir, exist_ok=True)
        html_file = os.path.join(output_dir, "deps.html")
        
        try:
            result = subprocess.run(
                # pydeps proje/main.py -T png -o dependencies.png --noshow
                ["pydeps", folder_path, "-T png -o dependencies.png --noshow"], 
                capture_output=True, text=True
            )
            if result.returncode != 0:
                logging.error(f"pydeps hatası: {result.stderr}")
            else:
                logging.info("Bağımlılık haritası oluşturuldu")
        except FileNotFoundError:
            logging.error("pydeps bulunamadı, lütfen yükleyin: pip install pydeps")
        except Exception as e:
            logging.error(f"Bağımlılık haritası oluşturulamadı: {e}")
            
    except Exception as e:
        logging.error(f"generate_dependency_map başarısız: {e}")
        raise

### 4. Yardımcı Fonksiyonlar ###
def remove_comments(content):
    """Koddan yorumları temizler"""
    try:
        if not isinstance(content, str):
            raise TypeError(f"Beklenen string, alınan {type(content)}")
            
        # Tek satır yorumları kaldır
        content = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
        
        # Çok satırlı docstring'leri kaldır
        content = re.sub(r'""".*?"""', '', content, flags=re.DOTALL)
        content = re.sub(r"'''.*?'''", '', content, flags=re.DOTALL)
        
        # Boş satırları filtrele
        return "\n".join(line for line in content.splitlines() if line.strip())
        
    except Exception as e:
        logging.error(f"remove_comments başarısız: {e}")
        return content  # Hata durumunda orijinal içeriği döndür

def fix_code_and_lint(folder_path, fix_tool, lint_tool, use_thread=False):
    """Kod formatlama ve linting işlemlerini yürütür"""
    messages = []
    threads = []
    
    def run_tool(cmd, label):
        try:
            proc = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                timeout=300  # 5 dakika zaman aşımı
            )
            msg = f"{label} çalıştırıldı:\n{proc.stdout}"
            if proc.stderr:
                msg += f"\nHatalar:\n{proc.stderr}"
            messages.append(msg)
            logging.info(f"{label} tamamlandı")
        except subprocess.TimeoutExpired:
            msg = f"{label} zaman aşımına uğradı"
            messages.append(msg)
            logging.warning(msg)
        except Exception as e:
            msg = f"{label} hatası: {str(e)}"
            messages.append(msg)
            logging.error(msg)

    # Kod formatlama araçları
    if fix_tool == "black":
        cmd = ["black", folder_path, "--line-length", "120", "--quiet"]
        if use_thread:
            t = threading.Thread(target=run_tool, args=(cmd, "black"))
            threads.append(t)
            t.start()
        else:
            run_tool(cmd, "black")
    elif fix_tool == "autopep8":
        cmd = ["autopep8", "--in-place", "--aggressive", "--recursive", 
               "--max-line-length=120", folder_path]
        if use_thread:
            t = threading.Thread(target=run_tool, args=(cmd, "autopep8"))
            threads.append(t)
            t.start()
        else:
            run_tool(cmd, "autopep8")

    # Linting araçları
    if lint_tool == "flake8":
        cmd = ["flake8", folder_path, "--max-line-length=120", "--statistics"]
        if use_thread:
            t = threading.Thread(target=run_tool, args=(cmd, "flake8"))
            threads.append(t)
            t.start()
        else:
            run_tool(cmd, "flake8")
    elif lint_tool == "pylint":
        cmd = ["pylint", folder_path, "--disable=line-too-long", "--output-format=text"]
        if use_thread:
            t = threading.Thread(target=run_tool, args=(cmd, "pylint"))
            threads.append(t)
            t.start()
        else:
            run_tool(cmd, "pylint")

    # Thread'lerin bitmesini bekle
    for t in threads:
        t.join()
        
    return "\n".join(messages)

def dep_analysis(folder_path, dep_tool, open_browser, extra_params=None):
    """Bağımlılık analizi yapar"""
    extra_params = extra_params or {}
    output_dir = os.path.join(folder_path, "birlesikdosyalar")
    messages = []
    
    try:
        os.makedirs(output_dir, exist_ok=True)

        if dep_tool == "pydeps":
            svg_file = os.path.join(output_dir, f"{os.path.basename(folder_path)}_deps.svg")
            cmd = ["pydeps", folder_path, "--output", svg_file]
            
            if "max_bacon" in extra_params:
                cmd.append(f"--max-bacon={extra_params['max_bacon']}")
                
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                messages.append(f"pydeps çıktısı:\n{proc.stdout}")
                if proc.stderr:
                    messages.append(f"pydeps hataları:\n{proc.stderr}")
                    
                if open_browser and os.path.exists(svg_file):
                    try:
                        import webbrowser
                        webbrowser.open(svg_file)
                    except Exception as e:
                        messages.append(f"Tarayıcı açma hatası: {e}")
            except subprocess.TimeoutExpired:
                messages.append("pydeps zaman aşımına uğradı")
            except Exception as e:
                messages.append(f"pydeps çalıştırma hatası: {e}")

        elif dep_tool == "pyan":
            dot_file = os.path.join(output_dir, "cikti.dot")
            svg_file = os.path.join(output_dir, "cikti.svg")
            cmd = ["pyan", folder_path, "--dot"]
            
            for param, flag in [("uses", "--uses"), ("defines", "--defines"), ("colored", "--colored")]:
                if extra_params.get(param):
                    cmd.append(flag)
                    
            try:
                # .dot dosyasını oluştur
                with open(dot_file, "w", encoding="utf-8") as f:
                    proc = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, timeout=300)
                    if proc.stderr:
                        messages.append(f"pyan hataları:\n{proc.stderr}")
                
                # SVG'ye dönüştür
                if os.path.exists(dot_file):
                    subprocess.run(["dot", "-Tsvg", dot_file, "-o", svg_file], 
                                 capture_output=True, text=True, timeout=300)
                    
                    if open_browser and os.path.exists(svg_file):
                        try:
                            import webbrowser
                            webbrowser.open(svg_file)
                        except Exception as e:
                            messages.append(f"Tarayıcı açma hatası: {e}")
            except subprocess.TimeoutExpired:
                messages.append("pyan zaman aşımına uğradı")
            except Exception as e:
                messages.append(f"pyan çalıştırma hatası: {e}")

        return "\n".join(messages)
        
    except Exception as e:
        logging.error(f"dep_analysis başarısız: {e}")
        return f"Hata: {str(e)}"

def call_external_tools(folder_path, tools_config, mbax_path, env_path, use_thread=False):
    """Harici araçları çağırır"""
    messages = []
    threads = []
    
    try:
        # Ortam değişkenlerini yükle
        load_dotenv("dbenv.env")
        
        # Yolları ayarla
        MBAIX_PATH = tools_config.get("mbaxpath") or os.getenv("MBAIX_PATH", "mbaix4.py")
        ENV_PATH = tools_config.get("envpath") or os.getenv("ENV_PATH", "env_olusturucu12.py")
        
        if tools_config.get("mbaix") and mbax_path and mbax_path != MBAIX_PATH:
            set_key("dbenv.env", "MBAIX_PATH", mbax_path)
            MBAIX_PATH = mbax_path
            
        if tools_config.get("envbul") and env_path and env_path != ENV_PATH:
            set_key("dbenv.env", "ENV_PATH", env_path)
            ENV_PATH = env_path

        def run_tool(cmd, label):
            try:
                proc = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True,
                    timeout=600  # 10 dakika zaman aşımı
                )
                msg = f"{label} çıktısı:\n{proc.stdout}"
                if proc.stderr:
                    msg += f"\nHatalar:\n{proc.stderr}"
                messages.append(msg)
                logging.info(f"{label} tamamlandı")
            except subprocess.TimeoutExpired:
                msg = f"{label} zaman aşımına uğradı"
                messages.append(msg)
                logging.warning(msg)
            except Exception as e:
                msg = f"{label} hatası: {str(e)}"
                messages.append(msg)
                logging.error(msg)

        # ENV_BUL aracı
        if tools_config.get("envbul") and os.path.exists(ENV_PATH):
            cmd = ["python", ENV_PATH, "--directory", folder_path, "--ext", "py"]
            if use_thread:
                t = threading.Thread(target=run_tool, args=(cmd, "env_bulucu12.py"))
                threads.append(t)
                t.start()
            else:
                run_tool(cmd, "env_bulucu12.py")

        # MBAIX aracı
        if tools_config.get("mbaix") and os.path.exists(MBAIX_PATH):
            cmd = ["python", MBAIX_PATH, "--klasor", folder_path, "--nogui"]
            if use_thread:
                t = threading.Thread(target=run_tool, args=(cmd, "mbaix4.py"))
                threads.append(t)
                t.start()
            else:
                run_tool(cmd, "mbaix4.py")

        # Thread'lerin bitmesini bekle
        for t in threads:
            t.join()
            
        return "\n".join(messages)
        
    except Exception as e:
        logging.error(f"call_external_tools başarısız: {e}")
        return f"Hata: {str(e)}"

### 5. Test Modülü ###
class TestFileCombiner(unittest.TestCase):
    """Dosya birleştirici için unit testler"""
    
    @classmethod
    def setUpClass(cls):
        """Testler için geçici bir klasör ve dosyalar oluştur"""
        cls.test_dir = tempfile.mkdtemp()
        cls.sample_files = []
        
        # Örnek Python dosyaları oluştur
        py_content = """# test.py
import os

class TestClass:
    def method1(self):
        \"\"\"Docstring\"\"\"
        return 42
        
def func1():
    return True
"""
        cls.create_test_file("test1.py", py_content)
        cls.create_test_file("test2.py", py_content.replace("test.py", "test2.py"))
        cls.create_test_file("empty.py", "")
        cls.create_test_file("not_py.txt", "Bu bir Python dosyası değil")
        
        # Loglama için çıktı dizini
        cls.output_dir = os.path.join(cls.test_dir, "birlesikdosyalar")
        
    @classmethod
    def tearDownClass(cls):
        """Test klasörünü temizle"""
        shutil.rmtree(cls.test_dir)
    
    @classmethod
    def create_test_file(cls, filename, content):
        """Test dosyası oluştur"""
        filepath = os.path.join(cls.test_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        cls.sample_files.append(filepath)
        return filepath
    
    def setUp(self):
        """Her test öncesi logları temizle"""
        logging.getLogger().handlers = []
    
    def test_detect_encoding(self):
        """Kodlama tespiti testi"""
        # UTF-8 dosya oluştur
        utf8_file = os.path.join(self.test_dir, "utf8.txt")
        with open(utf8_file, "w", encoding="utf-8") as f:
            f.write("Merhaba dünya")
            
        encoding = detect_encoding(utf8_file)
        self.assertEqual(encoding.lower(), "utf-8")
        
        # Olmayan dosya
        encoding = detect_encoding("olmayan_dosya.txt")
        self.assertEqual(encoding, "utf-8")
    
    def test_analyze_python_file(self):
        """Python dosya analizi testi"""
        result = analyze_python_file(self.sample_files[0], "utf-8")
        self.assertIsNotNone(result)
        
        module_name, classes, funcs, _, _, _, _, _, _, _ = result
        self.assertEqual(module_name, "test1")
        self.assertIn("TestClass", classes)
        self.assertIn("method1", classes["TestClass"])
        self.assertIn("func1", funcs)
        
        # Geçersiz dosya
        result = analyze_python_file("olmayan_dosya.py", "utf-8")
        self.assertIsNone(result)
    
    def test_process_files(self):
        """Dosya işleme testi"""
        # Multiprocessing olmadan test
        process_files(
            self.test_dir, "test_list.txt", "test_output.txt", 
            [".py"], True, True, "utf-8", False
        )
        
        # Çıktı dosyalarını kontrol et
        output_files = [
            "test_output.txt_yorumlu.txt",
            "test_output.txt_yorumsuz.txt",
            "test_list.txt",
            "istatistik.txt",
            "tumfonk.tablo.csv"
        ]
        
        for f in output_files:
            path = os.path.join(self.output_dir, f"test_{f}")
            self.assertTrue(os.path.exists(path), f"{path} bulunamadı")
            
        # Multiprocessing ile test
        process_files(
            self.test_dir, "test_list_mp.txt", "test_output_mp.txt", 
            [".py"], True, True, "utf-8", True
        )
        
    def test_code_quality_analysis(self):
        """Kod kalite analizi testi"""
        result = code_quality_analysis(self.sample_files[0], "utf-8")
        self.assertIsNotNone(result)
        
        self.assertIn("total_lines", result)
        self.assertIn("complexity", result)
        self.assertGreater(result["func_count"][0], 0)
        
        # Geçersiz dosya
        result = code_quality_analysis("olmayan_dosya.py", "utf-8")
        self.assertIsNone(result)
    
    def test_remove_comments(self):
        """Yorum kaldırma testi"""
        content = """# Bu bir yorum
print("Merhaba")  # Satır sonu yorumu
\"\"\"Çok satırlı
yorum\"\"\"
'''
Başka bir çok satırlı yorum
'''
"""
        cleaned = remove_comments(content)
        self.assertNotIn("# Bu bir yorum", cleaned)
        self.assertNotIn("# Satır sonu yorumu", cleaned)
        self.assertNotIn("Çok satırlı", cleaned)
        self.assertNotIn("Başka bir çok satırlı yorum", cleaned)
        self.assertIn('print("Merhaba")', cleaned)
        
        # Geçersiz giriş
        with self.assertRaises(TypeError):
            remove_comments(123)

    def test_generate_statistics(self):
        """İstatistik üretme testi"""
        # Analiz verilerini hazırla
        analysis_data = {}
        quality_data = {}
        
        for fp in self.sample_files[:2]:  # İlk iki Python dosyası
            if fp.endswith(".py"):
                analysis_data[fp] = analyze_python_file(fp, "utf-8")
                quality_data[fp] = code_quality_analysis(fp, "utf-8")
        
        generate_statistics(
            self.output_dir, "test_stats", 
            self.sample_files, analysis_data, quality_data, "utf-8"
        )
        
        # Çıktı dosyalarını kontrol et
        stat_files = [
            "test_stats_istatistik.txt",
            "test_stats_gereksinim.txt",
            "test_stats_cevresel.txt",
            "test_stats_alfabetik.txt"
        ]
        
        for f in stat_files:
            path = os.path.join(self.output_dir, f)
            self.assertTrue(os.path.exists(path), f"{path} bulunamadı")

### 6. GUI Modülü ###
class FileCombinerGUI:
    """Dosya birleştirici GUI sınıfı"""
    
    def __init__(self, root):
        self.root = root
        # Config dosyasını yükle
        self.config = self.load_config()
        
        # Değişkenleri config'ten al
        self.folder_var = tk.StringVar(value=self.config.get('folder', ''))
        self.output_var = tk.StringVar(value=self.config.get('output', DEFAULT_OUTPUT))
        # PROGRAMIN KENDISI
        self.root.title("Dosya Birleştirici CHATGPT+GROK+DEEPSEEK=++ME 6.07")
        self.root.geometry("800x600")
        
        # Ana çerçeve
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Klasör seçimi
        ttk.Label(main_frame, text="Klasör:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.folder_var = tk.StringVar()
        folder_entry = ttk.Entry(main_frame, textvariable=self.folder_var, width=50)
        folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(main_frame, text="Gözat", command=self.browse_folder).grid(row=0, column=2, pady=2)
        
        # Çıktı ayarları
        ttk.Label(main_frame, text="Çıktı Dosya Adı:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.output_var = tk.StringVar(value=DEFAULT_OUTPUT)
        ttk.Entry(main_frame, textvariable=self.output_var, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(main_frame, text="Uzantılar:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.ext_var = tk.StringVar(value=" ".join(DEFAULT_EXT))
        ttk.Entry(main_frame, textvariable=self.ext_var, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(main_frame, text="Kodlama:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.encoding_var = tk.StringVar(value="5")
        encoding_combo = ttk.Combobox(
            main_frame, textvariable=self.encoding_var, 
            values=[f"{k}: {v[1]}" for k, v in ENCODING_OPTIONS.items()],
            state="readonly", width=50
        )
        encoding_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        # Seçenekler
        options_frame = ttk.LabelFrame(main_frame, text="Seçenekler", padding="5")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.subdirs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Alt Klasörleri Tara", variable=self.subdirs_var).grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.append_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Üzerine Yaz", variable=self.append_var).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        self.mp_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Multiprocessing", variable=self.mp_var).grid(row=0, column=2, sticky=tk.W, padx=5)
        
        self.thread_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Threading", variable=self.thread_var).grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # Harici araçlar
        tools_frame = ttk.LabelFrame(main_frame, text="Harici Araçlar", padding="5")
        tools_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.tools_vars = {
            "envbul": tk.BooleanVar(), "mbaix": tk.BooleanVar(), 
            "black": tk.BooleanVar(), "autopep8": tk.BooleanVar(), 
            "flake8": tk.BooleanVar(), "pylint": tk.BooleanVar(),
            "pydeps": tk.BooleanVar(), "pyan": tk.BooleanVar()
        }
        
        # Araçları 4 sütuna yerleştir
        for i, (tool, var) in enumerate(self.tools_vars.items()):
            ttk.Checkbutton(
                tools_frame, text=tool.capitalize(), 
                variable=var
            ).grid(row=i//4, column=i%4, sticky=tk.W, padx=5)
        
        # Yol ayarları
        ttk.Label(main_frame, text="MBAIX Yolu:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.mbaxpath_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.mbaxpath_var, width=50).grid(row=6, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(main_frame, text="Gözat", command=lambda: self.browse_file(self.mbaxpath_var)).grid(row=6, column=2, pady=2)
        
        ttk.Label(main_frame, text="ENV Yolu:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.envpath_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.envpath_var, width=50).grid(row=7, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(main_frame, text="Gözat", command=lambda: self.browse_file(self.envpath_var)).grid(row=7, column=2, pady=2)
        
        # Çalıştır butonu
        ttk.Button(main_frame, text="Çalıştır", command=self.run).grid(row=8, column=1, pady=10)
        
        # Log alanı
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
        
        # Grid yapılandırması
        main_frame.columnconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Başlangıç mesajı
        self.log("Dosya Birleştirici CHATGPT+GROK+DEEPSEEK=++ME 6.07 başlatıldı. Lütfen bir klasör seçin.")
    
    def browse_folder(self):
        """Klasör seçme dialogunu açar"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)
            self.log(f"Seçilen klasör: {folder}")
    
    def browse_file(self, var):
        """Dosya seçme dialogunu açar"""
        file = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if file:
            var.set(file)
            self.log(f"Seçilen dosya: {file}")
    
    def log(self, message):
        """Log mesajını ekrana ve log alanına yazar"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        print(log_message.strip())
    
    def validate_inputs(self):
        """Girişleri doğrular"""
        folder_path = self.folder_var.get()
        output_file = self.output_var.get()
        
        if not folder_path:
            messagebox.showerror("Hata", "Lütfen bir klasör seçin!")
            return False
            
        if not os.path.isdir(folder_path):
            messagebox.showerror("Hata", "Geçersiz klasör yolu!")
            return False
            
        if not output_file:
            messagebox.showerror("Hata", "Çıktı dosya adı belirtmelisiniz!")
            return False
            
        # Araç yollarını kontrol et
        tools_config = {k: v.get() for k, v in self.tools_vars.items()}
        if tools_config.get("mbaix") and not self.mbaxpath_var.get():
            messagebox.showerror("Hata", "MBAIX için yol belirtmelisiniz!")
            return False
            
        if tools_config.get("envbul") and not self.envpath_var.get():
            messagebox.showerror("Hata", "ENV oluşturucu için yol belirtmelisiniz!")
            return False
            
        return True
    
    def run(self):
        """Ana işlemi başlatır"""
        if not self.validate_inputs():
            return
            
        try:
            # Parametreleri al
            folder_path = self.folder_var.get()
            output_file = self.output_var.get()
            extensions = self.ext_var.get().split() or DEFAULT_EXT
            encoding_key = self.encoding_var.get().split(":")[0].strip()
            encoding = ENCODING_OPTIONS.get(encoding_key, ENCODING_OPTIONS["5"])[0]
            
            include_subdirs = self.subdirs_var.get()
            overwrite_content = self.append_var.get()
            use_mp = self.mp_var.get()
            use_thread = self.thread_var.get()
            
            tools_config = {k: v.get() for k, v in self.tools_vars.items()}
            tools_config["mbaxpath"] = self.mbaxpath_var.get()
            tools_config["envpath"] = self.envpath_var.get()
            
            self.log("İşlem başlatılıyor...")
            
            # Dosyaları işle
            process_files(
                folder_path, DEFAULT_LIST, output_file, 
                extensions, include_subdirs, overwrite_content, 
                encoding, use_mp
            )
            
            # Harici araçları çalıştır
            if any(tools_config.values()):
                self.log("Harici araçlar çalıştırılıyor...")
                
                # Kod formatlama ve linting
                if tools_config.get("black") or tools_config.get("autopep8") or tools_config.get("flake8") or tools_config.get("pylint"):
                    fix_tool = "black" if tools_config.get("black") else "autopep8" if tools_config.get("autopep8") else None
                    lint_tool = "flake8" if tools_config.get("flake8") else "pylint" if tools_config.get("pylint") else None
                    
                    result = fix_code_and_lint(folder_path, fix_tool, lint_tool, use_thread)
                    self.log(f"Kod düzenleme sonucu:\n{result}")
                
                # Bağımlılık analizi
                if tools_config.get("pydeps") or tools_config.get("pyan"):
                    dep_tool = "pydeps" if tools_config.get("pydeps") else "pyan"
                    result = dep_analysis(folder_path, dep_tool, False)
                    self.log(f"Bağımlılık analizi sonucu:\n{result}")
                
                # Diğer araçlar
                if tools_config.get("envbul") or tools_config.get("mbaix"):
                    result = call_external_tools(
                        folder_path, tools_config, 
                        tools_config["mbaxpath"], tools_config["envpath"], 
                        use_thread
                    )
                    self.log(f"Harici araç sonucu:\n{result}")
            
            # Log dosyasını göster
            log_file, _ = setup_logging(folder_path)
            if log_file and os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    self.log("\nİşlem logları:\n" + f.read())
            
            messagebox.showinfo("Başarılı", "İşlem tamamlandı!")
            self.log("İşlem başarıyla tamamlandı.")
            
        except Exception as e:
            import traceback
            error_msg = f"İşlem başarısız: {str(e)}\n{traceback.format_exc()}"
            self.log(error_msg)
            messagebox.showerror("Hata", error_msg)
    def load_config(self):
        # Config dosyasını yükler
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Config dosyası okunamadı: {e}")
        return {}
        
    def save_config(self):
        # Config dosyasını kaydeder
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'folder': self.folder_var.get(),
                    'output': self.output_var.get(),
                    # Diğer ayarlar...
                }, f, indent=2)
        except Exception as e:
            print(f"Config dosyası yazılamadı: {e}")



### 7. Ana Modül ###

def load_config():
    """Config dosyasını yükler"""
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            logging.error(f"Config dosyası okunamadı: {e}")
    return config

def save_config(config):
    """Config dosyasını kaydeder"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logging.error(f"Config dosyası yazılamadı: {e}")

def run_in_command_line_mode(args):
    """Komut satırı modunda işlemleri yürütür"""
    try:
        logging.info(f"Komut satırı modunda çalıştırılıyor: {args.folder}")
        
        # Kodlama seçimi
        encoding_info = ENCODING_OPTIONS.get(args.encoding, ENCODING_OPTIONS["5"])
        encoding = encoding_info[0]
        
        # Temel dosya işleme
        process_files(
            args.folder, args.list, args.output, 
            args.ext, not args.nosubdirs, args.append, 
            encoding, args.mp
        )
        
        # Kod formatlama
        if args.fixcode:
            logging.info(f"Kod formatlama yapılıyor ({args.fixtool})")
            fix_code_and_lint(args.folder, args.fixtool, args.linttool, args.thread)
        
        # Bağımlılık analizi
        if args.depmap:
            logging.info(f"Bağımlılık analizi yapılıyor ({args.deptool})")
            extra_params = {
                "max_bacon": args.maxbacon,
                "uses": args.pyanuses,
                "defines": args.pyandefines,
                "colored": args.pyancolored
            }
            dep_analysis(args.folder, args.deptool, args.openbrowser, extra_params)
        
        # Harici araçlar
        if args.envbul or args.mbaix:
            logging.info("Harici araçlar çalıştırılıyor")
            tools_config = {
                "envbul": args.envbul,
                "mbaix": args.mbaix,
                "mbaxpath": args.mbaxpath,
                "envpath": args.envpath
            }
            call_external_tools(args.folder, tools_config, args.mbaxpath, args.envpath, args.thread)
        
        logging.info("İşlem başarıyla tamamlandı")
        return True
    
    except Exception as e:
        logging.error(f"Komut satırı modunda hata: {str(e)}")
        return False
def run_tests():
    """Unit testleri çalıştırır ve sonuçları kaydeder"""
    print("Unit testleri çalıştırılıyor...")
    
    # Test suite oluştur
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestFileCombiner)
    
    # Test sonuçlarını JSON'a kaydetmek için özel bir test runner
    class JSONTestRunner(unittest.TextTestRunner):
        def run(self, test):
            result = super().run(test)
            
            # Sonuçları topla
            test_results = {
                "testsRun": result.testsRun,
                "errors": len(result.errors),
                "failures": len(result.failures),
                "skipped": len(result.skipped),
                "successful": result.testsRun - len(result.errors) - len(result.failures)
            }
            
            # JSON dosyasına yaz
            with open(TEST_RESULTS_FILE, "w") as f:
                json.dump(test_results, f, indent=2)
                
            return result
    
    # Testleri çalıştır
    runner = JSONTestRunner(verbosity=2)
    runner.run(test_suite)
    
    print(f"Test sonuçları {TEST_RESULTS_FILE} dosyasına kaydedildi.")

def main():
    # Ana uygulama giriş noktası
        
    # Test modunda mı çalışıyor kontrol et
    if "--test" in sys.argv:
        run_tests()
        return

    # Config yükle
    config = load_config()
    
    # Argumanlari parse et
    args = arg_parser()
    
    # Config'i güncelle
    new_config = {
        'folder': args.folder if args.folder else config.get('folder', ''),
        'output': args.output,
        'ext': args.ext,
        'nosubdirs': args.nosubdirs,
        'append': args.append,
        'encoding': args.encoding,
        'mp': args.mp,
        'thread': args.thread,
        'fixcode': args.fixcode,
        'fixtool': args.fixtool,
        'linttool': args.linttool,
        'depmap': args.depmap,
        'deptool': args.deptool,
        'envbul': args.envbul,
        'mbaix': args.mbaix
    }
    save_config(new_config)
    
    # Komut satırı modu
    # if args.folder and os.path.isdir(args.folder):
    #     success = run_in_command_line_mode(args)
    #     sys.exit(0 if success else 1)
   
    # Eğer klasör argümanı verilmişse doğrudan işlemi başlat
    if args.folder and os.path.isdir(args.folder):
        try:
            print(f"Komut satırı modunda çalıştırılıyor: {args.folder}")
            process_files(
                args.folder, args.list, args.output, 
                args.ext, not args.nosubdirs, args.append, 
                ENCODING_OPTIONS.get(args.encoding, ENCODING_OPTIONS["5"])[0], 
                args.mp
            )
            return
        except Exception as e:
            print(f"Hata: {e}")
            sys.exit(1)
    
#     # GUI'yi başlat
#     root = tk.Tk()
#     try:
#         # Windows için taskbar ikonu
#         if sys.platform == "win32":
#             import ctypes
#             ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("DosyaBirleştirici.GRK6.04")
        
#         # Stil ayarları
#         style = ttk.Style()
#         style.theme_use("clam")
#         style.configure("TButton", padding=6)
#         style.configure("TLabel", padding=2)
#         style.configure("TEntry", padding=2)
        
#         app = FileCombinerGUI(root)
#         root.mainloop()
#     except Exception as e:
#         print(f"GUI başlatılamadı: {e}")
#         sys.exit(1)

# if __name__ == "__main__":
#     main()

    # GUI modu
    root = tk.Tk()
    try:
        # Windows için taskbar ikonu
        if sys.platform == "win32":
            try:
                import ctypes
                myappid = 'DosyaBirleştirici.GRK6.04'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception as e:
                logging.warning(f"Taskbar ikonu ayarlanamadı: {e}")
        
        # Stil ayarları
        style = ttk.Style()
        available_themes = style.theme_names()
        preferred_themes = ['clam', 'alt', 'default', 'vista']
        selected_theme = next((t for t in preferred_themes if t in available_themes), available_themes[0])
        style.theme_use(selected_theme)
        
        # Pencere boyutu ve konumu
        root.geometry("900x700")
        if sys.platform == "win32":
            root.state('zoomed')  # Windows'ta tam ekran başlat
        
        # GUI'yi başlat
        app = FileCombinerGUI(root)
        
        # Config'ten gelen klasörü yükle
        if config.get('folder') and os.path.isdir(config['folder']):
            app.folder_var.set(config['folder'])
            app.log(f"Önceki klasör yüklendi: {config['folder']}")
        
        root.mainloop()
        
    except Exception as e:
        logging.error(f"GUI başlatılamadı: {str(e)}")
        messagebox.showerror("Hata", f"GUI başlatılamadı:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Loglama ayarları (konsol çıktısı için)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('dosyabirlestirici.log', encoding='utf-8')
        ]
    )
    
    # Ana fonksiyonu çalıştır
    try:
        main()
    except Exception as e:
        logging.error(f"Kritik hata: {str(e)}", exc_info=True)
        sys.exit(1)