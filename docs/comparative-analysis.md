# SitWise — Benzer Uygulamalar ve Literatür Karşılaştırması (v2)

> **Kart:** SW-024  
> **Alan:** B (Rapor / Dokümantasyon / Sunucu)  
> **Referans:** SitWise Yol Haritası v2: Model, Veri Seti ve Görev Planı (21 Ekim 2026)  
> **Hedef:** Vize Raporu & Rapor için Kaynak Listesi — Bölüm 2 (Literatür Taraması ve Mevcut Sistemlerin Karşılaştırılması)  
> **Tarih:** Ekim 2026  
> **Durum:** Tamamlandı  

---

## 1. Giriş ve Kapsam

Masa başı çalışanlarda uzun süreli ekran maruziyeti ve hareketsizlik; kas-iskelet sistemi bozuklukları (özellikle ileri baş duruşu / boyun düzleşmesi, omuz asimetrisi, kifoz) ve Dijital Göz Yorgunluğu (Computer Vision Syndrome - CVS) semptomlarını tetiklemektedir. Birleşmiş Milletler Sürdürülebilir Kalkınma Amacı 3 (Sağlık ve Kaliteli Yaşam) ile uyumlu olan **SitWise** projesi; standart bir laptop/web kamerası kullanarak duruş, ekran mesafesi, göz kırpma sıklığı ve yorgunluğu izleyen, gizlilik öncelikli (privacy-first) bir masaüstü ergonomi asistanıdır.

SitWise **Yol Haritası v2** ile birlikte projenin odak noktası; yalnızca sabit kural/eşik kontrollerinden ibaret bir prototip olmaktan çıkarak, **cihaz içinde (on-device) çalışan eğitilmiş makine öğrenmesi modelleri**, **görüntüsüz koordinat tabanlı özel veri seti (SitWise-Desk)** ve **dürüst, karşılaştırmalı deneysel doğrulama (LOSO)** üzerine kurgulanmıştır.

Bu dokümanda;
1. Mevcut ticari, açık kaynaklı ve akademik sistemlerin kısıtları,
2. SitWise ile alternatif çözümlerin karşılaştırma matrisi,
3. "Hazır veri neden yetmiyor?" sorusunun yanıtı ve SitWise-Desk veri seti stratejisi,
4. Duruş, göz kırpma ve yorgunluk tespiti literatürü,
5. Raporlama için akademik kaynakça sunulmaktadır.

---

## 2. Mevcut Sistemler ve Temel Kısıtları

Piyasadaki ve literatürdeki çözümler genel olarak dört ana kategoride toplanmaktadır:

### 2.1. Ticari Kamera Tabanlı Araçlar (Örn. BLiiNK)
* **İnceleme:** Standart web kamerasıyla göz kırpma sıklığı, ekran mesafesi ve temel oturma postürünü takip eden ticari bir masaüstü aracıdır.
* **Kısıtları:**
  * **Kapalı ve Sabit Eşikli:** Karar mekanizmaları kapalıdır; farklı oturma alışkanlıkları ve çalışma ortamlarına dinamik olarak uyum sağlamaz.
  * **Yanlış Pozitif Yönetimi Yok:** Kullanıcı esnediğinde, su içtiğinde veya pozisyon değiştirdiğinde çıkan hatalı alarmları öğrenen bir geri bildirim döngüsü bulunmaz; bu durum bildirim yorgunluğuna (alert fatigue) yol açar.
  * **Görüntü İşleme Güveni:** Kapalı kaynaklı olması nedeniyle kullanıcıların kamera görüntüsünün akıbetine dair kurumsal gizlilik endişelerini tam olarak gideremez.

