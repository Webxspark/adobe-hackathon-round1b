import os
import json
import re
from pathlib import Path
import fitz  # PyMuPDF
from typing import List, Dict, Any, Tuple
from datetime import datetime
import argparse

def extract_text_from_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """Extract text sections from PDF with page information"""
    sections = []
    
    try:
        doc = fitz.open(pdf_path)
        
        # Simple approach: extract text from each page and create sections
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get plain text first
            text = page.get_text()
            lines = text.split('\n')
            
            # Filter out empty lines and clean text
            meaningful_lines = []
            for line in lines:
                line = line.strip()
                if len(line) > 10 and not line.isdigit():  # Skip page numbers and short lines
                    meaningful_lines.append(line)
            
            if meaningful_lines:
                # Create sections based on meaningful content blocks
                current_section = ""
                current_content = []
                
                for line in meaningful_lines:
                    # Heuristic for section headers (shorter lines, title case, etc.)
                    if (len(line) < 100 and 
                        (line.istitle() or line.isupper() or 
                         any(keyword in line.lower() for keyword in ['chapter', 'section', 'guide', 'overview', 'introduction']))):
                        
                        # Save previous section if exists
                        if current_section and current_content:
                            sections.append({
                                "title": current_section,
                                "page": page_num + 1,
                                "content": " ".join(current_content)
                            })
                        
                        # Start new section
                        current_section = line
                        current_content = []
                    else:
                        current_content.append(line)
                
                # Add final section
                if current_section and current_content:
                    sections.append({
                        "title": current_section,
                        "page": page_num + 1,
                        "content": " ".join(current_content)
                    })
                elif not current_section and current_content:
                    # If no clear header found, use page content as section
                    sections.append({
                        "title": f"Page {page_num + 1} Content",
                        "page": page_num + 1,
                        "content": " ".join(current_content)
                    })
        
        doc.close()
        
        # If no sections found through header detection, create page-based sections
        if not sections:
            doc = fitz.open(pdf_path)
            for page_num in range(min(3, len(doc))):  # First 3 pages only
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    # Take first meaningful line as title
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    if lines:
                        title = lines[0][:100] if len(lines[0]) > 10 else f"Page {page_num + 1}"
                        content = " ".join(lines[1:])[:500]  # Limit content
                        
                        sections.append({
                            "title": title,
                            "page": page_num + 1,
                            "content": content
                        })
            doc.close()
        
        return sections
    
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {str(e)}")
        return []

def analyze_relevance(sections: List[Dict[str, Any]], persona: str, job_description: str) -> List[Dict[str, Any]]:
    """Analyze sections for relevance to persona and job"""
    
    # Define keyword mappings for different personas
    persona_keywords = {
        "travel planner": ["trip", "travel", "visit", "tourist", "guide", "destination", "itinerary", "booking", "hotel", "restaurant", "attractions", "activities"],
        "hr professional": ["forms", "employee", "onboarding", "compliance", "policy", "procedure", "management", "workflow", "documentation", "training"],
        "food contractor": ["recipe", "menu", "cooking", "food", "ingredient", "meal", "dining", "catering", "buffet", "vegetarian", "preparation"]
    }
    
    # Define job-specific keywords
    job_keywords = []
    if "trip" in job_description.lower() or "travel" in job_description.lower():
        job_keywords.extend(["itinerary", "schedule", "planning", "group", "friends", "activities"])
    if "forms" in job_description.lower() or "fillable" in job_description.lower():
        job_keywords.extend(["pdf", "form", "fill", "sign", "create", "template"])
    if "menu" in job_description.lower() or "buffet" in job_description.lower():
        job_keywords.extend(["vegetarian", "corporate", "dinner", "meal", "buffet", "gathering"])
    
    relevant_sections = []
    
    for section in sections:
        score = 0
        content_lower = (section["title"] + " " + section.get("content", "")).lower()
        
        # Score based on persona keywords
        persona_key = persona.lower()
        if persona_key in persona_keywords:
            for keyword in persona_keywords[persona_key]:
                score += content_lower.count(keyword) * 2
        
        # Score based on job keywords
        for keyword in job_keywords:
            score += content_lower.count(keyword) * 3
        
        # Length bonus for substantial content
        if len(section.get("content", "")) > 100:
            score += 1
        
        if score > 0:
            section["relevance_score"] = score
            relevant_sections.append(section)
    
    # Sort by relevance score and return top sections
    relevant_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
    return relevant_sections[:20]  # Return top 20 relevant sections

