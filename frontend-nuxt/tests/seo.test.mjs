import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { createServer } from 'node:http'
import { once } from 'node:events'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { setTimeout as delay } from 'node:timers/promises'
import { before, after, test } from 'node:test'

const root = fileURLToPath(new URL('../', import.meta.url))
const site = 'https://opendgpa.shibaalin.com'
const place = `/places/${encodeURIComponent('臺北市')}`
const sysnam = `/sysnams/${encodeURIComponent('綜合行政')}`
const production = process.env.SEO_TEST_PRODUCTION === '1'
const backendRequests = []
let frontend
let baseURL
let logs = ''
let browser
const failures = new Set()

const xml = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://opendgpa.shibaalin.com/job/1001</loc></url></urlset>'
const backend = createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost')
  backendRequests.push(url)
  if (url.pathname.startsWith('/sitemap')) {
    if (url.pathname === '/sitemap-jobs-9999.xml') {
      res.writeHead(404, { 'Content-Type': 'text/plain' })
      return res.end('Page not found')
    }
    res.writeHead(200, { 'Content-Type': 'application/xml' })
    return res.end(url.pathname === '/sitemap.xml'
      ? '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://opendgpa.shibaalin.com/sitemap-jobs-1.xml</loc></sitemap></sitemapindex>'
      : xml)
  }
  res.setHeader('Content-Type', 'application/json')
  if (failures.has(url.pathname) || url.searchParams.get('org') === '故障') {
    res.writeHead(503)
    return res.end(JSON.stringify({ message: 'Temporary backend failure' }))
  }
  if (url.pathname === '/metadata/categories') return res.end(JSON.stringify({
    places: ['臺北市', '澎湖縣'], sysnams: ['綜合行政', '人事行政', '冷門職系']
  }))
  if (url.pathname.startsWith('/job_openings_chart')) return res.end(JSON.stringify({
    month: url.searchParams.get('month') || '11510', month_options: [{ value: '11510', label: '115年10月' }, { value: '11509', label: '115年9月' }],
    org_names: ['統計測試機關', '第二機關'], sys_names: ['統計測試職系', '第二職系'], job_counts: [12, 8]
  }))
  if (url.pathname.startsWith('/Active_job_openings/')) {
    if (url.pathname.endsWith('/999999')) {
      res.writeHead(404)
      return res.end(JSON.stringify({ message: 'Not found' }))
    }
    return res.end(JSON.stringify({ job: {
      id: 9001, org_name: '歷史測試機關', title: '約聘人員', sysnam: '綜合行政',
      date_from: '115/01/01', date_to: '115/01/08', announce_date: '115/01/01',
      work_quality: '須具相關經驗', work_item: '辦理行政業務', contact_method: '依公告報名',
      work_address: '臺北市', place: '臺北市'
    }, comments: [], duplicates: [] }))
  }
  if (url.pathname === '/metadata/last-update') return res.end(JSON.stringify({ date: '115/09/30' }))
  if (url.pathname !== '/') return res.end('{}')
  const page = Number(url.searchParams.get('page') || 1)
  const perPage = Number(url.searchParams.get('per_page') || 15)
  const offset = (page - 1) * perPage
  const totalCount = url.searchParams.get('places') === '澎湖縣'
    || ['人事行政', '冷門職系'].includes(url.searchParams.get('sysnam')) ? 0 : 60
  const jobs = Array.from({ length: Math.max(0, Math.min(perPage, totalCount - offset)) }, (_, i) => ({
    id: 1001 + offset + i, org: '測試機關', title: `職缺 ${offset + i + 1}`,
    sysnam: '綜合行政', rank: '5', rank_display: '5等', place: '臺北市',
    date_from: '115/09/30', date_to: '139/12/31', link: 'https://example.test/job',
    history_count: 0, comment_count: 0
  }))
  res.end(JSON.stringify({
    jobs, current_page: page, per_page: perPage, total_pages: Math.ceil(totalCount / perPage),
    total_count: totalCount, page_range: [1, 2, 3, 4], page_range_all: [1, 2, 3, 4],
    today_date: '1150930', yesterday_date: '1150929'
  }))
})

