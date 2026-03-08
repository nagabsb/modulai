import requests
import sys
from datetime import datetime

class ModulAITester:
    def __init__(self, base_url="https://teach-ai-hub-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        request_headers = {'Content-Type': 'application/json'}
        if headers:
            request_headers.update(headers)
        if self.token:
            request_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=request_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=request_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=request_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if response.content:
                    try:
                        return success, response.json()
                    except:
                        return success, response.text
                return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health endpoints"""
        success1, _ = self.run_test("Health Check", "GET", "", 200)
        success2, _ = self.run_test("API Root", "GET", "health", 200)
        return success1 and success2

    def test_packages(self):
        """Test token packages endpoint"""
        success, response = self.run_test("Token Packages", "GET", "packages", 200)
        if success and isinstance(response, list) and len(response) > 0:
            print(f"Found {len(response)} packages")
            return True
        return False

    def test_super_admin_login(self):
        """Test super admin login"""
        success, response = self.run_test(
            "Super Admin Login",
            "POST",
            "auth/login",
            200,
            data={"email": "ipankpaul107@gmail.com", "password": "Kakiku5."}
        )
        if success and 'token' in response:
            self.token = response['token']
            print(f"Admin logged in successfully. Role: {response.get('user', {}).get('role')}")
            return True
        return False

    def test_admin_dashboard(self):
        """Test admin dashboard stats"""
        if not self.token:
            print("❌ No token available for admin test")
            return False
        
        success, response = self.run_test("Admin Dashboard", "GET", "admin/dashboard", 200)
        if success:
            print(f"Dashboard stats - Users: {response.get('total_users', 0)}, Generations: {response.get('total_generations', 0)}")
            return True
        return False

    def test_admin_ai_settings(self):
        """Test AI settings endpoints"""
        if not self.token:
            print("❌ No token available for admin test")
            return False
        
        # Get AI settings
        success1, settings = self.run_test("Get AI Settings", "GET", "admin/ai-settings", 200)
        if success1:
            print(f"AI Settings - Provider: {settings.get('provider')}, Model: {settings.get('model')}")
        
        # Update AI settings
        success2, _ = self.run_test(
            "Update AI Settings", 
            "PUT", 
            "admin/ai-settings", 
            200,
            data={"provider": "gemini_flash_lite"}
        )
        
        return success1 and success2

    def test_generate_document(self):
        """Test document generation"""
        if not self.token:
            print("❌ No token available for generate test")
            return False
        
        test_data = {
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
            "jumlah_pg": 2,
            "jumlah_isian": 1,
            "jumlah_essay": 1,
            "sertakan_pembahasan": True,
            "use_custom_values": True,
            "resistor1": 2.0,
            "resistor2": 3.0,
            "voltage": 12.0
        }
        
        success, response = self.run_test(
            "Generate Physics Document with Custom Values",
            "POST",
            "generate",
            200,
            data=test_data
        )
        
        if success and 'result_html' in response:
            html_content = response['result_html']
            print(f"Generated document length: {len(html_content)} chars")
            
            # Check for physics diagram tags
            if '[DIAGRAM:' in html_content:
                print("✅ Document contains diagram tags")
            else:
                print("⚠️  No diagram tags found in generated content")
            
            # Check for custom values
            if '2' in html_content and '3' in html_content and '12' in html_content:
                print("✅ Custom physics values appear to be used")
            else:
                print("⚠️  Custom physics values may not be used")
            
            return True
        return False

    def test_user_registration(self):
        """Test user registration"""
        test_email = f"test_user_{datetime.now().strftime('%H%M%S')}@test.com"
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "email": test_email,
                "password": "TestPass123!",
                "name": "Test User",
                "phone": "08123456789",
                "school_name": "Test School"
            }
        )
        
        if success and 'token' in response:
            print(f"User registered: {response.get('user', {}).get('email')}")
            return True
        return False

def main():
    print("🚀 Starting ModulAI Backend Tests...")
    print("=" * 50)
    
    tester = ModulAITester()
    
    # Test health endpoints
    if not tester.test_health_check():
        print("❌ Health check failed, stopping tests")
        return 1
    
    # Test public endpoints
    tester.test_packages()
    tester.test_user_registration()
    
    # Test admin functionality
    if tester.test_super_admin_login():
        tester.test_admin_dashboard()
        tester.test_admin_ai_settings()
        tester.test_generate_document()
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())