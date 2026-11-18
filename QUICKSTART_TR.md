# 5 dakikada Video Edit Workbench (Türkçe)

Bu depoda **üç çalıştırılabilir ücretsiz yerel yol** var. `workbench.py` medya işlerini FFmpeg ile bilgisayarında yapar. Ücretli API kullanmaz, model indirme izni verilmedikçe Whisper indirmez, buluta görüntü yüklemez ve kaynak videoları değiştirmez.

## 1 — Bir kerelik kurulum

- Python **3.10+**, **FFmpeg/FFprobe** ve libx264 kurulu olmalı. Altyazıyı videoya gömmek için FFmpeg'in **libass** desteği gerekir.
- Git ile repoyu indir ve `python workbench.py doctor` çalıştır. Windows'ta `python`, macOS/Linux'ta `python3` gerekebilir.
- Daha önceki hassas kelime bazlı editör için isteğe bağlı olarak `python -m pip install -r requirements.txt faster-whisper` kullan. Yeni hızlı faceless/edit modları için Whisper ve NumPy zorunlu **değil**.

```sh
git clone https://github.com/Mert-Oezdemir/video-edit-workbench.git
cd video-edit-workbench
python workbench.py doctor
python workbench.py init my-videos
```

`my-videos/src/`: ham kaynaklar, senaryo, SRT ve hak sahibi olduğun görseller. `work/`: planlar ve iş kayıtları. `out/`: MP4, altyazı ve inceleme dosyaları. Oluşturulan hiçbir MP4 otomatik yayınlanmaz.

## 2 — Üç görevden birini seç

### A) Uzun videodan Shorts

Önce lisanslı/kendi kaydını `my-videos/src/recording.mp4` klasörüne koy. Bir transkript dosyan varsa:

```sh
python workbench.py shorts --project my-videos --input src/recording.mp4 --srt src/recording.srt --count 3 --burn-captions
```

SRT yoksa, mevcut **ücretsiz yerel** Faster Whisper'ı kullan. İlk model dosyası indirmesini **özellikle** kabul etmek için `--allow-model-download` ekle; indirme için internet gerekir ama ücretli ses API'si kullanılmaz:

```sh
python -m pip install faster-whisper
python workbench.py shorts --project my-videos --input src/recording.mp4 --use-whisper --model small --allow-model-download --burn-captions
```

Çıktılar `my-videos/out/shorts-recording/` altında. Klip seçimi, konuşma yoğunluğu ve giriş sinyalleri üzerinden **aday önerisidir**, gerçek AI akıl yürütmesi/viral başarı garantisi değildir. Mevcut AI aboneliğini kullanan bir kod ajanı daha iyi seçimi yapabilir: `--plan-only` ile aday JSON'u üretip ajanla gözden geçir ve `--selections` ile kullan. Kaynak sahibi olman ya da kullanım iznin olması gerekir.

### B) Yüz göstermeden sıfırdan Shorts

`my-videos/src/script.txt` içine birden çok paragraf (sahneler) koy veya `examples/faceless/script.txt` dosyasını kopyala.

```sh
python workbench.py faceless --project my-videos --script src/script.txt
```

Bu **sessiz** ama oynatılabilir, animasyon yerine okunabilir metin kartlarıyla hazırlanmış dikey MP4 üretir. İstersen telifini bildiğin görselleri `src/images/` içine koyup `--images src/images`, önceden kaydettiğin ses dosyasını `--narration src/voice.wav` olarak ekle. Tamamen yerel Piper kullanmak için `--piper-model src/model.onnx --voice-license-confirmed` seçeneği var: yerel Piper kurulu olmalı ve **ses modeli lisansına izin vermiş olmalısın**. Repo kendi başına ücretli AI video görüntüsü veya otomatik hikâye yazma API'si çalıştırmaz; metni mevcut AI aboneliğinle hazırlayabilirsin.

### C) Kendi videolarımı düzenlemek

```sh
python workbench.py edit --project my-videos --input src/take.mp4 --format portrait --remove-silence
```

Birden fazla girdi için `--input` seçeneğini tekrar et. `--start 12 --end 44` ile zaman aralığı ver. `--srt src/take.srt` ile kesintisiz **tek** klibe yerel altyazı ekle. Otomatik sessizlik temizleme ile SRT birlikte çalışmıyor (alıyazı zamanlarının bozulmasını önlemek için). Kelime hassasiyetinde, tekrar seçimi veya özel grafik için [mevcut gelişmiş düzenleyiciyi](reference/low-token.md) kullan.

## 3 — İnsan ve AI için arayüz

```sh
python workbench.py --help
python workbench.py tools
python workbench.py tools --mode faceless
python workbench.py shorts --help
python workbench.py faceless --help
python workbench.py edit --help
```

`AI_START.md` tek sayfalık AI ajanı başlangıcıdır. `AGENTS.md`, `SKILL.md` ve [ücretsiz araç kataloğu](reference/free-video-tool-stack.md) gelişmiş sistem seçimlerini içerir.

## 4 — Bilmen gereken sınırlar

- Her üretim için yeni hedef dosya/klasör kullan. **Var olan videoların üzerine yazılmaz.**
- Ücretsiz GitHub kodu ücretli HeyGen/Higgsfield/diğer sağlayıcı kredilerini ücretsiz yapmaz; bu modlar onlara bağlanmaz.
- İlk sürümde sesli yüzsüz video için yerel ses ya da izinli Piper modeli gerekir; sessiz video otomatik sunulur.
- Otomatik klip puanlaması basit yerel sezgiseldir; yayından önce sen seçmeli ve izlemelisin.
- Üçüncü taraf kaynak ve marka/logoları izinsiz çoğaltma. Lisansları incele.
- Tam araç listesi **hazır kurulum paketi değil**; yalnızca ihtiyacın olanları yerel olarak kurup test et.
- **Test:** `python -m unittest discover -s tests -v` ve `python workbench.py doctor`.

> Örnekler: [examples/README.md](examples/README.md). Sorun mu var? Önce `python workbench.py doctor` çalıştır, ardından ilgili `--help` sayfasını aç.
