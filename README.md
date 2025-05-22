# Sürü İHA Kontrol Sistemi – Otonom Görevli Drone Takımı

Bu proje, 3 veya daha fazla İHA’nın (İnsansız Hava Aracı) tam otonom biçimde görev yapmasını sağlayan, modüler, dağıtık ve görev odaklı bir sürü kontrol sistemini içermektedir. Projede **formasyon uçuşu**, **navigasyon**, **keşif**, ve **birey çıkarma/ekleme** gibi görevler, PID ve yapay potansiyel alan (APF) algoritmalarıyla kontrol edilmektedir. Proje Gazebo simülasyon ortamında test edilmiştir.

---

## İçindekiler

- [Amaç]
- [Gereksinimler]
- [Donanım]
- [Yazılım]
- [Proje Mimarisi]
- [Görev Tanımları]
- [Kontrol Algoritmaları]
- [Yazılım Arayüzü]
- [Keşif Sistemi & ArUco]
- [Simülasyon & Testler]
- [Kullanılan Teknolojiler]
- [Simülasyon]
--

## Amaç

Projede hedeflenen, birden fazla İHA’nın çeşitli görevlerde **tam otonom olarak** birlikte çalışmasını sağlayan dayanıklı, esnek ve gerçek zamanlı bir sürü sistemi kurmaktır. Sistem aşağıdaki zorluklara çözüm üretir:

- Haberleşme kesintileri
- Yeni birey eklenmesi ya da arıza durumunda çıkarılması
- Gerçek zamanlı keşif & iniş noktası belirleme
- Çarpışmasız navigasyon ve hassas konumlandırma

---

## Gereksinimler

### Donanım Gereksinimleri

- En az **3 adet otonom uçuşa uygun drone**
- Her drone’da:
  - GNSS (Küresel Navigasyon)
  - IMU (Atalet Ölçüm Birimi)
  - Barometre
  - Çarpışma önleme sensörleri
  - Keşif için yüksek çözünürlüklü kamera
- Yer istasyonu ile kablosuz haberleşme modülü
- ArUco işaretçilerini algılayabilecek kamera çözünürlüğü

### Yazılım Gereksinimleri

- Tam otonom sürü algoritması
- Formasyon geçişleri, birey çıkarma/ekleme ve navigasyon senaryoları desteği
- Haberleşme kaybı sonrası görev tamamlama
- ArUco işaretçisi tespiti ve konum iletimi
- Manuel müdahale olmadan görev süreci

---

## Proje Mimarisi

Modüler bir yapı benimsenmiştir. Aşağıdaki bileşenler bulunur:

- **Python**: Görev dağıtımı ve karar verme
- **MAVLink**: Drone haberleşmesi (UDP/TCP)
- **ROS2 + MAVProxy**: İHA kontrolü
- **Gazebo**: Fiziksel simülasyon ve test ortamı
- **Web Arayüzü**: HTML + JS üzerinden görev iletimi ve izleme

---

## Görev Tanımları

### 1. 3B Formasyon Görevi

- İHA’lar kalkıştan inişe kadar farklı formasyonlara geçer.
- Her formasyonda X metre mesafe, Z metre irtifa korunur.

### 2. Sürüyle Navigasyon Görevi

- İHA’lar önceden belirlenmiş noktalardan geçerek hedefe ulaşır.
- Yer kontrol bağlantısı kopsa bile görev tamamlanır.

### 3. Birey Ekleme / Çıkarma

- Uçuş sırasında bir İHA sürüden çıkarılır.
- Yeni bir birey dahil edilir.
- Formasyon bozulmadan görev tamamlanır.

### 4. Keşif Görevi

- Keşif dronları ArUco işaretçilerini tespit eder.
- Konum hedef dronlara iletilir.
- Hedef drone, işaretçiye hassas iniş yapar.

---

## Kontrol Algoritmaları

### PID (Proportional-Integral-Derivative)

- Hata payını minimize ederek sabit ve düzgün uçuş sağlar.

### Yapay Potansiyel Alan (APF)

- Çevresel engellere karşı hızlı tepki verir.
- Formasyon ve yol planlamasında etkilidir.

### PID + APF Hibrid Modeli

- PID ile hassas yönlendirme, APF ile çarpışma önleme
- Düşük maliyetli, gerçek zamanlı kontrol
- Kullanım Alanları:
  - Arama-kurtarma
  - Sürü formasyonu
  - Askeri görevler
  - Dinamik yarış senaryoları

---

## Yazılım Arayüzü

Web tabanlı, sade ve işlem gücü düşük bir arayüz ile:

- Görevler drone’lara atanır
- Uçuşlar izlenebilir
- Kullanılan Teknolojiler:
  - HTML, CSS, JS (frontend)
  - Python / NodeJS (backend)
    
---

## Keşif Sistemi & ArUco

### İşaretçi Hazırlama:

- 80x80 mm boyut
- `DICT_4X4_50` dictionary
- Mat kağıda çıktı alınıp mermer levhaya sabitlenir

### Keşif Süreci:

1. Alan iki eş parçaya ayrılır
2. Her drone kendi bölgesini grid tabanlı tarar
3. İşaretçi bulunduğunda konum 3. drone'a gönderilir
4. Hedef drone işaretçiye iniş yapar

---

## Simülasyon & Testler

### Kullanılan Formasyonlar:

- Çizgi Formasyonu
- V-Formasyonu
- Ok Başlı Formasyon
- Serbest Formasyon

### Test Ortamı:

- **Gazebo** ile 3D fiziksel simülasyon
- Çeşitli formasyonlar ve görev senaryoları denenmiştir
  
---

## Kullanılan Teknolojiler

| Bileşen | Teknoloji |
|--------|------------|
| Simülasyon | Gazebo |
| Kontrol | MAVProxy, ROS 2 |
| Algoritma | PID, APF |
| Haberleşme | MAVLink, UDP/TCP |
| Programlama | Python, JS |
| Arayüz | HTML/CSS/JS |
| Kamera | Raspberry Pi Kamera Modülü |
| İşaret Tespiti | ArUco (`cv2.aruco`) |

---
> Proje kapsamında yapılan geliştirmeler sadece yarışma değil, gerçek dünyadaki görev uygulamaları için de zemin oluşturmaktadır. Geliştirilen sistem modülerdir ve farklı görev tanımlarıyla genişletilebilir. ✨
---
