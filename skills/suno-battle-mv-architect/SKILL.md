---
name: suno-battle-mv-architect
description: >-
  Suno AI 音樂對決與多角色動態歌詞 MV 全自動製片廠 (Suno Rap Battle & Multi-Character Dynamic Lyric MV + YouTube Shorts Studio)。
  專為 Suno AI / Udio 生成歌曲、雙人說唱對決 (Rap Battle)、歷史/動漫人物跨時空交鋒、雙人對唱與多角色主題曲設計。
  全自動執行：Groq Whisper 字級時間戳對齊 (`lyrics_timeline.json` + `.srt` + `.txt`)、多角色陣營主題色動態切換 (Speaker-Adaptive Theme HUD)、
  11 幕 16:9 動漫分鏡並發生圖與斜角聚光燈自動合成備援、30fps 音訊重拍震動與 64 段對稱頻譜視覺化、
  Windows 中文路徑安全讀寫 (`imdecode`/`tofile`)、微軟正黑體零豆腐字 (`◆`/`【】`) 雙行膠囊字幕、
  Intel QSV (`-pix_fmt nv12`) 硬體加速渲染（15 秒試片 + 全曲 1080p MP4 + 可選 9:16 直式 Shorts 版），
  並隨片產出品質審查報告與 YouTube Shorts 爆款上架文案包（3 款標題、陣營投票互動說明欄、置頂留言、SEO 標籤）。
  當使用者提到「把 Suno 歌做成 MV」、「做說唱對決 MV」、「Rap Battle 動畫 MV」、「雙人對唱歌詞 MV」、「歷史人物對決 MV」、
  「音樂轉成 YouTube Shorts 動畫」或提供 MP3 要求生成多角色動態歌詞影片與 Shorts 文案時觸發。
---

# Suno AI 音樂對決與多角色動態歌詞 MV 全自動製片廠 (`suno-battle-mv-architect`)

## Overview

本技能將一首原始 AI 生成歌曲（如 Suno AI、Udio 的 `.mp3` / `.wav`，特別是雙人說唱 Battle、多角色對唱或敘事型主題曲）端到端轉化為 **1080p 30fps 音訊反應式動態歌詞 MV**，並同步產出 **SRT/JSON/TXT 字幕包**、**抽幀品管報告**與 **YouTube / YouTube Shorts 爆款互動上架文案包**。

### 核心技術突破與防呆機制

1. **多角色陣營主題色動態切換 (Speaker-Adaptive Theme Engine)**：
   - 依據當前演唱角色自動切換頂部 HUD 狀態列、角色膠囊徽章、底部 64 段音訊頻譜與背景漂浮粒子的主題色（例如：東區青龍 `#00E5FF`、西區赤虎 `#EF4444`、擂台主持琥珀金 `#F59E0B`、副歌雙雄交鋒紫金 `#D946EF`）。
2. **音訊能量反應式視覺 (Audio-Reactive Bass & Spectrum)**：
   - 自動提取 30fps RMS 音訊能量包絡線，驅動重拍微震動 (Bass Camera Shake)、畫面呼吸縮放，以及底部 64 段鏡像高斯平滑頻譜條。
3. **零豆腐字規範 (Zero-Tofu Glyph Enforcement)**：
   - Windows 內建 `msjhbd.ttc`（微軟正黑體粗體）不支援彩色 Emoji（如 `🎙️`、`🪭`、`⚔️`、`🐺`），直接繪製會產生方框豆腐字（`▯`）。本技能強制使用字型原生支援之幾何符號（`◆`、`【`、`】`、`★`），確保 100% 無缺字。
4. **Windows 中文路徑安全讀寫 (Unicode-Safe OpenCV I/O)**：
   - 全面以 `np.fromfile` + `cv2.imdecode` 與 `cv2.imencode` + `.tofile` 取代 `cv2.imread` / `cv2.imwrite`，徹底解決 Windows 桌面或專案中文路徑讀取失敗問題。
5. **分鏡限流自動合成備援 (Rate-Limit Composite Fallback)**：
   - 若並行生圖遇 API 429 限流，內建對角線分割聚光燈合成器（Diagonal Split Spotlight Compositor），自動將雙方主角特寫與模糊舞台背景合成為高張力對峙分鏡，絕不卡關。
6. **Intel QSV 硬體加速正確偵測 (`-pix_fmt nv12`)**：
   - 測試與啟動 `h264_qsv` 時顯式帶入 `-pix_fmt nv12`，避免假性偵測失敗，達成 14~25 fps 極速渲染（無 QSV 環境自動降級 `libx264 -preset ultrafast`）。

---

## Dependencies

