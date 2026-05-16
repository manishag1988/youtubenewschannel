# 100% Free AI YouTube Tech News Channel Roadmap

This roadmap covers every stage of producing a tech news YouTube channel using exclusively free tools—cloud-based and local. All recommendations are verified as 100% free as of May 2026, with no hidden paywalls or watermarks on outputs.

---

## 1. News & Content Research

**Goal**: Aggregate the latest tech news efficiently, identify trending stories, and gather source material for scripts.

| Tool | Type | Free Tier | Notes |
|------|------|-----------|-------|
| **Feedly** | Cloud | Free plan with unlimited feeds | Best for curating tech RSS feeds (TechCrunch, The Verge, Ars Technica, etc.). AI assist features available. |
| **FeedWave** | Cloud | Free tier with AI summaries | Gemini-powered summarization, privacy-first, auto-categorizes by topic. |
| **Particle** | Cloud | Free | Multi-source news summaries with strong source transparency. Best for fast catch-up. |
| **Google Alerts** | Cloud | Free | Set alerts for keywords like "AI news," "tech startup funding," "product launch." Email delivery. |
| **Horizon (GitHub)** | Self-hosted | Free (open-source) | Tech-news-specific aggregator. Fetches from Hacker News, RSS, Reddit, scores and summarizes with AI. Requires API keys (OpenAI, Claude, Gemini) which have free tiers. |

**Recommended workflow**: Use Feedly to follow 10-15 top tech outlets. Set Google Alerts for specific keywords. Run daily news check (30 min), pick 3-5 stories for the next video.

---

## 2. Script Writing

**Goal**: Convert news items into engaging, script-ready narratives optimized for video.

| Tool | Type | Free Tier | Notes |
|------|------|-----------|-------|
| **ChatGPT (OpenAI)** | Cloud | Free tier (GPT-4o access, limited) | Excellent for drafting news summaries. Prompt: "Write a 300-word YouTube intro for a tech news video about [topic]." |
| **Google Gemini** | Cloud | Free | 1.5 Pro model available. Strong for summarizing tech articles and generating video scripts. |
| **Claude (Anthropic)** | Cloud | Free tier, 5 messages/min | Great for nuanced script writing with consistent tone. |
| **DeepSeek** | Cloud | Free | Strong reasoning, good for tech explainer scripts. |
| **Outliner / Notion AI** | Cloud | Free tier | Use for structuring story arcs and bullet-point outlines. |

**Recommended workflow**: Feed the news into ChatGPT or Gemini with this prompt template:

```
Write a 2-minute YouTube narration script about [TOPIC]. 
Format: Hook (10 sec) → Context (30 sec) → Main story (60 sec) → Takeaway/CTA (20 sec).
Tone: Conversational, enthusiastic, tech-nerd energy. 
Include placeholders for B-roll descriptions in brackets.
```

Export as plain text, then import into your TTS tool.

---

## 3. Voiceover / Text-to-Speech

**Goal**: Convert scripts to natural-sounding audio for videos.

| Tool | Type | Free Tier | Notes |
|------|------|-----------|-------|
| **TTSMP3** | Cloud (browser-based) | 100% free, unlimited, no signup | 15+ natural AI voices. Up to 5,000 characters/generation. Output: MP3/WAV, no watermark. Uses Kokoro model. |
| **SoundTools** | Cloud (browser-based) | Unlimited, browser-only | Kokoro TTS model running locally. 20+ voices, no server uploads, complete privacy. |
| **Out Loud** | Desktop app | 100% free, open-source, offline | 50+ voices across 8 languages. MIT licensed. Runs locally—no internet needed after download. |
| **AnyVoice Lab** | Cloud | Unlimited free | 100+ voices in 50+ languages. 5,000 free credits to start. |
| **Google AI Studio (Gemini TTS)** | Cloud | Free tier | High-quality TTS via Gemini models. Sign in with Google. |
| **Fish Audio** | Cloud | 10,000 free credits/month | Good voice variety, supports Chinese and English well. |

