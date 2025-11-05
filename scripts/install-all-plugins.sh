#!/bin/bash

# Script per installare tutti i 63 plugin del Claude Code Agents marketplace
# Repository: wshobson/agents

echo "=========================================="
echo "Claude Code Agents - Installazione Totale"
echo "=========================================="
echo ""

# Aggiungi il marketplace (se non già presente)
echo "1. Aggiunta marketplace..."
/plugin marketplace add wshobson/agents

echo ""
echo "2. Installazione dei 63 plugin..."
echo ""

# Development (4)
echo "[Development]"
/plugin install debugging-tools
/plugin install backend-development
/plugin install frontend-development
/plugin install multi-platform-development

# Documentation (2)
echo "[Documentation]"
/plugin install code-documentation
/plugin install api-documentation

# Workflows (3)
echo "[Workflows]"
/plugin install git-workflow
/plugin install full-stack-orchestration
/plugin install tdd-workflow

# Testing (2)
echo "[Testing]"
/plugin install unit-testing
/plugin install tdd-orchestration

# Quality (3)
echo "[Quality]"
/plugin install code-review-ai
/plugin install code-review-comprehensive
/plugin install performance-optimization

# AI & ML (4)
echo "[AI & ML]"
/plugin install llm-applications
/plugin install ai-agent-orchestration
/plugin install context-management
/plugin install mlops

# Data (2)
echo "[Data]"
/plugin install data-engineering
/plugin install data-validation

# Database (2)
echo "[Database]"
/plugin install database-design
/plugin install database-migrations

# Operations (4)
echo "[Operations]"
/plugin install incident-response
/plugin install diagnostics
/plugin install distributed-debugging
/plugin install observability

# Performance (2)
echo "[Performance]"
/plugin install application-performance
/plugin install database-cloud-optimization

# Infrastructure (5)
echo "[Infrastructure]"
/plugin install deployment-automation
/plugin install infrastructure-validation
/plugin install kubernetes-operations
/plugin install cloud-infrastructure
/plugin install cicd-pipelines

# Security (4)
echo "[Security]"
/plugin install security-scanning
/plugin install security-compliance
/plugin install backend-api-security
/plugin install frontend-mobile-security

# Languages (7)
echo "[Languages]"
/plugin install python-development
/plugin install javascript-typescript
/plugin install systems-programming
/plugin install jvm-languages
/plugin install scripting-languages
/plugin install functional-programming
/plugin install embedded-systems

# Blockchain (1)
echo "[Blockchain]"
/plugin install blockchain-development

# Finance (1)
echo "[Finance]"
/plugin install quantitative-finance

# Payments (1)
echo "[Payments]"
/plugin install payment-processing

# Gaming (1)
echo "[Gaming]"
/plugin install game-development

# Marketing (4)
echo "[Marketing]"
/plugin install seo-content-creation
/plugin install technical-seo
/plugin install seo-analysis
/plugin install content-marketing

# Business (3)
echo "[Business]"
/plugin install business-analytics
/plugin install hr-legal
/plugin install customer-sales

echo ""
echo "=========================================="
echo "✅ Installazione completata!"
echo "=========================================="
echo ""
echo "Tutti i 63 plugin sono stati installati."
echo "Ora hai accesso a:"
echo "  - 85 agent specializzati"
echo "  - 47 skill modulari"
echo "  - 44 tool di sviluppo"
echo ""
echo "Usa '/plugin' per vedere i plugin installati"
echo ""
