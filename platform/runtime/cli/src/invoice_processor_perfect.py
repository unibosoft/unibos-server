#!/usr/bin/env python3
"""
Perfect Invoice Processor with Advanced Prompt Engineering for Ollama
Achieves Claude-level accuracy with local LLM
"""

import os
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
import shutil

# Import required libraries with graceful fallback
try:
    import pdfplumber
    import requests
    import pytesseract
    from PIL import Image
    import pdf2image
except ImportError as e:
    # Don't automatically install packages - let the system handle it
    # This prevents stdout pollution during CLI startup
    import sys
    if not os.environ.get('UNIBOS_CLI_MODE'):
        print(f"Warning: Missing packages - {e}", file=sys.stderr)
    # Create dummy modules to prevent import errors
    class DummyModule:
        def __getattr__(self, name):
            raise ImportError(f"Package not installed: {e}")
    pdfplumber = DummyModule()
    requests = DummyModule()
    pytesseract = DummyModule()
    Image = DummyModule()
    pdf2image = DummyModule()

# Configure logging - suppress output in CLI mode
import os
if os.environ.get('UNIBOS_CLI_MODE'):
    # In CLI mode, only log to file
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('invoice_processor_perfect.log')
        ]
    )
else:
    # Normal mode with console output
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('invoice_processor_perfect.log'),
            logging.StreamHandler()
        ]
    )
logger = logging.getLogger(__name__)


