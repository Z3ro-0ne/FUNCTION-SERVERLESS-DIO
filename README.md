# Serverless Asynchronous Data Ingestion Pipeline (DIO Course Practice)

An event-driven, asynchronous data ingestion pipeline built on Microsoft Azure. The architecture decouples the HTTP ingestion layer from the database persistence layer to ensure high throughput, fault tolerance, and cost-efficient scaling.

## Architecture Overview

```text
[Postman / Client] 
       │ (HTTP POST)
       ▼
[Logic App: la-serverless-dio] 
       │ (Immediate 202 Accepted)
       ▼
[Service Bus Queue: incoming-payload] 
       │ (Message Buffer)
       ▼
[Azure Function: func-serverless-dio (Service Bus Trigger)]
       │ (Database Insertion via pyodbc)
       ▼
[Azure SQL Database: db-serverless-dio (UserActions Table)]
```

### Key Components
*   **Ingestion Layer:** Azure Logic App exposes a public HTTP endpoint, validates the JSON schema, and pushes payloads to the queue. It returns a `202 Accepted` response immediately.
*   **Message Broker:** Azure Service Bus holds messages securely, ensuring zero data loss if the downstream database experiences downtime.
*   **Compute Layer:** A Python-based Azure Function (V2 programming model) automatically scales out to process queued messages.
*   **Database Layer:** Azure SQL Database securely stores the structured user action events.

---

## Technical Specifications

### Data Payload Schema
```json
{
  "userId": 8,
  "name": "Maria",
  "action": "Logout"
}
```

### Database Schema
```sql
CREATE TABLE UserActions (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    UserId INT NOT NULL,
    Name NVARCHAR(100) NOT NULL,
    Action NVARCHAR(50) NOT NULL,
    CreatedAt DATETIME DEFAULT GETDATE()
);
```

---

## Prerequisites

*   Python 3.11 (Matching Azure Functions Linux runtime)
*   [Azure Functions Core Tools v4](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
*   [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
*   VS Code with the Azure Databases, Account, and Functions Extensions

---

## Local Development Setup

1.  **Clone the repository and navigate to the project directory:**
    ```bash
    cd function-serverless-dio
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Local Settings:**
    Create a `local.settings.json` file in the root directory (this file is git-ignored):
    ```json
    {
      "IsEncrypted": false,
      "Values": {
        "AzureWebJobsStorage": "UseDevelopmentStorage=true",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "ServiceBusConnection": "Endpoint=sb://sb-serverless-dio.servicebus.windows.net/...RootManageSharedAccessKey=...",
        "SqlConnectionString": "Driver={ODBC Driver 18 for SQL Server};Server=tcp:sql-serverless-dio.database.windows.net,1433;Database=db-serverless-dio;UID=dioadmin;PWD=YourActualPassword;Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
      }
    }
    ```
    *Note: Ensure the `SqlConnectionString` uses standard ODBC syntax (`Database` instead of `.NET`'s `Initial Catalog`) and includes `TrustServerCertificate=yes` for local development.*

5.  **Run the function app locally:**
    ```bash
    func start
    ```

---

## Deployment to Azure

1.  **Provision Resources:**
    Ensure the Logic App, Service Bus Namespace, SQL Server/Database, and Function App (Linux, Python 3.11, Consumption Plan) are provisioned under the resource group `dio-serverles-pratica`.

2.  **Configure App Settings in Azure:**
    Add the following environment variables under **Settings > Configuration** (or **Environment variables**) of your Azure Function App:
    *   `ServiceBusConnection`
    *   `SqlConnectionString` (same values used in local configuration)

3.  **Deploy from VS Code:**
    *   Open the Azure extension in VS Code.
    *   Under Resources, find your Function App `func-serverless-dio`.
    *   Right-click and select **Deploy to Function App...**
    *   Select the root project folder and confirm deployment. Ensure the build completes remotely.

---

## Troubleshooting & Learnings

*   **Error `IM002` (Driver Not Found):** Resolved by installing *ODBC Driver 18 for SQL Server* locally and ensuring the connection string `Driver={...}` value matches the system registry exactly.
*   **Error `28000` (Login Failed for User `''`):** Occurs when passing .NET parameters (`User Id` / `Password`) to Python's `pyodbc`. Standardize credentials as `UID` and `PWD` in the connection string.
*   **Error `42S02` (Invalid Object Name):** Occurs if the database defaults to `master`. Replaced `.NET`'s `Initial Catalog` parameter with the standard ODBC `Database` parameter to force the connection context directly into `db-serverless-dio`.