本技能整合並協同以下既有技能（請優先參考對應技能規範，不重複造輪子）：

- **`audio-to-srt`**：使用 Groq Whisper (`whisper-large-v3-turbo`) 取得 word-level 與 segment-level 精準時間戳並校正繁體中文同音字。
- **`animated-mv-director`**：共用 16:9 動漫分鏡 Ken Burns 運鏡、1.2s Cross-Dissolve 轉場與 uint16 定點數 ROI 原處混色架構。
- **`draw-free` / `google-pics-ai` / `image-generator` Subagent**：用於並行生成 11 張 16:9 動漫分鏡底圖。
- **`short-video-workflow`**：用於 YouTube Shorts 9:16 直式版與短影音行銷包裝邏輯。

---

## Quick Start

當使用者提供音檔（如 `歌曲.mp3`）與歌詞（或由音檔自動轉錄）時，依序執行下列指令：

```powershell
# 1. 將技能範本複製到專案目錄（自動適配 Antigravity / Claude Code / Codex / 本地目錄）
$SkillDir = if (Test-Path "$HOME\.gemini\config\skills\suno-battle-mv-architect") { "$HOME\.gemini\config\skills\suno-battle-mv-architect" } elseif (Test-Path "$HOME\.claude\skills\suno-battle-mv-architect") { "$HOME\.claude\skills\suno-battle-mv-architect" } elseif (Test-Path "$HOME\.codex\skills\suno-battle-mv-architect") { "$HOME\.codex\skills\suno-battle-mv-architect" } else { ".\skills\suno-battle-mv-architect" }
Copy-Item "$SkillDir\scripts\render_engine_template.py" ".\render_engine.py"

# 2. 使用 Groq Whisper 提取字級時間戳 (需設定 GROQ_API_KEY 或 ~/.groq_api_key)
python "$SkillDir\scripts\transcribe_groq_words.py" --audio "歌曲.mp3" --output "whisper_raw.json"

# 3. 先導 15 秒試片渲染與自動抽幀質檢 (16:9 橫式)
python render_engine.py --mode preview --encoder auto --audio "歌曲.mp3" --timeline "lyrics_timeline.json" --output "專案_15s_preview.mp4"

# 4. 全曲完整版 1080p 渲染 (16:9 橫式)
python render_engine.py --mode full --encoder auto --audio "歌曲.mp3" --timeline "lyrics_timeline.json" --output "專案_full.mp4"

# 5. (可選) 產出 YouTube Shorts 專用 9:16 直式滿版 (1080x1920)
python render_engine.py --mode full --aspect 9:16 --encoder auto --audio "歌曲.mp3" --timeline "lyrics_timeline.json" --output "專案_shorts_9x16.mp4"
```

---

## Workflow（標準七階段工作流）

### 階段一：音檔查驗與 Groq 字級歌詞對齊
1. 將使用者提供的音檔複製至專案資料夾，執行 `ffprobe` 確認精準秒數、取樣率與聲道。
2. 執行 `scripts/transcribe_groq_words.py` 呼叫 Groq `whisper-large-v3-turbo`（含 `word` 與 `segment` 時間戳）。
3. 對照使用者提供的歌詞（若使用者未提供則直接依轉錄清字），將全曲切分為每段雙行（單行 ≤ 16 字）的結構化時間軸 `lyrics_timeline.json`，並標註：
   - `id`, `start`, `end`
   - `speaker`（角色顯示名稱，如 `臥龍・諸葛亮`）
   - `badge`（僅限 `◆`、`★`、`【】` 等幾何符號，**嚴禁 Emoji**）
   - `theme`（`amber` / `cyan` / `crimson` / `purple`）
   - `line1`, `line2`
4. 同步匯出標準 UTF-8 `.srt` 字幕檔與 `.txt` 純文字歌詞檔。

### 階段二：角色視覺 DNA 與 11 鏡動漫分鏡設計 (`storyboard_design.md`)
1. 建立 `storyboard_design.md`，明確鎖定各角色的 **Visual DNA**（髮型、服飾、代表道具、主題光效色溫）。
2. 規劃 10~11 個場景（涵蓋 Intro 舞台開場、選手介紹、Round 1 雙方交鋒、副歌能量對撞、Round 2 絕招對決、Outro 主持總結與觀眾投票定格），每鏡約 14~20 秒，指定 `zoom_in` / `zoom_out` / `pan_left` / `pan_right` 運鏡模式。

