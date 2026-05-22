# FastAPI Super Architecture - Clean Architecture + SOLID

## Istruzioni per GitHub Copilot

## 🏗️ **ARCHITETTURA PRINCIPALE**

### Gerarchia dei Layer (Dependency Rule)

## 🏗️ **ARCHITETTURA PRINCIPALE**

### Gerarchia dei Layer (Dependency Rule)

1. **Domain Layer** → Business Logic Pura (NO dipendenze esterne)
2. **Application Layer** → Use Cases, Orchestrazione (dipende solo da Domain)
3. **Infrastructure Layer** → Implementazioni concrete (dipende da Domain/Application)
4. **API Layer** → FastAPI endpoints (dipende da Application)

### FLUSSO DI DEPENDENCY:
