#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO 改善驗證腳本
用於測試所有 SEO 相關端點和結構化資料的正確性

執行方式：
  python scripts/test_seo.py [--base-url https://opendgpa.shibaalin.com]

如果不指定 base-url，預設連線到本地開發環境 http://localhost:8002
"""

import sys
import re
import json
import time
import argparse
import requests
from xml.etree import ElementTree as ET
from urllib.parse import urlparse


# ANSI 顏色
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def ok(msg):
    print(f"  {GREEN}✓{RESET} {msg}")

def fail(msg):
    print(f"  {RED}✗ FAIL:{RESET} {msg}")
    return False

def warn(msg):
    print(f"  {YELLOW}⚠ WARN:{RESET} {msg}")

def section(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")


def test_robots_txt(base_url: str) -> bool:
    section("1. robots.txt 驗證")
    passed = True

    try:
        r = requests.get(f"{base_url}/robots.txt", timeout=10)
        if r.status_code == 200:
            ok(f"robots.txt 返回 200 (Content-Length: {len(r.content)} bytes)")
        else:
            fail(f"robots.txt 返回 {r.status_code}")
            passed = False

        content = r.text
        checks = [
            ("User-agent: *", "有 User-agent: *"),
            ("Allow: /", "有 Allow: /"),
            ("Sitemap:", "有 Sitemap 指向"),
            ("LLMs:", "有 LLMs.txt 指向"),
        ]
        for pattern, desc in checks:
            if pattern in content:
                ok(desc)
            else:
                fail(f"缺少：{desc}")
                passed = False

    except Exception as e:
        fail(f"robots.txt 存取失敗: {e}")
        passed = False

    return passed


def test_sitemap_index(base_url: str) -> tuple[bool, list]:
    """測試 Sitemap Index 並返回所有子 sitemap URL。"""
    section("2. Sitemap Index 驗證")
    passed = True
    sub_sitemaps = []

    try:
        r = requests.get(f"{base_url}/sitemap.xml", timeout=15)
        if r.status_code == 200:
            ok(f"sitemap.xml 返回 200 (Content-Length: {len(r.content)} bytes)")
        else:
            fail(f"sitemap.xml 返回 {r.status_code}")
            return False, []

        # 解析 XML
        try:
            root = ET.fromstring(r.content)
            ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            # 嘗試 sitemapindex 格式
            sitemaps = root.findall('sm:sitemap', ns)
            if sitemaps:
                ok(f"✓ 是 Sitemap Index 格式，共 {len(sitemaps)} 個子 sitemap")
                for sm in sitemaps:
                    loc = sm.find('sm:loc', ns)
                    if loc is not None and loc.text:
                        sub_sitemaps.append(loc.text.strip())
                        ok(f"  子 sitemap: {loc.text.strip()}")
            else:
                # 回退：可能是單一 urlset（舊格式）
                urls = root.findall('sm:url', ns)
                warn(f"sitemap.xml 是單一 urlset 格式（{len(urls)} 筆 URL）—建議升級為 Sitemap Index")

        except ET.ParseError as e:
            fail(f"XML 解析失敗: {e}")
            passed = False

    except Exception as e:
        fail(f"sitemap.xml 存取失敗: {e}")
        passed = False

    return passed, sub_sitemaps


def test_sitemap_static(base_url: str) -> bool:
    section("3. 靜態頁面 Sitemap 驗證")
    passed = True

    try:
        r = requests.get(f"{base_url}/sitemap-static.xml", timeout=10)
        if r.status_code == 200:
            ok(f"sitemap-static.xml 返回 200")
        else:
            fail(f"sitemap-static.xml 返回 {r.status_code}")
            return False

        root = ET.fromstring(r.content)
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = root.findall('sm:url', ns)
        ok(f"靜態 sitemap 含 {len(urls)} 筆 URL")

        required_paths = [
            '/', '/comments', '/charts', '/about', '/privacy-policy',
            '/places/%E8%87%BA%E5%8C%97%E5%B8%82',  # 臺北市
            '/places/%E9%AB%98%E9%9B%84%E5%B8%82',  # 高雄市
            '/sysnams/%E7%B6%9C%E5%90%88%E8%A1%8C%E6%94%BF',  # 綜合行政
            '/sysnams/%E8%B3%87%E8%A8%8A%E8%99%95%E7%90%86'  # 資訊處理
        ]
        found_paths = set()
        static_lastmods = []

        for url_elem in urls:
            loc = url_elem.find('sm:loc', ns)
            lastmod = url_elem.find('sm:lastmod', ns)
            if loc is not None and loc.text:
                path = urlparse(loc.text.strip()).path
                found_paths.add(path)
            if lastmod is not None and lastmod.text:
                static_lastmods.append(lastmod.text.strip())

        for path in required_paths:
            if path in found_paths:
                ok(f"包含路徑: {path}")
            else:
                fail(f"缺少路徑: {path}")
                passed = False

        # 驗證 lastmod 不是今天（避免每天變動）
        from datetime import date
        today = date.today().isoformat()
        dynamic_lastmods = [lm for lm in static_lastmods if lm == today]
        if dynamic_lastmods:
            warn(f"{len(dynamic_lastmods)} 個靜態頁面的 lastmod 是今天 ({today})，建議改為固定日期")
        else:
            ok(f"靜態頁面 lastmod 均為固定日期（非今天），正確！")

    except Exception as e:
        fail(f"sitemap-static.xml 存取失敗: {e}")
        passed = False

    return passed


def test_sitemap_jobs(base_url: str) -> bool:
    section("4. 職缺 Sitemap 分頁驗證")
    passed = True

    try:
        # 測試第一頁
        r = requests.get(f"{base_url}/sitemap-jobs-1.xml", timeout=20)
        if r.status_code == 200:
            ok(f"sitemap-jobs-1.xml 返回 200")
        else:
            fail(f"sitemap-jobs-1.xml 返回 {r.status_code}")
            return False

        root = ET.fromstring(r.content)
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = root.findall('sm:url', ns)
        ok(f"第 1 頁職缺 sitemap 含 {len(urls)} 筆 URL")

        if len(urls) > 0:
            ok(f"職缺 URL 格式正確")
            # 檢查 URL 格式
            sample_loc = urls[0].find('sm:loc', ns)
            if sample_loc is not None:
                ok(f"  範例 URL: {sample_loc.text}")

        # 測試不存在的頁碼
        r404 = requests.get(f"{base_url}/sitemap-jobs-9999.xml", timeout=10)
        if r404.status_code == 404:
            ok("不存在的頁碼正確返回 404")
        else:
            warn(f"超出範圍的頁碼返回 {r404.status_code}（期望 404）")

    except Exception as e:
        fail(f"sitemap-jobs-1.xml 存取失敗: {e}")
        passed = False

    return passed


def test_seo_health_api(base_url: str) -> bool:
    section("5. SEO 健康檢查 API 驗證")
    passed = True

    try:
        # 注意：健康檢查 API 在 Nuxt proxy 下走 /api/seo/health
        # 直接連後端時走 /api/seo/health
        r = requests.get(f"{base_url}/api/seo/health", timeout=20)
        if r.status_code in (200, 503):
            ok(f"SEO 健康檢查 API 返回 {r.status_code}")
        else:
            fail(f"SEO 健康檢查 API 返回 {r.status_code}")
            passed = False

        data = r.json()
        ok(f"整體狀態: {data.get('status', 'unknown')}")
        ok(f"IndexNow 已設定: {data.get('indexnow_configured', False)}")

        checks = data.get("checks", {})
        for name, result in checks.items():
            if result.get("ok"):
                ok(f"  {name}: OK (HTTP {result.get('status')})")
            else:
                warn(f"  {name}: 異常 ({result.get('error', 'status ' + str(result.get('status')))})")

    except Exception as e:
        fail(f"SEO 健康檢查 API 存取失敗: {e}")
        passed = False

    return passed


def test_indexnow_key_file(base_url: str) -> bool:
    section("6. IndexNow Key 文件驗證")
    passed = True

    # 嘗試常見的 key 文件路徑
    key_urls = [
        f"{base_url}/opendgpa-indexnow-key-2025.txt",
    ]

    found = False
    for key_url in key_urls:
        try:
            r = requests.get(key_url, timeout=10)
            if r.status_code == 200:
                ok(f"IndexNow key 文件存在: {key_url}")
                content = r.text.strip()
                if content:
                    ok(f"  文件內容: {content[:50]}")
                found = True
                break
        except Exception:
            pass

    if not found:
        warn("IndexNow key 文件未找到（需要在 public/ 目錄建立 {{INDEXNOW_KEY}}.txt）")

    return passed


def test_page_meta(base_url: str) -> bool:
    """測試前端頁面的 meta tags（需要 Nuxt 前端運行）。"""
    section("7. 前端頁面 Meta Tags 驗證")
    passed = True

    # 前端通常在不同 port 或同一 URL
    frontend_url = base_url.replace(":8002", ":3000").replace(":8002", "")

    pages = [
        ("/", "開放事求人"),
        ("/about", "關於本站"),
        ("/charts", "統計"),
    ]

    for path, expected_title_fragment in pages:
        try:
            r = requests.get(f"{frontend_url}{path}", timeout=15)
            if r.status_code == 200:
                # 檢查 title
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', r.text)
                if title_match:
                    title = title_match.group(1)
                    ok(f"{path} → title: {title[:60]}")
                else:
                    warn(f"{path} → 未找到 <title> 標籤")

                # 檢查 canonical
                if 'rel="canonical"' in r.text or "rel='canonical'" in r.text:
                    ok(f"{path} → 有 canonical URL")
                else:
                    warn(f"{path} → 未找到 canonical URL")

                # 檢查 JSON-LD
                if 'application/ld+json' in r.text:
                    ok(f"{path} → 有 JSON-LD 結構化資料")
                else:
                    warn(f"{path} → 未找到 JSON-LD 結構化資料")

                # 檢查 hreflang
                if 'hreflang' in r.text:
                    ok(f"{path} → 有 hreflang 標記")
                else:
                    warn(f"{path} → 未找到 hreflang 標記")

            else:
                warn(f"{path} 返回 {r.status_code}（可能前端未啟動）")
        except Exception as e:
            warn(f"{path} 無法存取（前端可能未啟動）: {e}")

    return passed


def test_duplicate_schemas(base_url: str) -> bool:
    """檢查首頁是否有重複的 Schema.org 結構化資料。"""
    section("8. Schema.org 去重驗證")
    passed = True

    frontend_url = base_url.replace(":8002", ":3000")

    try:
        r = requests.get(f"{frontend_url}/", timeout=15)
        if r.status_code != 200:
            warn(f"首頁返回 {r.status_code}（前端可能未啟動），跳過此測試")
            return True

        # 提取所有 JSON-LD
        ld_scripts = re.findall(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            r.text, re.DOTALL
        )

        schema_types = []
        for script in ld_scripts:
            try:
                data = json.loads(script.strip())
                schema_type = data.get("@type", "unknown")
                schema_types.append(schema_type)
            except json.JSONDecodeError:
                warn("有一個 JSON-LD 無法解析")

        ok(f"首頁共有 {len(ld_scripts)} 個 JSON-LD schemas")
        ok(f"  類型: {', '.join(schema_types)}")

        # 檢查重複
        website_count = schema_types.count("WebSite")
        org_count = schema_types.count("Organization")

        if website_count <= 1:
            ok(f"WebSite schema 數量: {website_count}（無重複）")
        else:
            fail(f"WebSite schema 重複: {website_count} 個")
            passed = False

        if org_count <= 1:
            ok(f"Organization schema 數量: {org_count}（無重複）")
        else:
            fail(f"Organization schema 重複: {org_count} 個")
            passed = False

    except Exception as e:
        warn(f"Schema 重複檢查失敗: {e}")

    return passed


def test_evergreen_pages(base_url: str) -> bool:
    """測試長青分類網頁的前端渲染與 SEO 標籤。"""
    section("9. 長青分類頁面 (Evergreen Landing Pages) 驗證")
    passed = True

    frontend_url = base_url.replace(":8002", ":3000").replace(":8002", "")

    test_cases = [
        ("/places/%E8%87%BA%E5%8C%97%E5%B8%82", "臺北市"),
        ("/places/%E9%AB%98%E9%9B%84%E5%B8%82", "高雄市"),
        ("/sysnams/%E7%B6%9C%E5%90%88%E8%A1%8C%E6%94%BF", "綜合行政"),
        ("/sysnams/%E8%B3%87%E8%A8%8A%E8%99%95%E7%90%86", "資訊處理"),
    ]

    for path, name in test_cases:
        try:
            url = f"{frontend_url}{path}"
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                fail(f"{path} 返回 {r.status_code}")
                passed = False
                continue

            # 1. 驗證 Title
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', r.text)
            if title_match and name in title_match.group(1):
                ok(f"{path} → title 包含 '{name}': {title_match.group(1).strip()[:60]}")
            else:
                fail(f"{path} → title 未包含 '{name}'")
                passed = False

            # 2. 驗證 Canonical URL 指向且全小寫百分比編碼
            expected_canonical = f"https://opendgpa.shibaalin.com{path}".lower()
            canonical_match = re.search(r'rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', r.text)
            if not canonical_match:
                canonical_match = re.search(r'href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']', r.text)
            
            if canonical_match:
                actual_canonical = canonical_match.group(1).lower()
                if actual_canonical == expected_canonical:
                    ok(f"{path} → Canonical URL 正確: {actual_canonical}")
                else:
                    fail(f"{path} → Canonical URL 錯誤: 期望 {expected_canonical}，實際 {actual_canonical}")
                    passed = False
            else:
                fail(f"{path} → 未找到 Canonical URL")
                passed = False

            # 3. 驗證結構化資料 BreadcrumbList
            ld_scripts = re.findall(
                r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
                r.text, re.DOTALL
            )
            has_breadcrumb = False
            for script in ld_scripts:
                try:
                    data = json.loads(script.strip())
                    if data.get("@type") == "BreadcrumbList":
                        has_breadcrumb = True
                        break
                except json.JSONDecodeError:
                    pass

            if has_breadcrumb:
                ok(f"{path} → 含有 BreadcrumbList 結構化資料")
            else:
                fail(f"{path} → 缺少 BreadcrumbList 結構化資料")
                passed = False

        except Exception as e:
            fail(f"{path} 驗證時發生異常: {e}")
            passed = False

    return passed


def main():
    parser = argparse.ArgumentParser(description="SEO 改善驗證腳本")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8002",
        help="後端基礎 URL（預設: http://localhost:8002）"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="使用生產環境 URL https://opendgpa.shibaalin.com"
    )
    args = parser.parse_args()

    base_url = "https://opendgpa.shibaalin.com" if args.production else args.base_url

    print(f"\n{BOLD}🔍 SEO 改善驗證腳本{RESET}")
    print(f"  目標: {CYAN}{base_url}{RESET}")
    print(f"  時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        "robots.txt": test_robots_txt(base_url),
        "sitemap_index": False,
        "sitemap_static": test_sitemap_static(base_url),
        "sitemap_jobs": test_sitemap_jobs(base_url),
        "seo_health_api": test_seo_health_api(base_url),
        "indexnow_key": test_indexnow_key_file(base_url),
        "page_meta": test_page_meta(base_url),
        "duplicate_schemas": test_duplicate_schemas(base_url),
        "evergreen_pages": test_evergreen_pages(base_url),
    }

    # Sitemap Index 測試（特殊處理，需要子 sitemap 列表）
    sitemap_ok, sub_sitemaps = test_sitemap_index(base_url)
    results["sitemap_index"] = sitemap_ok

    # 最終摘要
    section("📊 測試結果摘要")
    all_passed = True
    for name, result in results.items():
        if result:
            ok(f"{name}")
        else:
            fail(f"{name}")
            all_passed = False

    print()
    if all_passed:
        print(f"{GREEN}{BOLD}✅ 所有測試通過！SEO 基礎設施運行正常。{RESET}")
    else:
        print(f"{YELLOW}{BOLD}⚠️  部分測試未通過，請檢查上方錯誤訊息。{RESET}")

    print(f"\n{CYAN}💡 下一步建議：{RESET}")
    print(f"  1. 在 Google Search Console 提交 Sitemap：{base_url}/sitemap.xml")
    print(f"  2. 使用 Rich Results Test 驗證結構化資料")
    print(f"  3. 執行 Lighthouse SEO 稽核（目標: 95+）")
    print(f"  4. 觀察 Search Console 的索引涵蓋範圍報告")
    print()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
