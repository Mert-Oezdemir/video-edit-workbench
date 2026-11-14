# Video Edit Workbench

This edition builds on [claude-video-edit](https://github.com/YildizDikme/claude-video-edit) by YildizDikme, commit `b7093e25373271cc33475958fe7d850a71da4223`. The upstream copyright notice and MIT license are in [LICENSE](LICENSE). The upstream example photos are omitted. The HTML template references Google Fonts and GSAP at runtime, and the repository does not bundle those dependencies.

## Understand before editing / Kurgudan önce konuyu anla

For each new video the host agent follows [editorial intake](reference/editorial-intake.md): inspect the topic, footage and requirements, agree on a concise plan, ask about current-source research and new user-supplied material, and get authorization for substantive content changes. No new runtime dependency is needed.

## Lightweight first / Önce hafif kurgu

The recommended default is Python + NumPy + FFmpeg/FFprobe + one local Whisper backend. Use one optional planner and one compact decision packet. No additional Python or Node dependencies are introduced by the low-token and creative scripts. A plain preview does not require Node, Chrome, MCP, GPU, multiple agents or an AI API. For an approved plain final use the existing source-resolution build and mix.py --no-sfx. Captions and simple cards are opt-in, using FFmpeg with libass. Visual QA, complex graphics, effects and the browser renderer are opt-in. Do not install Blender, Remotion, MediaPipe or other suggested tools by default.

**Türkçe:** Transkript → tek isteğe bağlı AI kararı → kesim/önizleme → onay → çıktı. Ek özellikler yalnızca gerektiğinde çalıştırılır.

Tool-capable AI agents can consult [the on-demand tool catalog](reference/tool-catalog.md) and install individual optional tools when a specific job needs them. The catalog is not a dependency list. See [AGENTS.md](AGENTS.md) for provider-neutral agent instructions.

## Provider-neutral low-token editing / Modelden bağımsız düşük tokenli kurgu

The optional [low-token workflow (Türkçe guide)](reference/low-token.md) passes compact transcript IDs to any planner, including Claude, Codex, another chat model, a compatible cloud/local API, or no AI at all. Existing Python/FFmpeg cutting, verification, graphics and rendering stay local. Start with `scripts/low_token.py` and `scripts/plan_provider.py`; review the proposed removals before applying them. No provider is required.

## Creative editing tools / Yaratıcı kurgu araçları

The optional [creative tools guide (Türkçe)](reference/creative-tools.md) adds local SRT/ASS captions, word-anchored reusable motion-text cards, 1080p portrait/landscape presets, FFmpeg overlay rendering and a non-destructive visual quality report. The existing GSAP/Three.js scene and 4K render remain available. No model is required for captions or QC.

## Quick start — lightweight (no server, no API key)

Clone this public repository, install Python 3.10+ and FFmpeg/FFprobe for your OS from their official sources, then run:

```sh
git clone https://github.com/Mert-Oezdemir/video-edit-workbench.git
cd video-edit-workbench
python -m venv .venv
```

Activate the environment (macOS/Linux: `source .venv/bin/activate`; Windows PowerShell: `.venv\Scripts\Activate.ps1`). Install one local transcription backend:

```sh
python -m pip install -r requirements.txt faster-whisper
python scripts/doctor.py
```

Use a separate working folder for your video. Put recordings in its `src/` directory. Tell any tool-capable coding agent to read this repository's `AGENTS.md` and edit that folder. It should follow the editorial intake, then use the [compact workflow](reference/low-token.md). The first Whisper run may download model weights; select a smaller multilingual model such as `small` on modest hardware, and use the same model during verification. The AI provider is optional.

For manual CLI use, see the [step-by-step workflow](reference/low-token.md); substitute the actual path to this repository for SKILL. For captions/cards see [creative tools](reference/creative-tools.md). Node, Chrome and the local MCP bridge are optional advanced features, not requirements for a plain edit. Never commit private recordings, transcripts, API keys or output files.


## Check an edit list before cutting

Run `python scripts/preflight.py --project PATH` after creating `work/edl.json`. The command checks the edit list and confirms referenced media and transcript files. It exits with status 1 on problems and leaves the project untouched. It requires Python 3.10+ and the standard library. The rest of the pipeline uses the dependencies listed below.

## Frame accuracy and transcription devices

Cut ranges round outward to cover the complete requested interval, including a partial final frame. Audio fades are bounded to the length of each piece, including single-frame pieces at high frame rates.

Faster-whisper defaults to CPU so CUDA libraries are optional. Use `--device cuda` or `--device auto` on both `scripts/transcribe.py` and `scripts/verify.py` when your GPU runtime is installed. A small model can be selected with `--model tiny.en` for an English smoke test. The default model is `large-v3`.

Run the regression checks with `python -m unittest discover -s tests -v` after installing NumPy.

## Upstream workflow

A Claude Code skill that edits talking-head, tutorial, explainer and Short videos together with you: word-accurate cuts, motion graphics locked to your words, sound effects made from math, honest loudness, frame-exact 4K renders.


> **This repo makes good edits possible. It does not make them for you.**
> The real power is still yours: your eye, your notes, your taste. Claude cuts, measures and builds fast. You watch, give notes and decide.

[Türkçe açıklama aşağıda](#türkçe).

## Advanced browser workflow (original skill)

**1. Install the optional browser tools.** Python 3.10+, ffmpeg, Node 20+, Google Chrome, and one Whisper backend.

macOS (Apple Silicon, with [Homebrew](https://brew.sh)):

```bash
brew install python ffmpeg node numpy whisperkit-cli
```

Linux or Windows: install ffmpeg, Node 20+ and Chrome from their sites, then (in a virtual environment if your system asks for one):

```bash
python3 -m pip install numpy faster-whisper
```

It is built and tested on macOS. Linux and Windows use the same tools but are less tested.

**2. Install the skill.**

```bash
git clone https://github.com/Mert-Oezdemir/video-edit-workbench ~/.claude/skills/video-edit
```

That is all. You do not paste anything into a prompt: Claude Code loads the skill by itself and uses it whenever you ask for a video edit. To update later: `git -C ~/.claude/skills/video-edit pull`.

**3. Edit a video.** Make a folder, put your raw clips in `src/`, and open Claude Code there:

```bash
mkdir my-video && cd my-video && mkdir src
# copy your clips into src/
claude
```

Then just say what you want, for example:

> Edit the clips in src into a 10-minute educational video. Cut retakes and pauses. Propose chapters. Calm graphics, no sound effects.

> This is a Short. Tight cuts, captions on, more energetic graphics.

**4. The first time, Claude gets to know you.** It asks a few questions in one message (your name, your colours, your logo, your usual videos, sound effects or not) and remembers the answers for every later video. See [It remembers you](#it-remembers-you).

## How a session goes

1. Claude transcribes the clips, makes a rough cut (retakes and pauses out, words never clipped) and gives you a preview link.
2. You watch and give notes with timestamps: "0:36 cut the pause after this word", "1:12 show an example here". One round at a time. Screenshots of what you mean help a lot.
3. Claude proposes chapters, then builds the graphics chapter by chapter, and you review each part.
4. Sound effects only if you want them.
5. When you approve the preview, Claude renders the final video (up to 4K) and gives you the length, the loudness and the YouTube chapter list.

Good edits come from these short review loops. Expect several rounds.

## What it can do

<table>
<tr>
<td width="50%">Explains with real data: the video's own sound, measured every 10 ms, the math on screen.</td>
<td width="50%">Frames that lock onto the part of the screen being talked about and follow the scroll.</td>
</tr>
<tr>
<td>Abstract ideas drawn: what "the model needs a lot of data" actually means.</td>
<td>Real results from the recording instead of invented examples.</td>
</tr>
<tr>
<td>Mistakes shown honestly: the real screenshot, the note, the fixed version.</td>
<td>Your name and colours from your profile, on every video.</td>
</tr>
</table>

The upstream workflow describes these uses of the editing tools.

## It remembers you

On the first run Claude asks, in one message: your name and role for the lower third, your channel and languages, the colours you like and the ones you never want, your logo, your usual video types, and whether you want sound effects. The answers go to `~/.claude/video-edit/profile.md` (your logo to `~/.claude/video-edit/brand/`) and are used in every later video without asking again.

When you give a rule meant for all your videos ("no sound on transitions", "always deliver 4K"), Claude adds it to the profile and tells you. The profile stays on your computer; it is never part of a project or a repository. You can open and edit it any time.

## Creative, with purpose

The skill tells Claude to explain, not decorate: draw the abstract idea, show a small "what is this" box for tools the viewer may not know, use the video's own measured data and your real screenshots, show mistakes with the real before and after, and vary the form instead of pasting the same card. Videos are split into chapters by meaning, with titles that say what the viewer gets.

Transitions are part of the template: a short chapter veil that closes before the cut, a text veil for inserts and montages, a blur dip where the picture jumps, a dark blur dip where a cut changes the subject, and a calm goodbye screen. They are silent by default.

## Why it works: Claude can't hear

Everything this skill knows about sound is measured: word timestamps from Whisper, a 10 ms energy envelope, loudness meters. So the workflow is built around that:

- **Cuts follow the measured energy, not guesses.** Each cut snaps to the real start and end of a word in the waveform.
- **Picture and sound share one clock.** Graphics and sound effects are triggered from the same timeline, so effects land on the picture without anyone listening for sync.
- **The voice is never processed by default.** No noise reduction, EQ or compression: one linear gain only. Those filters are the usual cause of muffled voices.
- **A human reviews every stage.** Your ear is the final check for clipped words and effect levels.

## Try it without footage

```bash
cd ~/.claude/skills/video-edit
python3 scripts/sfx.py lib --out template/sfx
python3 scripts/serve.py --project . --port 5600
```

Open http://127.0.0.1:5600/template/?demo and press Space.

## What is inside

```
SKILL.md              the workflow Claude follows
reference/audio.md    cutting rules, loudness, sound effects, captions (the most important file)
reference/style.md    glass cards, neutral palette, typography, motion, transitions, things to avoid
reference/profile.md  the creator profile Claude writes on the first run and reads every time
reference/edl.md      the edit-list format
scripts/              transcribe, cuts, build, verify, loudness, sfx, mix (Python) · render, audit (Node)
template/             a scene page: engine, glass-card styles, chapter veils, transitions, demo beats
```

## Video types

| Type | Graphics | Effects | Cuts |
|---|---|---|---|
| Educational / explainer | calm, clear diagrams, slow camera, three.js only when it explains | none, or only where a sound is the subject | natural |
| Talk | few long-lasting cards, never over the face | none by default | natural or tight |
| Tutorial | zoom into the screen, highlight frames, steps | optional soft clicks | natural |
| Short | bigger, faster, hook in 2 s, captions | allowed, under the voice | tight |

## Limits

- Claude can't judge taste, emotion, or whether a mix "sounds good". Listen to every flagged join and every effect level.
- Whisper makes mistakes with names and technical words. Check the transcript.
- It is made for talking-head, tutorial, screen-recording and Short videos. Colour grading, multi-camera edits and music videos are not covered.
- Long videos take time and tokens. On a smaller plan, work chapter by chapter.
- Rendering through a browser is slow, about 10 fps per worker at 1080p. Use several workers for long videos.

## License

MIT. See `LICENSE`.

---

## Türkçe

Konuşma, eğitim, ekran kaydı ve Short videolarını sizinle birlikte editleyen bir Claude Code skill'i: kelime sınırından kesim, sözlerinize kilitli animasyonlar, matematikten üretilen ses efektleri, doğru ses seviyesi ve kare kare 4K render.

> **Bu repo iyi edit yapmayı mümkün kılıyor, sizin yerinize yapmıyor.**
> Asıl güç hâlâ sizde: gözünüz, notlarınız, zevkiniz. Claude hızlı keser, ölçer ve kurar; siz izler, not verir ve karar verirsiniz.

### Gelişmiş tarayıcı iş akışı (orijinal skill)

**1. İsteğe bağlı tarayıcı araçlarını kurun.** Python 3.10+, ffmpeg, Node 20+, Google Chrome ve bir Whisper.

macOS (Apple Silicon, [Homebrew](https://brew.sh) ile):

```bash
brew install python ffmpeg node numpy whisperkit-cli
```

Linux ya da Windows: ffmpeg, Node 20+ ve Chrome'u kendi sitelerinden kurun, sonra (sisteminiz isterse bir sanal ortam içinde):

```bash
python3 -m pip install numpy faster-whisper
```

macOS'ta geliştirildi ve test edildi. Linux ve Windows aynı araçları kullanır ama daha az denendi.

**2. Skill'i kurun.**

```bash
git clone https://github.com/Mert-Oezdemir/video-edit-workbench ~/.claude/skills/video-edit
```

Bu kadar. Hiçbir şeyi prompta yapıştırmanız gerekmez: Claude Code skill'i kendisi yükler ve video editlemek istediğiniz her seferde kullanır. Güncellemek için: `git -C ~/.claude/skills/video-edit pull`.

**3. Video editleyin.** Bir klasör açın, ham kliplerinizi `src/` içine koyun ve Claude Code'u orada açın:

```bash
mkdir videom && cd videom && mkdir src
# kliplerinizi src/ içine kopyalayın
claude
```

Sonra ne istediğinizi söyleyin. Örneğin: "src içindeki klipleri 10 dakikalık bir eğitim videosuna çevir. Tekrarları ve duraksamaları kes, bölüm öner, animasyonlar sakin olsun, efekt koyma."

**4. İlk seferde Claude sizi tanır.** Tek mesajda birkaç soru sorar (adınız, renkleriniz, logonuz, genelde çektiğiniz videolar, ses efekti isteyip istemediğiniz) ve cevapları sonraki bütün videolar için hatırlar.

### Bir çalışma nasıl ilerler

1. Claude klipleri yazıya döker, kaba kurguyu yapar (tekrarlar ve duraksamalar çıkar, kelimeler kırpılmaz) ve size bir önizleme linki verir.
2. Siz izler ve zamanla not verirsiniz: "0:36'da bu kelimeden sonraki boşluğu kes", "1:12'de buraya örnek koy". Her seferinde bir tur. Ne demek istediğinizi gösteren ekran görüntüleri çok işe yarar.
3. Claude bölümleri önerir, sonra animasyonları bölüm bölüm kurar; her parçayı siz kontrol edersiniz.
4. Ses efektleri sadece isterseniz.
5. Önizlemeyi onayladığınızda Claude final videoyu (4K'ya kadar) render alır; süreyi, ses seviyesini ve YouTube bölüm listesini verir.

İyi edit bu kısa kontrol turlarından çıkar. Birkaç tur bekleyin.

### Sizi hatırlar

İlk kullanımda Claude tek mesajda sorar: alt bant (lower third) için adınız ve unvanınız, kanalınız ve dilleriniz, sevdiğiniz ve hiç istemediğiniz renkler, logonuz, genelde çektiğiniz video türleri ve ses efekti isteyip istemediğiniz. Cevaplar `~/.claude/video-edit/profile.md` dosyasına (logo `~/.claude/video-edit/brand/` klasörüne) kaydedilir ve sonraki her videoda tekrar sorulmadan kullanılır.

Tüm videolarınız için bir kural verdiğinizde ("geçişlerde ses olmasın", "her zaman 4K ver") Claude bunu profile ekler ve size söyler. Profil sizin bilgisayarınızda kalır, hiçbir projeye ya da repoya girmez. İstediğiniz zaman açıp düzenleyebilirsiniz.

### Yaratıcı ama amaçlı

Skill, Claude'a süslemeyi değil anlatmayı söyler: soyut fikri çizer, izleyicinin bilmeyebileceği araçlar için küçük bir "bu nedir" kutusu gösterir, videonun kendi ölçülmüş verisini ve sizin gerçek ekran görüntülerinizi kullanır, hataları gerçek önce/sonra haliyle gösterir. Video anlamına göre bölümlere ayrılır, başlıklar izleyicinin ne öğreneceğini söyler.

Geçişler şablonun içinde: kesimden önce kapanan kısa bölüm perdesi, araya giren videolar ve kesitler için yazılı perde, görüntünün sıçradığı yerde bulanık geçiş, konunun değiştiği kesimde kararan bulanık geçiş ve sakin bir veda ekranı. Varsayılan olarak geçişlerde ses yoktur.

### Neden işe yarıyor: Claude duymaz

Bu skill sesle ilgili her şeyi ölçerek yapar: Whisper kelime zamanları, 10 ms'lik enerji zarfı ve ses yüksekliği ölçümleri. Bu yüzden:

- **Kesimler ölçülen enerjiye göre yapılır.** Kelime başları ve sonları dalga formundaki gerçek yerinden kesilir.
- **Görüntü ve ses aynı saatten tetiklenir.** Animasyon da efekt de aynı zaman çizelgesinden çalıştığı için efekt görüntüye oturur.
- **Ses varsayılan olarak işlenmez.** Gürültü azaltma, EQ ya da kompresör yok, sadece doğrusal kazanç var. Boğuk sesin en sık sebebi bu filtreler.
- **Her aşamayı bir insan kontrol eder.** Kırpılmış kelimede ve efekt seviyesinde son karar sizin kulağınız.

### Sınırlar

- Claude zevki, duyguyu ya da bir sesin "güzel olup olmadığını" yargılayamaz. İşaretlenen her birleşimi ve her efekt seviyesini dinleyin.
- Whisper isimlerde ve teknik kelimelerde hata yapar. Dökümü kontrol edin.
- Konuşma, eğitim, ekran kaydı ve Short videoları için yapıldı. Renk düzeltme, çok kameralı kurgu ve müzik videoları kapsamında değil.
- Uzun videolar zaman ve token ister. Küçük bir pakette bölüm bölüm çalışın.

Lisans: MIT.

## Local server and agent connection

Install Node 22 or newer and Git. From this repository run:

```sh
npm ci
npm start
```

Open the loopback URL printed by the command. The runtime is pinned to a specific revision of [Project Agent Bridge](https://github.com/Mert-Oezdemir/project-agent-bridge).

To connect an MCP-compatible agent, run `npm run mcp:config --silent` and add its `mcpServers` entry to your host. Run `npm run doctor` to see local project and account configuration.

Chrome or Edge is needed for agent browser controls. You can set `CHROME` in `.env`, or run `npx playwright install chromium` to install a browser.

Copy `.env.example` to `.env` before adding account settings. Keep `.env` local. Restart the runtime after changing it.

The MCP `video_run` tool supports the documented pipeline steps. Set `PYTHON` to the Python interpreter with your installed dependencies and `PROJECT_WORKSPACE` to the editing project. FFmpeg and FFprobe must be on PATH. The local URL opens the built-in scene demo.