def process_collection(collection_path: Path) -> Dict[str, Any]:
    """Process a single collection directory"""
    
    # Load input configuration
    input_file = collection_path / "challenge1b_input.json"
    if not input_file.exists():
        print(f"Input file not found: {input_file}")
        return {}
    
    with open(input_file, 'r', encoding='utf-8') as f:
        input_config = json.load(f)
    
    # Extract configuration
    challenge_info = input_config.get("challenge_info", {})
    documents = input_config.get("documents", [])
    persona_data = input_config.get("persona", {})
    job_data = input_config.get("job_to_be_done", {})
    
    persona = persona_data.get("role", "Unknown")
    job_description = job_data.get("task", "") if isinstance(job_data, dict) else str(job_data)
    
    # Process PDFs
    pdf_dir = collection_path / "PDFs"
    all_sections = []
    processed_docs = []
    
    for doc_info in documents:
        filename = doc_info["filename"]
        pdf_path = pdf_dir / filename
        
        if pdf_path.exists():
            print(f"Processing {filename}...")
            sections = extract_text_from_pdf(pdf_path)
            
            # Add document info to sections
            for section in sections:
                section["document"] = filename
            
            all_sections.extend(sections)
            processed_docs.append(filename)
        else:
            print(f"PDF not found: {pdf_path}")
    
    # Analyze relevance
    relevant_sections = analyze_relevance(all_sections, persona, job_description)
    
    # Prepare output structure
    extracted_sections = []
    subsection_analysis = []
    
    for i, section in enumerate(relevant_sections[:10]):  # Top 10 sections
        extracted_sections.append({
            "document": section["document"],
            "section_title": section["title"],
            "importance_rank": i + 1,
            "page_number": section["page"]
        })
        
        subsection_analysis.append({
            "document": section["document"],
            "refined_text": section.get("content", "")[:300] + "..." if len(section.get("content", "")) > 300 else section.get("content", ""),
            "page_number": section["page"]
        })
    
    # Build final output
    output = {
        "metadata": {
            "input_documents": processed_docs,
            "persona": persona,
            "job_to_be_done": job_description,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis[:5]  # Top 5 for detailed analysis
    }
    
    return output

def main():
    """Main function to process collections"""
    parser = argparse.ArgumentParser(description='Process PDF collections for Challenge 1b')
    parser.add_argument('--collection', type=str, help='Specific collection to process')
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent
    
    if args.collection:
        # Process specific collection
        collection_path = base_dir / args.collection
        if collection_path.exists():
            print(f"Processing collection: {args.collection}")
            result = process_collection(collection_path)
            
            output_file = collection_path / "challenge1b_output.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            
            print(f"Output saved to: {output_file}")
        else:
            print(f"Collection not found: {collection_path}")
    else:
        # Process all collections
        collections = ["Collection 1", "Collection 2", "Collection 3"]
        
        for collection_name in collections:
            collection_path = base_dir / collection_name
            if collection_path.exists():
                print(f"\nProcessing {collection_name}...")
                result = process_collection(collection_path)
                
                output_file = collection_path / "challenge1b_output.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
                
                print(f"Output saved to: {output_file}")
                print(f"Processed {len(result.get('extracted_sections', []))} sections")

if __name__ == "__main__":
    main()
