import requests
import json

# Test login and document generation
base_url = "https://ai-edugen.preview.emergentagent.com"

# Login as super admin
login_response = requests.post(
    f"{base_url}/api/auth/login",
    json={"email": "ipankpaul107@gmail.com", "password": "Kakiku5."}
)

if login_response.status_code == 200:
    token = login_response.json()["token"]
    print("✅ Admin login successful")
    
    # Test document generation
    generate_data = {
        "doc_type": "soal",
        "jenjang": "SMA",
        "kelas": "10", 
        "kurikulum": "Merdeka",
        "semester": "Ganjil",
        "fase": "E",
        "mata_pelajaran": "Fisika",
        "topik": "Rangkaian Listrik",
        "alokasi_waktu": 90,
        "tingkat_kesulitan": "Sedang",
        "jumlah_pg": 1,
        "jumlah_isian": 1,
        "jumlah_essay": 1,
        "sertakan_pembahasan": True,
        "use_custom_values": True,
        "resistor1": 2.0,
        "resistor2": 3.0,
        "voltage": 12.0
    }
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    generate_response = requests.post(
        f"{base_url}/api/generate",
        json=generate_data,
        headers=headers,
        timeout=60
    )
    
    print(f"Generate status: {generate_response.status_code}")
    if generate_response.status_code == 200:
        result = generate_response.json()
        html_content = result.get('result_html', '')
        print(f"✅ Document generated successfully")
        print(f"Content length: {len(html_content)} chars")
        
        # Check for diagram tags
        if '[DIAGRAM:' in html_content:
            print("✅ Document contains diagram tags")
        else:
            print("⚠️  No diagram tags found")
            
        # Check for custom values
        if '2' in html_content and '3' in html_content and '12' in html_content:
            print("✅ Custom physics values appear to be used")
        else:
            print("⚠️  Custom physics values may not be used")
            
        print("\nFirst 300 chars of generated content:")
        print(html_content[:300] + "...")
    else:
        print(f"❌ Generate failed: {generate_response.text}")
else:
    print(f"❌ Login failed: {login_response.text}")