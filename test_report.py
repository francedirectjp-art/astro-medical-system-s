#!/usr/bin/env python3
"""
Test script to verify the 12,000+ character report generation
"""

import requests
import json
from datetime import datetime

# Test the report generation locally
def test_report_generation():
    # Base URL
    base_url = "http://localhost:5000"
    
    # Test data
    test_data = {
        'name': '山田 太郎',
        'birth_year': 1990,
        'birth_month': 4,
        'birth_day': 15,
        'birth_hour': 14,
        'birth_minute': 30,
        'prefecture': '東京都'
    }
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("Testing Astrology Medical Report Generation")
    print("=" * 50)
    print(f"Name: {test_data['name']}")
    print(f"Birth: {test_data['birth_year']}/{test_data['birth_month']}/{test_data['birth_day']} {test_data['birth_hour']}:{test_data['birth_minute']:02d}")
    print(f"Location: {test_data['prefecture']}")
    print("=" * 50)
    
    try:
        # Step 1: Submit the form to calculate celestial positions
        print("\n1. Calculating celestial positions...")
        response = session.post(f"{base_url}/result", data=test_data)
        
        if response.status_code == 200:
            print("   ✓ Celestial positions calculated successfully")
        else:
            print(f"   ✗ Error: Status code {response.status_code}")
            return
        
        # Step 2: Access the detailed report
        print("\n2. Generating detailed report...")
        report_url = f"{base_url}/detailed_report?name={test_data['name']}&archetype=超新星"
        response = session.get(report_url)
        
        if response.status_code == 200:
            print("   ✓ Report generated successfully")
            
            # Count characters in the generated content
            content = response.text
            
            # Look for generated content sections
            import re
            generated_sections = re.findall(r'<div class="generated-content">(.*?)</div>', content, re.DOTALL)
            
            total_chars = 0
            for section in generated_sections:
                # Remove HTML tags for character count
                text_only = re.sub(r'<[^>]+>', '', section)
                total_chars += len(text_only)
            
            print(f"\n3. Report Statistics:")
            print(f"   - Total generated content characters: {total_chars:,}")
            print(f"   - Number of chapters found: {len(generated_sections)}")
            
            if total_chars >= 12000:
                print(f"   ✓ SUCCESS: Generated {total_chars:,} characters (>= 12,000)")
            else:
                print(f"   ⚠ WARNING: Generated only {total_chars:,} characters (< 12,000)")
            
            # Save the report for inspection
            with open('/home/user/webapp/test_report.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n4. Report saved to: /home/user/webapp/test_report.html")
            
        else:
            print(f"   ✗ Error: Status code {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to Flask server")
        print("  Make sure the server is running on port 5000")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    test_report_generation()