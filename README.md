# 🤖 Auto Social Media Posting AI Agent

**বাংলায় AI-চালিত ভাইরাল ভিডিও জেনারেশন ও অটো-পোস্টিং বট**

এই প্রজেক্ট একটি সম্পূর্ণ অটোনোমাস AI সিস্টেম যা স্বয়ংক্রিয়ভাবে:
1. 🔍 **ট্রেন্ডিং টপিক খুঁজে বের করে** (Google Search Grounding + Gemini AI)
2. ✍️ **বাংলায় ভাইরাল স্ক্রিপ্ট লেখে** (Gemini API)
3. 🎨 **AI ইমেজ জেনারেট করে** (Pollinations AI — ফ্রি, কোনো API key লাগে না)
4. 🗣️ **বাংলায় ভয়েসওভার তৈরি করে** (Microsoft Edge Neural TTS — ফ্রি)
5. 🎬 **ভিডিও কম্পাইল করে** (MoviePy + PIL — সাবটাইটেল সহ)
6. 📱 **অটোমেটিক আপলোড করে** YouTube Shorts, TikTok, Facebook Reels-এ (Playwright ব্রাউজার অটোমেশন)
7. 📊 **টেলিগ্রাম নোটিফিকেশন পাঠায়** প্রতিটি ধাপে

---

## 📁 প্রজেক্ট স্ট্রাকচার

```
auto-socialmedia-posting-ai-agent/
├── .env                  # API keys ও কনফিগারেশন (গিটে পুশ হয় না)
├── .gitignore            # গিট ইগনোর ফাইল
├── requirements.txt      # Python ডিপেন্ডেন্সি তালিকা
├── config.py             # কনফিগারেশন লোডার
├── api_key_manager.py    # স্মার্ট API Key রোটেশন ম্যানেজার
├── trend_analyzer.py     # ট্রেন্ড অ্যানালাইসিস ও স্ক্রিপ্ট জেনারেশন
├── video_generator.py    # ভিডিও কম্পাইলার (TTS + ইমেজ + সাবটাইটেল)
├── social_poster.py      # ব্রাউজার অটোমেশন আপলোডার
├── queue_manager.py      # আপলোড কিউ ও হিস্ট্রি ডাটাবেস
├── telegram_notifier.py  # টেলিগ্রাম নোটিফিকেশন সিস্টেম
├── main.py               # মেইন অর্কেস্ট্রেটর ও শিডিউলার
├── app.py                # Flask ওয়েব সার্ভার (Render ডিপ্লয়মেন্ট)
├── download.py           # প্রজেক্ট ZIP ডাউনলোড ইউটিলিটি
├── Dockerfile            # Docker কনটেইনার কনফিগ
├── render.yaml           # Render.com ডিপ্লয়মেন্ট কনফিগ
└── render-cron.yaml      # Render Cron জব কনফিগ
```

---

## ⚡ কুইক স্টার্ট (Step by Step)

### ✅ Step 1: প্রজেক্ট ক্লোন করুন

```bash
git clone https://github.com/sheikhrifat734538-alt/auto-socialmedia-posting-ai-agent.git
cd auto-socialmedia-posting-ai-agent
```

### ✅ Step 2: Python Virtual Environment তৈরি করুন

```bash
python -m venv env
```

**Windows (PowerShell):**
```powershell
.\env\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.\env\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source env/bin/activate
```

### ✅ Step 3: ডিপেন্ডেন্সি ইন্সটল করুন

```bash
pip install -r requirements.txt
```

### ✅ Step 4: Playwright ব্রাউজার ইন্সটল করুন

```bash
playwright install chromium
```

### ✅ Step 5: `.env` ফাইল সেটআপ করুন

প্রজেক্ট ফোল্ডারে একটি `.env` ফাইল তৈরি করুন (যদি না থাকে):

