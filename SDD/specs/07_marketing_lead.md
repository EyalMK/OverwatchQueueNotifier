# Marketing Lead Specification
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0  
**Status**: Draft → Market Strategy

---

## 1. Go-to-Market Strategy (Phased)

### Phase 1: Stealth Beta (Weeks 1–4, Post-Sprint 0)
**Goal**: Gather early feedback, validate assumptions, stress-test infrastructure  
**Target**: 200–500 users (Discord communities)

- **Channels**: Overwatch subreddit, Discord gaming servers, Twitter (@game devs)
- **Messaging**: "We built a privacy-first AI tool to detect queue matches. Zero cloud, zero analytics. Help us test."
- **Incentive**: Early access, credit in release notes, free lifetime premium (if future tiers exist)
- **Recruitment**: Reddit post + "Looking for beta testers" tweet + Discord embeds
- **Feedback Loop**: Google Form + Discord channel for bug reports
- **Success Metrics**: 
  - 300+ signups
  - <5% uninstall rate after 1st week
  - 50+ bug reports / feature requests

### Phase 2: Soft Launch (Weeks 5–8, Post-Sprint 2)
**Goal**: Expand to broader audience, iterate based on beta feedback  
**Target**: 2K–5K users

- **Channels**: Twitch streamers (outreach), YouTube gaming channels, Reddit crosspost
- **Messaging**: "Overwatch Queue Notifier — Never Miss a Match Again"
- **Content**: Demo video (Remotion 90-sec), comparison to alternatives, testimonials from beta users
- **Positioning**: 
  - **vs. Manual checking**: "Stop alt-tabbing constantly. Never miss a queue."
  - **vs. Browser timers**: "AI-powered detection, not guessing. Works fullscreen."
  - **vs. Discord bots**: "Local inference, instant notifications, zero cloud."
- **SEO**: Blog post ("Why Queue Notifications Matter"), keyword: "Overwatch 2 queue monitor"
- **Launch Event**: Organize 1-hour Twitch stream with gameplay demo

### Phase 3: Growth (Weeks 9+, Post-Sprint 4)
**Goal**: Sustained growth via organic channels + paid amplification  
**Target**: 10K+ users

- **Channels**: 
  - Twitch/YouTube partnerships (affiliate, sponsorships)
  - Paid ads (Google Ads, Reddit Ads) targeting "Overwatch 2"
  - Product Hunt launch (if positioning unique)
  - Stream integrations (OBS plugins, Streamlabs)
- **Community**: Discord server for users, feature voting
- **Monetization**: Optional premium features ($0–5/month if v2.0 roadmap includes them)

---

## 2. Target Audience Segments

### Segment 1: Competitive Ranked Players
**Size**: ~200K (estimated across NA/EU/APAC)  
**Profile**: Ages 18–35, PC gamers, climb ladder (Gold+), 10+ hours/week  
**Pain**: Long queue times, fear of missing matches, rank decay pressure  
**Adoption Rate**: High (30%+ if known via Reddit/YT)  
**CAC**: $0.50–1.00 (organic, word-of-mouth)  
**Messaging**: *"Rank up while you AFK. Instant match notifications."*

### Segment 2: Casual Streamers
**Size**: ~50K (Twitch Overwatch channels, sub 100 viewers)  
**Profile**: Ages 18–40, stream 15–30 hours/week, monetizing  
**Pain**: Queue downtime = dead air on stream, chat engagement drops  
**Adoption Rate**: Very high (50%+, want better content)  
**CAC**: $2–5 per user (influencer outreach, sponsorships)  
**Messaging**: *"Fill queue time with chat interaction. Smart notifications keep pace."*

### Segment 3: Tank/Support Mains
**Size**: ~150K (longer queue times: 5–10 min avg)  
**Profile**: Ages 25–45, "main" specific role, patient, want reliability  
**Pain**: Checking phone during queue = distraction from IRL tasks  
**Adoption Rate**: Medium-High (40%+)  
**CAC**: $1.00 per user (Reddit/Discord ads)  
**Messaging**: *"No more queue peeking. Do your thing. We'll notify you."*

### Segment 4: Content Creators / Vloggers
**Size**: ~30K (YouTube OW2 content creators)  
**Profile**: Ages 18–50, creative professionals, high technical skill  
**Pain**: Need novel "first look" / "testing tool" content ideas  
**Adoption Rate**: Very high (70%+, makers want to showcase)  
**CAC**: $0 (free exposure, launch partnerships)  
**Messaging**: *"Test this cool new tool. Show your audience."*

### Segment 5: Casual Players (Control)
**Size**: ~500K (play <5 hours/week)  
**Profile**: Ages 15–50, occasional players, low engagement  
**Pain**: Not critical (can check manually)  
**Adoption Rate**: Low (10%)  
**Note**: Secondary target; ensure product doesn't scare them off with complexity

---

