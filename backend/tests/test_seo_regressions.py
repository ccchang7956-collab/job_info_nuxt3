import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ASYNC_DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from datetime import datetime
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch, AsyncMock
import xml.etree.ElementTree as ET
from fastapi import Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.Routers.MetadataRouter import get_categories, category_cache
from app.Services.SeoService import SeoService, sitemap_cache
from scripts.notify_google_indexing import active_notifications

NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class SeoDatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        category_cache.clear()
        sitemap_cache.clear()
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self.db = AsyncSession(self.engine)
        await self.db.execute(text("CREATE TABLE job_sysnam (sysnam TEXT)"))
        await self.db.execute(text("CREATE TABLE job_all_data (id INTEGER, sysnam TEXT, date_from TEXT, announce_date TEXT, date_to TEXT)"))
        await self.db.execute(text("INSERT INTO job_sysnam VALUES ('綜合行政'), ('冷門職系'), ('無'), (NULL)"))
        await self.db.execute(text("""INSERT INTO job_all_data VALUES
            (1, '歷史職系', '1151001', '1151001', '1151006'),
            (2, '綜合行政', '1151007', '1151007', '1151007'),
            (3, '綜合行政', '1151007', '1151007', '1151008'),
            (4, '綜合行政', '1151007', '1151007', '1151009')"""))

    async def asyncTearDown(self):
        await self.db.close()
        await self.engine.dispose()
        category_cache.clear()
        sitemap_cache.clear()

    async def test_categories_include_official_and_historical_not_only_popular(self):
        result = await get_categories(Response(), self.db)
        self.assertEqual(result["sysnams"], ['冷門職系', '歷史職系', '綜合行政'])
        self.assertEqual(len(result["places"]), 22)

    async def test_sitemap_includes_jobs_closing_today_and_stable_disjoint_pages(self):
        with patch('app.Services.JobService.get_roc_dates', return_value=('1151007', '1151006')), patch('app.Services.SeoService.SITEMAP_PAGE_SIZE', 2):
            first = ET.fromstring(await SeoService.get_sitemap_jobs_page(self.db, 1))
            second = ET.fromstring(await SeoService.get_sitemap_jobs_page(self.db, 2))
            ids = lambda xml: [node.text.rsplit('/', 1)[1] for node in xml.findall('s:url/s:loc', NS)]
            self.assertEqual(ids(first), ['4', '3'])
            self.assertEqual(ids(second), ['2'])
            self.assertIsNone(await SeoService.get_sitemap_jobs_page(self.db, 3))
            self.assertEqual(first.find('s:url/s:lastmod', NS).text, '2026-10-07')

    async def test_sitemap_database_outage_is_not_misreported_as_missing(self):
        db = AsyncMock()
        db.execute.side_effect = RuntimeError('fixture outage')
        with self.assertRaises(RuntimeError):
            await SeoService.get_sitemap_jobs_page(db, 1)

    async def test_static_sitemaps_do_not_invent_modification_dates(self):
        static = ET.fromstring(await SeoService.get_sitemap_static())
        index = ET.fromstring(await SeoService.get_sitemap_index())
        self.assertEqual(len(static), 45)
        self.assertEqual(static.findall('.//s:lastmod', NS), [])
        self.assertEqual(index.findall('.//s:lastmod', NS), [])


class IndexingPreviewTests(unittest.TestCase):
    def test_only_existing_active_jobs_are_prepared_without_network(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fixture.db'
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE job_all_data (id INTEGER, date_to TEXT)')
                db.executemany('INSERT INTO job_all_data VALUES (?, ?)', [(1, '1151006'), (2, '1151007'), (3, '1151008')])
            results = active_notifications(path, [1, 2, 2, 3, 999], 'https://example.test', datetime(2026, 10, 7))
            self.assertEqual(results, [
                {'url': 'https://example.test/job/2', 'type': 'URL_UPDATED'},
                {'url': 'https://example.test/job/3', 'type': 'URL_UPDATED'},
            ])

    def test_invalid_origin_and_ids_are_rejected_before_database_access(self):
        for origin, ids in [('http://example.test', [1]), ('https://example.test/path', [1]), ('https://example.test', [-1]), ('https://example.test', list(range(1, 202)))]:
            with self.subTest(origin=origin, ids=ids):
                with self.assertRaises(ValueError):
                    active_notifications('/nonexistent.db', ids, origin)


if __name__ == '__main__':
    unittest.main()
