#requests
#python-dotenv
#MONTE_CARLO_MCD_ID=01e7e9aaad3347469d76c65d3b96072f+djErdXMx
#MONTE_CARLO_MCD_TOKEN=DCrBeSRHDNQ7GV4ZYiCW9j5GDZTQmEnihxMr25nGcGM0uOQfQB2xRFhx

import os
from dotenv import load_dotenv
import requests
import json
from typing import Any, Dict, Optional

# Cargar variables de entorno
load_dotenv()

# Query (pegada tal cual). Puedes reducir/editar campos según necesites.
QUERY = r"""
query getAlerts($first: Int = 10, $cursor: String, $ids: [UUID!], $audienceIds: [UUID!], $hasJiraTickets: Boolean, $hasKeyAssets: Boolean, $hasServiceNowIncidents: Boolean, $hasOpsgenieIncidents: Boolean, $hasDatadogIncidents: Boolean, $hasAzureDevopsWorkItems: Boolean, $isNormalized: Boolean, $monitorIds: [UUID!], $monitorTags: [UUID!], $owners: [String], $priorities: [Priority], $severities: [Severity], $statuses: [AlertStatus], $subTypes: [AlertSubType!], $tableDatabases: [String!], $tableIds: [String!], $tableMcons: [String!], $tableSchemas: [String!], $tags: [TagKeyValuePairInput!], $types: [AlertType!], $domainIds: [UUID!], $dataProductIds: [UUID!], $orderBy: String = "-createdTime", $includeJiraTickets: Boolean = true, $includeServiceNowIncidents: Boolean = true, $includeOpsgenieIncidents: Boolean = true, $includeDatadogIncidents: Boolean = false, $includeAzureDevopsWorkItems: Boolean = false, $includeTotalCount: Boolean = false, $updatedTime: DateTimeRangeInput, $createdTime: DateTimeRangeInput, $excludeSubTypes: [AlertSubType!]) {
  getAlerts(
    ids: $ids
    first: $first
    after: $cursor
    createdTime: $createdTime
    updatedTime: $updatedTime
    orderBy: $orderBy
    filter: {include: {audienceIds: $audienceIds, hasJiraTickets: $hasJiraTickets, hasKeyAssets: $hasKeyAssets, hasServiceNowIncidents: $hasServiceNowIncidents, hasOpsgenieIncidents: $hasOpsgenieIncidents, hasDatadogIncidents: $hasDatadogIncidents, hasAzureDevopsWorkItems: $hasAzureDevopsWorkItems, isNormalized: $isNormalized, monitorIds: $monitorIds, monitorTags: $monitorTags, owners: $owners, priorities: $priorities, severities: $severities, statuses: $statuses, subTypes: $subTypes, tableDatabases: $tableDatabases, tableIds: $tableIds, tableMcons: $tableMcons, tableSchemas: $tableSchemas, tags: $tags, types: $types, domainIds: $domainIds, dataProductIds: $dataProductIds}, exclude: {subTypes: $excludeSubTypes}}
  ) {
    totalCount @include(if: $includeTotalCount)
    pageInfo {
      startCursor
      endCursor
      hasNextPage
      hasPreviousPage
      __typename
    }
    edges {
      node {
        id
        title
        type
        subTypes
        severity
        priority
        createdTime
        updatedTime
        status
        owner {
          email
          fullName
          __typename
        }
        tables {
          mcon
          tableId
          isKeyAsset
          __typename
        }
        jiraTickets @include(if: $includeJiraTickets) {
          id
          ticketKey
          ticketUrl
          createdAt
          createdBy {
            email
            fullName
            __typename
          }
          __typename
        }
        serviceNowIncidents @include(if: $includeServiceNowIncidents) {
          id
          incidentSysId
          createdAt
          originatesFromMcNotification
          incidentUrl
          __typename
        }
        opsgenieIncidents @include(if: $includeOpsgenieIncidents) {
          id
          tinyId
          alias
          alertId
          originatesFromMcNotification
          incidentUrl
          createdAt
          createdBy {
            email
            fullName
            __typename
          }
          integrationId
          __typename
        }
        datadogIncidents @include(if: $includeDatadogIncidents) {
          id
          incidentUrl
          createdAt
          integrationId
          displayName
          __typename
        }
        azureDevopsWorkItems @include(if: $includeAzureDevopsWorkItems) {
          id
          workItemId
          workItemType
          workItemUrl
          project
          createdAt
          createdBy {
            email
            fullName
            __typename
          }
          integrationId
          originatesFromMcNotification
          __typename
        }
        audiences {
          uuid
          label
          __typename
        }
        monitorTags {
          name
          value
          __typename
        }
        invalidRows
        domains {
          uuid
          name
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
}
"""

def run_query(endpoint: str, token: Optional[str], variables: Dict[str, Any]) -> Dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    # cabeceras adicionales requeridas y credenciales desde variables de entorno
    headers["x-mcd-id"] = os.getenv("MONTE_CARLO_MCD_ID")
    headers["x-mcd-token"] = os.getenv("MONTE_CARLO_MCD_TOKEN")
    print(headers)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    payload = {"query": QUERY, "variables": variables}
    resp = requests.post(endpoint, json=payload, headers=headers, timeout=30)
    print(f"Status code: {resp.status_code}")
    resp.raise_for_status()
    data = resp.json()
    print(resp.json())
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data.get("data", {})

def fetch_all_alerts(endpoint: str, token: Optional[str], vars_base: Dict[str, Any]):
    cursor = None
    all_nodes = []
    while True:
        vars_page = dict(vars_base)
        vars_page["cursor"] = cursor
        print("llegando a fetch_all_alerts")
        resp_data = run_query(endpoint, token, vars_page)
        page = resp_data.get("getAlerts", {})
        edges = page.get("edges", [])
        for e in edges:
            all_nodes.append(e.get("node"))
        page_info = page.get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
    return all_nodes

if __name__ == "__main__":
    # URL fija de la API
    endpoint = "https://graphql.getmontecarlo.com/graphql"
    token = None  # No necesitamos token ya que usamos x-mcd-id y x-mcd-token en headers

    variables = {
        "first": 20,
        "orderBy": "-createdTime",
        "includeJiraTickets": True,
        "includeServiceNowIncidents": True,
        "includeOpsgenieIncidents": True,
        "includeDatadogIncidents": True,
        "includeTotalCount": True,
        "createdTime": {
            "after": "2025-07-01T05:00:00.000Z",
            "before": "2025-08-01T04:59:59.999Z"
        },
        "updatedTime": None,
        "domainIds": None
    }

    alerts = fetch_all_alerts(endpoint, token, variables)
    print(f"Traídos {len(alerts)} alertas")
    # imprime primeras 3 para inspección
    print(json.dumps(alerts[:3], indent=2, default=str))