before(async () => {
  backend.listen(production ? Number(process.env.SEO_TEST_BACKEND_PORT || 18002) : 0, '127.0.0.1')
  await once(backend, 'listening')
  const backendURL = `http://127.0.0.1:${backend.address().port}`
  const portProbe = createServer()
  portProbe.listen(0, '127.0.0.1')
  await once(portProbe, 'listening')
  const port = portProbe.address().port
  await new Promise(resolve => portProbe.close(resolve))
  baseURL = `http://127.0.0.1:${port}`
  frontend = spawn(process.execPath, production
    ? ['.output/server/index.mjs']
    : ['node_modules/nuxt/bin/nuxt.mjs', 'dev', '--host', '127.0.0.1', '--port', String(port)], {
    cwd: root, detached: true,
    env: { ...process.env, BACKEND_URL: backendURL, NUXT_BACKEND_URL: backendURL,
      NUXT_PUBLIC_SITE_URL: site, HOST: '127.0.0.1', PORT: String(port) },
    stdio: ['ignore', 'pipe', 'pipe']
  })
  for (const stream of [frontend.stdout, frontend.stderr]) {
    stream.on('data', chunk => { logs = (logs + chunk).slice(-15000) })
  }
  let ready = false
  for (let attempt = 0; attempt < 120; attempt++) {
    if (frontend.exitCode !== null) throw new Error(`Nuxt exited:\n${logs}`)
    try {
      const response = await fetch(`${baseURL}/api/metadata/last-update`, { signal: AbortSignal.timeout(2000) })
      ready = response.ok
    } catch {}
    if (ready) break
    await delay(250)
  }
  if (!ready) throw new Error(`Nuxt did not start:\n${logs}`)
  if (process.env.SEO_TEST_PLAYWRIGHT_PATH) {
    const { chromium } = await import(pathToFileURL(process.env.SEO_TEST_PLAYWRIGHT_PATH).href)
    browser = await chromium.launch({ headless: true, channel: process.env.SEO_TEST_BROWSER_CHANNEL || undefined,
      executablePath: process.env.SEO_TEST_BROWSER_EXECUTABLE || undefined })
  }
})

after(async () => {
  await browser?.close()
  if (frontend?.pid && frontend.exitCode === null && frontend.signalCode === null) {
    const exited = once(frontend, 'exit')
    process.kill(-frontend.pid, 'SIGTERM')
    await Promise.race([exited, delay(5000)])
    if (frontend.exitCode === null && frontend.signalCode === null) process.kill(-frontend.pid, 'SIGKILL')
  }
  backend.closeAllConnections()
  await new Promise(resolve => backend.close(resolve))
})

async function html(path) {
  const response = await fetch(`${baseURL}${path}`)
  assert.equal(response.status, 200, `${path} should render successfully; ${logs.slice(-2000)}`)
  return response.text()
}

function canonical(body) {
  const tag = body.match(/<link\b[^>]*rel="canonical"[^>]*>/)?.[0]
  assert.ok(tag, 'SSR HTML must contain a canonical link')
  return tag.match(/href="([^"]+)"/)?.[1].replaceAll('&amp;', '&')
}

for (const path of ['/sitemap.xml', '/sitemap-static.xml', '/sitemap-jobs-1.xml', '/sitemap-jobs-2.xml']) {
  test(`${path} serves XML`, async () => {
    const response = await fetch(`${baseURL}${path}`)
    assert.equal(response.status, 200)
    assert.match(response.headers.get('content-type'), /application\/xml/)
    assert.match(await response.text(), path === '/sitemap.xml' ? /<sitemapindex/ : /<urlset/)
  })
}

test('missing job sitemap preserves backend 404', async () => {
  const response = await fetch(`${baseURL}/sitemap-jobs-9999.xml`)
  assert.equal(response.status, 404)
  assert.equal(await response.text(), 'Page not found')
})

for (const path of ['/sitemap-jobs-0.xml', '/sitemap-jobs-x.xml', '/sitemap-jobs-1.xml.bak']) {
  test(`${path} is not forwarded as a job sitemap`, async () => {
    const requestCount = backendRequests.length
    const response = await fetch(`${baseURL}${path}`)
    assert.equal(response.status, 404)
    assert.equal(backendRequests.slice(requestCount).some(url => url.pathname === path), false)
  })
}

for (const path of [place, sysnam]) {
  test(`${path} rejects out-of-range pages instead of indexing an empty listing`, async () => {
    const response = await fetch(`${baseURL}${path}?page=999`)
    assert.equal(response.status, 404)
    assert.match(await response.text(), /name="robots" content="noindex,follow"/)
  })
  test(`${path} page 2 renders different jobs and its own canonical`, async () => {
    const first = await html(path)
    const second = await html(`${path}?page=2`)
    assert.ok(first.includes('href="/job/1001"'))
    assert.ok(second.includes('href="/job/1021"'), 'page 2 must render its own jobs')
    assert.ok(!second.includes('href="/job/1001"'), 'page 2 must not repeat page 1 jobs')
    assert.ok(second.includes('第 2 頁'))
    assert.equal(canonical(first), `${site}${path}`)
    assert.equal(canonical(second), `${site}${path}?page=2`)
    const key = path === place ? 'places' : 'sysnam'
    const value = path === place ? '臺北市' : '綜合行政'
    assert.ok(backendRequests.some(url => url.pathname === '/' && url.searchParams.get(key) === value
      && url.searchParams.get('page') === '2' && url.searchParams.get('per_page') === '20'),
    'pagination must preserve the category filter in the backend request')
  })
  test(`${path} preserves non-default page size on SSR and canonical`, async () => {
    const body = await html(`${path}?page=2&per_page=15`)
    assert.ok(body.includes('href="/job/1016"'))
    assert.ok(!body.includes('href="/job/1001"'))
    assert.equal(canonical(body), `${site}${path}?page=2&per_page=15`)
  })
}

test('home pure pagination has its own canonical', async () => {
  const body = await html('/?page=2')
  assert.match(body, /href="\/job\/1016"/)
  assert.equal(canonical(body), `${site}/?page=2`)
})

test('home filter canonical remains the homepage', async () => {
  assert.equal(canonical(await html('/?page=2&org=測試')), `${site}/`)
})

test('sitemap handling leaves ordinary pages working', async () => {
  assert.match(await html('/about'), /關於/)
})

test('charts contain real statistics and methodology in SSR HTML', async () => {
  const body = await html('/charts')
  assert.match(body, /<table/)
  assert.match(body, /統計測試機關/)
  assert.match(body, /115年10月/)
  assert.match(body, /合計 20 筆/)
  assert.match(body, /並非全國職缺佔比/)
})

test('category SSR contains the full result count and source', async () => {
  const body = await html(place)
  assert.match(body, /<strong>60<\/strong>/)
  assert.match(body, /公告筆數不等於招募人數/)
})

for (const path of ['/places/不存在縣市', '/sysnams/不存在職系']) {
  test(`${path} is a genuine 404`, async () => {
    const response = await fetch(`${baseURL}${path}`)
    assert.equal(response.status, 404)
    assert.match(await response.text(), /noindex,follow/)
  })
}

test('a non-popular valid category with no open jobs stays indexable', async () => {
  assert.match(await html('/sysnams/冷門職系'), /name="robots" content="index,follow"/)
})

