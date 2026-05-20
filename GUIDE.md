# Bastet Pico 2 — Donanım Kurulum ve Bağlantı Kılavuzu

## Proje Hakkında

**Bastet** (Bastard Tetris) — Oyuncuya en kötü taşı seçen AI ile çalışan bir Tetris oyunu.
Raspberry Pi Pico 2 + 128x64 OLED ekran + 3 buton ile breadboard üzerinde çalışır.
Ekran 90° CW döndürülerek portre modunda (64×128) kullanılır.

---

## Malzeme Listesi

| # | Bileşen | Adet | Not |
|---|---------|------|-----|
| 1 | Raspberry Pi Pico 2 | 1 | MicroPython yüklü |
| 2 | SH1106 1.3" OLED Ekran | 1 | 4-pin I2C (VCC, GND, SCL, SDA) |
| 3 | Breadboard (830 delikli) | 1 | Standart boy |
| 4 | Tactile Push Button (6mm) | 3 | Momentary switch |
| 5 | Jumper kablo (erkek-erkek) | ~10 | Farklı renklerde |
| 6 | Micro USB kablosu | 1 | Güç + programlama |

---

## OLED Ekran Bağlantısı (I2C — 4 Pin)

| OLED Pin | Pico Pin | GPIO | Fiziksel Pin # | Kablo Rengi | Açıklama |
|----------|----------|------|---------------|-------------|----------|
| **VCC** | 3V3(OUT) | — | Pin 36 | 🔴 Kırmızı | 3.3V güç |
| **GND** | GND | — | Pin 38 | ⚫ Siyah | Toprak |
| **SCL** | GP1 | GPIO1 | Pin 2 | 🟡 Sarı | I2C Saat hattı |
| **SDA** | GP0 | GPIO0 | Pin 1 | 🔵 Mavi | I2C Veri hattı |

### I2C Ayarları
- **I2C Bus:** I2C0
- **Frekans:** 400 kHz (Fast Mode)
- **Adres:** 0x3C
- **Çözünürlük:** 128x64 piksel → 90° CW döndürülmüş 64x128 portre

> **ÖNEMLİ:** Ekran fiziksel olarak yatay takılır, yazılımda 90° saat yönünde
> döndürülerek dikey (portre) modda kullanılır. Ekranı takarken buna dikkat edin.

---

## Buton Bağlantıları (3 Buton)

Her buton bir GPIO pinine ve GND'ye bağlanır.
**Harici direnç gerekmez** — dahili pull-up yazılımda aktif edilir.

| Buton | GPIO | Fiziksel Pin # | Oyundaki Kullanım |
|-------|------|---------------|-------------------|
| **SOL** | GP2 | Pin 4 | Sola hareket / Menüde yukarı |
| **ORTA** | GP3 | Pin 5 | Hold-Reserve / Seç / Pause(uzun) |
| **SAĞ** | GP4 | Pin 6 | Sağa hareket / Menüde aşağı |

### Combo Kontrolleri (Oyunda)

| Combo | Eylem |
|-------|-------|
| ORTA + SAĞ (aynı anda) | Sağa döndür (CW) |
| ORTA + SOL (aynı anda) | Sola döndür (CCW) |
| SOL + ORTA + SAĞ (hepsi) | Hard drop (anında düşür) |
| ORTA (500ms basılı tut) | Pause menü |

### Buton Bağlama Şeması

```
Her buton için:

   Pico GPIO Pin ─────┐
                       │
                  ┌────┴────┐
                  │  BUTON  │
                  └────┬────┘
                       │
   Pico GND ──────────┘

   Dahili Pull-Up: 3.3V ──[~50kΩ]── GPIO Pin
   Basılı değil → HIGH (1)
   Basıldı      → LOW  (0)
```

### Buton Yerleşim Önerisi

```
   Breadboard üzerinde yan yana:

   ┌──────┐  ┌──────┐  ┌──────┐
   │ SOL  │  │ ORTA │  │ SAĞ  │
   │ GP2  │  │ GP3  │  │ GP4  │
   └──────┘  └──────┘  └──────┘
```

