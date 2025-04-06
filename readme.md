##Dosya Birleştirici ve Kod Analiz Aracı##

Bu proje, Python dosyalarını tarayarak dosya adlarını listeleyen, içeriklerini birleştiren ve ek olarak dosyaların kod kalitesini, yapısını, bağımlılıklarını ve çevresel ayarlarını analiz eden gelişmiş bir araçtır. Hem komut satırından (CLI) hem de GUI (grafik arayüz) modunda çalışabilmektedir.

Özellikler
Dosya Tarama ve Birleştirme:

Belirtilen klasör (ve alt klasörler) içerisinde belirli uzantıya sahip dosyaları tarar.

Dosya adlarını bir liste dosyası (ör. file_list.txt) oluşturur.

Dosya içeriklerini, orijinal (yorumlu) ve yorumlardan arındırılmış (yorumsuz) versiyonlarıyla birleştirir.

Kod Analizi:

Her Python dosyası için AST (Soyut Sözdizimi Ağacı) kullanılarak modül, sınıf ve fonksiyon bilgileri çıkarılır.

Kod kalitesi metrikleri; toplam satır sayısı, yorum oranı, fonksiyon/sınıf sayısı, hata yönetimi (try-except) gibi değerler hesaplanır.

Import ifadeleri, çevresel değişken kullanımları ve veritabanı bağlantıları tespit edilir.

Kod Düzeltme ve Linting:

Seçilebilir olarak autopep8 veya black kullanılarak kod formatlama yapılabilir.

flake8 veya pylint kullanılarak kod kalitesi raporu alınabilir.

Bağımlılık Analizi:

pydeps veya pyan gibi araçlar kullanılarak dosya bağımlılık grafiği oluşturulur ve isteğe bağlı olarak tarayıcıda görüntülenebilir.

Grafik Arayüz (GUI):

Tkinter tabanlı basit bir arayüz ile kullanıcı dostu girdi alma seçenekleri.

Argümanlar komut satırından verilebildiği gibi GUI üzerinden de girilebilir.

Loglama ve Konfigürasyon:

İşlem adımları ve hatalar log dosyaları aracılığıyla kaydedilir.

Son kullanılan ayarlar dosyabirlestirici_config.json dosyasında saklanır.

Kurulum
Öncelikle, projenin gerektirdiği modüllerin kurulu olduğundan emin olun. Eksik modüller otomatik olarak yüklenmeye çalışılmakta, fakat aşağıdaki modülleri pip ile kurmanız gerekebilir:

bash
Kopyala
Düzenle
pip install autopep8 black flake8 pylint pydeps pyan graphviz chardet python-dotenv coverage
Kullanım
Komut Satırı (CLI) Modu
Aşağıdaki örnek komut, /path/to/folder klasöründeki dosyaları tarayarak kod formatlama, linting ve bağımlılık analiz işlemlerini gerçekleştirir:

bash
Kopyala
Düzenle
python dosyabirlestirici.py /path/to/folder --fix-code --fix-tool black --lint-tool flake8 --dep-map --dep-tool pydeps
Ek parametreler:

--max-bacon: pydeps için maksimum bacon değeri.

--pyan-uses, --pyan-defines, --pyan-colored: pyan seçenekleri.

--open-browser: Oluşan bağımlılık grafiğini tarayıcıda açar.

Grafik Arayüz (GUI) Modu
GUI modunu başlatmak için:

bash
Kopyala
Düzenle
python dosyabirlestirici.py --gui
GUI modunda, kullanıcıdan dizin, dosya listesi ve içerik dosyası adları, filtrelenecek uzantılar, alt klasör dahil etme, ekleme/üzerine yazma ve kodlama seçenekleri gibi bilgiler alınır.

Üretilen Çıktılar
Proje çalıştırıldığında, hedef klasör altında birlesikdosyalar adlı bir klasör oluşturulur. Bu klasörde:

Dosya listesi dosyası (ör. file_list.txt)

Birleştirilmiş içerik dosyaları (hem yorumlu hem yorumsuz, .txt ve .py formatlarında)