```env
# --- AI API Keys (Sequential Rotation) ---
GEMINI_API_KEY=আপনার_প্রথম_কী_এখানে
GEMINI_API_KEY_2=আপনার_দ্বিতীয়_কী_এখানে
GEMINI_API_KEY_3=আপনার_তৃতীয়_কী_এখানে
# আরও কী যোগ করতে: GEMINI_API_KEY_4, GEMINI_API_KEY_5, ...

# --- Telegram Notification Settings ---
TELEGRAM_BOT_TOKEN=আপনার_বট_টোকেন
TELEGRAM_CHAT_ID=@আপনার_চ্যানেল_বা_চ্যাট_আইডি

# --- Posting Timing Configuration (24-hour format) ---
MORNING_POST_TIME=09:00
AFTERNOON_POST_TIME=15:00
EVENING_POST_TIME=21:00
```

> 💡 **Gemini API Key পেতে:** https://aistudio.google.com/app/apikey
> 💡 **Telegram Bot তৈরি করতে:** @BotFather-এ `/newbot` কমান্ড দিন

---

## 🔧 কমান্ড রেফারেন্স

### 🔐 1. সোশ্যাল মিডিয়া লগইন (প্রথমবার অবশ্যই করতে হবে)

```bash
python social_poster.py --login
```

