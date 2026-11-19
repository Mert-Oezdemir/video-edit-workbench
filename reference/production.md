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

## Lemo-Opuscar görsel içerik parçası (yerel Workbench timeline)

Lemo **rakip/alternatif mod değildir**. İster uzun videodan Shorts, ister
faceless, ister kendi çekiminin kurgusu olsun, Workbench'in mevcut
\`production.json\` sıralamasındaki **tek bir görsel sahne** olarak eklenebilir.
İstenen stili yerel olarak bulmak için
[ajan kılavuzu](lemo-opuscar-agent-workflow.md) ve
[stil keşfi](lemo-opuscar.md) belgelerini kullan.

Bunun için Lemo'nun kendi motorunda **önceden oluşturulmuş** yerel videonun
proje içinde bulunması gerekir; Workbench Lemo'yu kendiliğinden çalıştırmaz.
Örnek bir intro klibini manuel olarak
\`my-project/work/external/lemo-opuscar/intro.mp4\` konumuna koyup
mevcut \`external_handoff.py\` ile proje içinde doğrulama manifesti oluştur:

~~~sh
python scripts/external_handoff.py --project my-project \
  --tool lemo-opuscar --mode own-footage --kind rendered-video \
  --asset work/external/lemo-opuscar/intro.mp4 \
  --out work/handoffs/lemo-intro.json \
  --provenance "Own rights-cleared Lemo code render"
~~~

\`python scripts/produce.py --project my-project init --mode own-footage\`
komutuyla mevcut projeyi oluştur; sonra \`production.json\` dosyasındaki
\`segments\` listesine **birincil kurgu kaydıyla birlikte** şunu ekle:

~~~json
{
  "schema_version": 1,
  "mode": "own-footage",
  "framing": "fit",
  "segments": [
    {
      "source": "work/external/lemo-opuscar/intro.mp4",
      "start": 0,
      "duration": 3,
      "visual_component": {
        "tool": "lemo-opuscar",
        "style": "neon-tubes",
        "handoff": "work/handoffs/lemo-intro.json"
      }
    },
    {"source": "src/own-take.mp4", "start": 0, "duration": 12}
  ],
  "captions": []
}
~~~

Bu **yeni bir Workbench üretim modu değildir**: aynı \`doctor → preview →
final --approve-preview SHA256\` komutları hem orijinal videoyu hem Lemo
görsel sahnesini **tek MP4** olarak işler. Segmentler listede bulunduğu
sırayla görünür; giriş/ara/kapanış için görsel segmenti uygun sıraya koy.
Altyazı zamanları **tüm yeni çıktı timeline'ına** göre düzenlenmelidir; Lemo
sahnesi eklenince mevcut altyazıların başlangıçları otomatik kaydırılmaz.
Ses, Lemo klibinde varsa standart segment sesi olarak kullanılır; müzik,
narration ve bölüm seviyeleri ayrıca incelenmelidir.

\`visual_component\` alanının amacı, stilin ve harici video kaynağının
**izlenebilirliğini ve güvenliğini doğrulamak**. Doğrudan
\`source\` alanı da gerçek medyadır: Workbench onunla beraber segmentleri
render eder. Bileşene ait handoff aynı projedeki
\`work/handoffs/*.json\` dosyasında bulunmalı, \`lemo-opuscar\` kaynağını,
\`rendered-video\` türünü, proje modunu ve *tam aynı medyayı* göstermelidir.
Bu kontrol Lemo'nun sahne tekniğini veya stil sadakatini otomatik test etmez.

Görsel segment ve handoff dosyası da mevcut SHA256 önizleme kimliğine dahil
edilir. Birisi kaynak dosyayı, zaman çizelgesini veya handoff'u değiştirdiğinde
eski önizleme onayı **geçersizleşir**. Doğrulanmamış medya otomatik olarak
kabul edilmez, hiçbir mevcut çıktı üzerine yazılmaz. \`workbench.py shorts\`
ve \`workbench.py edit\` hızlı başlangıç yolları aynı kalır: görsel bileşenli
kurgu için \`scripts/produce.py\` kullanılır.

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