## 3. Messaging Framework

### Core Value Propositions

| Value Prop | Audience | Message |
|-----------|----------|---------|
| **Never miss a match** | All | Game state detection works in 50ms—instant know when match arrives |
| **Privacy-first** | Competitive, creators | All inference local. Zero cloud analytics. Your data stays yours. |
| **Zero setup** | Casual | Download, install, run. No config. Notifications work immediately. |
| **AI-powered reliability** | Tech-savvy | ML-based perception beats image hashing. <1 false positive/hour. |
| **Extensible** | Streamers | Discord webhook integration, custom notifications, API ready. |

### Taglines (Short)

1. **"Never Miss Queue Again"** — Direct, benefit-focused (primary CTAs)
2. **"Local. Free. Smart."** — Value (privacy, cost, AI) in 3 words
3. **"Queue Detection Redefined"** — Product positioning (new category)
4. **"Overwatch Gets a Brain"** — Creative, AI-centric, approachable

### Elevator Pitch (60 seconds)

> *"Overwatch Queue Notifier is a privacy-first desktop app that uses AI to detect Overwatch 2 queue and match states in real time. No cloud, no analytics, no sign-up—just download, install, and you'll get instant notifications (desktop + Discord) when a match is found. Whether you're a ranked grinder tired of alt-tabbing or a streamer looking to fill queue time, this tool keeps you in the game. It's free, open-source, and it works."*

---

## 4. Launch Timeline & Milestones

| Date | Milestone | Deliverables | Success Metric |
|------|-----------|--------------|----------------|
| **Feb 06** (Today) | Specs Complete | All 10 specs + backlog | 100+ pages documentation |
| **Feb 20** | Sprint 0 Done | Tray app skeleton, AI perception MVP | Desktop notifications firing |
| **Mar 06** | Beta Launch | v0.1.0 on GitHub Releases | 200+ GitHub stars |
| **Mar 20** | Sprint 2 Complete | Full detection (all states), Discord webhook | 1K+ Discord server members |
| **Apr 03** | Content Launch | Demo video, comparison blog, launch tweet | 10K video views, 500+ shares |
| **Apr 17** | Soft Launch | Marketing push (Reddit, Twitch) | 2K+ users |
| **May 01** | Growth Phase | Influencer partnerships, paid ads | 5K+ users |
| **Jun 01** | v1.0 Release | Stable, documented, auto-update working | 10K+ stars, 500+ Discord server |

---

## 5. Channel Strategy

### Reddit (Primary)
- **Subreddit**: r/Overwatch, r/Overwatch2, r/pcgaming
- **Frequency**: 1 launch post + 1 post-launch "feature release" post every month
- **Format**: Demo GIF + 2-sentence description + GitHub link
- **Budget**: $0 (organic posts)
- **Expected CAC**: $0.50 per user (high engagement subreddits)
- **Conversion Rate**: 5–10% (of upvote viewers)

### Twitter / X (Community)
- **Handle**: @OverwatchQNotif (fictional)
- **Frequency**: 2–3 posts/week (updates, tips, user testimonials)
- **Community**: Follow OW2 streamers, reply to queue complaints, retweet highlights
- **Engagement**: Giveaways (free premium if v2 exists) to followers
- **Budget**: $0 (organic, paid ads optional)
- **Expected CAC**: $1.00 per user (lower engagement platform for niche)

### Discord (Community Hub)
- **Server**: Dedicated community server (roles: testers, contributors, streamers)
- **Channels**: #announcements, #bug-reports, #feature-requests, #screenshots, #streaming-help
- **Engagement**: Monthly "state of the union" call, feature voting
- **Growth**: Cross-link in Reddit posts, Twitch ext panel, website
- **Conversion**: High (engaged, power users)

### Twitch / YouTube (Video Content)
- **Demo Video**: 90-second Remotion animation (from prompts/remotion-video-prompt.md)
  - Hosted on YouTube
  - Embedded in GitHub README + blog post
  - Shared as Twitter thread
- **Streamer Partnerships** (Post-launch):
  - Reach out to Overwatch content creators (5K–50K followers)
  - Free premium tier + GitHub credit
  - Request "first look" stream (30 min)
  - Budget: $0 (mutual benefit, exposure)
  - Expected reach: 50K–200K viewers per partnership × 5 partners = 250K+ impressions

### Blog / SEO
- **Owned Channel**: Dev blog (on GitHub Pages or Medium)
- **Content Strategy**:
  - **Post 1**: "How AI Queue Detection Works" (1500 words, technical deep-dive)
  - **Post 2**: "Why We Built a Local-First Queue Notifier" (1000 words, philosophy + privacy)
  - **Post 3**: "Overwatch 2 Queue Timings by Rank" (data analysis, infographic)
- **SEO Target Keywords**: 
  - "Overwatch queue notifier"
  - "OW2 queue detection"
  - "Overwatch match finder"
  - "AI game state notifier"
