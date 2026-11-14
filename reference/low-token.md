# Düşük tokenli, modelden bağımsız kurgu

Bu yol Claude Code'a veya belirli bir aboneliğe bağlı değildir. Mevcut
video motoru (Python, FFmpeg, Whisper ve HTML/GSAP sahnesi) korunur.
Yeni katman yalnızca kaba kurgu için hangi konuşma parçalarının çıkarılacağını
önerir. Yapay zekâ ham videoyu, kelime zamanlarını ve işlem loglarını almak
zorunda değildir.

## Mimari

    src/ -> yerel transcribe.py -> work/transcripts + env
        -> low_token.py prepare -> küçük JSON
        -> seçilebilir plan_provider.py / herhangi bir sohbet
        -> insan kontrolü -> decisions.json
        -> low_token.py apply -> work/edl.json
        -> low_token.py preview -> cuts + build + verify -> proxy.mp4

Plan sözleşmesi: `{"revision":"paketteki tam kimlik","drop":["a:2","b:4"]}`.
Modelin komut, dosya yolu veya zaman kodu döndürmesine gerek yok. Belirsiz
parçalar korunur. Yerel tekrar ipuçları yalnızca adaydır; otomatik silinmez.
Mevcut EDL ve karar dosyaları sessizce üzerine yazılmaz.

## Kurulum ve kullanım

Python 3.10+, FFmpeg/FFprobe, NumPy ve bir Whisper backend'i gerekir. Alttaki
komutları video projesinin klasöründe çalıştır; `SKILL` yazan kısmı bu deponun
gerçek diziniyle değiştir. Örnek iki adet 30 fps uyumlu konuşma klibi içindir.
Her klibi gerçek kayıt sırasına göre belirt.

```sh
python SKILL/scripts/transcribe.py --project . src/take-01.mp4 src/take-02.mp4 --lang tr --backend faster-whisper
python SKILL/scripts/low_token.py --project . prepare --out work/planner-input.json
```

Sıra değişecekse prepare ve apply komutlarına aynı `--clips ID1 ID2` listesini
ekle. Kimlikler work/clips.json içindedir. Bu sürüm sessiz B-roll ve ayrı ses
kaydıyla otomatik kurgu yapmaz; mevcut EDL iş akışını kullan.

## Yapay zekâyı seç (yalnızca bir seçenek)

**API gerektirmeyen herhangi bir sohbet veya kod ajanı (Claude, ChatGPT, Codex,
Gemini vb.):**

```sh
python SKILL/scripts/plan_provider.py --packet work/planner-input.json --out work/planner-prompt.txt prompt
```

Oluşan metni seçtiğin araca ver (ya da ajana dosyayı okut). Yalnızca dönen JSON'u
work/decisions.json olarak kaydet. Harici araca yapıştırmak transkripti paylaşır;
gizli içerikleri gerekirse yerelde tut.

**Yerel Ollama veya OpenAI uyumlu sunucu:** endpoint ve model kurulumuna göre değişir.

```sh
python SKILL/scripts/plan_provider.py --packet work/planner-input.json --out work/decisions.json api --endpoint http://127.0.0.1:11434/v1/chat/completions --model MODEL
```

**Bulut API:** OpenAI uyumlu chat-completions veya Anthropic Messages protokolü.
Modelin kullanılan protokolü/parametreleri desteklemesi gerekir. API anahtarını
ortam değişkenine koy; repoya yazma. Örnek:

```sh
python SKILL/scripts/plan_provider.py --packet work/planner-input.json --out work/decisions.json api --endpoint https://api.anthropic.com/v1/messages --protocol anthropic --model MODEL --key-env ANTHROPIC_API_KEY --allow-remote
```

OpenAI uyumlu diğer sağlayıcılarda `--protocol chat` (varsayılan), sağlayıcının
tam endpoint'i, model adı ve doğru anahtar ortam değişkenini kullan. Yerel
sunucu dışındaki API'ler için `--allow-remote` zorunludur. Yönlendirmeler izlenmez.
API çağrısı ücretli olabilir ve yazılı transkripti sağlayıcıya gönderir.

**Özel CLI adaptörü:** stdin'den prompt alıp stdout'a sadece sözleşmeye uygun
JSON yazan herhangi bir program bağlanabilir. `cli --argv` JSON dizisi
olarak kullanıcının seçtiği çalıştırılabilir dosyayı ve argümanları alır
(örnek: `["python","my_adapter.py"]`). Kabuk çalıştırılmaz. Kendi adaptörünü
ve izinlerini kontrol et; üçüncü taraf kod ajanını araç izinleri kapalı,
salt okunur/sandbox ortamında çalıştır. Her ürünün kendi CLI arayüzü farklıdır.

**Hiç yapay zekâ kullanmadan:**

```sh
python SKILL/scripts/plan_provider.py --packet work/planner-input.json --out work/decisions.json keep-all
```

Bu seçenek bütün transkript parçalarını korur; mevcut kesme motoru doğal
duraklamaları düzenler. Konuşma tekrarı otomatik kaldırılmaz.

## Uygula ve önizle

Önce decisions.json içindeki çıkarılacak kimlikleri transkriptle karşılaştır.
Yanlış bir çıkarma varsa listeden sil. Sonra:

```sh
python SKILL/scripts/low_token.py --project . apply --decisions work/decisions.json --fps 30
python SKILL/scripts/low_token.py --project . preview --lang tr --backend faster-whisper
```

FPS kaynakla uyumlu olmalı. Gerekirse `--pace tight` kullan.
Apply var olan EDL'nin üzerine yazmaz. Yeni bir tur için önce eski EDL'yi,
programı ve önizlemeyi ayrı bir yedeğe taşı. Preview mevcut önizlemeyi varsayılan
olarak değiştirmez. İstersen yedek aldıktan ve oynatıcıyı kapattıktan sonra
`--rebuild` kullanabilirsin. Önizlemeyi aç ve work/verify.txt içindeki işaretleri
dinle; temiz rapor bile kusursuz kesim garantisi değildir. Ayrıntılı işlem
logları work/low-token-logs/ altında kalır.

Bölümler, grafikler, ses efektleri ve final render için mevcut SKILL.md ve
reference/ dosyalarındaki araçları kullan. Bu ilk sürüm sadece kaba kurgu
planlayıcısını değiştirilebilir yapar; otomatik grafik planlayıcısı, yeni
Remotion motoru veya arayüz eklemez. Tam kelime içi düzeltmeler için EDL'yi
manuel düzenle. Uzun transkriptlerde paket hâlâ büyük olabilir; klipleri
gruplara ayırarak ayrı projelerde hazırlamak mümkündür. Token tasarrufu
garanti edilmez ve henüz ölçülmemiştir.

Testler: `python -m unittest discover -s tests -p test_low_token.py -v`.
Bunlar sentetik veriyle sözleşmeyi ve offline adaptörleri kontrol eder;
gerçek medya veya ücretli sağlayıcı gerektirmez.
