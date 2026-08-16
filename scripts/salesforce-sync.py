#!/usr/bin/env python3
"""
Script para sincronizar dados reais do Salesforce via MCP.
Executado automaticamente por GitHub Actions a cada 1 hora.
Gera JSONs que são consumidos pelo dashboard estático.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Tentar importar do MCP Client local
    sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "mcp-client" / "src"))
    from salesforce_connector import MCPClient
except ImportError:
    logger.warning("MCP Client não encontrado. Usando dados de fallback.")
    MCPClient = None


async def fetch_salesforce_data():
    """Busca dados reais do Salesforce via MCP"""

    try:
        # Verificar credenciais
        client_id = os.getenv("SF_CLIENT_ID")
        client_secret = os.getenv("SF_CLIENT_SECRET")
        refresh_token = os.getenv("SF_REFRESH_TOKEN")

        if not all([client_id, client_secret, refresh_token]):
            logger.error("❌ Credenciais Salesforce não configuradas!")
            logger.info("Configure os secrets no GitHub:")
            logger.info("  - SF_CLIENT_ID")
            logger.info("  - SF_CLIENT_SECRET")
            logger.info("  - SF_REFRESH_TOKEN")
            return generate_fallback_data()

        if MCPClient is None:
            logger.warning("⚠️ MCP Client não disponível. Usando dados de fallback.")
            return generate_fallback_data()

        logger.info("🔄 Conectando ao Salesforce via MCP...")

        mcp = MCPClient(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token
        )

        await mcp.authenticate()
        logger.info("✅ Autenticado no Salesforce")

        # 1. Buscar Cases
        logger.info("📋 Buscando Cases...")
        cases_result = await mcp.soql_query("""
            SELECT Id, CaseNumber, Subject, Status, Priority, CreatedDate, Owner.Name
            FROM Case
            ORDER BY CreatedDate DESC
            LIMIT 100
        """)
        cases = cases_result.get("records", [])

        # 2. Buscar Reports
        logger.info("📊 Buscando Reports...")
        reports_result = await mcp.soql_query("""
            SELECT Id, Name, Description, CreatedDate, CreatedBy.Name
            FROM Report
            ORDER BY CreatedDate DESC
            LIMIT 50
        """)
        reports = reports_result.get("records", [])

        # 3. Buscar Accounts
        logger.info("🏢 Buscando Accounts...")
        accounts_result = await mcp.soql_query("""
            SELECT Id, Name, Industry, Revenue, CreatedDate
            FROM Account
            ORDER BY Revenue DESC
            LIMIT 20
        """)
        accounts = accounts_result.get("records", [])

        logger.info(f"✅ Dados obtidos: {len(cases)} cases, {len(reports)} reports, {len(accounts)} accounts")

        return {
            "cases": cases,
            "reports": reports,
            "accounts": accounts,
            "success": True
        }

    except Exception as e:
        logger.error(f"❌ Erro ao conectar Salesforce: {str(e)}")
        logger.info("Usando dados de fallback para evitar quebra de dashboard")
        return generate_fallback_data()


def generate_fallback_data():
    """Gera dados de fallback quando Salesforce não está disponível"""
    logger.info("📦 Gerando dados de fallback...")

    fallback_cases = [
        {
            "Id": f"5001Q00000Ir{i:03d}",
            "CaseNumber": f"00{1001 + i}",
            "Subject": f"Suporte Técnico - Caso #{i+1}",
            "Status": ["New", "In Progress", "On Hold", "Resolved"][i % 4],
            "Priority": ["High", "Medium", "Low"][i % 3],
            "CreatedDate": f"2026-08-{16 - (i % 15):02d}T10:30:00.000Z",
            "Owner": {"Name": ["João Silva", "Maria Santos", "Carlos Oliveira"][i % 3]}
        }
        for i in range(25)
    ]

    fallback_reports = [
        {
            "Id": f"00P1Q00000Ir{i:03d}",
            "Name": f"Relatório de {['Vendas', 'Casos', 'Contas'][i % 3]} - Q3",
            "Description": f"Relatório automático gerado pelo dashboard",
            "CreatedDate": f"2026-08-{15 - (i % 15):02d}T14:20:00.000Z",
            "CreatedBy": {"Name": ["Admin", "Gerente", "Analista"][i % 3]}
        }
        for i in range(15)
    ]

    fallback_accounts = [
        {
            "Id": f"0011Q00000Ir{i:03d}",
            "Name": f"Empresa {chr(65 + (i % 26))}{chr(65 + ((i+1) % 26))} Ltda",
            "Industry": ["Technology", "Finance", "Healthcare", "Retail"][i % 4],
            "Revenue": (1000000 * (20 - i)),
            "CreatedDate": f"2026-07-{28 - (i % 28):02d}T09:15:00.000Z"
        }
        for i in range(15)
    ]

    return {
        "cases": fallback_cases,
        "reports": fallback_reports,
        "accounts": fallback_accounts,
        "success": False
    }


def save_json_files(data):
    """Salva dados em JSONs para consumo do dashboard"""

    output_dir = Path("docs/data")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Processar Cases
    cases_json = {
        "total": len(data["cases"]),
        "records": [
            {
                "id": case.get("Id", "N/A"),
                "number": case.get("CaseNumber", "N/A"),
                "subject": case.get("Subject", "N/A"),
                "status": case.get("Status", "N/A"),
                "priority": case.get("Priority", "N/A"),
                "created": case.get("CreatedDate", "N/A"),
                "owner": case.get("Owner", {}).get("Name", "N/A") if isinstance(case.get("Owner"), dict) else "N/A"
            }
            for case in data["cases"]
        ],
        "lastSync": datetime.utcnow().isoformat() + "Z",
        "isLive": data.get("success", False)
    }

    # Processar Reports
    reports_json = {
        "total": len(data["reports"]),
        "records": [
            {
                "id": report.get("Id", "N/A"),
                "name": report.get("Name", "N/A"),
                "description": report.get("Description", "N/A"),
                "created": report.get("CreatedDate", "N/A"),
                "createdBy": report.get("CreatedBy", {}).get("Name", "N/A") if isinstance(report.get("CreatedBy"), dict) else "N/A"
            }
            for report in data["reports"]
        ],
        "lastSync": datetime.utcnow().isoformat() + "Z",
        "isLive": data.get("success", False)
    }

    # Processar Accounts
    accounts_json = {
        "total": len(data["accounts"]),
        "records": [
            {
                "id": account.get("Id", "N/A"),
                "name": account.get("Name", "N/A"),
                "industry": account.get("Industry", "N/A"),
                "revenue": account.get("Revenue", 0),
                "created": account.get("CreatedDate", "N/A")
            }
            for account in data["accounts"]
        ],
        "lastSync": datetime.utcnow().isoformat() + "Z",
        "isLive": data.get("success", False)
    }

    # Salvar Files
    with open(output_dir / "cases.json", "w", encoding="utf-8") as f:
        json.dump(cases_json, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Salvou cases.json ({cases_json['total']} registros)")

    with open(output_dir / "reports.json", "w", encoding="utf-8") as f:
        json.dump(reports_json, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Salvou reports.json ({reports_json['total']} registros)")

    with open(output_dir / "accounts.json", "w", encoding="utf-8") as f:
        json.dump(accounts_json, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Salvou accounts.json ({accounts_json['total']} registros)")

    # Metadata
    metadata = {
        "lastSync": datetime.utcnow().isoformat() + "Z",
        "recordsCount": {
            "cases": len(data["cases"]),
            "reports": len(data["reports"]),
            "accounts": len(data["accounts"])
        },
        "status": "success" if data.get("success") else "fallback",
        "isLive": data.get("success", False)
    }

    with open(output_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    logger.info("✅ Salvou metadata.json")

    return metadata


def main():
    """Função principal"""
    import asyncio

    logger.info("=" * 60)
    logger.info("🚀 Sincronização Salesforce → GitHub Pages")
    logger.info("=" * 60)

    try:
        # Buscar dados
        data = asyncio.run(fetch_salesforce_data())

        # Salvar JSONs
        metadata = save_json_files(data)

        logger.info("=" * 60)
        logger.info("✅ SINCRONIZAÇÃO COMPLETA!")
        logger.info(f"   Cases: {metadata['recordsCount']['cases']}")
        logger.info(f"   Reports: {metadata['recordsCount']['reports']}")
        logger.info(f"   Accounts: {metadata['recordsCount']['accounts']}")
        logger.info(f"   Status: {metadata['status'].upper()}")
        logger.info(f"   Última atualização: {metadata['lastSync']}")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"❌ ERRO: {str(e)}")
        logger.error("=" * 60)
        return 1


if __name__ == "__main__":
    exit(main())
