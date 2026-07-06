# SEO Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Address Google Search Console indexing issues by rendering FAQ content on the homepage and making expired job detail pages indexable with clear expiration alerts.

**Architecture:** Render the existing FAQ data from JSON-LD schema into a semantic details/summary Accordion block at the bottom of the homepage. Modify job detail robots meta logic to allow indexing of expired jobs while displaying an Amber banner alerting users to the expiration and providing navigation back to the active listings.

**Tech Stack:** Nuxt 3, Vue 3, Tailwind CSS, Heroicons.

## Global Constraints

- Keep UI clean and responsive with Tailwind CSS.
- Ensure all custom content and translations are in Traditional Chinese (繁體中文).
- Do not introduce unused dependencies.
- Build must compile cleanly with `npm run build` inside `frontend-nuxt/` folder.

---

### Task 1: Render FAQ Accordion on Homepage

**Files:**
- Modify: `frontend-nuxt/pages/index.vue:801-834` (near the bottom, inside `<template>`)

**Interfaces:**
- Consumes: FAQ JSON-LD schema content.
- Produces: Visual Accordion matching the schema content.

- [ ] **Step 1: Locate insertion point in index.vue**

We will insert the FAQ section at the end of the `<main>` element, just below the `Results Section`.
Specifically, find `</section>` (around line 830 in `index.vue` or near the end of results list wrapper) and insert the FAQ block before the closing `</main>`.

- [ ] **Step 2: Add FAQ Accordion UI code to template**

