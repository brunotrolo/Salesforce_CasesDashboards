# Shared (frontends/shared)

Pacote `@reports/shared` — código reutilizável entre os micro frontends.

## Conteúdo

```
src/
  ├── types/report.ts        # Tipos de relatório (Report, ReportStatus, ReportType, ...)
  ├── utils/formatters.ts    # Formatação (number, currency, date)
  ├── utils/logger.ts        # Logger estruturado
  ├── api/apiClient.ts       # Cliente axios com auth JWT + interceptor 401
  └── test/setup.ts          # Setup do Vitest (jsdom, jest-dom)
```

## Uso

Cada app importa via alias `@shared` (configurado no `vite.config.ts`,
`vitest.config.ts` e `tsconfig.json`):

```ts
import { Report, ReportStatus } from '@shared/types/report'
import { formatNumber } from '@shared/utils/formatters'
import { logger } from '@shared/utils/logger'
import { apiClient } from '@shared/api/apiClient'
```

## Dependências

- `date-fns` (production — usado por `formatters.ts`)
- `vitest`, `jsdom`, `@testing-library/*` (dev — usados por `test/setup.ts`)

Instalar deps: `npm install` em `frontends/shared/`.