for (const [path, endpoint] of [[place, '/'], [sysnam, '/'], ['/charts', '/job_openings_chart'], [place, '/metadata/categories'], [`${place}?page=999`, '/metadata/categories'], ['/job/9002', '/Active_job_openings/9002']]) {
  test(`${path} returns 503 on ${endpoint} failure without noindex`, async () => {
    failures.add(endpoint)
    try {
      const response = await fetch(`${baseURL}${path}`)
      assert.equal(response.status, 503)
      assert.match(response.headers.get('cache-control'), /no-store/)
      assert.doesNotMatch(await response.text(), /name="robots" content="noindex/)
    } finally { failures.delete(endpoint) }
  })
}

test('charts hydrate with SSR data and retain tab and month controls', {
  skip: !process.env.SEO_TEST_PLAYWRIGHT_PATH
}, async () => {
  const context = await browser.newContext({ serviceWorkers: 'block' })
  await context.route('**/*', route => new URL(route.request().url()).hostname === '127.0.0.1' ? route.continue() : route.abort())
  const page = await context.newPage()
  const errors = []
  page.on('pageerror', error => errors.push(error.message))
  try {
    await page.goto(`${baseURL}/charts`)
    await page.waitForFunction(() => document.querySelector('table')?.textContent.includes('統計測試機關'))
    await page.getByRole('button', { name: '職系開缺數', exact: true }).click()
    await page.waitForFunction(() => document.querySelector('table')?.textContent.includes('統計測試職系'))
    await page.getByRole('combobox').last().selectOption('11509')
    await page.waitForFunction(() => document.body.textContent.includes('115年9月職系開缺數'))
    assert.equal(errors.length, 0, errors.join('\n'))
  } finally { await context.close() }
})

test('homepage API failure returns 503 instead of a successful empty page', async () => {
  const response = await fetch(`${baseURL}/?org=故障`)
  assert.equal(response.status, 503)
  assert.match(response.headers.get('cache-control'), /no-store/)
})

test('a job URL immediately recovers after API failure within the SWR window', async () => {
  assert.match(await html('/job/9002'), /歷史測試機關/)
})

test('expired jobs remain indexable with accurate schema', async () => {
  const body = await html('/job/9001')
  assert.match(body, /此職缺已截止報名/)
  assert.match(body, /name="robots" content="index,follow"/)
  const schemas = [...body.matchAll(/<script\b[^>]*type="application\/ld\+json"[^>]*>(.*?)<\/script>/gs)].map(match => JSON.parse(match[1]))
  const posting = schemas.find(schema => schema['@type'] === 'JobPosting')
  assert.equal(posting.validThrough, '2026-01-08T23:59:59+08:00')
  assert.equal(posting.hiringOrganization.sameAs, undefined)
  assert.equal(posting.jobBenefits, undefined)
  assert.equal(posting.employmentType, undefined)
  assert.doesNotMatch(body, /hreflang=/)
})

test('missing jobs return 404 and noindex', async () => {
  const response = await fetch(`${baseURL}/job/999999`)
  assert.equal(response.status, 404)
  assert.match(await response.text(), /name="robots" content="noindex,follow"/)
})

test('logs allow crawling so Google can read their noindex directive', async () => {
  assert.doesNotMatch(await html('/robots.txt'), /Disallow:\s*\/logs/)
})

for (const path of [`/places/${encodeURIComponent('澎湖縣')}`, `/sysnams/${encodeURIComponent('人事行政')}`]) {
  test(`${path} keeps an empty valid category's first page available`, async () => {
    const body = await html(path)
    assert.ok(body.includes('目前無最新職缺'))
    assert.match(body, /name="robots" content="index,follow"/)
  })
}

for (const path of [place, sysnam]) {
  test(`${path} client pagination, history, page size and jump stay in sync`, {
    skip: !process.env.SEO_TEST_PLAYWRIGHT_PATH
  }, async () => {
    const context = await browser.newContext({ serviceWorkers: 'block' })
    await context.route('**/*', route => {
      return new URL(route.request().url()).hostname === '127.0.0.1' ? route.continue() : route.abort()
    })
    const page = await context.newPage()
    try {
      await page.goto(`${baseURL}${path}`)
      await page.getByRole('link', { name: '下一頁', exact: true }).click()
      await page.waitForFunction(() => document.body.textContent.includes('第 2 頁')
        && document.querySelector('a[href="/job/1021"]'))
      assert.equal(new URL(page.url()).searchParams.get('page'), '2')
      assert.equal(await page.locator('link[rel="canonical"]').getAttribute('href'), `${site}${path}?page=2`)

      await page.goBack()
      await page.waitForFunction(() => document.body.textContent.includes('第 1 頁')
        && document.querySelector('a[href="/job/1001"]'))
      await page.goForward()
      await page.waitForFunction(() => document.body.textContent.includes('第 2 頁')
        && document.querySelector('a[href="/job/1021"]'))

      await page.getByRole('combobox').selectOption('15')
      await page.waitForFunction(() => document.body.textContent.includes('第 1 頁')
        && document.querySelector('a[href="/job/1001"]')
        && new URL(location.href).searchParams.get('per_page') === '15')
      assert.equal(new URL(page.url()).searchParams.get('page'), null)
      assert.equal(await page.locator('link[rel="canonical"]').getAttribute('href'), `${site}${path}?per_page=15`)

      await page.getByRole('spinbutton').fill('3')
      await page.getByRole('button', { name: 'GO', exact: true }).click()
      await page.waitForFunction(() => document.body.textContent.includes('第 3 頁')
        && document.querySelector('a[href="/job/1031"]'))
      assert.equal(new URL(page.url()).searchParams.get('page'), '3')
      assert.equal(await page.locator('link[rel="canonical"]').getAttribute('href'), `${site}${path}?page=3&per_page=15`)

      const response = await page.goto(`${baseURL}${path}?page=999`)
      assert.equal(response.status(), 404)
      assert.equal(await page.locator('meta[name="robots"]').getAttribute('content'), 'noindex,follow')
      await page.getByRole('link', { name: '返回第一頁', exact: true }).click()
      await page.waitForFunction(() => document.body.textContent.includes('第 1 頁')
        && document.querySelector('a[href="/job/1001"]'))
      assert.equal(await page.locator('meta[name="robots"]').getAttribute('content'), 'index,follow')
    } finally {
      await context.close()
    }
  })
}
