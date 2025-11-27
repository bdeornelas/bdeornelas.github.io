---
name: medical-guidelines
description: Expert system for querying and extracting information from medical clinical guidelines with automatic source location and citation. Focuses on ESC (European Society of Cardiology) Guidelines.
version: 1.0.0
---

# Medical Guidelines Plugin

Intelligent query system for evidence-based medical guidelines with automated PDF location and citation extraction.

## Purpose

This plugin provides specialized agents and skills for:
- Querying ESC (European Society of Cardiology) clinical guidelines
- Automatically locating relevant information across multiple guideline PDFs
- Extracting exact citations with recommendation class/level
- Providing evidence-based clinical answers with proper source attribution

## Architecture

```
medical-guidelines/
├── PLUGIN.md (this file)
├── skills/
│   └── esc-guidelines-query/
│       └── SKILL.md (ESC Guidelines Query System)
└── agents/ (future)
    └── esc-expert.md (future ESC Guidelines Expert Agent)
```

## Available Skills

### esc-guidelines-query
Expert system for querying ESC Guidelines with automatic PDF location and citation extraction.

**Use when**:
- Answering clinical cardiovascular questions
- Finding ESC recommendations on specific conditions
- Extracting diagnostic or therapeutic guidelines
- Verifying treatment protocols against ESC standards

**Key Features**:
- 3-phase intelligent retrieval (Locate → Read → Cite)
- Automatic TOC analysis for PDF identification
- Exact citation extraction with page numbers
- Recommendation class/level inclusion
- Multi-guideline comparison support

## Data Sources

### ESC Guidelines Repository
- **Location**: `references/esc-guidelines/`
- **Index**: `ESC_GUIDELINES_TOC.md` (Master table of contents)
- **Coverage**: 2020-2025 ESC Guidelines
- **Total Guidelines**: ~50+ comprehensive cardiovascular guidelines

### Available Guidelines (2024)
- Atrial Fibrillation
- Chronic Coronary Syndromes
- Hypertension
- Peripheral Arterial & Aortic Diseases

### Available Guidelines (2023)
- Acute Coronary Syndromes
- Cardiomyopathies
- Cardiovascular Disease & Diabetes
- Endocarditis

### Available Guidelines (2022)
- Cardio-oncology
- Valvular Heart Disease
- Pulmonary Hypertension
- Ventricular Arrhythmias

### Available Guidelines (2021)
- Heart Failure
- Pacing & Cardiac Resynchronization Therapy
- Cardiovascular Disease Prevention

### Available Guidelines (2020)
- Adult Congenital Heart Disease
- Sports Cardiology
- Non-ST Elevation ACS
- Atrial Fibrillation (previous version)

## Usage Examples

### Example 1: Diagnostic Criteria
```markdown
User: "Quali sono i criteri ESC per diagnosi di stenosi aortica severa?"

Response includes:
- Exact diagnostic thresholds
- Echo criteria (AVA, mean gradient, Vmax)
- ESC recommendation class/level
- Source: 2022_Valvular_Heart_Disease.pdf, Section X, p. Y
```

### Example 2: Treatment Thresholds
```markdown
User: "A che diametro si opera l'aorta ascendente?"

Response includes:
- Surgical thresholds (general: ≥55mm, bicuspid valve: ≥50mm, Marfan: ≥50mm)
- Recommendation class/level for each scenario
- Special population variations
- Source: 2024_Peripheral_Arterial_Aortic.pdf, Section 9.2.5.1
```

### Example 3: Imaging Recommendations
```markdown
User: "Quando fare TC vs RM per aneurisma aortico?"

Response includes:
- Comparison table of CT vs MRI indications
- First-line imaging recommendations
- Follow-up imaging protocols
- Source: 2024_Peripheral_Arterial_Aortic.pdf, Section 5.4
```

## Integration with Ultrathink Agents

This plugin is designed to work seamlessly with:

### Backend Development
- Building clinical decision support APIs
- Implementing guideline-based recommendation engines
- Creating medical data validation systems

### Frontend Development
- Developing clinical guideline browsers
- Building interactive decision trees
- Creating medical education platforms

### Data Engineering
- Processing medical guideline PDFs
- Building medical knowledge graphs
- Implementing clinical NLP pipelines

## Best Practices

1. **Always cite sources**: Include PDF name, section, and page number
2. **Include evidence level**: Recommendation class (I/IIa/IIb/III) and level (A/B/C)
3. **Provide context**: Mention patient-specific factors and special populations
4. **Cross-reference**: Check multiple related sections for comprehensive answers
5. **Quote exactly**: Don't paraphrase ESC recommendations

## Future Enhancements

- [ ] Add agents for specific ESC guideline domains
- [ ] Implement multi-guideline comparison workflows
- [ ] Add commands for guideline update tracking
- [ ] Create skills for evidence level interpretation
- [ ] Build guideline conflict resolution system
- [ ] Add support for other society guidelines (ACC/AHA, etc.)

## Clinical Disclaimer

This plugin is designed for **educational and reference purposes** only. All clinical recommendations should be verified against the official ESC Guidelines PDFs. Clinical decisions should be made by qualified healthcare professionals considering individual patient circumstances.

## Contribution Guidelines

When adding new skills or agents to this plugin:
1. Follow ESC recommendation formatting standards
2. Always include exact citations with page numbers
3. Maintain separation between guideline quotes and interpretation
4. Test against multiple ESC guideline PDFs
5. Document all data sources clearly

## Resources

- **ESC Guidelines**: https://www.escardio.org/Guidelines
- **Repository TOC**: `ESC_GUIDELINES_TOC.md`
- **PDF Directory**: `references/esc-guidelines/`

---

**Plugin maintained by**: Ultrathink Agents Framework
**Last updated**: 2025-11-27
**Version**: 1.0.0
