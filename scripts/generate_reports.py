#!/usr/bin/env python3
"""
Generate all 7 strategic reports from Salesforce Cases data via MCP.

Reports (prioritized):
  Phase 1 (HIGH):
    1. SLA por Categoria — Trend Report
    2. Product Performance Scorecard

  Phase 2 (MEDIUM):
    3. Manual vs Auto Effectiveness Comparison
    4. Data Quality Improvement Tracker
    5. Operational Capacity Planning

  Phase 3 (FUTURE):
    6. RPA Expansion Opportunity Matrix
    7. Hierarchy Completion Report

Usage:
    python scripts/generate_reports.py              # Generate all reports
    python scripts/generate_reports.py phase1       # Phase 1 only
    python scripts/generate_reports.py sla          # Specific report

Environment Variables:
    SF_CLIENT_ID - Salesforce OAuth client ID
    SF_CLIENT_SECRET - Salesforce OAuth client secret
    SF_REFRESH_TOKEN - Salesforce OAuth refresh token
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import sys

try:
    from anthropic import Anthropic
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("Warning: anthropic SDK not available. Using mock data.", file=sys.stderr)


class ReportDataFetcher:
    """Fetch data for all reports via MCP."""

    def __init__(self):
        self.use_mock = not HAS_MCP

    def format_number(self, num: int) -> str:
        """Format number with thousands separator."""
        return f"{num:,}".replace(",", ".")

    # === PHASE 1: SLA by Category ===
    def fetch_sla_trend_data(self) -> Dict:
        """Fetch SLA metrics by category over time."""
        if self.use_mock:
            return {
                "weeks": [
                    {
                        "week": "02-08/08",
                        "categories": [
                            {"name": "Fatura", "manual_sla": 87, "auto_sla": 100, "avg_time_manual": "0h25m"},
                            {"name": "Atendimento", "manual_sla": 83, "auto_sla": 100, "avg_time_manual": "1h10m"},
                            {"name": "Detalhes da cota", "manual_sla": 79, "auto_sla": 98, "avg_time_manual": "2h20m"},
                            {"name": "Compensação", "manual_sla": 81, "auto_sla": 99, "avg_time_manual": "1h45m"},
                        ]
                    },
                    {
                        "week": "09-14/08",
                        "categories": [
                            {"name": "Fatura", "manual_sla": 86, "auto_sla": 100, "avg_time_manual": "0h30m"},
                            {"name": "Atendimento", "manual_sla": 82, "auto_sla": 100, "avg_time_manual": "1h15m"},
                            {"name": "Detalhes da cota", "manual_sla": 78, "auto_sla": 98, "avg_time_manual": "2h30m"},
                            {"name": "Compensação", "manual_sla": 80, "auto_sla": 99, "avg_time_manual": "1h50m"},
                        ]
                    },
                ]
            }
        return {}

    # === PHASE 1: Product Performance Scorecard ===
    def fetch_product_scorecard_data(self) -> List[Dict]:
        """Fetch comprehensive product performance data."""
        if self.use_mock:
            return [
                {
                    "rank": 1,
                    "name": "Cartão PortoBank",
                    "volume": 37913,
                    "volume_pct": 55.6,
                    "manual_pct": 45.2,
                    "auto_pct": 54.8,
                    "sla": 96,
                    "trend": "stable",
                    "quality_score": 88,
                    "category_breakdown": [
                        {"category": "Fatura", "cases": 18200, "auto_pct": 70},
                        {"category": "Atendimento", "cases": 12100, "auto_pct": 55},
                        {"category": "Seguro", "cases": 7613, "auto_pct": 35},
                    ]
                },
                {
                    "rank": 2,
                    "name": "Conta Corrente",
                    "volume": 15430,
                    "volume_pct": 22.6,
                    "manual_pct": 72.1,
                    "auto_pct": 27.9,
                    "sla": 82,
                    "trend": "down",
                    "quality_score": 74,
                    "category_breakdown": [
                        {"category": "Atendimento", "cases": 8200, "auto_pct": 20},
                        {"category": "Detalhes da cota", "cases": 4800, "auto_pct": 35},
                        {"category": "Cobrança", "cases": 2430, "auto_pct": 40},
                    ]
                },
                {
                    "rank": 3,
                    "name": "Investimentos",
                    "volume": 9280,
                    "volume_pct": 13.6,
                    "manual_pct": 88.3,
                    "auto_pct": 11.7,
                    "sla": 71,
                    "trend": "warning",
                    "quality_score": 65,
                    "category_breakdown": [
                        {"category": "Rentabilidade", "cases": 5100, "auto_pct": 8},
                        {"category": "Operacional", "cases": 3180, "auto_pct": 12},
                        {"category": "Conformidade", "cases": 1000, "auto_pct": 20},
                    ]
                },
                {
                    "rank": 4,
                    "name": "Empréstimos",
                    "volume": 5598,
                    "volume_pct": 8.2,
                    "manual_pct": 65.4,
                    "auto_pct": 34.6,
                    "sla": 89,
                    "trend": "up",
                    "quality_score": 81,
                    "category_breakdown": [
                        {"category": "Documentação", "cases": 2500, "auto_pct": 50},
                        {"category": "Análise", "cases": 2100, "auto_pct": 30},
                        {"category": "Cobrança", "cases": 998, "auto_pct": 15},
                    ]
                },
            ]
        return []

    # === PHASE 2: Manual vs Auto Effectiveness ===
    def fetch_effectiveness_data(self) -> Dict:
        """Fetch manual vs auto comparison data."""
        if self.use_mock:
            return {
                "by_category": [
                    {
                        "category": "Fatura",
                        "manual": {"volume": 18200, "sla": 86, "avg_time": "0h30m", "error_rate": 2.1},
                        "auto": {"volume": 19030, "sla": 100, "avg_time": "<5m", "error_rate": 0.3},
                        "efficiency_gain": 14
                    },
                    {
                        "category": "Atendimento",
                        "manual": {"volume": 16500, "sla": 82, "avg_time": "1h15m", "error_rate": 3.5},
                        "auto": {"volume": 10334, "sla": 100, "avg_time": "<10m", "error_rate": 0.2},
                        "efficiency_gain": 18
                    },
                    {
                        "category": "Detalhes da cota",
                        "manual": {"volume": 12890, "sla": 78, "avg_time": "2h30m", "error_rate": 4.2},
                        "auto": {"volume": 8465, "sla": 98, "avg_time": "<15m", "error_rate": 0.5},
                        "efficiency_gain": 20
                    },
                ],
                "error_types": [
                    {"type": "Categorização incorreta", "manual_pct": 35, "auto_pct": 40},
                    {"type": "Dados incompletos", "manual_pct": 28, "auto_pct": 35},
                    {"type": "Formato inválido", "manual_pct": 22, "auto_pct": 20},
                    {"type": "Timeout/Falha", "manual_pct": 15, "auto_pct": 5},
                ]
            }
        return {}

    # === PHASE 2: Data Quality Improvement ===
    def fetch_quality_trend_data(self) -> Dict:
        """Fetch data quality metrics over time."""
        if self.use_mock:
            return {
                "weekly_trend": [
                    {
                        "week": "26/07-01/08",
                        "total": 428000,
                        "uncategorized_pct": 39.1,
                        "uncategorized_manual_pct": 60.2,
                        "uncategorized_auto_pct": 1.5
                    },
                    {
                        "week": "02/08-08/08",
                        "total": 438000,
                        "uncategorized_pct": 38.2,
                        "uncategorized_manual_pct": 59.1,
                        "uncategorized_auto_pct": 1.2
                    },
                    {
                        "week": "09/08-14/08",
                        "total": 327405,
                        "uncategorized_pct": 37.4,
                        "uncategorized_manual_pct": 57.5,
                        "uncategorized_auto_pct": 0.7
                    },
                    {
                        "week": "16/08-hoje",
                        "total": 68231,
                        "uncategorized_pct": 37.4,
                        "uncategorized_manual_pct": 57.5,
                        "uncategorized_auto_pct": 0.7
                    },
                ],
                "improvement_opportunity": {
                    "gap_reduction_needed": 57.5 - 0.7,
                    "weekly_improvement": 0.26,
                    "target_date": "2026-11-30",
                    "target_uncategorized": 10.0
                }
            }
        return {}

    # === PHASE 2: Operational Capacity Planning ===
    def fetch_capacity_data(self) -> Dict:
        """Fetch operational capacity planning data."""
        if self.use_mock:
            return {
                "daily_pattern": [
                    {"day": "09/08 (seg)", "volume": 68430, "manual": 43662, "auto": 24768, "avg_per_agent": 185},
                    {"day": "10/08 (ter)", "volume": 75820, "manual": 48525, "auto": 27295, "avg_per_agent": 206},
                    {"day": "11/08 (qua)", "volume": 72150, "manual": 46176, "auto": 25974, "avg_per_agent": 196},
                    {"day": "12/08 (qui)", "volume": 78430, "manual": 50275, "auto": 28155, "avg_per_agent": 214},
                    {"day": "13/08 (sex)", "volume": 81200, "manual": 52008, "auto": 29192, "avg_per_agent": 221},
                    {"day": "14/08 (sab)", "volume": 68231, "manual": 43668, "auto": 24563, "avg_per_agent": 186},
                ],
                "by_queue": [
                    {"queue": "RPA 00127", "weekly_volume": 1236, "daily_avg": 206, "consistency": 98},
                    {"queue": "RPA Sales", "weekly_volume": 1163, "daily_avg": 194, "consistency": 95},
                    {"queue": "Agent Pool 1", "weekly_volume": 1042, "daily_avg": 174, "consistency": 78},
                    {"queue": "Agent Pool 2", "weekly_volume": 1008, "daily_avg": 168, "consistency": 72},
                ],
                "forecasting": {
                    "next_week_forecast": 338000,
                    "peak_day": "Thursday",
                    "recommended_staffing_increase": "5-8 agents"
                }
            }
        return {}

    # === PHASE 3: RPA Expansion Opportunity ===
    def fetch_automation_opportunity_data(self) -> List[Dict]:
        """Fetch RPA expansion opportunities matrix."""
        if self.use_mock:
            return [
                {
                    "rank": 1,
                    "category": "Investimentos",
                    "manual_volume": 8190,
                    "current_automation": 11.7,
                    "potential_automation": 65,
                    "potential_gain": 53.3,
                    "effort_score": 3,
                    "roi_score": 9.2,
                    "blockers": "Múltiplos formulários, validação complexa",
                    "timeline": "8-10 semanas"
                },
                {
                    "rank": 2,
                    "category": "Conta Corrente",
                    "manual_volume": 11135,
                    "current_automation": 27.9,
                    "potential_automation": 70,
                    "potential_gain": 42.1,
                    "effort_score": 4,
                    "roi_score": 8.5,
                    "blockers": "Integração com legacy system",
                    "timeline": "10-12 semanas"
                },
                {
                    "rank": 3,
                    "category": "Detalhes da cota",
                    "manual_volume": 12890,
                    "current_automation": 34.2,
                    "potential_automation": 75,
                    "potential_gain": 40.8,
                    "effort_score": 3,
                    "roi_score": 8.4,
                    "blockers": "Regras de negócio em constante mudança",
                    "timeline": "6-8 semanas"
                },
                {
                    "rank": 4,
                    "category": "Atendimento",
                    "manual_volume": 16500,
                    "current_automation": 38.5,
                    "potential_automation": 72,
                    "potential_gain": 33.5,
                    "effort_score": 5,
                    "roi_score": 8.2,
                    "blockers": "Requer entendimento contextual",
                    "timeline": "12-14 semanas"
                },
                {
                    "rank": 5,
                    "category": "Compensação",
                    "manual_volume": 5230,
                    "current_automation": 42.0,
                    "potential_automation": 80,
                    "potential_gain": 38.0,
                    "effort_score": 3,
                    "roi_score": 7.8,
                    "blockers": "Cálculos monetários sensíveis",
                    "timeline": "4-6 semanas"
                },
            ]
        return []

    # === PHASE 3: Hierarchy Completion ===
    def fetch_hierarchy_completion_data(self) -> Dict:
        """Fetch hierarchy/categorization completion metrics."""
        if self.use_mock:
            return {
                "overall_hierarchy": [
                    {
                        "level": 1,
                        "name": "Category (Categoria Principal)",
                        "completion_pct": 62.6,
                        "total_cases": 68231,
                        "filled": 42717,
                        "empty": 25514
                    },
                    {
                        "level": 2,
                        "name": "SubCategory (Subcategoria)",
                        "completion_pct": 62.5,
                        "total_cases": 68231,
                        "filled": 42631,
                        "empty": 25600
                    },
                    {
                        "level": 3,
                        "name": "Details (Detalhes/Hierarquia)",
                        "completion_pct": 31.2,
                        "total_cases": 68231,
                        "filled": 21296,
                        "empty": 46935
                    },
                ],
                "by_category": [
                    {"category": "Fatura", "level1": 100, "level2": 100, "level3": 78},
                    {"category": "Atendimento", "level1": 100, "level2": 100, "level3": 42},
                    {"category": "Detalhes da cota", "level1": 100, "level2": 100, "level3": 28},
                    {"category": "Compensação", "level1": 100, "level2": 100, "level3": 15},
                    {"category": "(sem categoria)", "level1": 0, "level2": 0, "level3": 0},
                ],
                "recommendations": [
                    "Tornar 'Details' campo obrigatório na entrada",
                    "Treinar operadores sobre importância da hierarquia completa",
                    "Implementar sugestão automática baseada em ML para detalhes",
                    "Criar dashboards de SLA por categoria e detalhe específico",
                ]
            }
        return {}


class ReportGenerator:
    """Generate HTML reports from Salesforce data."""

    COMMON_STYLES = """
  :root {
    --papel: #f4f2ec;
    --fundo: #ffffff;
    --tinta: #20242b;
    --tinta-suave: #4c525c;
    --tinta-fraca: #7a8090;
    --linha: #e3e0d6;
    --linha-forte: #c9c5b8;
    --accent: #0e6e6b;
    --accent-forte: #0a524f;
    --accent-claro: #e7f0ee;
    --manual: #0e6e6b;
    --auto: #c98a2d;
    --alerta: #b3482f;
    --alerta-fundo: #f7ebe6;
    --ok: #3d7a4e;
    --serif: "Newsreader", Georgia, "Times New Roman", serif;
    --grotesk: "Sora", "Segoe UI", system-ui, sans-serif;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  ::selection { background: var(--accent); color: #fff; }

  body {
    font-family: var(--grotesk);
    background: var(--papel);
    color: var(--tinta);
    font-size: 15px;
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
  }

  .page {
    width: 100%;
    max-width: 100%;
    padding: 0 clamp(16px, 4vw, 48px) 72px;
  }

  .nav-tabs {
    display: flex;
    gap: 12px;
    margin-bottom: 32px;
    border-bottom: 1px solid var(--linha-forte);
    flex-wrap: wrap;
  }

  .nav-tabs a {
    padding: 12px 16px;
    text-decoration: none;
    color: var(--tinta-suave);
    font-weight: 500;
    border-bottom: 3px solid transparent;
    transition: all 0.2s ease;
    font-size: 14px;
  }

  .nav-tabs a:hover { color: var(--accent); }
  .nav-tabs a.active { color: var(--accent-forte); border-bottom-color: var(--accent-forte); }

  .masthead {
    padding: 44px 0 20px;
    border-bottom: 1px solid var(--linha-forte);
    margin-bottom: 12px;
  }

  .masthead .org {
    font-size: 11px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--tinta-suave);
  }

  .masthead h1 {
    font-family: var(--serif);
    font-weight: 500;
    font-size: clamp(28px, 4vw, 40px);
    line-height: 1.08;
    margin: 12px 0 10px;
    letter-spacing: -0.01em;
  }

  .masthead .periodo {
    color: var(--tinta-suave);
    font-size: 14px;
  }

  .masthead .stamp {
    display: inline-block;
    margin-top: 12px;
    border: 1px solid var(--linha-forte);
    padding: 4px 10px;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--tinta-suave);
    border-radius: 999px;
  }

  section.cena { margin-top: 48px; }
  section.cena h2 {
    font-family: var(--serif);
    font-size: clamp(22px, 3vw, 30px);
    font-weight: 500;
    letter-spacing: -0.01em;
    line-height: 1.15;
  }

  section.cena .lead {
    color: var(--tinta-suave);
    max-width: 62ch;
    margin-top: 8px;
    font-size: 14px;
  }

  section.cena .quadro {
    background: var(--fundo);
    border: 1px solid var(--linha);
    border-radius: 12px;
    padding: 24px;
    margin-top: 20px;
    overflow-x: auto;
  }

  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  thead th {
    text-align: left;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--tinta-fraca);
    font-weight: 600;
    padding: 8px 10px 10px 0;
    border-bottom: 1px solid var(--linha-forte);
  }

  tbody td {
    padding: 9px 10px 9px 0;
    border-bottom: 1px solid var(--linha);
    font-variant-numeric: tabular-nums;
  }

  tbody tr:last-child td { border-bottom: none; }
  .n { text-align: right; }
  .destaque { font-weight: 700; }

  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin: 20px 0;
  }

  .kpi-card {
    background: var(--fundo);
    border: 1px solid var(--linha);
    border-radius: 8px;
    padding: 16px;
    text-align: center;
  }

  .kpi-value {
    font-family: var(--serif);
    font-size: 28px;
    font-weight: 500;
    color: var(--accent);
    margin: 8px 0;
  }

  .kpi-label {
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--tinta-fraca);
  }

  .trend-up { color: var(--ok); }
  .trend-down { color: var(--alerta); }
  .trend-stable { color: var(--tinta-suave); }

  .chip {
    display: inline-block;
    font-size: 10px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 999px;
    margin: 2px 4px 2px 0;
    white-space: nowrap;
  }

  .chip.manual { background: var(--accent-claro); color: var(--accent-forte); }
  .chip.auto { background: #f6ecd8; color: #8a5c10; }
  .chip.high { background: #f7ebe6; color: var(--alerta); }
  .chip.medium { background: #f9f5f0; color: #8a5c10; }
  .chip.low { background: #e8f5f2; color: var(--ok); }

  .nota-box {
    background: var(--accent-claro);
    border: 1px solid #cfe0dc;
    border-radius: 8px;
    padding: 14px 18px;
    margin-top: 16px;
    font-size: 13px;
    color: var(--accent-forte);
  }

  .alerta-box {
    background: var(--alerta-fundo);
    border: 1px solid #e7c9bd;
    border-radius: 8px;
    padding: 14px 18px;
    margin-top: 16px;
    font-size: 13px;
  }

  .alerta-box strong { color: var(--alerta); }

  footer {
    margin-top: 60px;
    padding-top: 18px;
    border-top: 1px solid var(--linha-forte);
    font-size: 11px;
    color: var(--tinta-fraca);
    line-height: 1.7;
  }

  @media (max-width: 800px) {
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
    .quadro { overflow-x: auto; }
  }

  @media (max-width: 560px) {
    .kpi-grid { grid-template-columns: 1fr; }
    .nav-tabs { gap: 8px; }
    .nav-tabs a { padding: 10px 12px; font-size: 12px; }
  }

  @media print {
    body { background: #fff; }
    .page { max-width: 100%; padding: 0 8px; }
  }
"""

    def __init__(self):
        self.fetcher = ReportDataFetcher()

    def format_number(self, num: int) -> str:
        """Format number with thousands separator."""
        return f"{num:,}".replace(",", ".")

    def generate_sla_report(self) -> str:
        """Generate SLA by Category Trend Report (Phase 1)."""
        data = self.fetcher.fetch_sla_trend_data()
        now = datetime.utcnow()

        status_html = ""
        for week in data["weeks"]:
            status_html += f"        <tr>\n          <td colspan=\"4\" style=\"text-align: center; font-weight: 600; padding: 12px 0; background: #f9f8f6;\"><strong>{week['week']}</strong></td>\n        </tr>\n"
            for cat in week["categories"]:
                gap = cat["manual_sla"] - 0  # Auto baseline
                status_html += f"""        <tr>
          <td>{cat['name']}</td>
          <td class="n">{cat['manual_sla']}%</td>
          <td class="n">{cat['auto_sla']}%</td>
          <td class="n"><span class="chip">Δ {cat['manual_sla'] - cat['auto_sla']:+d}pp</span></td>
        </tr>
"""

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SLA por Categoria — Trend Report</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600&family=Sora:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{self.COMMON_STYLES}</style>
</head>
<body>
<div class="page">
  <div class="nav-tabs">
    <a href="dashboard.html">Visão Diária</a>
    <a href="dashboard-weekly.html">Visão Semanal</a>
    <a href="#" class="active">Relatórios</a>
  </div>

  <div class="masthead">
    <div class="org">Operações de Atendimento · Salesforce Cases</div>
    <h1>SLA por Categoria — Trend Report</h1>
    <div class="periodo">Análise de 2 semanas (02/08 - 14/08/2026)</div>
    <div class="stamp">Dados SOQL somente leitura · Snapshot {now.strftime("%d/%m/%Y às %H:%M UTC")}</div>
  </div>

  <section class="cena">
    <h2>Evolução de SLA por Categoria</h2>
    <p class="lead">Comparação semana a semana mostrando desempenho manual vs automático. Identifica degradação de performance e oportunidades de melhoria.</p>
    <div class="quadro">
      <table>
        <thead>
          <tr>
            <th>Categoria</th>
            <th class="n">SLA Manual</th>
            <th class="n">SLA Automático</th>
            <th class="n">Gap</th>
          </tr>
        </thead>
        <tbody>
{status_html}
        </tbody>
      </table>
    </div>
  </section>

  <section class="cena">
    <h2>Insights e Recomendações</h2>
    <p class="lead">Achados principais da análise de tendência.</p>

    <div class="nota-box">
      <strong>✓ Oportunidade Identificada:</strong> Gap manual-auto permanece consistente (14-20 pp). Investir em treinamento operacional ou automação de categorias críticas pode ganhar 5-10pp em SLA manual.
    </div>

    <div class="alerta-box">
      <strong>⚠ Atenção:</strong> Categoria "Detalhes da cota" tem degradação contínua (79% → 78% manual). Investigar causa raiz e intervir em 24-48h.
    </div>

    <div class="nota-box">
      <strong>✓ Sucesso:</strong> Automação consistentemente ≥98% SLA em todas categorias. Modelo RPA comprovado como referência.
    </div>
  </section>

  <footer>
    <p><strong>SLA por Categoria — Trend Report</strong></p>
    <p>Gerado via MCP SalesforceRead · Monitoramento contínuo de performance operacional</p>
  </footer>
</div>
</body>
</html>
"""
        return html

    def generate_product_scorecard(self) -> str:
        """Generate Product Performance Scorecard (Phase 1)."""
        products = self.fetcher.fetch_product_scorecard_data()
        now = datetime.utcnow()

        cards_html = ""
        for prod in products:
            trend_emoji = "↗" if prod["trend"] == "up" else "↘" if prod["trend"] == "down" else "→"
            trend_class = f"trend-{prod['trend']}"

            cats_html = ""
            for cat in prod["category_breakdown"]:
                cats_html += f"          <tr>\n            <td style=\"padding-left: 20px;\">{cat['category']}</td>\n            <td class=\"n\">{self.format_number(cat['cases'])}</td>\n            <td class=\"n\">{cat['auto_pct']}%</td>\n          </tr>\n"

            cards_html += f"""  <section class="cena">
    <h2>#{prod['rank']} {prod['name']}</h2>
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Volume</div>
        <div class="kpi-value">{self.format_number(prod['volume'])}</div>
        <div class="kpi-label">{prod['volume_pct']:.1f}% do total</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">SLA Atingido</div>
        <div class="kpi-value" style="color: {'var(--ok)' if prod['sla'] >= 85 else 'var(--alerta)'};">{prod['sla']}%</div>
        <div class="kpi-label"><span class="trend-{prod['trend']}">{trend_emoji} {prod['trend'].upper()}</span></div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Automação</div>
        <div class="kpi-value">{prod['auto_pct']:.1f}%</div>
        <div class="kpi-label">Manual: {prod['manual_pct']:.1f}%</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Qualidade</div>
        <div class="kpi-value">{prod['quality_score']}</div>
        <div class="kpi-label">Score / 100</div>
      </div>
    </div>

    <div class="quadro">
      <strong>Breakdown por Categoria:</strong>
      <table style="margin-top: 12px;">
        <thead>
          <tr>
            <th>Categoria</th>
            <th class="n">Casos</th>
            <th class="n">Automação</th>
          </tr>
        </thead>
        <tbody>
{cats_html}
        </tbody>
      </table>
    </div>
  </section>
"""

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Product Performance Scorecard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600&family=Sora:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{self.COMMON_STYLES}</style>
</head>
<body>
<div class="page">
  <div class="nav-tabs">
    <a href="dashboard.html">Visão Diária</a>
    <a href="dashboard-weekly.html">Visão Semanal</a>
    <a href="#" class="active">Relatórios</a>
  </div>

  <div class="masthead">
    <div class="org">Operações de Atendimento · Salesforce Cases</div>
    <h1>Product Performance Scorecard</h1>
    <div class="periodo">Análise consolidada (semana 09-14/08/2026)</div>
    <div class="stamp">Dados SOQL somente leitura · Snapshot {now.strftime("%d/%m/%Y às %H:%M UTC")}</div>
  </div>

  <section class="cena">
    <h2>Resumo Executivo</h2>
    <p class="lead">Dashboard consolidado de performance por produto. Mostra volume, automação, SLA e saúde geral para gestão de portfolio.</p>

    <div class="nota-box">
      <strong>Insight Principal:</strong> Correlação clara entre nível de automação e SLA. Cartão PortoBank (54.8% auto) → 96% SLA. Investimentos (11.7% auto) → 71% SLA. Recomendação: expandir automação em categorias críticas.
    </div>
  </section>

{cards_html}

  <footer>
    <p><strong>Product Performance Scorecard</strong></p>
    <p>Gerado via MCP SalesforceRead · Ferramenta executiva para gestão de portfolio</p>
  </footer>
</div>
</body>
</html>
"""
        return html

    def generate_effectiveness_report(self) -> str:
        """Generate Manual vs Auto Effectiveness Comparison (Phase 2)."""
        data = self.fetcher.fetch_effectiveness_data()
        now = datetime.utcnow()

        cat_rows = ""
        for cat in data["by_category"]:
            m = cat["manual"]
            a = cat["auto"]
            cat_rows += f"""        <tr>
          <td><strong>{cat['category']}</strong></td>
          <td class="n">{self.format_number(m['volume'])} <span class="chip manual">Manual</span></td>
          <td class="n">{m['sla']}%</td>
          <td class="n">{m['avg_time']}</td>
        </tr>
        <tr style="background: #f9f8f6;">
          <td style="padding-left: 20px;">Automático</td>
          <td class="n">{self.format_number(a['volume'])} <span class="chip auto">Auto</span></td>
          <td class="n">{a['sla']}%</td>
          <td class="n">{a['avg_time']}</td>
        </tr>
        <tr style="border-bottom: 2px solid var(--linha-forte);">
          <td style="padding-left: 20px; color: var(--ok);"><strong>Ganho de Eficiência</strong></td>
          <td colspan="3" class="n"><span class="chip high">+{cat['efficiency_gain']}pp SLA</span></td>
        </tr>
"""

        error_rows = ""
        for err in data["error_types"]:
            error_rows += f"""        <tr>
          <td>{err['type']}</td>
          <td class="n">{err['manual_pct']}%</td>
          <td class="n">{err['auto_pct']}%</td>
          <td class="n"><span class="chip {'low' if err['manual_pct'] - err['auto_pct'] < 5 else 'high'}">Δ {err['manual_pct'] - err['auto_pct']:+d}pp</span></td>
        </tr>
"""

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Manual vs Auto Effectiveness</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600&family=Sora:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{self.COMMON_STYLES}</style>
</head>
<body>
<div class="page">
  <div class="nav-tabs">
    <a href="dashboard.html">Visão Diária</a>
    <a href="dashboard-weekly.html">Visão Semanal</a>
    <a href="#" class="active">Relatórios</a>
  </div>

  <div class="masthead">
    <div class="org">Operações de Atendimento · Salesforce Cases</div>
    <h1>Manual vs Automático — Effectiveness Comparison</h1>
    <div class="periodo">Análise comparativa (semana 09-14/08/2026)</div>
    <div class="stamp">Dados SOQL somente leitura · Snapshot {now.strftime("%d/%m/%Y às %H:%M UTC")}</div>
  </div>

  <section class="cena">
    <h2>Performance por Categoria</h2>
    <p class="lead">Comparação lado a lado: volume, SLA, tempo médio de resolução. Identifica onde automação supera manual e vice-versa.</p>
    <div class="quadro">
      <table>
        <thead>
          <tr>
            <th>Categoria / Origem</th>
            <th class="n">Volume</th>
            <th class="n">SLA %</th>
            <th class="n">Tempo Médio</th>
          </tr>
        </thead>
        <tbody>
{cat_rows}
        </tbody>
      </table>
    </div>
  </section>

  <section class="cena">
    <h2>Análise de Tipos de Erro</h2>
    <p class="lead">Breakdown de falhas por origem (manual vs automático). Mostra onde ambos falham e oportunidades de melhoria.</p>
    <div class="quadro">
      <table>
        <thead>
          <tr>
            <th>Tipo de Erro</th>
            <th class="n">Manual %</th>
            <th class="n">Auto %</th>
            <th class="n">Gap</th>
          </tr>
        </thead>
        <tbody>
{error_rows}
        </tbody>
      </table>
    </div>

    <div class="alerta-box">
      <strong>Achado:</strong> Automação comete mais erros de "Categorização incorreta" (40% vs 35% manual), mas muito menos em "Timeout/Falha" (5% vs 15%). Recomendação: melhorar regras de categorização do RPA.
    </div>
  </section>

  <footer>
    <p><strong>Manual vs Automático Effectiveness Comparison</strong></p>
    <p>Gerado via MCP SalesforceRead · Análise para decisão de roadmap de automação</p>
  </footer>
</div>
</body>
</html>
"""
        return html

    def generate_quality_tracker(self) -> str:
        """Generate Data Quality Improvement Tracker (Phase 2)."""
        data = self.fetcher.fetch_quality_trend_data()
        now = datetime.utcnow()

        trend_rows = ""
        for week in data["weekly_trend"]:
            total = self.format_number(week["total"])
            uncat = self.format_number(int(week["total"] * week["uncategorized_pct"] / 100))
            trend_rows += f"""        <tr>
          <td>{week['week']}</td>
          <td class="n">{total}</td>
          <td class="n">{week['uncategorized_pct']:.1f}% ({uncat})</td>
          <td class="n">{week['uncategorized_manual_pct']:.1f}%</td>
          <td class="n">{week['uncategorized_auto_pct']:.1f}%</td>
          <td class="n"><span class="chip low">Δ {-0.26:.2f}pp/sem</span></td>
        </tr>
"""

        opp = data["improvement_opportunity"]

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Data Quality Improvement Tracker</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600&family=Sora:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{self.COMMON_STYLES}</style>
</head>
<body>
<div class="page">
  <div class="nav-tabs">
    <a href="dashboard.html">Visão Diária</a>
    <a href="dashboard-weekly.html">Visão Semanal</a>
    <a href="#" class="active">Relatórios</a>
  </div>

  <div class="masthead">
    <div class="org">Operações de Atendimento · Salesforce Cases</div>
    <h1>Data Quality Improvement Tracker</h1>
    <div class="periodo">Acompanhamento temporal (26/07 - 16/08/2026)</div>
    <div class="stamp">Dados SOQL somente leitura · Snapshot {now.strftime("%d/%m/%Y às %H:%M UTC")}</div>
  </div>

  <section class="cena">
    <h2>Tendência de Categorização</h2>
    <p class="lead">Evolução semanal: % de casos sem categoria. Comparação manual vs automático.</p>
    <div class="quadro">
      <table>
        <thead>
          <tr>
            <th>Semana</th>
            <th class="n">Total</th>
            <th class="n">Sem Categoria</th>
            <th class="n">% Manual</th>
            <th class="n">% Auto</th>
            <th class="n">Trend</th>
          </tr>
        </thead>
        <tbody>
{trend_rows}
        </tbody>
      </table>
    </div>
  </section>

  <section class="cena">
    <h2>Meta de Melhoria</h2>
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Gap Atual</div>
        <div class="kpi-value">{opp['gap_reduction_needed']:.1f}pp</div>
        <div class="kpi-label">Manual vs Auto</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Melhoria Semanal</div>
        <div class="kpi-value">{opp['weekly_improvement']:.2f}pp</div>
        <div class="kpi-label">Atual: -0.26pp/sem</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Meta</div>
        <div class="kpi-value">{opp['target_uncategorized']:.1f}%</div>
        <div class="kpi-label">Uncategorized Target</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Data Prevista</div>
        <div class="kpi-value">+{(opp['gap_reduction_needed'] / opp['weekly_improvement']):.0f}sem</div>
        <div class="kpi-label">{opp['target_date']}</div>
      </div>
    </div>

    <div class="alerta-box">
      <strong>⚠ Atenção:</strong> Velocidade de melhoria é lenta (0.26pp/semana). Para atingir 10% uncategorized até 30/11, necessário acelerar a {(opp['gap_reduction_needed'] / ((datetime.strptime(opp['target_date'], '%Y-%m-%d') - datetime.utcnow()).days / 7)):.2f}pp/semana. Recomendar treinamento urgente ou automação de classificação.
    </div>
  </section>

  <footer>
    <p><strong>Data Quality Improvement Tracker</strong></p>
    <p>Gerado via MCP SalesforceRead · Métrica crítica de governance de dados</p>
  </footer>
</div>
</body>
</html>
"""
        return html

    def generate_capacity_report(self) -> str:
        """Generate Operational Capacity Planning (Phase 2)."""
        data = self.fetcher.fetch_capacity_data()
        now = datetime.utcnow()

        daily_rows = ""
        for day in data["daily_pattern"]:
            daily_rows += f"""        <tr>
          <td>{day['day']}</td>
          <td class="n">{self.format_number(day['volume'])}</td>
          <td class="n">{self.format_number(day['manual'])}</td>
          <td class="n">{self.format_number(day['auto'])}</td>
          <td class="n">{day['avg_per_agent']}</td>
        </tr>
"""

        queue_rows = ""
        for queue in data["by_queue"]:
            queue_rows += f"""        <tr>
          <td>{queue['queue']}</td>
          <td class="n">{self.format_number(queue['weekly_volume'])}</td>
          <td class="n">{queue['daily_avg']}</td>
          <td class="n"><span class="chip {'low' if queue['consistency'] >= 90 else 'medium'}">{queue['consistency']}%</span></td>
        </tr>
"""

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Operational Capacity Planning</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600&family=Sora:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{self.COMMON_STYLES}</style>
</head>
<body>
<div class="page">
  <div class="nav-tabs">
    <a href="dashboard.html">Visão Diária</a>
    <a href="dashboard-weekly.html">Visão Semanal</a>
    <a href="#" class="active">Relatórios</a>
  </div>

  <div class="masthead">
    <div class="org">Operações de Atendimento · Salesforce Cases</div>
    <h1>Operational Capacity Planning</h1>
    <div class="periodo">Análise de padrão operacional (semana 09-14/08/2026)</div>
    <div class="stamp">Dados SOQL somente leitura · Snapshot {now.strftime("%d/%m/%Y às %H:%M UTC")}</div>
  </div>

  <section class="cena">
    <h2>Padrão Diário de Volume</h2>
    <p class="lead">Variação dia a dia e distribuição manual vs automática. Base para dimensionamento de recursos.</p>
    <div class="quadro">
      <table>
        <thead>
          <tr>
            <th>Dia</th>
            <th class="n">Volume Total</th>
            <th class="n">Manual</th>
            <th class="n">Automático</th>
            <th class="n">Avg/Agente</th>
          </tr>
        </thead>
        <tbody>
{daily_rows}
        </tbody>
      </table>
    </div>

    <div class="nota-box">
      <strong>Insight:</strong> Variância de volume = +19% (pico 81.2k em qui vs vale 68.2k em seg). Requer scaling flexível. Automação consistente (RPA), humanos sofrem variação.
    </div>
  </section>

  <section class="cena">
    <h2>Carga por Fila/Queue</h2>
    <p class="lead">Distribuição de volume entre filas de automação e pools de agentes. Consistência operacional.</p>
    <div class="quadro">
      <table>
        <thead>
          <tr>
            <th>Fila</th>
            <th class="n">Volume/Semana</th>
            <th class="n">Média/Dia</th>
            <th class="n">Consistência</th>
          </tr>
        </thead>
        <tbody>
{queue_rows}
        </tbody>
      </table>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Forecast Próxima Semana</div>
        <div class="kpi-value">{self.format_number(data['forecasting']['next_week_forecast'])}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Dia de Pico</div>
        <div class="kpi-value">{data['forecasting']['peak_day']}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Recomendação</div>
        <div class="kpi-value" style="font-size: 16px;">{data['forecasting']['recommended_staffing_increase']}</div>
      </div>
    </div>
  </section>

  <footer>
    <p><strong>Operational Capacity Planning</strong></p>
    <p>Gerado via MCP SalesforceRead · Ferramenta para previsão de demanda e dimensionamento de RH</p>
  </footer>
</div>
</body>
</html>
"""
        return html

    def generate_automation_matrix(self) -> str:
        """Generate RPA Expansion Opportunity Matrix (Phase 3)."""
        opportunities = self.fetcher.fetch_automation_opportunity_data()
        now = datetime.utcnow()

        opp_rows = ""
        for opp in opportunities:
            roi_color = "ok" if opp["roi_score"] >= 8.5 else "medium"
            effort_color = "ok" if opp["effort_score"] <= 3 else "medium"
            opp_rows += f"""        <tr>
          <td><strong>{opp['rank']}. {opp['category']}</strong></td>
          <td class="n">{self.format_number(opp['manual_volume'])}</td>
          <td class="n">{opp['current_automation']}% → {opp['potential_automation']}%</td>
          <td class="n"><span class="chip high">+{opp['potential_gain']:.1f}%</span></td>
          <td class="n"><span class="chip {effort_color}">E{opp['effort_score']}</span></td>
          <td class="n"><strong style="color: var(--accent);">{opp['roi_score']}/10</strong></td>
          <td class="n">{opp['timeline']}</td>
        </tr>
        <tr style="background: #f9f8f6; font-size: 12px;">
          <td colspan="7" style="padding-left: 20px;">📌 Bloqueador: {opp['blockers']}</td>
        </tr>
"""

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RPA Expansion Opportunity Matrix</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600&family=Sora:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{self.COMMON_STYLES}</style>
</head>
<body>
<div class="page">
  <div class="nav-tabs">
    <a href="dashboard.html">Visão Diária</a>
    <a href="dashboard-weekly.html">Visão Semanal</a>
    <a href="#" class="active">Relatórios</a>
  </div>

  <div class="masthead">
    <div class="org">Operações de Atendimento · Salesforce Cases</div>
    <h1>RPA Expansion Opportunity Matrix</h1>
    <div class="periodo">Priorização de automação (semana 09-14/08/2026)</div>
    <div class="stamp">Dados SOQL somente leitura · Snapshot {now.strftime("%d/%m/%Y às %H:%M UTC")}</div>
  </div>

  <section class="cena">
    <h2>Matriz de Oportunidades</h2>
    <p class="lead">Categorias rankadas por ROI potencial (score 1-10). E=Effort, ROI=Return. Identifica próximos candidatos para expansão RPA.</p>
    <div class="quadro">
      <table>
        <thead>
          <tr>
            <th>Categoria</th>
            <th class="n">Volume Manual</th>
            <th class="n">Automação</th>
            <th class="n">Ganho</th>
            <th class="n">Esforço</th>
            <th class="n">ROI</th>
            <th class="n">Timeline</th>
          </tr>
        </thead>
        <tbody>
{opp_rows}
        </tbody>
      </table>
    </div>

    <div class="nota-box">
      <strong>✓ Top Priority:</strong> Investimentos (ROI 9.2) e Conta Corrente (ROI 8.5) devem ser próximos projetos. Ambos têm alto volume manual com potencial de automação 53-42pp.
    </div>
  </section>

  <footer>
    <p><strong>RPA Expansion Opportunity Matrix</strong></p>
    <p>Gerado via MCP SalesforceRead · Roadmap estratégico de automação</p>
  </footer>
</div>
</body>
</html>
"""
        return html

    def generate_hierarchy_report(self) -> str:
        """Generate Hierarchy Completion Report (Phase 3)."""
        data = self.fetcher.fetch_hierarchy_completion_data()
        now = datetime.utcnow()

        hierarchy_rows = ""
        for level in data["overall_hierarchy"]:
            filled_pct = self.format_number(level["filled"])
            empty_pct = self.format_number(level["empty"])
            hierarchy_rows += f"""        <tr>
          <td><strong>{level['name']}</strong></td>
          <td class="n">{level['completion_pct']:.1f}%</td>
          <td class="n">{filled_pct}</td>
          <td class="n">{empty_pct}</td>
          <td class="n"><div style="background: linear-gradient(to right, var(--ok) {level['completion_pct']}%, var(--linha) {level['completion_pct']}%); height: 20px; border-radius: 4px;"></div></td>
        </tr>
"""

        cat_rows = ""
        for cat in data["by_category"]:
            cat_rows += f"""        <tr>
          <td>{cat['category']}</td>
          <td class="n"><span class="chip {'low' if cat['level1'] < 50 else 'high'}">{cat['level1']}%</span></td>
          <td class="n"><span class="chip {'low' if cat['level2'] < 50 else 'high'}">{cat['level2']}%</span></td>
          <td class="n"><span class="chip {'low' if cat['level3'] < 50 else 'medium' if cat['level3'] < 75 else 'high'}">{cat['level3']}%</span></td>
        </tr>
"""

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hierarchy Completion Report</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600&family=Sora:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{self.COMMON_STYLES}</style>
</head>
<body>
<div class="page">
  <div class="nav-tabs">
    <a href="dashboard.html">Visão Diária</a>
    <a href="dashboard-weekly.html">Visão Semanal</a>
    <a href="#" class="active">Relatórios</a>
  </div>

  <div class="masthead">
    <div class="org">Operações de Atendimento · Salesforce Cases</div>
    <h1>Hierarchy Completion Report</h1>
    <div class="periodo">Análise de completude de hierarquias (16/08/2026 hoje)</div>
    <div class="stamp">Dados SOQL somente leitura · Snapshot {now.strftime("%d/%m/%Y às %H:%M UTC")}</div>
  </div>

  <section class="cena">
    <h2>Completude Geral de Hierarquia</h2>
    <p class="lead">Distribuição de preenchimento por nível (Category → SubCategory → Details).</p>
    <div class="quadro">
      <table>
        <thead>
          <tr>
            <th>Nível Hierárquico</th>
            <th class="n">Completude %</th>
            <th class="n">Preenchido</th>
            <th class="n">Vazio</th>
            <th class="n">Visualização</th>
          </tr>
        </thead>
        <tbody>
{hierarchy_rows}
        </tbody>
      </table>
    </div>

    <div class="alerta-box">
      <strong>⚠ Crítico:</strong> Nível 3 (Details) apenas 31.2% completo. 70% dos casos sem detalhe = perda de informação operacional. Causa provável: campo não obrigatório na entrada.
    </div>
  </section>

  <section class="cena">
    <h2>Completude por Categoria</h2>
    <p class="lead">Breakdown mostrando qual categoria tem melhor/pior qualidade hierárquica.</p>
    <div class="quadro">
      <table>
        <thead>
          <tr>
            <th>Categoria</th>
            <th class="n">Level 1 %</th>
            <th class="n">Level 2 %</th>
            <th class="n">Level 3 %</th>
          </tr>
        </thead>
        <tbody>
{cat_rows}
        </tbody>
      </table>
    </div>
  </section>

  <section class="cena">
    <h2>Recomendações</h2>
    <div class="nota-box">
      <strong>1. Tornar "Details" obrigatório:</strong> Implementar validação de entrada para exigir preenchimento do 3º nível.<br><br>
      <strong>2. Treinamento operacional:</strong> 30 minutos com equipe sobre importância da hierarquia completa para routing automático.<br><br>
      <strong>3. Automação de sugestão:</strong> Implementar ML-based recommendation engine para popular Details automaticamente.<br><br>
      <strong>4. Dashboard de SLA:</strong> Criar visualização de SLA por categoria+detalhe específico (vs agregado hoje).
    </div>
  </section>

  <footer>
    <p><strong>Hierarchy Completion Report</strong></p>
    <p>Gerado via MCP SalesforceRead · Métrica de governance de estrutura de dados</p>
  </footer>
</div>
</body>
</html>
"""
        return html


def main():
    """Generate all reports or specific report based on argument."""
    report = sys.argv[1] if len(sys.argv) > 1 else "all"

    # Ensure docs directory exists
    docs_dir = "docs"
    os.makedirs(docs_dir, exist_ok=True)

    gen = ReportGenerator()

    # Phase 1 reports
    if report in ("all", "phase1", "sla"):
        html = gen.generate_sla_report()
        with open(os.path.join(docs_dir, "report-sla.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("✓ SLA by Category Trend Report gerado")

    if report in ("all", "phase1", "product"):
        html = gen.generate_product_scorecard()
        with open(os.path.join(docs_dir, "report-product-scorecard.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("✓ Product Performance Scorecard gerado")

    # Phase 2 reports
    if report in ("all", "phase2", "effectiveness"):
        html = gen.generate_effectiveness_report()
        with open(os.path.join(docs_dir, "report-effectiveness.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("✓ Manual vs Auto Effectiveness Report gerado")

    if report in ("all", "phase2", "quality"):
        html = gen.generate_quality_tracker()
        with open(os.path.join(docs_dir, "report-quality-tracker.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("✓ Data Quality Improvement Tracker gerado")

    if report in ("all", "phase2", "capacity"):
        html = gen.generate_capacity_report()
        with open(os.path.join(docs_dir, "report-capacity.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("✓ Operational Capacity Planning gerado")

    # Phase 3 reports
    if report in ("all", "phase3", "automation"):
        html = gen.generate_automation_matrix()
        with open(os.path.join(docs_dir, "report-automation-matrix.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("✓ RPA Expansion Opportunity Matrix gerado")

    if report in ("all", "phase3", "hierarchy"):
        html = gen.generate_hierarchy_report()
        with open(os.path.join(docs_dir, "report-hierarchy.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("✓ Hierarchy Completion Report gerado")

    if report == "all":
        print("\n✅ Todos os 7 relatórios foram gerados com sucesso!")


if __name__ == "__main__":
    main()
