import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET
import re

def extract_text_from_xml(xml_string, pmc_id):
    """Try multiple strategies to extract text from XML"""
    paragraphs = []
    
    try:
        root = ET.fromstring(xml_string)
        
        # Strategy 1: Look for <body> section with <p> tags (standard JATS)
        body = root.find('.//body')
        if body is not None:
            for p in body.iter('p'):
                text = get_element_text(p)
                if text:
                    paragraphs.append(text)
        
        # Strategy 2: If no body, try <abstract> section
        if not paragraphs:
            abstract = root.find('.//abstract')
            if abstract is not None:
                for p in abstract.iter('p'):
                    text = get_element_text(p)
                    if text:
                        paragraphs.append(text)
        
        # Strategy 3: Look for <sec> (sections) anywhere in the document
        if not paragraphs:
            for sec in root.iter('sec'):
                for p in sec.iter('p'):
                    text = get_element_text(p)
                    if text:
                        paragraphs.append(text)
        
        # Strategy 4: Just find all <p> tags anywhere
        if not paragraphs:
            for p in root.iter('p'):
                text = get_element_text(p)
                if text:
                    paragraphs.append(text)
        
        return paragraphs
        
    except ET.ParseError:
        # Try to fix common XML issues
        return extract_from_broken_xml(xml_string, pmc_id)
    except Exception as e:
        print(f"  Error processing {pmc_id}: {e}")
        return []

def get_element_text(element):
    """Extract all text from an element including nested elements"""
    text_parts = [element.text or '']
    for child in element:
        text_parts.append(get_element_text(child))
        text_parts.append(child.tail or '')
    return ''.join(text_parts).strip()

def extract_from_broken_xml(xml_string, pmc_id):
    """Try to extract paragraphs from malformed XML using regex"""
    paragraphs = []
    
    # Look for <p>...</p> tags using regex
    p_pattern = r'<p[^>]*>(.*?)</p>'
    matches = re.findall(p_pattern, xml_string, re.DOTALL)
    
    for match in matches:
        # Remove any remaining XML tags
        text = re.sub(r'<[^>]+>', '', match)
        text = text.strip()
        if text and len(text) > 20:  # Ignore very short matches
            paragraphs.append(text)
    
    return paragraphs

# Read CSV
csv_file = 'SB_publication_PMC_with_bioc.csv'
df = pd.read_csv(csv_file)

print(f"Processing {len(df)} articles with enhanced extraction...\n")

# Create output directory
data_dir = Path('data')
data_dir.mkdir(exist_ok=True)

successful = 0
still_failed = 0
failed_ids = []

for idx, row in df.iterrows():
    pmc_id = row['PMC_ID']
    xml_string = row['BioC_XML']
    
    if idx % 100 == 0:
        print(f"Processing {idx+1}/{len(df)}...")
    
    # Skip if already exists
    txt_file = data_dir / f"{pmc_id}.txt"
    if txt_file.exists():
        successful += 1
        continue
    
    # Skip if no XML data
    if pd.isna(xml_string) or not xml_string.strip():
        still_failed += 1
        failed_ids.append(pmc_id)
        continue
    
    # Extract paragraphs with multiple strategies
    paragraphs = extract_text_from_xml(xml_string, pmc_id)
    
    if paragraphs:
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(paragraphs))
        successful += 1
    else:
        still_failed += 1
        failed_ids.append(pmc_id)

print(f"\n{'='*60}")
print(f"Final Results:")
print(f"Successfully extracted: {successful}/{len(df)}")
print(f"Still failed: {still_failed}/{len(df)}")
print(f"\nText files saved to: {data_dir}")

if failed_ids:
    with open('still_failed_ids.txt', 'w') as f:
        f.write('\n'.join(failed_ids))
    print(f"Saved {len(failed_ids)} failed IDs to: still_failed_ids.txt")