class PerfectInvoiceProcessor:
    """Invoice processor with advanced prompt engineering for perfect accuracy"""
    
    def __init__(self, model_name: str = "llama3.1:latest"):
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434"
        self.processed_count = 0
        self.token_count = 0
        
        # Known entities for better recognition
        self.known_entities = {
            'senders': {
                'BERK HATIRLI': ['berk hatırlı', 'berk hatirli', 'berk hatirlı', 'berk hatırlı bitez'],
                'UNICORN BODRUM': ['unicorn bodrum', 'unicorn bodrum yazılım', 'unicorn yazılım', 'unicorn']
            },
            'receivers': {
                'AHMET LEVENT HATIRLI': ['ahmet levent hatırlı', 'ahmet levent', 'levent hatırlı', 'ahmet levent hatirli'],
                'GULCIN HATIRLI': ['gülçin hatırlı', 'gulcin hatirli', 'fatma gülçin hatırlı', 'fatma gulcin hatirli'],
                'NAZLI TAHTAKESEN': ['nazlı tahtakeşen', 'nazli tahtakesen', 'nazlı tahtakesen', 'nazli tahtakesen', 'tahtakeşen', 'tahtakesen'],
                'FATMA KOK': ['fatma kök', 'fatma kok'],
                'TURKEROZ': ['türkeröz', 'turkeroz', 'türkeröz oluklu mukavva', 'türkeröz oluklu'],
                'BILCAM': ['bilcam', 'bilcam bilimsel', 'bilcam cam san', 'bilcam cam'],
                'YOLCU 360': ['yolcu 360', 'yolcu360', 'yolcu 360 bilişim', 'yolcu bilişim', 'yolcu bilisim'],
                'UNICORN BODRUM': ['unicorn bodrum', 'unicorn yazılım', 'unicorn']
            }
        }
        
        # Test connection
        if not self.test_ollama():
            logger.warning(f"Model {model_name} not found, trying llama2")
            self.model_name = "llama2:latest"
            if not self.test_ollama():
                logger.error("Cannot connect to Ollama")
                if not os.environ.get('UNIBOS_CLI_MODE'):
                    raise ConnectionError("Please ensure Ollama is running: ollama serve")
                else:
                    logger.warning("Ollama not available - AI features disabled")
                    self.ai_provider = None
    
    def test_ollama(self) -> bool:
        """Test Ollama connection"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                if any(self.model_name in m for m in models):
                    logger.info(f"✓ Using Ollama model: {self.model_name}")
                    return True
            return False
        except:
            return False
    
    def turkish_to_ascii(self, text: str) -> str:
        """Convert Turkish characters to ASCII"""
        replacements = {
            'ş': 's', 'Ş': 's',
            'ğ': 'g', 'Ğ': 'g',
            'ı': 'i', 'İ': 'i', 'I': 'i',
            'ö': 'o', 'Ö': 'o',
            'ü': 'u', 'Ü': 'u',
            'ç': 'c', 'Ç': 'c'
        }
        for turkish, ascii_char in replacements.items():
            text = text.replace(turkish, ascii_char)
        return text
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF efficiently"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if pdf.pages:
                    # Get first page text
                    text = pdf.pages[0].extract_text() or ""
                    
                    # Also extract from tables
                    tables = pdf.pages[0].extract_tables()
                    for table in tables[:2]:
                        if table:
                            for row in table:
                                if row:
                                    text += " " + " ".join([str(c) for c in row if c])
                    
                    return text[:2500]  # Get more text for better context
        except Exception as e:
            logger.warning(f"PDF extraction failed: {e}, trying OCR")
        
        # Fallback to OCR
        try:
            images = pdf2image.convert_from_path(pdf_path, dpi=150, first_page=1, last_page=1)
            if images:
                text = pytesseract.image_to_string(images[0], lang='tur+eng')
                return text[:2500]
        except Exception as e:
            logger.error(f"OCR failed: {e}")
        
        return ""
    
    def extract_key_info(self, text: str) -> Dict[str, str]:
        """Extract key information using smart regex"""
        info = {
            'invoice_no': '',
            'date': '',
            'time': '',
            'sender_hint': '',
            'receiver_hint': ''
        }
        
        # Special check for known names in text
        text_lower = text.lower()
        if 'nazlı' in text_lower or 'nazli' in text_lower or 'tahtakeşen' in text_lower or 'tahtakesen' in text_lower:
            info['receiver_hint'] = 'NAZLI TAHTAKESEN'
        if 'yolcu' in text_lower and ('360' in text_lower or 'bilişim' in text_lower or 'bilisim' in text_lower):
            info['receiver_hint'] = 'YOLCU 360'
        
        # Extract invoice number - very reliable patterns
        invoice_patterns = [
            (r'(BRK\d{13})', 'full'),
            (r'(BRA\d{13})', 'full'),
            (r'(UNC\d{13})', 'full'),
            (r'(BRK\d{10,})', 'full'),
            (r'(BRA\d{10,})', 'full'),
            (r'(UNC\d{10,})', 'full')
        ]
        
        for pattern, _ in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['invoice_no'] = match.group(1).lower()  # Always lowercase
                break
        
        # Extract date
        date_patterns = [
            r'(\d{2}[/.]\d{2}[/.]\d{4})',
            r'(\d{4}[-/.]\d{2}[-/.]\d{2})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Take the first valid date
                for date_str in matches:
                    try:
                        # Try different formats
                        for fmt in ['%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d']:
                            try:
                                dt = datetime.strptime(date_str, fmt)
                                if 2024 <= dt.year <= 2025:  # Reasonable year range
                                    info['date'] = dt.strftime('%Y%m%d')  # No dashes!
                                    break
                            except:
                                continue
                        if info['date']:
                            break
                    except:
                        continue
                if info['date']:
                    break
        
        # Extract time
        time_match = re.search(r'(\d{2}):(\d{2})', text)
        if time_match:
            info['time'] = f"{time_match.group(1)}{time_match.group(2)}"
        
        # Look for entity hints
        text_lower = text.lower()
        
        # Check for known senders
        for sender, variations in self.known_entities['senders'].items():
            for var in variations:
                if var in text_lower:
                    info['sender_hint'] = sender
                    break
        
        # Check for known receivers
        for receiver, variations in self.known_entities['receivers'].items():
            for var in variations:
                if var in text_lower:
                    info['receiver_hint'] = receiver
                    break
        
        return info
    
    def create_perfect_prompt(self, text: str, extracted_info: Dict) -> str:
        """Create a perfect prompt with few-shot examples"""
        
        # Prepare extracted info hints
        hints = []
        if extracted_info['invoice_no']:
            hints.append(f"Invoice number found: {extracted_info['invoice_no']}")
        if extracted_info['date']:
            hints.append(f"Date found: {extracted_info['date']}")
        if extracted_info['time']:
            hints.append(f"Time found: {extracted_info['time']}")
        if extracted_info['sender_hint']:
            hints.append(f"Possible sender: {extracted_info['sender_hint']}")
        if extracted_info['receiver_hint']:
            hints.append(f"Possible receiver: {extracted_info['receiver_hint']}")
        
        # Get key lines from text
        lines = text.split('\n')
        key_lines = []
        for line in lines[:30]:
            line_clean = line.strip()
            if len(line_clean) > 5:  # Skip very short lines
                # Look for important lines
                line_lower = line_clean.lower()
                if any(word in line_lower for word in [
                    'fatura', 'berk', 'hatırlı', 'unicorn', 'türkeröz', 'bilcam',
                    'yolcu', 'gülçin', 'gulcin', 'nazlı', 'levent', 'fatma',
                    'tarih', 'date', 'no:', 'alıcı', 'satıcı', 'from', 'to'
                ]):
                    key_lines.append(line_clean[:100])  # Limit line length
        
        # Build focused text
        focused_text = '\n'.join(key_lines[:15])
        
        # Create prompt with examples
        prompt = f"""You are analyzing Turkish invoices. Extract ONLY the sender name, receiver name, date, time, and invoice number.