- **Expected Organic Traffic**: 500–2K monthly unique visitors

### Email (Post-Signup)
- **List**: Users who beta-sign-up (optional newsletter in tray settings)
- **Frequency**: Monthly "Latest Features" + bug fixes
- **Conversions**: Upgrade to premium, feature voting, testimonials
- **Example Email**:
  ```
  Subject: [Overwatch Queue Notifier] v0.3.0 Released: Faster Detection

  Hi [Name],

  We've optimized AI inference to <40ms (was 50ms). Also added:
  - Multi-profile calibration per resolution
  - Discord embed customization
  - 50% lower CPU usage

  Download v0.3.0: [GitHub Release Link]

  What's next? We're considering mobile push notifications. Vote here: [Poll]

  —The Queue Notifier Team
  ```

---

## 6. Success Metrics & Tracking

| Metric | Target (6 months) | Measurement | Importance |
|--------|-------------------|-------------|-----------|
| **GitHub Stars** | 10K | GitHub API | High (credibility signal) |
| **Installed Users** | 5K–10K | Auto-update telemetry (opt-in) | High |
| **Active Users DAU** | 1K–2K | App usage telemetry (opt-in) | Medium |
| **Discord Server Size** | 500+ members | Discord analytics | Medium |
| **Video Views** | 50K+ | YouTube analytics | Medium |
| **Blog Traffic** | 2K monthly unique | Google Analytics | Low |
| **Uninstall Rate** | <5% after week 1 | Installer telemetry | Critical |
| **False Positives** | <1 per 4h queue | User reports + logs | Critical |
| **User Retention (30d)** | >70% | Telemetry | High |

---

## 7. Competitive Positioning

### Competitive Landscape

| Competitor | Strengths | Weaknesses | Our Adv. |
|-----------|-----------|-----------|---------|
| **Manual Checking** | Guaranteed accurate | Context-switch fatigue, misses | Zero effort |
| **Browser Queue Timer** | Shows EST time | Manual refresh, inaccurate | AI-powered, automatic |
| **Discord Bot** | Server-integrated | Cloud-dependent, high latency | Local, 50ms |
| **Third-party Tools** | Some exist | Closed-source, privacy risk | Open-source, verifiable |
| **OW2 Native** | Official | Limited, no notifications | Advanced, flexible |

### Positioning Statement

> *Overwatch Queue Notifier is the only privacy-first, AI-powered queue detection tool that works locally with zero cloud dependency. Built for competitive players and streamers who want instant, reliable match notifications without sacrificing data privacy.*

---

## 8. Content Plan (6 Months)

### Month 1: Foundation (Feb–Mar)
- [ ] Demo video released (Remotion 90-sec)
- [ ] Blog post: "Our Philosophy: Local-First Design"
- [ ] Reddit launch post: "I built a queue notifier for OW2"
- [ ] Twitter launch: Announcement + demo link

### Month 2: Validation (Mar–Apr)
- [ ] Beta feedback blog post ("What We Learned")
- [ ] Streamer features (3× "first look" streams)
- [ ] Feature request vote on Discord
- [ ] Quarterly roadmap post

### Month 3: Growth (Apr–May)
- [ ] SEO blog: "Overwatch Queue Detection Explained" (technical)
- [ ] Infographic: "Queue Times by Role/Rank"
- [ ] Paid ad campaign (Reddit + Google Ads): $500 budget
- [ ] User testimonial video compilation (2 min)

### Month 4–6: Momentum (May–Jul)
- [ ] v1.0 launch announcement (all channels)
- [ ] Product Hunt launch
- [ ] Premium tier (if applicable): pricing blog
- [ ] Streaming guide: "How to Integrate with OBS"

---

## 9. Budget (6 Months)

| Item | Cost | ROI | Notes |
|------|------|-----|-------|
| Domain + hosting | $50 | N/A | GitHub Pages + GitHub releases (free) |
| Paid ads (Google/Reddit) | $500 | High | Targeted keywords, ~500 signups |
| Code signing certificate | $300 | Critical | Production Windows code signing |
| Influencer partnerships | $0 | Very High | Free exposure for creators |
| Content creation (contractor) | $1000 (opt) | Medium | Blog posts, comparison articles |
| **Total** | **$1850+** | — | Bootstrapped, minimal spend |

---

## 10. Next Steps

1. ✅ **Marketing spec approved** → Create content calendar
2. ⏭️ **Demo video generation** → Use Remotion prompt (Sprint 1)
3. ⏭️ **Blog setup** → Publish launch post on Medium (Sprint 2)
4. ⏭️ **Social media accounts** → Twitter, Reddit community (Pre-launch)
5. ⏭️ **Influencer outreach** → Reach 10 OW2 creators (Pre-launch)

**Owner**: Marketing Lead  
**Stakeholders**: Product Manager, Business Lead, Community Manager