---

## Tam Pin Haritası

```
Raspberry Pi Pico 2 — Pin Kullanım Haritası
═══════════════════════════════════════════

           ┌───────────────────┐
  GP0  ────┤ 1   (I2C SDA)  40 ├──── VBUS (5V USB)
  GP1  ────┤ 2   (I2C SCL)  39 ├──── VSYS
  GND  ────┤ 3              38 ├──── GND ◄── OLED GND
  GP2  ────┤ 4   (SOL)      37 ├────
  GP3  ────┤ 5   (ORTA)     36 ├──── 3V3(OUT) ◄── OLED VCC
  GP4  ────┤ 6   (SAĞ)      35 ├────
  GP5  ────┤ 7              34 ├────
  GND  ────┤ 8              33 ├──── GND
  GP6  ────┤ 9              32 ├────
  GP7  ────┤ 10             31 ├────
           ┤ ...            ...├
           └───────────────────┘

  Kullanılan pinler:
  ● GP0  → I2C0 SDA (OLED veri)
  ● GP1  → I2C0 SCL (OLED saat)
  ● GP2  → SOL buton
  ● GP3  → ORTA buton
  ● GP4  → SAĞ buton
  ● 3V3  → OLED VCC (güç)
  ● GND  → OLED GND + butonlar GND
```

---

## Breadboard Kurulum Adımları

### 1. Pico'yu Yerleştir
- Pico 2'yi breadboard'un ortasına, merkez oluğu geçecek şekilde yerleştir
- USB portu breadboard'un üst kenarına bakacak şekilde

### 2. GND Hattını Hazırla
- Pico GND → breadboard (-) güç hattı

### 3. OLED'i Bağla
1. 🔴 VCC → 3V3(OUT) (Pin 36)
2. ⚫ GND → GND hattı
3. 🟡 SCL → GP1 (Pin 2)
4. 🔵 SDA → GP0 (Pin 1)
5. **Ekranı dikey konumda yerleştir** (90° CW döndürülmüş)

### 4. Butonları Bağla
1. 3 butonu breadboard'a yan yana yerleştir
2. Her butonun bir bacağını GND hattına bağla
3. Diğer bacağını GPIO pinine bağla:
   - SOL → GP2, ORTA → GP3, SAĞ → GP4

---

## Yazılım Yapısı

```
Pico üzerindeki dosya yapısı:
/
├── boot.py              ← Sistem başlatma (GC aktif)
├── main.py              ← Ana program (otomatik çalışır)
├── config.py            ← Pin, I2C, oyun ayarları
├── display.py           ← 90° CW ekran döndürme wrapper
├── lib/
│   └── sh1106.py        ← OLED sürücü (robert-hh/SH1106)
├── game/
│   ├── __init__.py
│   ├── engine.py        ← Bastet AI + Tetris motoru
│   ├── input.py         ← 3 buton + combo algılama
│   ├── pieces.py        ← 7 tetromino × 4 rotasyon
│   └── renderer.py      ← OLED çizim (portre modu)
└── ui/
    ├── __init__.py
    ├── menu.py           ← Ana menü (3 buton)
    └── screens.py        ← Splash + Hakkında ekranları
```

---

## Sorun Giderme

| Sorun | Olası Neden | Çözüm |
|-------|------------|-------|
| OLED'de görüntü yok | VCC/GND ters | Kablo bağlantılarını kontrol et |
| Görüntü ters/yatay | Ekran döndürülmemiş | Ekranı fiziksel olarak 90° CW çevir |
| I2C tarama boş | SDA/SCL ters | GP0↔SDA ve GP1↔SCL kontrol et |
| Buton tepki vermiyor | GND bağlı değil | Butonun GND bacağını kontrol et |
| Combo çalışmıyor | Zamanlaması kaçıyor | İki butona aynı anda basın |
| `main.py` çalışmıyor | Import hatası | REPL'da çalıştırıp hatayı oku |
| Pico'ya bağlanamıyor | main.py döngüde | USB takarken BOOTSEL basılı tut |