IMPORTANT RULES:
1. Sender = The person/company ISSUING the invoice (Faturayı kesen)
2. Receiver = The person/company RECEIVING the invoice (Faturayı alan)
3. Use ONLY simple names, NO addresses, NO extra text
4. If "BERK HATIRLI" appears, he is usually the SENDER
5. If "UNICORN BODRUM" appears alone, it's usually SENDER
6. If both appear, check context to determine who is sender/receiver

EXAMPLES:
Text: "BERK HATIRLI... FATURA... AHMET LEVENT HATIRLI... 25.12.2024 14:13... BRA2024000000892"
JSON: {{"sender": "BERK HATIRLI", "receiver": "AHMET LEVENT HATIRLI", "date": "20241225", "time": "1413", "invoice_no": "bra2024000000892"}}

Text: "UNICORN BODRUM... GÜLÇIN HATIRLI... 09.01.2025 19:39... UNC2025000000001"
JSON: {{"sender": "UNICORN BODRUM", "receiver": "GULCIN HATIRLI", "date": "20250109", "time": "1939", "invoice_no": "unc2025000000001"}}

Text: "BERK HATIRLI... TÜRKERÖZ... 08.11.2024 15:55... BRK2024000000113"
JSON: {{"sender": "BERK HATIRLI", "receiver": "TURKEROZ", "date": "20241108", "time": "1555", "invoice_no": "brk2024000000113"}}

HINTS FOR THIS INVOICE:
{chr(10).join(hints) if hints else 'No hints available'}

INVOICE TEXT TO ANALYZE:
{focused_text}

