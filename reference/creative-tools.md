# Yaratıcı kurgu araçları (isteğe bağlı)

Bu katman mevcut GSAP/Three.js sahne motorunu değiştirmez. Basit videolarda
kod yazdırmadan altyazı ve animasyonlu metin kartları oluşturur; daha karmaşık
grafikler mevcut tarayıcı motorunda yapılabilir. Her iki yol da aynı
`work/program.json` zaman çizelgesini kullanır.

## 1. Otomatik altyazı

Önce kaba kurguyu oluştur ve onayla. Komutlardaki SKILL, bu deponun gerçek
dizinidir. Video projesinin dizininde:

```sh
python SKILL/scripts/creative_overlay.py --program work/program.json --preset education export --out-dir work/creative
```

Çıktı: `captions.srt` (YouTube gibi platformlara ayrı yüklenebilir) ve
`overlay.ass` (stil ve kartlarla birlikte videoya gömülebilir).
Programdaki gerçek kelime zamanları kullanılır; altyazı için tekrar AI gerekmez.
Türkçe metin UTF-8 olarak yazılır. Whisper hatalarını ve okunabilirliği kontrol et.
Bu sürüm kelime kelime karaoke değil, kısa okunabilir ifade grupları üretir.

## 2. Şablonlu animasyonlar: modeli sen seç

```sh
python SKILL/scripts/creative_overlay.py --program work/program.json --preset education brief --out work/cards-brief.json
```

Dosyayı tercih ettiğin sohbet modeline veya kod ajanına ver. Transkripti
bulut sağlayıcısına göndermeden önce gizlilik tercihini kontrol et. Yerel
model veya manuel plan da mümkün. Çıktıyı `work/cards.json` olarak kaydet.
Bu adım otomatik API adaptörüne bağlanmış değildir; mevcut plan_provider.py
kaba kurgu içindir.

Örnek (revision ve word kimlikleri kendi brief dosyandan gelmeli):

```json
{
  "revision": "BRIEF_ICINDEKI_TAM_KIMLIK",
  "cards": [
    {"word": 0, "kind": "section", "text": "Başlangıç", "seconds": 3},
    {"word": 42, "kind": "keyword", "text": "Önemli fikir", "seconds": 4}
  ]
}
```

Şablonlar: `section` (bölüm başlığı), `keyword` (anahtar fikir),
`lower-third` (isim veya kısa tanıtım kartı). Kartlar sözün başında
açılır ve yumuşak geçişle kapanır. Aynı anda kart yığılmaz; metin uzunluğu,
süre ve kart aralığı kontrol edilir. Model HTML, FFmpeg komutu veya
rastgele zaman kodu yazmaz.

Videoyu tekrar kurgularsan brief ve kart planını yeniden üret; eski planlar
programın SHA-256 kimliğiyle reddedilir. Onayladığın kartları altyazıyla birleştir:

```sh
python SKILL/scripts/creative_overlay.py --program work/program.json --preset education export --out-dir work/creative-v2 --cards work/cards.json
```

## 3. Basit video çıktı motoru

```sh
python SKILL/scripts/creative_overlay.py --program work/program.json --preset education render --video work/proxy.mp4 --ass work/creative-v2/overlay.ass --out out/styled-preview.mp4
```

Önce out dizinini oluştur. FFmpeg dağıtımında libass ve libx264 gerekir.
Aynı programla eşleşen video ve ASS dosyasını kullan. Kart ve altyazı
yerleşimini görerek kontrol et; yüz algılama/otomatik keepout henüz yok.
Arial veya sistemde Türkçe karakterleri destekleyen eşdeğer font gereklidir.
Render yolu 1080p ve H.264 üretir; mevcut 4K tarayıcı render yolu ayrıdır.
`short` dikey 1080x1920 tuvaldir, kaynak en-boy oranını koruyup gerekirse
kenarlara boşluk bırakır; akıllı yüz takibi veya otomatik kırpma yapmaz.

| Preset | Tuval | Altyazı |
| --- | --- | --- |
| education | 1920x1080 | sakin, daha uzun ifadeler |
| tutorial | 1920x1080 | kısa, okunabilir ifadeler |
| short | 1080x1920 | büyük yazı, kısa ifadeler |

## 4. Görsel kalite kontrolü

```sh
python SKILL/scripts/visual_review.py out/styled-preview.mp4 --out work/visual-review.json
```

FFmpeg yerelde siyah görüntü, donma, belirgin sahne değişimi ve uzun
sessizlik adaylarını bulur. JSON raporunda olay ve saniye bulunur. Bunlar
hata garantisi değildir: statik slayt, fade ve anlatım durakları kasıtlı
olabilir. Video otomatik kesilmez veya değiştirilmez. Mevcut verify.py ve
loudness.py ile birlikte kullan.

## 5. Daha gelişmiş araç adayları (henüz entegre değil)

- [PySceneDetect](https://www.scenedetect.com/docs/latest/api/detectors.html):
  farklı sahne algılama yöntemleri, B-roll ve arşiv indeksleme.
- [MediaPipe Face Detector](https://developers.google.com/edge/mediapipe/solutions/vision/face_detector):
  yüz konumuyla altyazı/kart yerleşimi ve güvenli dikey kırpma.
- [Remotion](https://www.remotion.dev/docs/): React tabanlı parametrik motion
  graphics ve alternatif render yolu; mevcut GSAP motoruyla gereksiz
  tekrar yaratmamak için ihtiyaç olduğunda ve lisansı değerlendirilerek.

Gelişmiş araçlar bu PR'da kurulmadı. Modelden bağımsız şablon ve FFmpeg
yolu ek bağımlılıkları düşük tutmak için önce seçildi. AI'nın her video
için yeniden animasyon kodu üretmesine gerek yok.

## Test

```sh
python -m unittest discover -s tests -p test_creative_tools.py -v
```

Sentetik veri testleri altyazı zamanlamasını, kart sözleşmesini ve
FFmpeg log ayrıştırmayı kapsar. Gerçek medya, font ve render testi ayrıca
yapılmalıdır.