Modify [frontend-nuxt/pages/index.vue](file:///Users/ccchang/Project/job_info_nuxt3/frontend-nuxt/pages/index.vue) to include the FAQ block right before `</main>`:

```html
    <!-- FAQ Section -->
    <section aria-label="常見問題" class="mt-12 border-t border-slate-200 pt-10">
      <h2 class="text-xl font-bold text-slate-800 mb-6 text-center">常見問題 FAQ</h2>
      <div class="max-w-3xl mx-auto space-y-4">
        <details class="group bg-white rounded-xl border border-slate-200 p-4 [&_summary::-webkit-details-marker]:hidden">
          <summary class="flex items-center justify-between cursor-pointer focus:outline-none select-none">
            <span class="font-semibold text-slate-800">如何搜尋公務員職缺？</span>
            <ChevronDownIcon class="w-5 h-5 text-slate-400 group-open:rotate-180 transition-transform" />
          </summary>
          <p class="mt-3 text-slate-600 text-sm leading-relaxed whitespace-pre-wrap">在開放事求人首頁使用關鍵字搜尋，可依機關、職系、職稱、地點等條件篩選，快速找到適合的公務員職缺。</p>
        </details>

        <details class="group bg-white rounded-xl border border-slate-200 p-4 [&_summary::-webkit-details-marker]:hidden">
          <summary class="flex items-center justify-between cursor-pointer focus:outline-none select-none">
            <span class="font-semibold text-slate-800">開放事求人的資料來源是什麼？</span>
            <ChevronDownIcon class="w-5 h-5 text-slate-400 group-open:rotate-180 transition-transform" />
          </summary>
          <p class="mt-3 text-slate-600 text-sm leading-relaxed whitespace-pre-wrap">資料來源為政府資料開放平臺之「行政院人事行政總處事求人機關徵才資料」，每日自動同步更新，確保資料即時性。</p>
        </details>

        <details class="group bg-white rounded-xl border border-slate-200 p-4 [&_summary::-webkit-details-marker]:hidden">
          <summary class="flex items-center justify-between cursor-pointer focus:outline-none select-none">
            <span class="font-semibold text-slate-800">什麼是重複開缺？</span>
            <ChevronDownIcon class="w-5 h-5 text-slate-400 group-open:rotate-180 transition-transform" />
          </summary>
          <p class="mt-3 text-slate-600 text-sm leading-relaxed whitespace-pre-wrap">當相同機關、相同職稱的職缺重複出現時，系統會標示為「重複開缺」，幫助您判斷該職位可能較不穩定或流動率較高。</p>
        </details>

        <details class="group bg-white rounded-xl border border-slate-200 p-4 [&_summary::-webkit-details-marker]:hidden">
          <summary class="flex items-center justify-between cursor-pointer focus:outline-none select-none">
            <span class="font-semibold text-slate-800">可以在手機上使用嗎？</span>
            <ChevronDownIcon class="w-5 h-5 text-slate-400 group-open:rotate-180 transition-transform" />
          </summary>
          <p class="mt-3 text-slate-600 text-sm leading-relaxed whitespace-pre-wrap">是的，開放事求人支援 PWA（漸進式網頁應用程式），可以安裝到手機桌面像 App 一樣使用，並支援離線瀏覽已查看過的職缺。</p>
        </details>
      </div>
    </section>
```

- [ ] **Step 3: Run dev server and manually verify visual placement**

Run: `npm run dev` in `frontend-nuxt/` directory.
Expected: Frontend starts, visit `http://localhost:3000` (or local dev port), scroll to the bottom to verify the FAQ block renders properly and is expandable.

- [ ] **Step 4: Run production build check**

Run: `npm run build` in `frontend-nuxt/` directory.
Expected: Build finishes with no errors.

- [ ] **Step 5: Commit changes**

```bash
git add frontend-nuxt/pages/index.vue
git commit -m "feat: render FAQ accordion on homepage to align with schema"
```

---

### Task 2: Enable Indexing and Add Expiration Warning on Job Detail Page

**Files:**
- Modify: `frontend-nuxt/pages/job/[id].vue:4`, `frontend-nuxt/pages/job/[id].vue:152`, `frontend-nuxt/pages/job/[id].vue:290-305`

**Interfaces:**
- Consumes: `isJobExpired` computed boolean, `ExclamationTriangleIcon` from `@heroicons/vue/24/outline`.
- Produces: Updated Robots Meta allowing search indexing, warning banner when job is expired.

- [ ] **Step 1: Import ExclamationTriangleIcon**

In [frontend-nuxt/pages/job/\[id\].vue](file:///Users/ccchang/Project/job_info_nuxt3/frontend-nuxt/pages/job/%5Bid%5D.vue#L4), replace the icon import statement:
```typescript
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'
```
with:
```typescript
import { ArrowLeftIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
```

- [ ] **Step 2: Update Robots Meta configuration**

In [frontend-nuxt/pages/job/\[id\].vue](file:///Users/ccchang/Project/job_info_nuxt3/frontend-nuxt/pages/job/%5Bid%5D.vue#L152), replace the robots meta line:
```typescript
  robots: () => (job.value && isJobExpired.value) ? 'noindex,follow' : 'index,follow',
```
with:
```typescript
  robots: () => job.value ? 'index,follow' : 'noindex,follow',
```

- [ ] **Step 3: Add warning banner for expired jobs**

In [frontend-nuxt/pages/job/\[id\].vue](file:///Users/ccchang/Project/job_info_nuxt3/frontend-nuxt/pages/job/%5Bid%5D.vue#L290-L293) (inside `<template>`, right after the `<nav aria-label="breadcrumb">` block but before `LoadingSpinner`), insert the following warning block:

```html
    <!-- Expired Warning Banner -->
    <div v-if="job && isJobExpired" class="mb-6 bg-amber-50 border border-amber-200 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm animate-fade-in">
      <div class="flex items-center gap-3 text-amber-800">
        <ExclamationTriangleIcon class="w-6 h-6 flex-shrink-0" />
        <div>
          <p class="font-bold">此職缺已截止報名</p>
          <p class="text-sm text-amber-700 mt-0.5">本職缺已於 {{ job.date_to }} 截止收件，僅保留歷史資料供參考。</p>
        </div>
      </div>
      <NuxtLink 
        to="/" 
        class="inline-flex items-center justify-center px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm font-medium transition-colors shadow-sm whitespace-nowrap"
      >
        查看最新職缺列表
      </NuxtLink>
    </div>
```

- [ ] **Step 4: Verify details page manually with dev server**

Run: `npm run dev` in `frontend-nuxt/` directory.
Expected: Navigate to an active job page: no warning is shown. Navigate to an expired job page (or modify local DB state): the amber warning banner is shown, robots meta tag contains `content="index,follow"`.

- [ ] **Step 5: Run production build check**

Run: `npm run build` in `frontend-nuxt/` directory.
Expected: Nuxt build compiles successfully.

- [ ] **Step 6: Commit changes**

```bash
git add frontend-nuxt/pages/job/\[id\].vue
git commit -m "feat: enable indexing for expired jobs and show warning banner"
```