এই কমান্ড একটি **ভিজিবল ব্রাউজার উইন্ডো** খুলবে। আপনাকে ম্যানুয়ালি লগইন করতে হবে:
- **Tab 1:** YouTube Studio (https://studio.youtube.com)
- **Tab 2:** TikTok (https://www.tiktok.com/login)
- **Tab 3:** Facebook (https://www.facebook.com)

লগইন শেষ হলে ব্রাউজার বন্ধ করুন। সেশন সেভ হয়ে যাবে।

---

### 🧪 2. কনফিগারেশন চেক

```bash
python config.py
```

আউটপুট দেখাবে সব কনফিগারেশন ঠিক আছে কিনা।

---

### 🔑 3. API Key স্ট্যাটাস চেক

```bash
python api_key_manager.py
```

আউটপুট দেখাবে:
- কয়টি key অ্যাক্টিভ
- কয়টি key কুলডাউনে
- প্রতিটি key-র বর্তমান অবস্থা

---

### 🔍 4. ট্রেন্ড অ্যানালাইজার টেস্ট (শুধু স্ক্রিপ্ট জেনারেশন)

```bash
python trend_analyzer.py
```

- Gemini AI দিয়ে ট্রেন্ডিং টপিক খুঁজে স্ক্রিপ্ট তৈরি করবে
- API key রোটেশন অটোমেটিক হবে
- সব key শেষ হলে fallback concept ব্যবহার করবে

---

### 🎬 5. ভিডিও জেনারেটর টেস্ট (শুধু ভিডিও তৈরি)

```bash
python video_generator.py
```

- একটি টেস্ট ভিডিও তৈরি করবে `generated_videos/` ফোল্ডারে
- AI ইমেজ ডাউনলোড + বাংলা TTS ভয়েসওভার + সাবটাইটেল

---

### 📢 6. টেলিগ্রাম নোটিফায়ার টেস্ট

```bash
python telegram_notifier.py
```

- একটি টেস্ট মেসেজ পাঠাবে আপনার টেলিগ্রাম চ্যানেলে

---

### 🚀 7. সম্পূর্ণ সাইকেল টেস্ট রান (ম্যানুয়াল — এক বার চালাবে)

```bash
python main.py --test-run
```

এই কমান্ড পুরো ওয়ার্কফ্লো **একবার** চালাবে:
1. ✅ পেন্ডিং আপলোড কিউ চেক
2. ✅ ট্রেন্ড খুঁজে স্ক্রিপ্ট লেখা
3. ✅ ভিডিও কম্পাইল করা
4. ✅ সোশ্যাল মিডিয়ায় আপলোড করা
5. ✅ টেলিগ্রাম নোটিফিকেশন পাঠানো

---

### ⏰ 8. অটো-শিডিউলার মোড (প্রতিদিন ৩ বার)

```bash
python main.py
```

এই কমান্ড বটকে **24/7 চালু** রাখবে। বট `.env`-তে সেট করা সময়ে অটোমেটিক কাজ করবে:
- 🌅 সকাল: `09:00`
- 🌤️ বিকেল: `15:00`
- 🌙 রাত: `21:00`

> ⚠️ **গুরুত্বপূর্ণ:** এই মোডে কম্পিউটার/টার্মিনাল বন্ধ করবেন না।

---

### 🌐 9. Flask ওয়েব সার্ভার (Render/Cloud)

```bash
python app.py
```

এন্ডপয়েন্ট:
| Route | Method | কাজ |
|-------|--------|-----|
| `/health` | GET | সার্ভার হেলথ চেক |
| `/login` | POST | ব্রাউজার লগইন শুরু |
| `/post_all` | POST | সম্পূর্ণ সাইকেল চালানো |
| `/download` | GET | প্রজেক্ট ZIP ডাউনলোড |

---

## 🔄 API Key রোটেশন সিস্টেম

এই প্রজেক্টে **স্মার্ট সিকোয়েন্শিয়াল API Key রোটেশন** ব্যবহার করা হয়:

```
রান শুরু → Key 1 ট্রাই
              ↓
         সফল? → ✅ কাজ শেষ!
              ↓ (429 এরর)
         Key 1 → ২৪ ঘণ্টা কুলডাউন → Key 2 ট্রাই
              ↓ (429 এরর)
         Key 2 → ২৪ ঘণ্টা কুলডাউন → Key 3 ট্রাই...
              ↓
         সব Key শেষ? → Fallback concept ব্যবহার
              ↓
         ২৪ ঘণ্টা পর → কুলডাউন অটো রিসেট
```

**নতুন key যোগ করতে:** `.env` ফাইলে `GEMINI_API_KEY_7=...`, `GEMINI_API_KEY_8=...` যোগ করুন।

---

## 📱 সম্পূর্ণ ওয়ার্কফ্লো ডায়াগ্রাম

```
┌─────────────────────────────────────────────────────────┐
│                   main.py (Scheduler)                    │
│         প্রতিদিন ৩ বার নির্দিষ্ট সময়ে চালু হয়               │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              queue_manager.py (Queue Check)               │
│   পেন্ডিং/ফেইল আপলোড আছে? → হ্যাঁ → রি-আপলোড           │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│     trend_analyzer.py + api_key_manager.py               │
│   Google Search → ট্রেন্ডিং টপিক → বাংলা স্ক্রিপ্ট          │
│   (API Key রোটেশন: Key1 → Key2 → Key3 → ...)            │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              video_generator.py                          │
│   AI ইমেজ → বাংলা TTS → সাবটাইটেল → MP4 ভিডিও           │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              social_poster.py (Browser Upload)            │
│   YouTube Shorts + TikTok + Facebook Reels-এ আপলোড      │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│              telegram_notifier.py                        │
│   সফল/ব্যর্থ নোটিফিকেশন টেলিগ্রামে পাঠায়                  │
└─────────────────────────────────────────────────────────┘
```

---

## 💰 খরচের বিবরণ

| সার্ভিস | খরচ | নোট |
|---------|------|------|
| Gemini API | ✅ ফ্রি | ফ্রি টায়ারে প্রতি মিনিটে 15 রিকোয়েস্ট |
| Pollinations AI (ইমেজ) | ✅ ফ্রি | কোনো API key লাগে না |
| Edge TTS (ভয়েস) | ✅ ফ্রি | Microsoft Edge নিউরাল TTS |
| Playwright (ব্রাউজার) | ✅ ফ্রি | ওপেন সোর্স |
| Telegram Bot | ✅ ফ্রি | @BotFather থেকে তৈরি |
| Render (হোস্টিং) | ⚠️ ফ্রি ১ মাস | তারপর ~$7/মাস |

> 💡 **সম্পূর্ণ ফ্রিতে চালাতে:** লোকালি `python main.py` দিয়ে চালান, Render-এর দরকার নেই!

---

## 🛡️ সিকিউরিটি নোট

- `.env` ফাইল কখনও গিটে পুশ হয় না (`.gitignore`-এ আছে)
- `api_key_state.json` কুলডাউন ডাটা লোকাল, গিটে যায় না
- `browser_sessions/` ফোল্ডার গিটে যায় না (লগইন সেশন)

---

## 📝 লাইসেন্স

এই প্রজেক্ট শিক্ষামূলক উদ্দেশ্যে তৈরি করা হয়েছে।

---

**তৈরি করেছেন:** [Sheikh Rifat](https://github.com/sheikhrifat734538-alt)
