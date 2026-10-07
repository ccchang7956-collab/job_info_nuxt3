# Nuxt Minimal Starter

## SEO regression checks

Run `npm run test:seo` to start temporary Nuxt and fixture backend servers and check sitemap routing, SSR pagination, and canonical URLs. These tests do not use the production site or database. Optional browser checks are skipped unless `SEO_TEST_PLAYWRIGHT_PATH` points to an existing Playwright module; no new browser dependency is required for the HTTP checks.

For a production-server check, build with the fixture backend URL, then run:

```bash
BACKEND_URL=http://127.0.0.1:18002 npm run build
SEO_TEST_PRODUCTION=1 npm run test:seo
```

This build uses a local test backend. Rebuild with the real `BACKEND_URL` before deploying; Docker Compose supplies its existing `http://backend:8002` build argument automatically.

Deployment notes are in [the indexing audit](../docs/GOOGLE_SEARCH_INDEXING_AUDIT_2026-09-30.md). Job sitemap requests are handled by Nuxt, so this fix does not require an Nginx configuration change.

The latest [SEO / GEO changes and deployment notes](../docs/SEO_GEO_CHANGES_2026-10-07.md) cover SSR statistics, category validation, error status/cache handling, and the optional Google Indexing API preview tool. Deploy frontend and backend together for the new category metadata endpoint.

Look at the [Nuxt documentation](https://nuxt.com/docs/getting-started/introduction) to learn more.

## Setup

Make sure to install dependencies:

```bash
# npm
npm install

# pnpm
pnpm install

# yarn
yarn install

# bun
bun install
```

## Development Server

Start the development server on `http://localhost:3000`:

```bash
# npm
npm run dev

# pnpm
pnpm dev

# yarn
yarn dev

# bun
bun run dev
```

## Production

Build the application for production:

```bash
# npm
npm run build

# pnpm
pnpm build

# yarn
yarn build

# bun
bun run build
```

Locally preview production build:

```bash
# npm
npm run preview

# pnpm
pnpm preview

# yarn
yarn preview

# bun
bun run preview
```

Check out the [deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.