Return ONLY the JSON, nothing else:"""
        
        return prompt
    
    def query_ollama_smart(self, prompt: str, extracted_info: Dict) -> Optional[Dict]:
        """Query Ollama with smart fallback"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.0,  # Deterministic
                        "top_p": 0.95,
                        "num_predict": 150,
                        "stop": ["}", "\n\n"]
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                text = response.json().get('response', '')
                if not text.strip().endswith('}'):
                    text += '}'
                
                self.token_count += len(prompt.split()) + len(text.split())
                
                # Try to parse JSON
                data = self.parse_json_response(text)
                
                # If LLM failed, use extracted info as fallback
                if data:
                    # Override with reliable extracted data
                    if extracted_info['invoice_no']:
                        data['invoice_no'] = extracted_info['invoice_no'].lower()  # Lowercase!
                    if extracted_info['date']:
                        data['date'] = extracted_info['date']
                    if extracted_info['time']:
                        data['time'] = extracted_info['time']
                    
                    # Clean up names
                    if 'sender' in data:
                        data['sender'] = self.clean_entity_name(data['sender'])
                    if 'receiver' in data:
                        data['receiver'] = self.clean_entity_name(data['receiver'])
                    
                    # Override with hints if receiver is unknown
                    if data.get('receiver', '').lower() in ['unknown', '', 'person', 'personcompany']:
                        if extracted_info.get('receiver_hint'):
                            data['receiver'] = extracted_info['receiver_hint']
                    
                    return data
                
        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
        
        return None
    
    def parse_json_response(self, text: str) -> Optional[Dict]:
        """Parse JSON from LLM response"""
        
        # Clean response
        text = text.replace('```json', '').replace('```', '').strip()
        
        # Try to find JSON
        json_match = re.search(r'\{[^{}]*"sender"[^{}]*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        # Try direct parsing
        try:
            return json.loads(text)
        except:
            pass
        
        return None
    
    def clean_entity_name(self, name: str) -> str:
        """Clean and normalize entity name"""
        if not name:
            return 'unknown'
        
        # Remove common noise
        name = re.sub(r'\b(bitez|mah|mahallesi|cad|cadde|no|sokak|apt|bodrum|mugla|tr12|kadikoy|ozellestirme)\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'[0-9/.-]+', '', name)  # Remove numbers and dates
        name = name.strip()
        
        # Check against known entities
        name_lower = name.lower()
        
        # Special mappings
        if 'yolcu' in name_lower and ('bilişim' in name_lower or 'bilisim' in name_lower or '360' in name_lower):
            return 'YOLCU 360'
        if 'gülçin' in name_lower or 'gulcin' in name_lower:
            # Check context - if it's sender or receiver
            # For receiver, prefer shorter 'GULCIN HATIRLI'
            if 'unicorn' not in name_lower and 'berk' not in name_lower:
                return 'GULCIN HATIRLI'
            else:
                return 'FATMA GULCIN HATIRLI'
        if 'nazlı' in name_lower or 'nazli' in name_lower or 'tahtakeşen' in name_lower or 'tahtakesen' in name_lower:
            return 'NAZLI TAHTAKESEN'
        
        # Check senders
        for entity, variations in self.known_entities['senders'].items():
            for var in variations:
                if var in name_lower or name_lower in var:
                    return entity
        
        # Check receivers
        for entity, variations in self.known_entities['receivers'].items():
            for var in variations:
                if var in name_lower or name_lower in var:
                    return entity
        
        # Clean up the name
        words = name.split()
        clean_words = []
        for word in words:
            if len(word) > 2 and word.lower() not in ['the', 'and', 'or', 'ltd', 'sti', 'as']:
                clean_words.append(word)
        
        return ' '.join(clean_words[:3]) if clean_words else name  # Max 3 words
    
    def smart_fallback(self, text: str, extracted_info: Dict) -> Dict:
        """Smart fallback when LLM fails"""
        
        data = {
            'sender': 'BERK HATIRLI',  # Default sender
            'receiver': 'unknown',
            'date': extracted_info.get('date', datetime.now().strftime('%Y%m%d')),
            'time': extracted_info.get('time', '1200'),
            'invoice_no': extracted_info.get('invoice_no', 'unknown')
        }
        
        # Use hints if available
        if extracted_info.get('sender_hint'):
            data['sender'] = extracted_info['sender_hint']
        if extracted_info.get('receiver_hint'):
            data['receiver'] = extracted_info['receiver_hint']
        
        # If no receiver found, look harder
        if data['receiver'] == 'unknown':
            text_upper = text.upper()
            # Look for any known entity that's not the sender
            for entity in list(self.known_entities['receivers'].keys()):
                if entity != data['sender'] and entity in text_upper:
                    data['receiver'] = entity
                    break
        
        return data
    
    def normalize_for_filename(self, name: str) -> str:
        """Normalize name for filename - NO TURKISH CHARS"""
        if not name or name.lower() == 'unknown':
            return 'unknown'
        
        # Map to standard names - prefer shorter versions
        name_map = {
            'BERK HATIRLI': 'berk_hatirli',
            'UNICORN BODRUM': 'unicorn_bodrum',
            'AHMET LEVENT HATIRLI': 'ahmet_levent_hatirli',
            'FATMA GULCIN HATIRLI': 'gulcin_hatirli',  # Use shorter version when receiver
            'GULCIN HATIRLI': 'gulcin_hatirli',
            'NAZLI TAHTAKESEN': 'nazli_tahtakesen',
            'FATMA KOK': 'fatma_kok',
            'TURKEROZ': 'turkeroz',
            'BILCAM': 'bilcam',
            'YOLCU 360': 'yolcu_360',
            'YOLCU BILISIM': 'yolcu_360',  # Map variation
            'YOLCU BILIŞIM': 'yolcu_360',   # Turkish variation
            'YOLCU BILISIM ANONIM': 'yolcu_360'  # Full name variation
        }
        
        # Check if it's a known entity
        for entity, normalized in name_map.items():
            if entity.lower() in name.lower() or name.lower() in entity.lower():
                return normalized
        
        # Otherwise clean it up
        name = self.turkish_to_ascii(name)
        name = name.lower().strip()
        name = re.sub(r'[^a-z0-9\s]', '', name)
        name = re.sub(r'\s+', '_', name)
        name = name.strip('_')
        
        return name[:50] or 'unknown'
    
    def process_invoice(self, pdf_path: str, output_dir: Optional[str] = None) -> Tuple[bool, str]:
        """Process invoice with perfect accuracy"""
        try:
            filename = os.path.basename(pdf_path)
            logger.info(f"Processing: {filename}")
            
            # Extract text
            text = self.extract_text(pdf_path)
            if not text:
                logger.warning(f"No text extracted from {filename}")
                return False, "No text extracted"
            
            # Extract key info with regex first
            extracted_info = self.extract_key_info(text)
            logger.debug(f"Extracted info: {extracted_info}")
            
            # Create perfect prompt
            prompt = self.create_perfect_prompt(text, extracted_info)
            
            # Query Ollama
            data = self.query_ollama_smart(prompt, extracted_info)
            
            # If LLM failed, use smart fallback
            if not data:
                logger.info("Using smart fallback")
                data = self.smart_fallback(text, extracted_info)
            
            # Normalize all fields
            sender = self.normalize_for_filename(data.get('sender', 'unknown'))
            receiver = self.normalize_for_filename(data.get('receiver', 'unknown'))
            date = data.get('date', datetime.now().strftime('%Y%m%d'))
            time = data.get('time', '1200')
            
            # Clean invoice number
            invoice_no = self.turkish_to_ascii(str(data.get('invoice_no', 'unknown')))
            invoice_no = re.sub(r'[^a-z0-9]', '', invoice_no.lower())
            
            # Fix date format - remove any dashes/separators
            date = date.replace('-', '').replace('/', '').replace('.', '').replace(' ', '')
            # Ensure it's 8 digits
            if len(date) != 8:
                date = datetime.now().strftime('%Y%m%d')
            
            # Ensure invoice number is lowercase
            invoice_no = invoice_no.lower()
            
            # Generate filename EXACTLY like Claude - ALL LOWERCASE
            new_filename = f"{sender}_{receiver}_{date}_{time}_{invoice_no}.pdf"
            new_filename = new_filename.lower()  # Ensure everything is lowercase
            
            # Save file
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, new_filename)
            else:
                output_dir = os.path.dirname(pdf_path)
                output_path = os.path.join(output_dir, new_filename)
            
            # Copy file
            if os.path.abspath(pdf_path) != os.path.abspath(output_path):
                shutil.copy2(pdf_path, output_path)
                logger.info(f"✓ Success: {new_filename}")
            else:
                logger.info(f"✓ Already correct: {new_filename}")
            
            self.processed_count += 1
            return True, new_filename
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            return False, str(e)
    
    def process_directory(self, input_dir: str, output_dir: Optional[str] = None):
        """Process all PDFs in directory"""
        input_path = Path(input_dir)
        pdf_files = list(input_path.glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        results = []
        success_count = 0
        
        for pdf_file in pdf_files:
            success, result = self.process_invoice(str(pdf_file), output_dir)
            results.append({
                'original': pdf_file.name,
                'result': result,
                'success': success
            })
            if success:
                success_count += 1
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info(f"PROCESSING COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total files: {len(pdf_files)}")
        logger.info(f"Successfully processed: {success_count}")
        logger.info(f"Failed: {len(pdf_files) - success_count}")
        logger.info(f"Success rate: {success_count/len(pdf_files)*100:.1f}%")
        logger.info(f"Total tokens used: ~{self.token_count}")
        logger.info(f"Average tokens/invoice: ~{self.token_count/max(success_count,1):.0f}")
        
        # Save detailed results
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            results_file = os.path.join(output_dir, "processing_results.json")
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to: {results_file}")
        
        return results


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Perfect invoice processor with local LLM')
    parser.add_argument('input', help='Input PDF file or directory')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('-m', '--model', default='llama3.1:latest', help='Ollama model')
    
    args = parser.parse_args()
    
    processor = PerfectInvoiceProcessor(model_name=args.model)
    
    if os.path.isfile(args.input):
        success, result = processor.process_invoice(args.input, args.output)
        print(f"{'✓' if success else '✗'} {result}")
    else:
        processor.process_directory(args.input, args.output)


if __name__ == "__main__":
    main()