# Üç modlu yerel üretim

Bu yürütücü mevcut editöre ek bir kısa video kompozisyon yoludur. Yerel
FFmpeg/FFprobe ve libass gerekir; NumPy, Whisper, GPU, Node veya API zorunlu
değildir. Mevcut transkripsiyon ve kelime sınırı düzenleme araçları korunur.

## İnsan için başlangıç

Depo klasöründen, Python 3.10+ ile:

```sh
python scripts/produce.py --project work/my-short init --mode long-to-shorts
```

`work/my-short/src/` içine kendi medyanı koy. `production.json` dosyasındaki
yer tutucuyu düzenle veya mevcut Codex/Claude oturumuna aşağıdaki sözleşmeyi
ver. Diğer modlar `faceless` ve `own-footage`. Üçü de aynı yerel render motorunu
kullanır; mod adı ayrı bir AI modelini veya harici projeyi çalıştırmaz.

```sh
python scripts/produce.py --project work/my-short doctor
python scripts/produce.py --project work/my-short preview
```

`out/preview.mp4` dosyasını izle. Komutun yazdırdığı SHA256 değerini, yalnızca
önizlemeyi onaylıyorsan kullan:

```sh
python scripts/produce.py --project work/my-short final --approve-preview SHA256
```

Önizleme 360×640, final 1080×1920 H.264/AAC MP4, 30 fps'dir. Final komutu
önizlemenin, proje tanımının ve kaynakların SHA256 değerlerini doğrular.
İçerik değiştiyse eski onay kabul edilmez. Yeni turdan önce önceki `out/`
klasörünü ayrı bir yedeğe taşı; kaynakları koru. Çıktılar üzerine yazılmaz.
Başarısız işlem parçaları inceleme için `work/production-*/` altında kalır.

## Mevcut abonelikteki AI ajanı için sözleşme

1. Konuyu, hedef süreyi ve yerel malzemeyi incele; editorial-intake.md'yi izle.
2. Ücretli API, bulut veya yeni abonelik kullanma. Model gerektiğinde mevcut
   oturumda planla; bu yürütücü model çağırmaz.
3. Uzun videoda mevcut transkripsiyon araçlarından yararlanarak anlamlı
   kesitleri seç. `start` kaynak saniyesidir; `duration` seçilen kesit süresidir.
   Bir projede bir Short oluştur; farklı adaylara ayrı proje klasörleri aç.
4. Kendi çekimlerinde sıralamayı ve seçilen aralıkları belirt. Otomatik
   sessizlik kesme/kelime sınırları gerekiyorsa mevcut cuts.py hattını kullan.
5. Yüzsüz videoda yerel görsel veya video sahnelerini sırala. Seslendirme
   isteniyorsa önceden yerelde üretilmiş bir ses dosyasını `narration` olarak
   belirt. Piper/ComfyUI otomatik kurulmaz veya çalıştırılmaz. Seslendirme
   yoksa klip sesi korunur, sessiz görsellere sessiz ses izi eklenir.
6. Altyazıları **çıktının zaman çizelgesinde** ver. Buradaki altyazılar kullanıcı
   veya ajanın sağladığı metinlerdir; kendiliğinden transkripsiyon yapılmaz.
7. doctor ve preview çalıştır, önizlemeyi kullanıcıya göster. Final onayı
   kullanıcı incelemesinden sonra verilir. Otomatik yayınlama yoktur.

Örnek tanımlar: [examples/production](../examples/production). Medya dosyaları
dağıtılmaz; örneklerin `src/` yollarına kendi dosyalarını koymalısın.

## Sınırlar ve doğrulama

- `framing: fit` tüm görüntüyü siyah kenarlarla korur. `crop` merkezden keser;
  yüz takibi veya otomatik konu takibi yapmaz.
- Sabit görseller belirtilen süre boyunca gösterilir. AI görsel/video üretimi,
  Piper TTS, HyperFrames veya OpenMontage adaptörü bu sürümde yoktur.
- Ayrı `narration` yalnızca `faceless` modundadır; storyboard'dan kısa olamaz,
  uzun olduğunda çıktı süresinde kesilir ve sahnelerin sesinin yerine geçer.
- Yerel yollar proje içinde kalmalıdır. Ağ protokolleri FFmpeg girişlerinde
  kapalıdır. Komutlar kabuk kullanılmadan çalışır. Bu bir OS güvenlik sandbox'ı
  değildir; harici kodları veya paketleri kontrol altına almaz.
- Ön kontrol binary, kodek, ASS filtresi, medya türü ve süreleri denetler;
  render sonrası boyut/süre ve tam decode kontrolü yapılır. Kalite, kadraj,
  metin doğruluğu ve haklar insan tarafından değerlendirilir.
- Bir projede en fazla 200 segment, segment başına 1 saat, toplam 2 saat.
  Kesimler 30 fps'e yeniden örneklenir; kelime sınırı motorunun yerine geçmez.

## Varsayılan ücret engeli

`plan_provider.py` uzak API çağrılarını varsayılan olarak reddeder. Ücretli
akış isteyen bir kullanıcı hem `VIDEO_WORKBENCH_ZERO_SPEND=0` ayarlamalı hem
`--allow-remote` vermelidir. Normal kullanımda bunları değiştirme. Yerel
sunucular ve kullanıcı tarafından seçilen CLI adaptörlerinin kendi davranışı
ayrıca kontrol edilmelidir; yerel bir sunucunun buluta yönlendirmediği garanti
edilmez. Üretim yürütücüsünün API/CLI sağlayıcı seçeneği yoktur.
