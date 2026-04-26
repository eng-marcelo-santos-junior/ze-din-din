# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Zé Din Din** is a personal finance web app for Brazilian families. Core features: income/expense tracking, spending categorization, budget limits, financial indicators, and AI-driven insights from historical data.

Design constraint: if a user can't understand a screen in 5 seconds, it's too complex.

## Tech Stack

| Layer | Choice |
|---|---|
| Frontend | Next.js (App Router), TypeScript, TailwindCSS |
| Backend | Next.js API Routes (primary) or FastAPI |
| ORM | Prisma |
| Database | PostgreSQL |
| Auth | JWT or OAuth (Google) |
| Deploy | Vercel |

## Commands

The project has not been scaffolded yet. Once initialized with Next.js, standard commands will be:

```bash
npm run dev       # start dev server
npm run build     # production build
npm run lint      # ESLint
npm run test      # run all tests
npm run test -- --testPathPattern=<file>  # run a single test file
npx prisma migrate dev   # apply DB migrations
npx prisma studio        # open DB GUI
```

## Naming Conventions

- Variables and functions: `camelCase`
- Files and directories: `kebab-case`
- React components: `PascalCase`
- Database models and columns: follow Prisma conventions (`PascalCase` models, `camelCase` fields)

## Architecture Notes

- Use Next.js **App Router** (`app/` directory), not Pages Router.
- API routes live under `app/api/`. Keep business logic out of route handlers — move it to a `lib/` or `services/` layer so it stays testable.
- Prisma schema is the single source of truth for the data model. All financial domain types derive from it.
- Financial calculations (budget remaining, monthly balance, category totals) must be deterministic and unit-tested. Keep them in pure functions separate from UI and API code.
