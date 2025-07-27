# Challenge 1b: Multi-Collection PDF Analysis

## Overview
Advanced PDF analysis solution that processes multiple document collections and extracts relevant content based on specific personas and use cases.

## Project Structure
```
Challenge_1b/
├── Collection 1/                    # Travel Planning
│   ├── PDFs/                       # South of France guides
│   ├── challenge1b_input.json      # Input configuration
│   └── challenge1b_output.json     # Analysis results
├── Collection 2/                    # Adobe Acrobat Learning
│   ├── PDFs/                       # Acrobat tutorials
│   ├── challenge1b_input.json      # Input configuration
│   └── challenge1b_output.json     # Analysis results
├── Collection 3/                    # Recipe Collection
│   ├── PDFs/                       # Cooking guides
│   ├── challenge1b_input.json      # Input configuration
│   └── challenge1b_output.json     # Analysis results
├── Dockerfile                       # Docker configuration
├── process_collections.py          # Main processing script
├── approach_explanation.md         # Methodology explanation
└── README.md                       # This documentation
```

## Collections

### Collection 1: Travel Planning
- **Challenge ID**: round_1b_002
- **Persona**: Travel Planner
- **Task**: Plan a 4-day trip for 10 college friends to South of France
- **Documents**: 7 travel guides

### Collection 2: Adobe Acrobat Learning
- **Challenge ID**: round_1b_003
- **Persona**: HR Professional
- **Task**: Create and manage fillable forms for onboarding and compliance
- **Documents**: 15 Acrobat guides

### Collection 3: Recipe Collection
- **Challenge ID**: round_1b_001
- **Persona**: Food Contractor
- **Task**: Prepare vegetarian buffet-style dinner menu for corporate gathering
- **Documents**: 9 cooking guides

## Docker Commands

### Build Command
```bash
docker build --platform linux/amd64 -t <reponame.someidentifier> .
```

### Run Command
```bash
docker run --rm <reponame.someidentifier>
```

### View Output Files
```bash
# Copy outputs from container to view results
docker run --name temp-container <reponame.someidentifier>
docker cp temp-container:"/app/Collection 1/challenge1b_output.json" ./collection1_output.json
docker cp temp-container:"/app/Collection 2/challenge1b_output.json" ./collection2_output.json
docker cp temp-container:"/app/Collection 3/challenge1b_output.json" ./collection3_output.json
docker rm temp-container

# View the results
cat collection1_output.json | python3 -m json.tool
```

## Input/Output Format

### Input JSON Structure
```json
{
  "challenge_info": {
    "challenge_id": "round_1b_XXX",
    "test_case_name": "specific_test_case"
  },
  "documents": [{"filename": "doc.pdf", "title": "Title"}],
  "persona": {"role": "User Persona"},
  "job_to_be_done": {"task": "Use case description"}
}
```

### Output JSON Structure
```json
{
  "metadata": {
    "input_documents": ["list"],
    "persona": "User Persona",
    "job_to_be_done": "Task description"
  },
  "extracted_sections": [
    {
      "document": "source.pdf",
      "section_title": "Title",
      "importance_rank": 1,
      "page_number": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "source.pdf",
      "refined_text": "Content",
      "page_number": 1
    }
  ]
}
```

## Technical Implementation

### Core Processing (`process_collections.py`)
- **PDF Text Extraction**: Uses PyMuPDF for robust document processing
- **Persona-Driven Analysis**: Keyword-based relevance scoring for different user roles
- **Content Prioritization**: Ranks sections by importance to specific personas and tasks
- **Structured Output**: Generates compliant JSON format for all collections

### Libraries Used
- **PyMuPDF (1.24.14)**: PDF processing and text extraction
- **Python 3.10**: Core runtime environment
- **pathlib, json**: File handling and data processing

### Performance
- **Processing Time**: ~2 seconds for all 3 collections
- **Docker Image Size**: ~200MB
- **Memory Usage**: <500MB
- **CPU Only**: No GPU dependencies required

## Key Features
- Persona-based content analysis
- Importance ranking of extracted sections
- Multi-collection document processing
- Structured JSON output with metadata
- Fully containerized solution
- Meets all technical constraints (≤60s, ≤1GB, CPU-only)

---

**Note**: This solution processes all three collections automatically and generates `challenge1b_output.json` files in each Collection directory.
