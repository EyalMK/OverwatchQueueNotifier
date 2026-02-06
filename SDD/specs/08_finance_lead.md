# Finance Lead Specification
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0  
**Status**: Draft → Financial Model

---

## 1. Infrastructure Cost Estimate (Monthly)

### Compute
| Service | Usage | Cost |
|---------|-------|------|
| **GitHub Actions CI/CD** | 1K min/month (test + build) | $0 (free tier includes 2K min) |
| **GitHub Releases** | 500 MB/month (MSI downloads) | $0 (GitHub included) |
| **Total Compute** | — | **$0/month** |

**Rationale**: Windows desktop app runs locally. No server required. GitHub free tier is sufficient for CI/CD and release hosting.

---

### Database
| Service | Usage | Cost |
|---------|-------|------|
| **SQLite (Local)** | Local file (~50 MB per user) | $0 (free) |
| **Optional: Backup sync (Dropbox/OneDrive)** | User-initiated (not provided) | $0 (user's account) |
| **Total Database** | — | **$0/month** |

**Rationale**: All data is local to user's machine. No cloud database needed for MVP.

---

### Storage & CDN
| Service | Usage | Cost |
|--------|-------|------|
| **GitHub Release Assets** | Downloads: 1GB/month (est. 5K users × 200MB MSI) | $0 (included in GitHub) |
| **Optional: Sentry error reporting** | 100K events/month (opt-in, users >5K) | $29/month (free tier: 5K events) |
| **Optional: Blog hosting** | GitHub Pages (free) | $0 |
| **Total Storage** | — | **$0–29/month** |

**Decision**: No paid storage needed for v1.0. Sentry optional and pay-as-you-grow.

---

### Third-Party Services
| Service | Usage | Cost |
|---------|-------|------|
| **Discord Webhooks** | User-configured, free | $0 |
| **Code Signing Cert** | Annual (1× purchase, not recurring) | $300/year ÷ 12 = **$25/month amortized** |
| **Domain (.com)** | Annual renewal | $12/year ÷ 12 = **$1/month** |
| **Total Services** | — | **$26/month** |

---

### Summary: Monthly Infrastructure Cost

```
Development:      $0
Database:         $0
Storage/CDN:      $0–29/month (optional Sentry)
Services:         $26/month (code signing + domain)
─────────────────────────────
TOTAL:            $26–55/month (Sentry optional)
```

**Projection**: $312–660/year (bootstrapped, negligible)

---

## 2. AI/LLM Cost Estimate (Per Sprint)

### Development Phase (Sprints 0–6)

| Task | Model | Tokens/Sprint | Cost/Sprint | Cost/6 sprints |
|------|-------|---------------|------------|----------------|
| **Spec generation** | Claude Opus | 200K | $15 | $90 |
| **Code generation** (backend, frontend, docs) | Claude Sonnet | 600K | $30 | $180 |
| **Test case generation** | Claude Haiku | 300K | $4.50 | $27 |
| **Documentation refine** | Claude Sonnet | 200K | $10 | $60 |
| **Architecture review** | Claude Opus | 100K | $7.50 | $45 |
| **Prompt generation** (Gemini diagrams, Remotion) | Claude Sonnet | 100K | $5 | $30 |
| **Code review / debuggin** | Claude Haiku | 200K | $3 | $18 |
| **TOTAL AI DEV** | — | **1.7M tokens** | **$75/sprint** | **$450 total** |

**Model Selection Rationale**:
- **Haiku (40%)**: Fast iteration, boilerplate code, test generation
- **Sonnet (45%)**: Features, architecture, docs, code review
- **Opus (15%)**: Complex decisions, spec synthesis, final review

**Projection**: ~$450 AI cost for entire development (6 sprints), assuming agent-assisted authoring.

---

### Post-Launch (Iterations)

| Activity | Frequency | Cost |
|----------|-----------|------|
| Feature development | 1 sprint/month | $75/sprint = $900/yr |
| Bug triage & fixes | Ad-hoc | ~$100/month = $1.2K/yr |
| User support & feedback analysis | Ad-hoc | ~$50/month = $600/yr |
| **Total Post-Launch AI** | — | **~$2.7K/year** |

---

## 3. Pricing Strategy (v1.0: Freemium)

### Tier Structure (v1.0)

| Feature | Free | Premium (v2+) |
|---------|------|--------------|
| Queue detection | ✓ | ✓ |
| Desktop notifications | ✓ | ✓ |
| Discord webhook | ✓ | ✓ |
| Calibration profiles | ✓ (1 per res) | ✓ (unlimited) |
| Detection history | Last 100 | Unlimited (30 days) |
| Priority support | — | ✓ (email) |
| **Price** | **$0** | **$2–5/month** (planned v2) |

**v1.0 Decision**: 100% free (bootstrap phase, build community)

**v2.0 Monetization Option** (Optional, post-1.0):
- **Free tier**: Core detection + desktop/Discord notifs
- **Premium**: $2.99/month (multi-resolution unlimited, history export, priority support)
- **Expected conversion**: 2–5% of user base → 100–500 paying users at $2.99 = $3K–15K/yr at full scale

---

## 4. Revenue Projections (3, 6, 12 months)

### Growth Assumptions

| Metric | 3mo | 6mo | 12mo |
|--------|-----|-----|------|
| **Total Installed** | 2,000 | 10,000 | 50,000 |
| **Monthly Active** | 1,200 (60% DAU) | 7,000 (70%) | 35,000 (70%) |
| **Premium Conversion** | 0% | 0% | 2.5% (post-launch) |
| **Paid Users** | 0 | 0 | 1,250 |

### Revenue Projection (if Premium Tier Launches in Month 12)

```
Month 3 (v0.2 Beta):    $0 (free-only)
Month 6 (v1.0 Launch):  $0 (free-only)
Month 12 (v2.0 Premium): $0 → $3,750/month (1,250 users × $3/month)

Year 1 Total: $0 (freemium)
Year 2 Revenue (from month 12 onward): $45K–60K/yr (ramp to 2,500 paying users)
```

**Conservative Estimate**: 2–5% conversion rate of monthly active users = $0–15K/year at full scale (not relying on this for MVP viability).

---

## 5. Unit Economics

### Cost Per User (Marginal)

| Cost Item | Per-User Cost |
|-----------|---------------|
| GitHub Action mins | <$0.01 (1 min per user for one-time build) |
| Release CDN bandwidth | $0.02–0.05 (~200 MB MSI) |
| Infrastructure | $0.01–0.02 (DB, logging, support) |
| **Marginal Cost / User** | **~$0.05** |

### Lifetime Value (LTV) — Free Model

```
LTV = ARPU × Customer Lifetime (months)

Assumptions:
- ARPU = $0 (free model) + $3/month if 2% convert to premium in Mo6
- Average lifetime = 12 months
- Organic retention = 70% at 6 months, 50% at 12 months

LTV = ($0 + $0.06) × 12 = $0.72
```

**Interpretation**: Free-to-premium model generates minimal direct revenue; value is in:
1. Community building (organic growth) → future Premium conversions
2. Open-source credibility → partnerships / sponsorships
3. Data insights (aggregated, privacy-preserving) → potential B2B revenue stream (future)

### Customer Acquisition Cost (CAC)

| Channel | CAC | Notes |
|---------|-----|-------|
| **Organic (Reddit, Twitter)** | $0 | Viral/word-of-mouth |
| **Influencer partnerships** | $0–1 | Barter (free premium) |
| **Paid ads (Google/Reddit)** | $1–3 | If launched (optional) |
| **Blended CAC** | **$0.50–1.50** | Weighted average |

### LTV:CAC Ratio

```
LTV:CAC = $0.72 : $1.00 = 0.72:1 (break-even in Year 2 if Premium converts 5%)

If Premium launch successful (5% conversion):
LTV:CAC = $1.50–3.00 : $1.00 = 3:1 (healthy ratio)
```

---

## 6. Budget Allocation by Phase

### Phase 1: Development (Feb–May, 4 sprints)

```
Development (engineering hours)  ~100 hours @ $100/hr (stipend/equity)   $0 (volunteer labor)
AI Assistant costs (Claude)       Token usage: 1.7M tokens              $450
Infrastructure (code cert)        $25/month × 4 months                  $100
Marketing (content creation)      ~$500 (optional paid ads)            $500
─────────────────────────────────────────────────────────────────────
PHASE 1 TOTAL                                                         $1,050
```

### Phase 2: Launch & Growth (Jun–Aug, 2 sprints)

```
Development continued             ~50 hours @ $100/hr                  $0
AI Assistant costs                ~$150 (less heavy dev)              $150
Infrastructure                    $26/month × 3 months                 $78
Marketing (social, ads)           Influencer partnerships + paid ads   $500
Community management              Discord, Reddit moderation          $0
─────────────────────────────────────────────────────────────────────
PHASE 2 TOTAL                                                        $728
```

### Remaining Year 1 (Sep–Dec, ongoing updates)

```
Maintenance & bug fixes            ~30 hours/month @ $100/hr            $0
AI usage (support, docs)          ~$100/month                          $400
Infrastructure                    $26/month × 4 months                 $104
Marketing                         Content creation, partner dev        $800
─────────────────────────────────────────────────────────────────────
PHASE 3 TOTAL (Sep–Dec)                                             $1,304
```

### Year 1 Grand Total

```
Phase 1 (Feb–May):   $1,050
Phase 2 (Jun–Aug):   $728
Phase 3 (Sep–Dec):   $1,304
────────────────────────────
YEAR 1 TOTAL:        $3,082
```

**Financing**: Growth mindset (pre-revenue). Relies on volunteer dev time or equity compensation.

---

## 7. Break-Even Analysis

### Scenario 1: Free-Only Model (Classic Open-Source)

```
Annual Costs:            ~$3K–5K (infra, tools)
Annual Revenue (Free):   $0
Monthly Burn Rate:       $250–400/month
Runway (bootstrapped):   Self-sustaining after month 6 (community growth covers costs)

Break-Even Condition: 
  - Sponsorships from Nvidia/Microsoft (AI hardware companies)
  - Partnership revenue (Twitch, Discord integrations)
  - Donations / GitHub Sponsors ($1–5k/month from community)
```

### Scenario 2: Hybrid Model (Free + Premium, v2.0)

```
Launch Premium in Month 12:   $3/user/month,  2.5% conversion = $1,250 paying users

Monthly Revenue (Mo 12):      $1,250 × $3 = $3,750
Monthly Revenue (Mo 24):      $2,500 × $3 = $7,500 (ramp over 12 mo)

Annual Cost (year 2):         ~$4K (infrastructure stabilized)
Annual Revenue (year 2):      ~$45K (conservative ramp to 1,250 avg paying)

Break-Even Month:            Month 12–14 (Premium launch month)
Profit (Year 2):             +$41K (attractive for future VC if needed)
```

**Recommendation**: Ship v1.0 as free, validate 10K+ users, then launch Premium in v2.0 (Month 12+) if community is strong.

---

## 8. Cost Optimizations

| Item | Current | Optimized | Savings |
|------|---------|-----------|---------|
| Code signing cert | $300/year (DigiCert EV) | $60/year (self-signed for testing, free for GitHub) | $240/year |
| Sentry (error tracking) | Free tier (5K events) | Build minimal logging (local JSON) | $0–29/month |
| GitHub Pro (optional) | $4/month | Stick with free tier | $48/year |
| Domain | $12/year | Use GitHub Pages + Reddit for docs | $12/year |
| **Total Optimization Potential** | **~$960/year** | — | — |

**Outcome**: Full v1.0 launch can be achieved for **<$1K total investment**.

---

## 9. Funding Strategy (If Needed for Acceleration)

### Warm Bootstrap (Most Likely)
- **Founder time**: 500–1000 hours unpaid (equity stake)
- **Community contributions**: Bug reports, translations, marketing
- **GitHub Sponsors**: Solicit $1–5K/month from open-source community
- **Sponsorships**: Nvidia, Intel, Microsoft (AI tools alignment)

### Seed Round (v2.0 Timing, if Pursuing)
- **Pre-seed**: $150K–300K (achieve 10K+ users, Premium beta)
- **Seed**: $500K–1M (expand team, B2B partnerships, mobile)
- **Use of Funds**:
  - Full-time developer × 2 ($120K/yr)
  - Marketer ($60K/yr)
  - Infrastructure scaling ($10K/yr)

---

## 10. Financial Assumptions & Sensitivity

### Key Assumptions

1. **Organic growth**: 50% month-over-month DAU (conservative for gaming tool)
2. **Retention**: 60% month 1 → 70% month 3 → 50% month 12 (steady state)
3. **Premium conversion**: 2–5% (once launched in v2.0)
4. **No acquisition spend required**: Community-driven growth (Reddit, Discord, Twitter)
5. **Infrastructure scales linearly** with user count (<$0.05/user)

### Sensitivity Analysis

| Scenario | Users (12mo) | Revenue (yr2) | Viability |
|----------|-------------|--------------|-----------|
| **Conservative** (1% mo growth) | 10K | $5K | Hobby project |
| **Baseline** (5% mo growth) | 50K | $45K | Sustainable OSS |
| **Optimistic** (10% mo growth) | 100K | $90K | VC-fundable |

---

## 11. Next Steps

1. ✅ **Finance spec approved** → Track actual spend against budget
2. ⏭️ **Set up GitHub Sponsors** → Enable community support (Pre-launch)
3. ⏭️ **Monthly financial reports** → Track user growth + server costs (Post-launch)
4. ⏭️ **Premium v2.0 design** → Plan monetization tier structure (Post-Sprint 4)
5. ⏭️ **Sponsorship outreach** → Contact hardware partners (if needed for runway)

**Owner**: Finance Lead  
**Stakeholders**: Product Manager, Business Lead, Investor/Board

---

## 12. Summary Table: Year 1 Financial Snapshot

| Category | Amount |
|----------|--------|
| **Revenue** | $0 (free-only) |
| **Costs (Operational)** | ~$3,000 |
| **Costs (AI / Dev Tools)** | ~$450 |
| **Costs (Marketing)** | ~$1,300 |
| **Total Year 1 Spend** | **~$4,750** |
| **Funding Source** | Bootstrap, community sponsorships |
| **Runway Assumption** | Volunteer dev time |
| **Break-Even Timeline** | Month 6 (infrastructure only, ignoring labor) |
| **Path to Profitability** | Launch Premium in v2.0 (mon 12), target $45K/yr by year 2 |