### 2.2. Basit Postür Takip Araçları (Örn. Posturr)
* **İnceleme:** Kamera üzerinden kullanıcının dik oturup oturmadığını izleyen açık/yarı-açık kaynaklı masaüstü araçlarıdır.
* **Kısıtları:**
  * Yalnızca gövde eğimine bakar; göz kırpma refleksini (CVS), ekran mesafesini ve zihinsel/fiziksel yorgunluğu izlemez.
  * Seans takibi, zaman serisi analitiği ve tarihsel raporlama katmanı yoktur.
  * Model tabanlı olmayıp basit piksel veya landmark farkı eşikleriyle çalıştığı için kamera açısı değişimlerinde çöker.

### 2.3. Zamanlayıcı ve Mola Uygulamaları (Örn. SitApp, Pomodoro Araçları)
* **İnceleme:** 20-20-20 kuralı veya Pomodoro tekniğiyle belirli aralıklarla mola hatırlatması yapan kural tabanlı yazılımlardır.
* **Kısıtları:**
  * Biyomekanik veya görsel takip içermez; kullanıcının o sırada gerçekten kambur olup olmadığını, ekrana yapışıp yapışmadığını veya göz kırpma sayısının düşüp düşmediğini bilemez.
  * Kullanıcının gerçek yorgunluk düzeyini hesaba katmadan katı zaman dilimlerinde bildirim üretir.

### 2.4. Giyilebilir Sensörler (Örn. Upright GO, Akıllı Korseler)
* **İnceleme:** Omurgaya yapıştırılan veya boyna takılan, ivmeölçer ve jiroskop (IMU) barındıran fiziksel donanımlardır.
* **Kısıtları:**
  * Ek donanım maliyeti yüksektir (satın alma, yedek yapışkan bantlar vb.).
  * Fiziksel olarak vücutta taşınması gerektiğinden uzun süreli kullanım konforu ve benimsenme oranı düşüktür.
  * Göz yorgunluğunu ve ekran mesafesini ölçemez; şarj gereksinimi vardır.

### 2.5. Tipik Akademik Modeller ve Literatürdeki Prototipler
* **İnceleme:** MediaPipe, OpenPose, Soukupová & Čech EAR algoritması gibi bilgisayarlı görü temellerini kullanan makaleler ve örnek kodlar.
* **Kısıtları (Hazır Veri ve Değerlendirme Yanılsaması):**
  * **Veri Uyuşmazlığı:** Akademik duruş veri setleri genellikle yandan çekilmiş, ayakta duran veya sentetik robotik hareketlerden oluşur. Tipik masa başı önden laptop kamerası açısını ve klavye/telefon kullanımı gibi doğal durumları yansıtmaz.
  * **Veri Sızıntısı (Data Leakage):** Birçok çalışma, aynı kişinin karelerini hem eğitim hem test setine rastgele dağıtarak yapay biçimde %95+ doğruluk raporlar; model hiç görmediği yeni bir kullanıcıda test edildiğinde başarı dramatik olarak düşer.
  * **Ürünleşme Eksikliği:** Genellikle jupyter notebook seviyesinde kalır; cihaz içi hafif ONNX çıkarımı (inference), işletim sistemi arka plan entegrasyonu ve istemci-sunucu mimarisine sahip uçtan uca bir ürüne dönüştürülmez.

---

## 3. Karşılaştırma Matrisi

Aşağıdaki tablo, SitWise (Yol Haritası v2) ile piyasadaki ve literatürdeki alternatif çözümleri çok boyutlu olarak karşılaştırmaktadır:

| Karşılaştırma Ölçütü | SitWise (Yol Haritası v2) | BLiiNK | Posturr | SitApp / Pomodoro | Upright GO | Tipik Akademik Çalışma |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Gereken Donanım** | Standart Laptop Webcam | Standart Webcam | Standart Webcam | Donanım Yok | Özel IMU Donanımı | Kamera / Yüksek GPU |
| **Ek Donanım Maliyeti** | **0 TL (Maliyetsiz)** | 0 TL | 0 TL | 0 TL | Yüksek Donanım Satın Alma | Değişken |
| **Postür Tespiti** | **Eğitilmiş Model (4 Sınıf) + Normalizasyon** | Kural tabanlı / Kapalı | Basit Eşik | Yok | Eğim Sensörü | Model (Genelde tek sınıf/açı) |
| **Göz Kırpma Tespiti (CVS)** | **EAR + Zaman Penceresi Analitiği** | Var | Yok | Yok | Yok | Var (Yalnızca EAR formülü) |
| **Ekran Mesafesi Ölçümü** | **İris Çapı + Regresyon (40/60/80 cm)** | Var | Kısıtlı | Yok | Yok | Kısıtlı / Ayrı derinlik kamerası |
| **Erken Yorgunluk Tespiti** | **Çoklu Metrik (PERCLOS, Kırpma, Esneme, Baş)** | Basit süre sayacı | Yok | Yok | Yok | Sadece uykulu sürücü modelleri |
| **Model Çalışma Yeri** | **Cihaz İçi ONNX Runtime (CPU ≤ %15, ≤10ms)** | İstemci | İstemci | İstemci | Mikrodenetleyici | Python / Cloud / GPU |
| **Gizlilik Güvencesi** | **Görüntüsüz (RAM'de işlenir; disk/ağ=0 görüntü)** | Kısmen Yerel | Yerel | Kamera Yok | Sensör Verisi | Genelde veri seti video kaydı |
| **Özel Masa Başı Veri Seti** | **Var (SitWise-Desk: 7 adımlı protokol)** | Bilinmiyor (Kapalı) | Yok | Yok | Yok | Sentetik / Yandan duruş setleri |
| **Dürüst Değerlendirme (LOSO)** | **Var (Görülmemiş kişilerde test, LOSO)** | Yok / Belirsiz | Yok | Yok | Yok | Nadiren (Çoğunlukla random split) |
| **Karşılaştırmalı Deney** | **4 Yaklaşım (Kural, Hazır Veri, Kendi Veri, Kişisel)**| Yok | Yok | Yok | Yok | Genelde tek model |
| **Kişiselleştirme** | **5 sn Kalibrasyon + "Yanlış Uyarı" ile Eşik Kaydırma** | Yok | Kısıtlı | Yok | Butonla Sıfırlama | Yok / Sabit Eşik |
| **Dış CDN Bağımlılığı** | **Yok (Yerel Wasm & Model Paketleri)** | Belirsiz | Değişken | Yok | Mobil Uygulama | Genellikle CDN bağımlı |
| **İstemci Mimarisi** | **İzole Electron (Context Isolation, Sandbox)** | Kapalı kaynak | Değişken | Standart | Mobil Arayüz | Notebook / Script |
| **Seans ve Skorlama** | **PostgreSQL + 0-100 Günlük Ergonomi Skoru** | Var (Bulut) | Yok | Basit Sayaç | Var (Mobil) | Yok |
| **Açık Veri / Bilimsel Çıktı** | **Model Kartı, Veri Kartı, Anonim Veri Seti** | Yok (Ticari) | Kısmen Kod | Kısmen Kod | Yok | Sadece Makale |

---

## 4. SitWise v2'nin Temel İnovasyonları ve Bizi Ayıran Yönler

SitWise v2, sıradan bir "hazır kütüphane bağlama" projesi değildir. Projeyi literatürdeki ve okuldaki diğer çalışmalardan ayıran 7 temel mühendislik unsuru şunlardır:

### 4.1. "Model Eğittik" Demek Değil: Doğru Veriyi Tasarlayıp Toplamak (SitWise-Desk)
Çoğu bilgisayarlı görü projesi internetten hazır bir veri seti indirip aynı set üzerinde %95 doğruluk raporlayarak tamamlanır. Ancak jürinin *"Bu veri gerçek kullanım ortamınıza uyuyor mu?"* sorusuna yanıt veremezler.
* Hazır duruş setleri (Roboflow vb.) çoğunlukla yandan açıyla çekilmiş veya ayakta duran insanları kapsar.
* SitWise, laptop kamerasının önden açısına ve gerçek masa başı oturma senaryosuna uygun **SitWise-Desk** veri setini tasarlamıştır.
* 7 adımlı senaryo protokolüyle (kalibrasyon, dik, öne eğik, kambur, yana yatık, 40/60/80 cm mesafe ve serbest çalışma) toplanır.
* **SW-085** deneyi ile *"Hazır veri bizim kurulumumuza neden uymuyor?"* sorusunun sayısal cevabı verilir.

### 4.2. Görüntüsüz Veri ve Cihaz İçi Hafif Çıkarım (ONNX)
* Toplanan veri setinde ve çalışan uygulamada **tek bir görüntü dahi kaydedilmez ve iletilmez**.
* MediaPipe Tasks (FaceLandmarker ve PoseLandmarker) ile kameradan anlık elde edilen 3D koordinatlar doğrudan skaler özelliklere (boyun açısı, omuz eğimi, burun-omuz mesafesi, iris çapı, EAR) dönüştürülür.
* Eğitilen hafif makine öğrenmesi modelleri (Logistic Regression, Random Forest, LightGBM) **ONNX formatına çevrilerek istemcide ONNX Runtime** ile çalıştırılır (kare başına işlem süresi ≤ 10 ms, CPU kullanımı ≤ %15).
* Sunucuya (FastAPI + PostgreSQL) yalnızca seans özetleri ve skaler metrikler gider.

### 4.3. Dürüst Ölçüm ve Metodolojik Doğruluk (LOSO)
* Makine öğrenmesinde yaygın yapılan "aynı kişinin bir karesini eğitime, diğer karesini teste koyma" hatası kesin olarak engellenmiştir.
* Değerlendirmeler **Kişiye Göre Ayrılmış Çapraz Doğrulama (Leave-One-Subject-Out - LOSO)** ile yürütülür.
* Ayrıca modelin eğitiminde hiç yer almamış 10–15 kişilik ayrı bir **gönüllü test seti** ile nihai doğruluk (Makro F1 ≥ 0,85) ölçülür.

### 4.4. 4 Yaklaşımın Karşılaştırmalı Deneyi
Final tesliminde ve vize formunda tek bir sistemin başarısı değil, aynı test setinde yan yana 4 farklı yaklaşım kıyaslanır:
1. Kural tabanlı sabit eşik
2. Sadece hazır veriyle eğitilmiş model (Roboflow vb.)
3. Kendi veri setimizle (SitWise-Desk) eğitilmiş model
4. Kişiselleştirilmiş model (+ kalibrasyon ve eşik kaydırma)

### 4.5. Ölçülebilir İki Aşamalı Kişiselleştirme
Sabit modeller bireyler arası anatomik ve donanımsal farklar (masa yüksekliği, boy, kamera açısı) nedeniyle yüksek oranda yanlış alarm üretir.
* **Aşama 1 (Normalizasyon):** Seans başındaki 5 saniyelik dik oturma kalibrasyonu ile kullanıcının kendi baz çizgisi (`mean`, `std`) alınır; özellikler bu baz çizgiye göre oranlanır.
* **Aşama 2 (Öğrenen Eşik - SW-046):** Kullanıcı arayüzündeki **"Yanlış Uyarı"** butonu sayesinde model yeniden eğitilmeden karar eşiği o kullanıcı için geriye kaydırılır. Başarı kriteri olarak yanlış uyarı oranındaki **≥ %30 düşüş** raporlanır.

### 4.6. Çok Boyutlu Yorgunluk Kestirimi (UTA-RLDD & Davranışsal Metrikler)
Sadece mola saati tutmak yerine;
* Göz kırpma frekansı,
* Göz kapalılık oranı (PERCLOS - Percentage of Eye Closure),
* Ortalama kırpma süresi,
* Ağız açıklığı oranı (esneme - Mouth Aspect Ratio / MAR),
* Baş düşmesi / sallanması,
* Duruş bozulma sıklığı,
parametreleri dakikalık pencerelerde birleştirilerek 0–100 arası yorgunluk skoruna dönüştürülür. Model UTA-RLDD araştırma veri seti üzerinde doğrulanır ve kullanıcıların gün sonu 1–5 skala cevaplarıyla karşılaştırılır.

### 4.7. Profesyonel Dokümantasyon: Model Kartı ve Veri Seti Kartı
Akademik ve endüstriyel etik standartlara uygun olarak:
* Veri setinin nasıl toplandığını, rıza koşullarını ve dağılımlarını açıklayan **Veri Seti Kartı (Datasheet)**,
* Modelin sınırlarını, girdi/çıktılarını ve performans kırılımlarını açıklayan **Model Kartı (Model Card)** hazırlanır ve açık bilim katkısı olarak Zenodo/GitHub üzerinde anonim paylaşılır.

---

## 5. Literatür Taraması ve Teorik Altyapı

### 5.1. Göz Kırpma Tespiti ve Dijital Göz Yorgunluğu (CVS)
* **Temel Problem:** Bilgisayar başında çalışan bireylerde normalde dakikada 15–20 olan göz kırpma sıklığı, odaklanma nedeniyle dakikada 5–7 seviyesine düşmekte; bu durum göz kuruluğuna, yanmaya ve baş ağrısına yol açmaktadır (Blehm et al., 2005; Gowrisankaran & Sheedy, 2015).
* **Eye Aspect Ratio (EAR) Yöntemi:** Soukupová ve Čech (2016), yüz landmark noktaları üzerinden göz kapaklarının dikey ve yatay mesafelerini oranlayan EAR metriğini önermiştir:
  $$\text{EAR} = \frac{||p_2 - p_6|| + ||p_3 - p_5||}{2 ||p_1 - p_4||}$$
* **SitWise Yaklaşımı:** MediaPipe FaceLandmarker ile elde edilen 6 göz landmark noktası üzerinden EAR zaman serisi hesaplanır. Sabit EAR eşiği ile pencere tabanlı sınıflandırıcı Eyeblink8 ve RT-BENE referans alınarak kıyaslanır; kırpma sayısı dakikalık doğrulukla (±2 hata sınırı) takip edilir.

### 5.2. Postür Analizi ve Biyomekanik
* **İleri Baş Duruşu ve Kifoz:** Başın nötr hizada her 2.5 cm öne eğilmesi, boyun omurlarına binen yükü yaklaşık 4.5–5 kg artırmaktadır. Cagnie et al. (2007), ofis çalışanlarında boyun ağrısının en büyük risk faktörünün uzun süreli sabit ve öne eğik duruş olduğunu kanıtlamıştır.
* **Landmark Tabanlı Postür Tespiti:** Cao et al. (OpenPose, 2017) ve Bazarevsky et al. (MediaPipe Pose, 2020) gibi modeller derin öğrenmeyle insan eklemlerini tespit edebilmektedir.
* **Neden Hazır Veri Yetmiyor?:** Literatürdeki duruş setleri (ör. Roboflow duruş etiketleri) genellikle üçüncü şahıs bakış açısından çekilmiştir. SitWise'da ise kullanıcı kameraya 40–80 cm mesafede, yalnızca göğüs ve baş hizası görünen masa başı açısındadır. Bu nedenle SitWise; baş açısı, boyun eğimi, burun-omuz dikey mesafesi ve omuz asimetrisini kalibrasyona göre bağıl oranlar olarak hesaplar.

### 5.3. Yorgunluk Tespiti ve PERCLOS
* **PERCLOS Metriği:** Wierwille et al. (1994) tarafından geliştirilen ve literatürde göz kapağının %80 ve üzeri kapalı kaldığı sürenin toplam süreye oranını ifade eden PERCLOS, uykululuk ve dikkat dağınıklığının en güvenilir göstergesidir.
* **UTA-RLDD Veri Seti:** Ghoddoosian ve Zhu (2019), gerçek yaşam yorgunluk tespiti için 60 katılımcı ve 30 saatlik video içeren UTA Real-Life Drowsiness Dataset (UTA-RLDD) setini tanıtmıştır. Bu veri seti, katılımcıların uyanık, hafif uykulu ve aşırı uykulu hallerini etiketlemiştir. SitWise, yorgunluk modelini bu set üzerinde eğitmekte/doğrulamaktadır.

### 5.4. Makine Öğrenmesi Değerlendirme Metodolojisi ve Şeffaflık
* **Veri Sızıntısının Önlenmesi (LOSO):** Biyometrik örüntü tanımada k-fold cross validation rastgele yapıldığında aynı kişinin verileri sızar. Bu yanılsamayı engellemek için Leave-One-Subject-Out (LOSO) yaklaşımı zorunludur.
* **Model ve Veri Kartları:** Mitchell et al. (2019) tarafından önerilen *Model Cards* ve Gebru et al. (2021) tarafından önerilen *Datasheets for Datasets*, yapay zekâ modellerinin tarafsızlığını, kısıtlarını ve eğitim verisi detaylarını şeffaflaştıran uluslararası standartlardır.

---

## 6. Rapor ve Sunum İçin Kaynakça (References)

1. **Soukupová, T., & Čech, J. (2016).** *Real-Time Eye Blink Detection using Facial Landmarks.* 21st Computer Vision Winter Workshop (CVWW), Rimske Toplice, Slovenia.
2. **Ghoddoosian, R., & Zhu, M. (2019).** *A Realistic Dataset and Baseline Temporal Model for Detecting Depression/Drowsiness using Facial Landmarks.* Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV) Workshops, pp. 0-0. [UTA-RLDD Dataset].
3. **Lugaresi, C., Tang, J., Nash, H., McClanahan, C., Uboweja, E., Hays, M., ... & Grundmann, M. (2019).** *MediaPipe: A Framework for Building Perception Pipelines.* arXiv preprint arXiv:1906.08172.
4. **Bazarevsky, V., Grishchenko, I., Raveendran, K., Zhu, T., Zhang, F., & Grundmann, M. (2020).** *BlazePose: On-device Real-time Body Pose Tracking.* arXiv preprint arXiv:2006.10204.
5. **Blehm, C., Vishnu, S., Khattak, A., Mitra, S., & Yee, R. W. (2005).** *Computer Vision Syndrome: A Review.* Survey of Ophthalmology, 50(3), 253-262.
6. **Gowrisankaran, S., & Sheedy, J. E. (2015).** *Computer vision syndrome: A review.* Work: A Journal of Prevention, Assessment and Rehabilitation, 52(2), 303-314.
7. **Cagnie, B., Danneels, L., Van Tiggelen, D., De Loose, V., & Cambier, D. (2007).** *Individual and work related risk factors for neck pain among office workers: A cross sectional study.* European Spine Journal, 16(5), 679-686.
8. **Wierwille, W. W., Ellsworth, L. A., Wreggit, S. S., Fairbanks, R. J., & Kirn, C. L. (1994).** *Research on Vehicle-Based Driver Status/Performance Monitoring; Development, Validation, and Refinement of Algorithms for Detection of Driver Drowsiness.* National Highway Traffic Safety Administration (NHTSA) Technical Report, DOT-HS-808-247.
9. **Fuhl, W., Santini, T., Kasneci, G., & Kasneci, E. (2018).** *RT-BENE: A Dataset and Benchmark for Real-Time Blink Estimation in Natural Environments.* ACM Symposium on Eye Tracking Research and Applications (ETRA).
10. **Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., ... & Liu, T. Y. (2017).** *LightGBM: A Highly Efficient Gradient Boosting Decision Tree.* Advances in Neural Information Processing Systems (NeurIPS), 30.
11. **Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., ... & Gebru, T. (2019).** *Model Cards for Model Reporting.* Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT*), pp. 220-229.
12. **Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021).** *Datasheets for Datasets.* Communications of the ACM, 64(12), 86-92.
13. **Electron Security Guidelines. (2024).** *Context Isolation and Sandboxing in Desktop Applications.* ElectronJS Documentation. https://www.electronjs.org/docs/latest/tutorial/security
