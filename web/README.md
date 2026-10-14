# Reservoir Cloud — protótipo de plataforma web

Dashboard React + TypeScript + Vite, desenvolvido para acompanhar o projeto de telemetria ECM50-A07.

## Executar

Requisitos: Node.js 20+ e npm.

```bash
cd web
npm install
npm run dev
```

Abra a URL exibida pelo Vite. Para gerar a versão de produção: `npm run build`.

## Estado atual

- Interface responsiva com navegação, KPIs, reservatórios, indicadores 4–20 mA, gráfico, eventos e dispositivos.
- Busca de reservatórios e exportação CSV de dados demonstrativos.
- Dados **100% simulados** em `src/data.ts`. O gráfico e o período selecionado não consultam uma API.
- Sem login, persistência, broker MQTT, backend ou comunicação com o ECM50-A07.
- Valores e estados dos dispositivos são ilustrativos; não usar para operação de campo.

## Integração planejada

1. API autenticada: `GET /api/v1/reservoirs`, `GET /api/v1/reservoirs/:id/history`, `GET /api/v1/events`, `GET /api/v1/devices`.
2. Backend recebe MQTT/TLS do equipamento e persiste telemetria no banco de dados.
3. Atualizações ao vivo via WebSocket/SSE e identificação de dados desatualizados.
4. Autenticação, isolamento por organização, auditoria, alertas e relatórios reais.

Nunca exponha credenciais MQTT do dispositivo no navegador. O navegador deve conversar apenas com uma API autenticada do backend.
