#!/usr/bin/env python3
"""
Script para sincronizar dados reais do Salesforce via REST API OAuth2.
Executado automaticamente por GitHub Actions a cada 1 hora.
Gera JSONs que são consumidos pelo dashboard estático.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
import logging
import requests
from urllib.parse import urlencode

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Salesforce OAuth2 endpoints
SALESFORCE_LOGIN_URL = "https://login.salesforce.com"
OAUTH_TOKEN_ENDPOINT = f"{SALESFORCE_LOGIN_URL}/services/oauth2/token"
SOBJECT_API_ENDPOINT = "/services/data/v57.0"


def get_access_token(client_id, client_secret, refresh_token):
    """Obtém um novo access token usando o refresh token"""

    try:
        logger.info("🔑 Obtendo novo access token...")

        payload = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token
        }

        response = requests.post(OAUTH_TOKEN_ENDPOINT, data=payload, timeout=30)
        response.raise_for_status()

        token_data = response.json()
        access_token = token_data.get("access_token")
        instance_url = token_data.get("instance_url")

        logger.info(f"✅ Token obtido com sucesso (instance: {instance_url})")
        return access_token, instance_url

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro ao obter token: {str(e)}")
        if hasattr(e.response, 'text'):
            logger.error(f"   Response: {e.response.text}")
        raise


def execute_soql(access_token, instance_url, query):
    """Executa uma query SOQL no Salesforce"""

    url = f"{instance_url}{SOBJECT_API_ENDPOINT}/query"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    params = {"q": query}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro ao executar SOQL: {str(e)}")
        if hasattr(e.response, 'text'):
            logger.error(f"   Response: {e.response.text}")
        raise


async def fetch_salesforce_data():
    """Busca dados reais do Salesforce via OAuth2 REST API"""

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

        logger.info("🔄 Conectando ao Salesforce via OAuth2...")

        # Obter access token
        access_token, instance_url = get_access_token(
            client_id,
            client_secret,
            refresh_token
        )
        logger.info("✅ Autenticado no Salesforce")

        # 1. Volume total (hoje)
        logger.info("📊 Volume total...")
        total_query = "SELECT COUNT(Id) total FROM Case WHERE CreatedDate = TODAY"
        total_result = execute_soql(access_token, instance_url, total_query)
        total_cases = total_result.get("records", [{}])[0].get("total", 0)

        # 2. Manual vs Automático
        logger.info("🤖 Criação manual vs automática...")
        creation_query = """
            SELECT CreatedAutomatically__c, COUNT(Id) total
            FROM Case
            WHERE CreatedDate = TODAY
            GROUP BY CreatedAutomatically__c
        """
        creation_result = execute_soql(access_token, instance_url, creation_query)
        manual_total = automatic_total = 0
        for record in creation_result.get("records", []):
            if record.get("CreatedAutomatically__c") is False:
                manual_total = record.get("total", 0)
            elif record.get("CreatedAutomatically__c") is True:
                automatic_total = record.get("total", 0)

        # 3. Status
        logger.info("📋 Distribuição por Status...")
        status_query = """
            SELECT Status, COUNT(Id) total
            FROM Case
            WHERE CreatedDate = TODAY
            GROUP BY Status
            ORDER BY total DESC
        """
        status_result = execute_soql(access_token, instance_url, status_query)
        status_data = [
            {"label": r.get("Status", "N/A"), "value": r.get("total", 0)}
            for r in status_result.get("records", [])
        ]

        # 4. Prioridade
        logger.info("🚨 Distribuição por Prioridade...")
        priority_query = """
            SELECT Priority, COUNT(Id) total
            FROM Case
            WHERE CreatedDate = TODAY
            GROUP BY Priority
            ORDER BY total DESC
        """
        priority_result = execute_soql(access_token, instance_url, priority_query)
        priority_data = [
            {"label": r.get("Priority", "N/A"), "value": r.get("total", 0)}
            for r in priority_result.get("records", [])
        ]

        # 5. Top Categorias (usando campos legados agrupáveis)
        logger.info("📂 Top Categorias...")
        categories_query = """
            SELECT Category__c, COUNT(Id) total
            FROM Case
            WHERE CreatedDate = TODAY AND Category__c != null
            GROUP BY Category__c
            ORDER BY total DESC
            LIMIT 10
        """
        categories_result = execute_soql(access_token, instance_url, categories_query)
        categories_data = [
            {"label": r.get("Category__c", "N/A"), "value": r.get("total", 0)}
            for r in categories_result.get("records", [])
        ]

        # 6. Casos encerrados (para SLA)
        logger.info("✅ Casos encerrados...")
        closed_query = """
            SELECT COUNT(Id) total
            FROM Case
            WHERE CreatedDate = TODAY
              AND Status IN ('Closed', 'Fechado Com Sucesso', 'Protocolo Fechado')
        """
        closed_result = execute_soql(access_token, instance_url, closed_query)
        closed_cases = closed_result.get("records", [{}])[0].get("total", 0)

        # 7. Casos sem categoria (qualidade de dados)
        logger.info("⚠️ Qualidade de Dados...")
        quality_query = """
            SELECT CreatedAutomatically__c, COUNT(Id) total
            FROM Case
            WHERE CreatedDate = TODAY AND Category__c = null
            GROUP BY CreatedAutomatically__c
        """
        quality_result = execute_soql(access_token, instance_url, quality_query)
        no_category_manual = 0
        no_category_automatic = 0
        for record in quality_result.get("records", []):
            if record.get("CreatedAutomatically__c") is False:
                no_category_manual = record.get("total", 0)
            elif record.get("CreatedAutomatically__c") is True:
                no_category_automatic = record.get("total", 0)
        no_category_total = no_category_manual + no_category_automatic

        logger.info(f"✅ Sincronização bem-sucedida!")

        return {
            "summary": {
                "total_cases": total_cases,
                "manual_cases": manual_total,
                "automatic_cases": automatic_total,
                "closed_cases": closed_cases,
                "no_category": no_category_total
            },
            "categories": categories_data,
            "status": status_data,
            "priority": priority_data,
            "creation_type": [
                {"label": "Manual", "value": manual_total},
                {"label": "Automático", "value": automatic_total},
            ],
            "quality": [
                {"label": "Manual", "value": no_category_manual},
                {"label": "Automático", "value": no_category_automatic},
            ],
            "sla": {
                "median_total": 0,
                "mean_manual": 10.6,
                "mean_automatic": 0,
                "sample_size": 0
            },
            "success": True
        }

    except Exception as e:
        logger.error(f"❌ Erro ao conectar Salesforce: {str(e)}")
        logger.info("Usando dados de fallback para evitar quebra de dashboard")
        return generate_fallback_data()


def generate_fallback_data():
    """Gera dados de fallback quando Salesforce não está disponível"""
    logger.info("📦 Gerando dados de fallback...")

    return {
        "summary": {
            "total_cases": 68222,
            "manual_cases": 44063,
            "automatic_cases": 24159,
            "closed_cases": 41775,
            "no_category": 25505
        },
        "categories": [
            {"label": "Fatura", "value": 7339},
            {"label": "Atendimento", "value": 5623},
            {"label": "Detalhes da cota", "value": 4601},
            {"label": "Limite", "value": 4190},
            {"label": "Autorizações", "value": 3658},
            {"label": "Prog. Relacionamento", "value": 3134},
            {"label": "Manutenção Cartão", "value": 2535},
            {"label": "Retenção de Cartões", "value": 2233},
            {"label": "Protocolo", "value": 1391},
            {"label": "Massificado", "value": 1201},
        ],
        "status": [
            {"label": "Closed", "value": 33558},
            {"label": "Em atendimento", "value": 24823},
            {"label": "Fechado Com Sucesso", "value": 7809},
            {"label": "New", "value": 1398},
            {"label": "Protocolo Fechado", "value": 408},
            {"label": "InAnalysis", "value": 205},
            {"label": "Rejeitado", "value": 18},
            {"label": "Erro envio CSU", "value": 3},
        ],
        "priority": [
            {"label": "Normal", "value": 52209},
            {"label": "Ultra", "value": 16009},
            {"label": "UrgenteRechamada", "value": 4},
        ],
        "creation_type": [
            {"label": "Manual", "value": 44063},
            {"label": "Automático", "value": 24159},
        ],
        "quality": [
            {"label": "Manual", "value": 25338},
            {"label": "Automático", "value": 167},
        ],
        "sla": {
            "median_total": 0,
            "mean_manual": 10.6,
            "mean_automatic": 0,
            "sample_size": 2000
        },
        "success": False
    }


def save_json_files(data):
    """Salva dados estruturados em JSON único para consumo do dashboard"""

    output_dir = Path("docs/data")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Criar JSON único com todos os dados estruturados
    dashboard_data = {
        "lastSync": datetime.utcnow().isoformat() + "Z",
        "isLive": data.get("success", False),
        "summary": data.get("summary", {}),
        "categories": data.get("categories", []),
        "status": data.get("status", []),
        "priority": data.get("priority", []),
        "creationType": data.get("creation_type", []),
        "quality": data.get("quality", []),
        "sla": data.get("sla", {})
    }

    # Salvar arquivo único
    with open(output_dir / "dashboard.json", "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
    logger.info("✅ Salvou dashboard.json")

    # Manter metadata.json para compatibilidade
    metadata = {
        "lastSync": dashboard_data["lastSync"],
        "status": "success" if data.get("success") else "fallback",
        "isLive": data.get("success", False),
        "summary": {
            "total_cases": data.get("summary", {}).get("total_cases", 0),
            "manual_cases": data.get("summary", {}).get("manual_cases", 0),
            "automatic_cases": data.get("summary", {}).get("automatic_cases", 0),
            "closed_cases": data.get("summary", {}).get("closed_cases", 0),
            "no_category": data.get("summary", {}).get("no_category", 0),
        }
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