**Recommended workflow**: Use TTSMP3 for speed and simplicity. Paste script, select voice (Adam or Rachel recommended for tech news), generate, download MP3. For total offline privacy, install Out Loud and run locally.

---

## 4. AI Video Generation (Visuals/B-Roll)

**Goal**: Generate AI visuals to accompany news narration, create motion graphics, or produce full AI-generated segments.

| Tool | Type | Free Tier | Notes |
|------|------|-----------|-------|
| **Kling AI 3.0** | Cloud | ~66 credits/day (refreshes daily) | Best for cinematic realism. 720p free, up to 10s clips. Daily credit refresh makes this sustainable. |
| **LoreMotion** | Cloud | Unlimited (with ad) | Uses LTX-Video 2.3. 720p MP4, no watermark. One short ad plays while rendering. 16:9, 9:16, 1:1, 4:3. |
| **Free.ai (CogVideoX)** | Cloud | 2,500 tokens/day (anonymous), 10,000 with signup | 2-6 second clips, 480p. Powered by open-source CogVideoX. No signup required. |
| **SeaArt** | Cloud | Generous free tier | Good quality, free credit pool for images and video. |
| **Luma Dream Machine** | Cloud | 8 videos/month (draft mode) | Decent quality, limited monthly. |
| **Pika Labs** | Cloud | ~80 credits/month | 3-4 second clips, stylized effects. |
| **WaveSpeedAI** | Cloud | Free tier with credits | Multi-model access (WAN, Kling, Veo, etc.) in one interface. Good for comparison. |

**For B-roll only**: Generate 3-5 second clips matching each script segment. Stitch together in editor. Kling offers the best quality-to-availability ratio for daily use.

**Alternative for local generation** (requires GPU):
- **ComfyUI + WAN 2.1/2.2** (self-hosted): Unlimited, no watermark. Requires NVIDIA GPU with 24GB+ VRAM.
- **LTX Desktop**: Open-source, runs locally. Requires RTX 5090 (32GB VRAM)—high barrier but truly free if you have the hardware.

---

## 5. AI Image Generation (Thumbnails, Graphics)

**Goal**: Create thumbnail images and title cards for videos.

| Tool | Type | Free Tier | Notes |
|------|------|-----------|-------|
| **Canva (Magic Media)** | Cloud | Limited free credits/day | AI image generation integrated into full design editor. Good for thumbnails with text overlay. |
| **Thumb-Free** | Cloud | 100% free, unlimited, no login | Enter video title + upload photo → AI generates multiple CTR-optimized thumbnails. |
| **Leonardo AI** | Cloud | 150 credits/day (free) | Strong for custom scenes. Good for creating unique thumbnail backgrounds. |
| **Flux (via fal.ai / SeaArt)** | Cloud | Free tier available | Excellent prompt adherence, good for tech-themed visuals. |
| **EditThisPic** | Cloud | 1 free edit/week, no signup | Upload photo → AI enhances for thumbnail style (contrast, colors, focus). |

**Recommended workflow**: Use Thumb-Free for quick thumbnail generation from title + your photo. For custom graphics, use Leonardo AI or Canva's Magic Media.

---

## 6. Video Editing

**Goal**: Assemble narration, AI video clips, images, and graphics into a final video.

| Tool | Type | Free Tier | Notes |
|------|------|-----------|-------|
| **CapCut** | Desktop/Mobile | 100% free, no watermark | Best all-around. Auto-caption, text-to-speech, background removal, smart cutout, AI filters. Works on mobile and desktop. Export up to 4K. |
| **DaVinci Resolve** | Desktop | Free version, full features | Professional-grade. Color correction, advanced audio, AI features (face refinement, speed warp). Steeper learning curve. |
| **Klippy** | Browser-based | 100% free, no signup, no watermark | AI-powered captions, easy interface, browser-based. |
| **Clipchamp** | Browser-based | Free (Microsoft) | Integrated with Windows. AI auto-compose, auto subtitles, AI voiceover. 1080p export free. |
| **OpenCut** | Desktop | 100% free, open-source, no watermark | Privacy-first alternative to CapCut. Cross-platform (Windows, macOS, Linux). |
| **OpenShot** | Desktop | 100% free, open-source | Beginner-friendly, basic keyframe animation. |
| **Kdenlive** | Desktop | 100% free, open-source | Linux-focused but available on all platforms. More advanced features than OpenShot. |

