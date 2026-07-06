# 最終代碼審查修復實施計劃 (Final Code Review Fixes Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修復 Robots Meta 邏輯以避免 de-index，並在 Tailwind 設定中加入淡入（fade-in）自訂動畫以配合 `[id].vue` 中的 class。

**Architecture:** 
1. 在 `frontend-nuxt/pages/job/[id].vue` 中，修正 `useSeoMeta` 的 `robots` 欄位邏輯與其上的註解，讓 `fetchError` 存在或 `job` 存在時都能回傳 `'index,follow'`。
2. 在 `frontend-nuxt/tailwind.config.js` 的 `theme.extend` 內加入 `animation` 與 `keyframes` 的設定。
3. 執行產線編譯 `npm run build` 來驗證程式碼與 Tailwind 設定的正確性。

**Tech Stack:** Nuxt 4, Vue 3, TailwindCSS, TypeScript

## Global Constraints

- 專案根目錄：`/Users/ccchang/Project/job_info_nuxt3`
- 前端目錄：`frontend-nuxt`

---

### Task 1: 修復 Robots Meta 邏輯與註解

**Files:**
- Modify: `frontend-nuxt/pages/job/[id].vue:150-152`

**Interfaces:**
- Consumes: `fetchError` 與 `job`
- Produces: 更新後的 `robots` 回傳值，確保在 API 錯誤或職缺存在時均為 `index,follow`

- [ ] **Step 1: 修改 robots 設定與註解**

在 `frontend-nuxt/pages/job/[id].vue` 中，尋找：
```typescript
  // 只有確認職缺已過期才設 noindex；API 失敗（job.value=null）時保持 index
  // 避免後端短暫錯誤導致 Googlebot 看到 noindex 而永久拒絕收錄
  robots: () => job.value ? 'index,follow' : 'noindex,follow',
```

將其修改為：
```typescript
  // 只有當確定查無此職缺且無 API 錯誤（例如真正的 404）時才設 noindex
  // 避免後端短暫網絡抖動或 API 錯誤導致 Googlebot 看到 noindex 而永久將網頁移出索引 (De-index)
  robots: () => (fetchError.value || job.value) ? 'index,follow' : 'noindex,follow',
```

- [ ] **Step 2: 執行 Git Diff 來驗證修改**

執行指令：
```bash
git diff frontend-nuxt/pages/job/\[id\].vue
```
預期輸出：
顯示變更的註解與 robots 邏輯。

- [ ] **Step 3: 提交此變更**

執行指令：
```bash
git add frontend-nuxt/pages/job/\[id\].vue
git commit -m "fix(seo): update robots meta logic to protect index during transient api errors"
```

---

### Task 2: 新增 Tailwind 自訂淡入動畫

**Files:**
- Modify: `frontend-nuxt/tailwind.config.js:12-31`

**Interfaces:**
- Produces: 新增 `animate-fade-in` 類別的定義（`animation.fade-in` 和 `keyframes.fadeIn`）

- [ ] **Step 1: 修改 tailwind.config.js**

在 `frontend-nuxt/tailwind.config.js` 的 `theme.extend` 內，尋找：
```javascript
    theme: {
        extend: {
            fontFamily: {
                sans: ['"Noto Sans TC"', 'system-ui', '-apple-system', 'sans-serif'],
            },
            colors: {
                primary: {
                    50: '#f4f8fb',
                    100: '#e3eff6',
                    200: '#cce0ef',
                    300: '#99c2e2',
                    400: '#66a3d3',
                    500: '#408cc4',
                    600: '#337AB7', // Base color requested by user
                    700: '#296292',
                    800: '#204d74',
                    900: '#1a3e5c',
                    950: '#11283d',
                },
            }
        },
    },
```

將其修改為：
```javascript
    theme: {
        extend: {
            fontFamily: {
                sans: ['"Noto Sans TC"', 'system-ui', '-apple-system', 'sans-serif'],
            },
            colors: {
                primary: {
                    50: '#f4f8fb',
                    100: '#e3eff6',
                    200: '#cce0ef',
                    300: '#99c2e2',
                    400: '#66a3d3',
                    500: '#408cc4',
                    600: '#337AB7', // Base color requested by user
                    700: '#296292',
                    800: '#204d74',
                    900: '#1a3e5c',
                    950: '#11283d',
                },
            },
            animation: {
                'fade-in': 'fadeIn 0.3s ease-out',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0', transform: 'translateY(-4px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                }
            }
        },
    },
```

- [ ] **Step 2: 執行 Git Diff 來驗證修改**

執行指令：
```bash
git diff frontend-nuxt/tailwind.config.js
```
預期輸出：
顯示 `animation` 與 `keyframes` 的新增。

- [ ] **Step 3: 提交此變更**

執行指令：
```bash
git add frontend-nuxt/tailwind.config.js
git commit -m "feat(theme): add fade-in animation to tailwind config"
```

---

### Task 3: 執行 Production Build 驗證

- [ ] **Step 1: 執行產線編譯**

在 `/Users/ccchang/Project/job_info_nuxt3/frontend-nuxt` 目錄下執行指令：
```bash
npm run build
```
預期輸出：
編譯成功，無 TypeScript 錯誤或 CSS 建置錯誤。
