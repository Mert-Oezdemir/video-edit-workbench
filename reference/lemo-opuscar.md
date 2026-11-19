# Lemo-Opuscar — isteğe bağlı sinematik stil planlama

**Durum:** Yerel stil keşfi + planlama ve **Workbench production.json içinde doğrulanmış görsel sahne** desteği hazır. Lemo filminin kodla üretimi hâlâ ayrı upstream araç zincirinde yapılır; Workbench'in mevcut FFmpeg/Whisper, Shorts, faceless ve own-footage yolları korunur.

[Lemo-Opuscar](https://github.com/lemomo-ai/lemo-opuscar), kodla film üretmek için 99 stil sunan, özellikle Claude Code odaklı bağımsız bir projedir. Bu adaptör yerel stil JSON kayıtlarını okuyup bir ön plan çıkarır. **Lemo, Workbench'e alternatif bir mod değil; bütün mevcut üretim modlarının içine eklenebilen görsel içerik bileşenidir.** Lemo'nun film üreten motoru Workbench'e gömülü değildir, ancak ayrı üretilmiş klipler mevcut production.json zaman çizelgesinde doğrudan birleştirilebilir.

## Ajanın karar ağacı ve yetenek haritası

Ajanın ne zaman Lemo kullanacağı, ne zaman mevcut `workbench.py` iş akışında
kalacağı, 99 stilin kullanım alanları, hangi komutun sadece plan verdiği ve
hangi kalite/onay kontrollerinin gerektiği:
**[Lemo-Opuscar agent workflow](lemo-opuscar-agent-workflow.md)**.

Yerel kütüphanede stilleri anahtar kelimeyle daraltmak için:
`python scripts/lemo_opuscar.py search --query "explainer" --limit 8 --json`.
Bu yalnızca metadata aramasıdır; otomatik üretim veya kalite sıralaması değildir.

## İlk kullanım

Önce Workbench projesi oluştur:

    python workbench.py init my-videos

İhtiyacın varsa ve upstream kaynağını incelediysen Lemo'yu ayrı bir dizine **elle** kur:

    git clone https://github.com/lemomo-ai/lemo-opuscar.git ~/lemo-opuscar

Mevcut yerel klonu kullanarak:

    python scripts/lemo_opuscar.py doctor --json
    python scripts/lemo_opuscar.py list
    python scripts/lemo_opuscar.py list --json
    python scripts/lemo_opuscar.py plan --project my-videos --style neon-tubes

Varsayılan kütüphane ~/lemo-opuscar dizinidir. Farklı dizin için her komuta **--library PATH** ekle veya **LEMO_OPUSCAR_LIBRARY** ortam değişkenini kullan.

Plan yalnızca yeni bir **my-videos/work/style-plans/lemo-neon-tubes.json** dosyası oluşturur; mevcut dosyanın üzerine yazmaz. İkinci plan için **--name take-2.json** kullanılabilir. JSON, seçilen stilin adı/kategorisi, yerel orijinal STYLE.md dosyasına yol referansı, lisans notları ve insan onayı adımlarını içerir. Stil rehberinin metni kopyalanmaz. Plan video değildir, kurulumu başlatmaz ve onay anlamına gelmez.

## Harici üretimden Workbench'e dönüş

Lemo ile gerçek film yapmayı seçersen [orijinal kurulum ve kullanım yönergelerini](https://github.com/lemomo-ai/lemo-opuscar#install) incele. Bu, Workbench'in hızlı yerel faceless render komutundan ayrı bir uygulamadır. Upstream Node 20+, Python 3.11+, FFmpeg 7+ ve uygun bir kodlama ajanı ister; bazı stiller resim üretme aracı da gerektirebilir.

Lemo tarafından ayrı üretilmiş, hakları sana ait bir MP4 dosyasını örneğin **my-videos/work/external/lemo-opuscar/film.mp4** konumuna **elle** yerleştir. Sonra:

    python scripts/external_handoff.py --project my-videos --tool lemo-opuscar --mode faceless --kind rendered-video --asset work/external/lemo-opuscar/film.mp4 --out work/handoffs/lemo-film.json --provenance "Local Lemo production; rights reviewed"

Bu işlem mevcut MP4'ü FFprobe ile kontrol eder ve **pending-human-review**, **approved: false** bir manifest oluşturur. Ardından videoyu **mevcut Workbench production.json segments listesine** visual_component alanıyla ekleyebilirsin; Workbench aynı preview/final motoruyla onu diğer görüntülerle render eder. Stil manifestinin olması **tek başına onay değildir**; gerçek önizleme onayı gerekir. Detaylı [yerel bileşen örneği](production.md#lemo-opuscar-görsel-içerik-parçası-yerel-workbench-timeline).

## Lisans, maliyet ve sınırlar

- Upstream'in kendi kodu MIT, Markdown stil rehberleri ve promptları **CC BY-NC 4.0** kapsamındadır. Orijinal lisans film yapımına yönelik sınırlı ek izin sunar; rehberleri genel amaçlı ticari bir üründe yeniden dağıtma izni vermez. Stil rehberleri ve demo medyaları bu repoya alınmaz.
- Üçüncü taraf ses/görsel/font ve karakterler ayrı haklarla korunabilir. Ticari kullanım öncesi [upstream LICENSE](https://github.com/lemomo-ai/lemo-opuscar/blob/main/LICENSE) ve ilgili CREDITS belgelerini incele.
- Bu adaptör **hiçbir ağ isteği, otomatik indirme, kurulum, ücretli API/model çağrısı, medya yükleme veya video render** işlemi yapmaz.
- Stil planı, mevcut footage kurgusu ile birbirini dışlamaz: Lemo videoları uzun-to-shorts, faceless veya own-footage projelerinde isteğe bağlı giriş, ara sahne veya kapanış olarak kullanılabilir. Basit kesme ve altyazı işleri için Lemo yine gerekli değildir.
- Testler: **python -m unittest discover -s tests -v**. Yerel kütüphane varsa **python scripts/lemo_opuscar.py doctor --json**.
