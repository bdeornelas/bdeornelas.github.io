#!/bin/bash

# Script to install all Claude Code plugins
# Run this with: bash scripts/install-plugins.sh

echo "Installing Claude Code plugins..."

# Development plugins
claude plugin install debugging-tools
claude plugin install backend-development
claude plugin install frontend-development
claude plugin install multi-platform-development

# Documentation plugins
claude plugin install code-documentation
claude plugin install api-documentation

# Workflow plugins
claude plugin install git-workflow
claude plugin install full-stack-orchestration
claude plugin install tdd-workflow

# Testing plugins
claude plugin install unit-testing
claude plugin install tdd-orchestration

# Quality plugins
claude plugin install code-review-ai
claude plugin install code-review-comprehensive
claude plugin install performance-optimization

# AI & ML plugins
claude plugin install llm-applications
claude plugin install ai-agent-orchestration
claude plugin install context-management
claude plugin install mlops

# Data plugins
claude plugin install data-engineering
claude plugin install data-validation

# Database plugins
claude plugin install database-design
claude plugin install database-migrations

# Operations plugins
claude plugin install incident-response
claude plugin install diagnostics
claude plugin install distributed-debugging
claude plugin install observability

# Performance plugins
claude plugin install application-performance
claude plugin install database-cloud-optimization

# Infrastructure plugins
claude plugin install deployment-automation
claude plugin install infrastructure-validation
claude plugin install kubernetes-operations
claude plugin install cloud-infrastructure
claude plugin install cicd-pipelines

# Security plugins
claude plugin install security-scanning
claude plugin install security-compliance
claude plugin install backend-api-security
claude plugin install frontend-mobile-security

# Language plugins
claude plugin install python-development
claude plugin install javascript-typescript
claude plugin install systems-programming
claude plugin install jvm-languages
claude plugin install scripting-languages
claude plugin install functional-programming
claude plugin install embedded-systems

# Blockchain & Finance plugins
claude plugin install blockchain-development
claude plugin install quantitative-finance
claude plugin install payment-processing

# Other plugins
claude plugin install game-development
claude plugin install seo-content-creation
claude plugin install technical-seo
claude plugin install seo-analysis
claude plugin install content-marketing
claude plugin install business-analytics
claude plugin install hr-legal
claude plugin install customer-sales

echo "All plugins installed successfully!"