### 階段三：多 Subagent 並發生圖與自動合成備援 (`assets/`)
1. 啟動平行 `image-generator` Subagent 生成 `assets/scene_01.png` ~ `assets/scene_11.png`（16:9 橫幅，提示詞結尾必加 `NO text, NO watermark, NO letters`）。
2. 若任一分鏡遭遇 API 429 限流，`render_engine.py` 會自動觸發對角線分割聚光燈合成器（Diagonal Split Spotlight Compositor），將雙方特寫與舞台背景合成為對峙畫面，確保 11 張分鏡 100% 齊全。

### 階段四：音訊反應與角色自適應渲染引擎 (`render_engine.py`)
1. 預先將所有歌詞與角色膠囊徽章渲染為 RGBA 記憶體貼片（設定 `stroke_width=3` 黑色描邊確保高對比可讀性）。
2. 逐幀結合：
   - Ken Burns 運鏡 + 1.2 秒雙向 Cross-Dissolve 轉場 + 重拍鏡頭微震動
   - 底部漸層暗角遮罩 + 64 段音訊反應頻譜條 + 48 顆主題色上昇微粒
   - 頂部對決 HUD 橫幅 + 即時歌曲進度條 + 底部安全區雙行歌詞膠囊

### 階段五：15 秒試片抽幀品管與全曲渲染 (`qc_frames/`)
1. 先跑 `--mode preview` 產出 15 秒試片並抽幀至 `qc_frames/`，使用 `read_file` 視覺檢查：
   - 確認無任何 `▯` 豆腐字方框
   - 確認字幕置於安全區且不遮擋主角臉部
2. 試片通過後，立即執行 `--mode full` 完成全曲渲染，並於各角色段落抽取 4~6 張關鍵品管幀寫入 `quality_audit_report.md`。

### 階段六：YouTube & YouTube Shorts 爆款上架文案包 (`youtube_shorts_pack.md`)
每次交付（或當使用者要求上架 YouTube / Shorts 時），自動產出可直接複製貼上的行銷文案包：
1. **Shorts 爆款標題候選 3 款**（反差型、懸疑對決型、金句爆點型，附 `#Shorts`）。
2. **YouTube / Shorts 說明欄完整文案**：
   - 開場高張力 Hook
   - 雙陣營角色代表金句與亮點介紹
   - **觀眾投票互動 CTA**（例如：「👉 投【1】支持角色 A vs 👉 投【2】支持角色 B，在留言區刷起來！」大幅提升留言互動率）
   - 製作資訊與 `#Shorts` Hashtag 矩陣
3. **置頂留言範本（Pinned Comment）**：引導觀眾二選一投票與分享最愛歌詞。
4. **後台標籤（Tags）一鍵複製串**：以半形逗號分隔的 15~20 個高流量關鍵字。

---

## Utility Scripts

本技能於 `scripts/` 目錄提供兩個核心腳本範本：

1. `scripts/transcribe_groq_words.py`
   - 自動壓縮音檔為 16kHz 單聲道 MP3（避免超過 Groq 25MB 上限）並呼叫 Groq `whisper-large-v3-turbo` 取得字級與句級時間碼 JSON。
   - 用法：`python transcribe_groq_words.py --audio "input.mp3" --output "whisper_raw.json"`
2. `scripts/render_engine_template.py`
   - 支援 `--mode [preview|full]`、`--aspect [16:9|9:16]`、`--encoder [auto|qsv|x264]`、`--audio`、`--timeline`、`--scenes`、`--output`。
   - 內建中文路徑安全讀寫、零豆腐字檢查、音訊頻譜分析與 QSV `-pix_fmt nv12` 自動偵測。

---

## Common Mistakes（常見踩坑與防呆守則）

1. **在微軟正黑體 (`msjhbd.ttc`) 中使用 Emoji 導致方框豆腐字 (`▯`)**：
   - ❌ 錯誤：`badge: "🪭 臥龍・諸葛亮"` 或標題含 `⚔️`、`🎙️`。
   - ✅ 正確：一律改用 `◆`、`★`、`【`、`】` 等基本幾何符號，如 `"◆ 臥龍・諸葛亮"`。
2. **在 Windows 中文資料夾下直接呼叫 `cv2.imread` / `cv2.imwrite`**：
   - ❌ 錯誤：`cv2.imread(path)` 遇到中文路徑會靜默回傳 `None` 並報錯 `can't open/read file`。
   - ✅ 正確：務必使用 `cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)`。
3. **`h264_qsv` 偵測未指定 `-pix_fmt nv12` 導致誤判不支援**：
   - ❌ 錯誤：直接將 `rgb24`/`bgr24` 送入 `h264_qsv` 測試會回傳失敗。
   - ✅ 正確：在 FFmpeg 參數中加入 `-pix_fmt nv12`。