**Recommended workflow**: CapCut is the fastest path from script to finished video. Import TTS audio, add AI-generated video clips, add auto-captions (CapCut generates these), add thumbnail overlay, export.

---

## 7. AI-Powered Enhancements

**Goal**: Add subtitles, translations, background music, and finishing touches.

| Tool | Type | Free Tier | Notes |
|------|------|-----------|-------|
| **CapCut (Auto-captions)** | Included in editor | Free | Automatically generates captions from audio. |
| **YouTube Create** | Mobile app | Free | Google's AI video tool. Available in US, UK, Canada, Australia, NZ. Generates from script, adds visuals. Good for Shorts. |
| **Pixabay / Pixabay Music** | Cloud | Free, royalty-free | Background music for videos. No attribution required. |
| **Epidemic Sound (Free tier)** | Cloud | Limited free | Alternative music source. |
| **Moises.ai** | Cloud | Free tier | AI music separation and remixing. |

---

## 8. Publishing & SEO

**Goal**: Optimize video for YouTube discovery.

| Tool | Type | Free Tier | Notes |
|------|------|-----------|-------|
| **TubeBuddy** | Browser extension | Free tier | Keyword research, SEO suggestions, thumbnail A/B testing. |
| **vidIQ** | Browser extension | Free tier | Video ideas, SEO score, competitor analysis. |
| **YouTube Analytics** | Built-in | Free | Native analytics for watch time, retention, demographics. |

---

## Recommended Production Workflow

### Daily (30-45 min)
1. **News gathering** (15 min): Check Feedly + Google Alerts, pick 3 stories.
2. **Script generation** (10 min): Paste stories into ChatGPT/Gemini, generate script.
3. **Voiceover** (5 min): Paste script into TTSMP3, download MP3.
4. **Video generation** (10-15 min): Generate 3-5 AI B-roll clips via Kling or LoreMotion.

### Editing (15-20 min per video)
5. Open CapCut → import audio + video clips → add auto-captions → add thumbnail → export.

### Thumbnail (2-3 min)
6. Use Thumb-Free or Canva to generate thumbnail from video title.

### Weekly cadence
- Start with 3 videos/week (Mon/Wed/Fri).
- As workflow matures, scale to 5 videos/week.

---

## Quick-Start Tool Stack

| Stage | Recommended Free Tool |
|-------|----------------------|
| News aggregation | Feedly + Google Alerts |
| Script writing | ChatGPT (free tier) |
| Voiceover | TTSMP3 |
| Video generation | Kling AI (daily credits) |
| Image generation | Thumb-Free / Leonardo AI |
| Video editing | CapCut |
| Captions | CapCut auto-captions |
| Music | Pixabay |
| SEO | TubeBuddy (free tier) |

---

## Key Notes

- **No watermark** on free exports: CapCut, DaVinci Resolve, OpenCut, Kling (free tier exports), LoreMotion, TTSMP3, Thumb-Free.
- **Credit rotation**: Use Kling's daily 66 credits as primary video source. Supplement with LoreMotion or Free.ai when Kling credits run low.
- **Local-only alternatives**: Out Loud (TTS), ComfyUI + WAN (video), DaVinci Resolve (edit). These require no internet after installation and respect privacy.
- **Scaling**: As you produce more videos, you can self-host more tools (ComfyUI, LTX Desktop) to eliminate cloud limits entirely—but these require capable hardware.

---

This stack is fully functional today with $0 ongoing cost. Production time per video: ~60-90 minutes at the start, dropping to ~45 minutes once the workflow is internalized.