İstatistik raporu (<klasör_adı>_istatistik.txt)

Fonksiyon kütüphanesi raporu (<klasör_adı>_toplu_fonksiyonlar_kod_kutuphanesi.txt)

Gereksinim ve çevresel değişken dosyaları (<klasör_adı>.gereksinim.txt, <klasör_adı>.cevresel.txt)

Bağımlılık grafiği (SVG formatında, pydeps/pyan tarafından oluşturulan)

Daha detaylı bilgi için README ve yardım ekranını inceleyebilirsiniz.

Analiz detayları için dosyabirlestirici.py dosyasında yer alan argüman işleme kısmı örneğin;

────────────────────────────── programcinin_not_defteri.md ──────────────────────────────

Programcının Not Defteri
Bu doküman, dosyabirlestirici projesinin detaylı iş akışını, kullanılan modülleri, sınıfları, fonksiyonları ve üretilen dosya yapılarını anlatmaktadır.

1. Proje Genel Yapısı
Proje, dosya tarama, içerik birleştirme, kod analizi, kod formatlama ve bağımlılık analiz işlemlerini gerçekleştiren bir dizi modül ve fonksiyondan oluşur. Ana dosya (örneğin, dosyabirlestirici.py) kullanıcıdan CLI argümanları alır, gerekli modülleri çağırır ve ilgili işlemleri başlatır. Projede ayrıca GUI tabanlı kullanıcı girişi sağlayan gui_app modülü de bulunmaktadır.

Ana argüman işleme kısmı, CLI ve GUI modlarını birbirinden ayırmak için argparse ile gerçekleştirilmekte;

2. Temel Fonksiyonlar ve İşlevleri
2.1. Dosya Tarama ve Birleştirme
process_files() Fonksiyonu:

Girdi: Klasör yolu, dosya listesi adı, içerik dosyası adı, uzantı filtreleri, alt klasörlerin dahil edilip edilmeyeceği, içerik üzerine yazma veya ekleme tercihi, encoding seçeneği.

İş Akışı:

Hedef klasör altında birlesikdosyalar adlı çıktı klasörü oluşturulur.

Belirtilen klasör (ve alt klasörler) taranarak, uzantıya uygun dosyaların isimleri ve yolları toplanır.

Her dosya için orijinal içerik okunur; dosya listesi dosyası oluşturularak dosya isimleri yazılır.

İçerik dosyaları iki versiyonda üretilir:

Yorumlu (yorumlar dahil): Her dosyanın tam içeriği, dosya adı başlıklarıyla birlikte eklenir.

Yorumsuz (yorumlar temizlenmiş): remove_comments() fonksiyonu ile yorumlar kaldırılarak içerik birleştirilir.

Üretilen Dosyalar:

Dosya listesi (ör. file_list.txt)

Birleştirilmiş içerik dosyaları (ör. combined_content_yorumlu.txt, combined_content_yorumsuz.py)

2.2. Kod Analizi
analyze_python_file() Fonksiyonu:

Amaç: Python dosyalarını AST kullanarak analiz eder.

Çıktılar:

Modul adı

Sınıf ve fonksiyon listeleri (sınıf içinde tanımlı fonksiyonlar ve bağımsız fonksiyonlar)

Dosyadaki yorum satırı sayısı ve yorum dışı satır sayısı

Fonksiyonların tam kodları (satır aralıklarına göre)

Import ifadeleri, çevresel değişken kullanımları ve veritabanı bağlantılarını içeren listeler

Not: Syntax hatası durumunda, temel bilgileri (örneğin, dosya adı, yorum sayısı vb.) döndürür.

code_quality_analysis() Fonksiyonu:

Amaç: Kod kalitesini ölçmek için metrikler hesaplar.

Hesaplanan Metrikler:

Toplam satır sayısı, yorum satırı sayısı, yorum oranı

Fonksiyon ve sınıf sayısı

Hata yönetimi (try-except) yapısı sayısı

2.3. Yardımcı Fonksiyonlar
remove_comments() Fonksiyonu:

Düzenli ifadeler (regex) kullanılarak, Python dosyalarından yorum satırlarını ve çok satırlı string yorumları kaldırır.

get_user_input() Fonksiyonu:

Hem CLI hem GUI ortamında kullanıcıdan gerekli parametreleri (klasör yolu, dosya isimleri, uzantı filtreleri, alt klasör dahil etme, ekleme/üzerine yazma, encoding) alır.

2.4. Kod Formatlama ve Linting
fix_code_and_lint() Fonksiyonu:

Seçilen kod formatlama aracı (autopep8 veya black) ile kodları otomatik olarak düzenler.

Linting işlemi için (flake8 veya pylint) rapor oluşturur.

Komut satırı ile dış araçları çalıştırmak üzere subprocess modülü kullanılır.

2.5. Bağımlılık Analizi
dep_analysis() Fonksiyonu:

Seçilen araç (pydeps veya pyan) kullanılarak dosya bağımlılık grafikleri oluşturur.

Oluşturulan grafik SVG formatında kaydedilir ve isteğe bağlı olarak tarayıcıda açılır.

Ek parametreler (örneğin, pyan için --uses, --defines, --colored veya pydeps için --max-bacon) desteklenir.

call_env_bulucu() veya call_env_bulucu4() Fonksiyonları:

Harici bir “env_bulucu” aracı çalıştırarak, dosyalardaki çevresel değişkenlerin raporlanmasını sağlar.

3. Üretim Klasörü ve Dosya Yapısı
Çalıştırıldığında, hedef klasör içinde aşağıdaki yapı oluşturulur:

perl
Kopyala
Düzenle
<hedef_klasör>/
 └── birlesikdosyalar/
      ├── file_list.txt        # İşlenen dosyaların isim listesini içerir.
      ├── combined_content_yorumlu.txt (.py)  # Dosyaların orijinal içeriklerinin birleşimi.
      ├── combined_content_yorumsuz.txt (.py)  # Yorumlar temizlenmiş içerik birleşimi.
      ├── <klasör_adı>_istatistik.txt         # Kod kalitesi ve analiz metriklerini içerir.
      ├── <klasör_adı>_toplu_fonksiyonlar_kod_kutuphanesi.txt  # Tüm fonksiyonlar, sınıflar ve modüllerin alfabetik listesi.
      ├── <klasör_adı>.gereksinim.txt           # Import ifadeleri ve kullanılan kütüphanelerin listesi.
      ├── <klasör_adı>.cevresel.txt             # Çevresel değişken kullanım raporu.
      ├── <klasör_adı>.alfabetik.txt            # Modül, sınıf ve fonksiyon isimlerinin alfabetik sıralaması.
      └── <hedef>.svg                          # Bağımlılık grafiği (pydeps/pyan tarafından oluşturulan).
Log dosyaları ve hata raporları da işlem sırasında oluşturulur. Tüm ayarlar, dosyabirlestirici_config.json dosyasında güncel tutulur.

4. Özet İş Akışı
Başlangıç:

Kullanıcı, CLI veya GUI üzerinden hedef klasörü ve ilgili parametreleri belirler.

Dosya Tarama:

Belirtilen klasördeki uygun dosyalar taranır.

İçerik Birleştirme:

Dosya isimleri ve içerikleri toplanır; yorumlu ve yorumsuz olarak ayrı dosyalara yazılır.

Kod Analizi:

Her .py dosyası AST ile analiz edilip, sınıf, fonksiyon, import ve diğer metrikler çıkarılır.

Raporlama:

Toplam istatistikler, fonksiyon detayları ve alfabetik listeler raporlanır.

Ek İşlemler:

İstenirse kod formatlama, linting ve bağımlılık analizi yapılır.

Çıktı:

Tüm sonuçlar birlesikdosyalar klasörü altında düzenli dosya yapısı olarak saklanır.

Bu detaylar, projenin ana dosya yapısı ve akışının temelini oluşturur. Daha fazla detay için kodun ilgili bölümlerine (ör. dosyabirlestirici.py) bakılabilir.
