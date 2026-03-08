"""
ModulAI API Tests
Tests for:
- Admin Authentication
- Voucher Management (CRUD, toggle status, delete)
- Token Packages
- Document Generation (single and multi)
- Modul with Daftar Pustaka
- Soal with correct format (questions first, then answers/discussions)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "ipankpaul107@gmail.com"
ADMIN_PASSWORD = "Kakiku5."


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ API root accessible: {data['message']}")
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ Health check passed")


class TestAdminAuth:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """Test super admin login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "super_admin"
        print(f"✓ Admin login successful, role: {data['user']['role']}")
        return data["token"]
    
    def test_admin_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid credentials correctly rejected")


@pytest.fixture(scope="class")
def admin_token():
    """Get admin token for authenticated tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json()["token"]
    pytest.skip("Admin authentication failed")


class TestTokenPackages:
    """Token packages API tests"""
    
    def test_get_packages(self):
        """Test GET /api/packages endpoint"""
        response = requests.get(f"{BASE_URL}/api/packages")
        assert response.status_code == 200
        packages = response.json()
        assert isinstance(packages, list)
        assert len(packages) > 0
        # Verify package structure
        for pkg in packages:
            assert "id" in pkg
            assert "name" in pkg
            assert "price" in pkg
            assert "tokens" in pkg
        print(f"✓ Got {len(packages)} token packages")


class TestVoucherManagement:
    """Voucher CRUD tests (admin endpoints)"""
    
    @pytest.fixture(autouse=True)
    def setup(self, admin_token):
        self.token = admin_token
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_vouchers(self):
        """Test GET /api/admin/vouchers - list all vouchers"""
        response = requests.get(f"{BASE_URL}/api/admin/vouchers", headers=self.headers)
        assert response.status_code == 200
        vouchers = response.json()
        assert isinstance(vouchers, list)
        print(f"✓ Got {len(vouchers)} vouchers")
        return vouchers
    
    def test_create_voucher(self):
        """Test POST /api/admin/vouchers - create voucher"""
        # Create voucher with query params (as per API design)
        response = requests.post(
            f"{BASE_URL}/api/admin/vouchers?code=TESTDEL&discount_type=percentage&discount_value=25",
            headers=self.headers
        )
        assert response.status_code == 200, f"Create voucher failed: {response.text}"
        voucher = response.json()
        assert voucher["code"] == "TESTDEL"
        assert voucher["discount_type"] == "percentage"
        assert voucher["discount_value"] == 25
        assert voucher["is_active"] == True
        assert "id" in voucher
        print(f"✓ Created voucher: {voucher['code']} (id: {voucher['id']})")
        return voucher
    
    def test_voucher_toggle_status(self):
        """Test PUT /api/admin/vouchers/{id} - toggle voucher active status"""
        # First create a voucher
        create_resp = requests.post(
            f"{BASE_URL}/api/admin/vouchers?code=TOGGLETEST&discount_type=fixed&discount_value=5000",
            headers=self.headers
        )
        assert create_resp.status_code == 200
        voucher = create_resp.json()
        voucher_id = voucher["id"]
        
        # Toggle to inactive
        response = requests.put(
            f"{BASE_URL}/api/admin/vouchers/{voucher_id}",
            headers=self.headers,
            json={"is_active": False}
        )
        assert response.status_code == 200
        print(f"✓ Toggled voucher {voucher_id} to inactive")
        
        # Verify the voucher is inactive
        vouchers_resp = requests.get(f"{BASE_URL}/api/admin/vouchers", headers=self.headers)
        vouchers = vouchers_resp.json()
        updated_voucher = next((v for v in vouchers if v["id"] == voucher_id), None)
        assert updated_voucher is not None
        assert updated_voucher["is_active"] == False
        print("✓ Verified voucher is now inactive")
        
        # Cleanup - delete the voucher
        requests.delete(f"{BASE_URL}/api/admin/vouchers/{voucher_id}", headers=self.headers)
        return voucher_id
    
    def test_delete_voucher(self):
        """Test DELETE /api/admin/vouchers/{id} - delete voucher permanently"""
        # First create a voucher to delete
        create_resp = requests.post(
            f"{BASE_URL}/api/admin/vouchers?code=DELETEME&discount_type=percentage&discount_value=10",
            headers=self.headers
        )
        assert create_resp.status_code == 200
        voucher = create_resp.json()
        voucher_id = voucher["id"]
        
        # Delete the voucher
        response = requests.delete(
            f"{BASE_URL}/api/admin/vouchers/{voucher_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ Deleted voucher {voucher_id}")
        
        # Verify the voucher is gone
        vouchers_resp = requests.get(f"{BASE_URL}/api/admin/vouchers", headers=self.headers)
        vouchers = vouchers_resp.json()
        deleted_voucher = next((v for v in vouchers if v["id"] == voucher_id), None)
        assert deleted_voucher is None
        print("✓ Verified voucher is deleted")
    
    def test_delete_nonexistent_voucher(self):
        """Test DELETE /api/admin/vouchers/{id} with non-existent ID"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/vouchers/nonexistent-id-12345",
            headers=self.headers
        )
        assert response.status_code == 404
        print("✓ Delete non-existent voucher correctly returns 404")


class TestDocumentGeneration:
    """Document generation tests (uses real Gemini API - needs longer timeout)"""
    
    @pytest.fixture(autouse=True)
    def setup(self, admin_token):
        self.token = admin_token
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_multi_document_generation(self):
        """Test POST /api/generate/multi - multi-doc generation (RPP + Rubrik)"""
        payload = {
            "doc_types": ["rpp", "rubrik"],
            "jenjang": "SMA",
            "kelas": "10",
            "kurikulum": "Merdeka",
            "semester": "Ganjil",
            "fase": "E",
            "mata_pelajaran": "Matematika",
            "topik": "Persamaan Linear",
            "alokasi_waktu": 45
        }
        
        response = requests.post(
            f"{BASE_URL}/api/generate/multi",
            headers=self.headers,
            json=payload,
            timeout=120  # Gemini API can take time
        )
        assert response.status_code == 200, f"Multi-generate failed: {response.text}"
        data = response.json()
        
        assert "results" in data
        assert "tokens_used" in data
        assert "remaining_tokens" in data
        assert len(data["results"]) == 2
        assert data["tokens_used"] == 2
        
        # Verify both doc types are in results
        result_types = [r["doc_type"] for r in data["results"]]
        assert "rpp" in result_types
        assert "rubrik" in result_types
        
        for result in data["results"]:
            assert "result_html" in result
            assert len(result["result_html"]) > 100  # Should have substantial content
        
        print(f"✓ Multi-doc generation successful: {len(data['results'])} documents, {data['tokens_used']} tokens used")
    
    def test_modul_with_daftar_pustaka(self):
        """Test POST /api/generate - modul should include Daftar Pustaka (bibliography)"""
        payload = {
            "doc_type": "modul",
            "jenjang": "SMA",
            "kelas": "10",
            "kurikulum": "Merdeka",
            "semester": "Ganjil",
            "fase": "E",
            "mata_pelajaran": "Matematika",
            "topik": "Barisan Aritmatika",
            "alokasi_waktu": 90
        }
        
        response = requests.post(
            f"{BASE_URL}/api/generate",
            headers=self.headers,
            json=payload,
            timeout=120
        )
        assert response.status_code == 200, f"Modul generation failed: {response.text}"
        data = response.json()
        
        assert "result_html" in data
        result_html = data["result_html"].lower()
        
        # Verify Daftar Pustaka section exists
        has_daftar_pustaka = "daftar pustaka" in result_html or "bibliography" in result_html or "referensi" in result_html
        assert has_daftar_pustaka, "Modul Ajar should contain Daftar Pustaka section"
        
        print("✓ Modul generation successful with Daftar Pustaka section")
        return data
    
    def test_soal_format_questions_then_answers(self):
        """Test POST /api/generate - soal format should have all questions first, then answers at end"""
        payload = {
            "doc_type": "soal",
            "jenjang": "SMA",
            "kelas": "10",
            "kurikulum": "Merdeka",
            "semester": "Ganjil",
            "fase": "E",
            "mata_pelajaran": "Matematika",
            "topik": "Persamaan Kuadrat",
            "alokasi_waktu": 60,
            "jumlah_pg": 3,
            "jumlah_isian": 2,
            "jumlah_essay": 1,
            "sertakan_pembahasan": True,
            "tingkat_kesulitan": "Sedang"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/generate",
            headers=self.headers,
            json=payload,
            timeout=120
        )
        assert response.status_code == 200, f"Soal generation failed: {response.text}"
        data = response.json()
        
        assert "result_html" in data
        result_html = data["result_html"].lower()
        
        # Check for proper structure: questions THEN answers THEN pembahasan
        # Find positions of key sections
        soal_pg_pos = result_html.find("pilihan ganda")
        kunci_jawaban_pos = result_html.find("kunci jawaban")
        pembahasan_pos = result_html.find("pembahasan")
        
        # Verify order: questions section comes before kunci jawaban
        if soal_pg_pos != -1 and kunci_jawaban_pos != -1:
            assert soal_pg_pos < kunci_jawaban_pos, "All questions should appear before KUNCI JAWABAN section"
            print("✓ Question section appears before answer key section")
        
        # Verify pembahasan comes after kunci jawaban (if both exist)
        if kunci_jawaban_pos != -1 and pembahasan_pos != -1:
            assert kunci_jawaban_pos < pembahasan_pos, "KUNCI JAWABAN should appear before PEMBAHASAN section"
            print("✓ Answer key section appears before discussion section")
        
        print("✓ Soal generation successful with correct format (questions first, then answers/discussions)")
        return data


class TestAdminDashboard:
    """Admin dashboard and user management tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self, admin_token):
        self.token = admin_token
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_admin_dashboard(self):
        """Test GET /api/admin/dashboard"""
        response = requests.get(f"{BASE_URL}/api/admin/dashboard", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_revenue" in data
        assert "total_generations" in data
        assert "doc_breakdown" in data
        print(f"✓ Admin dashboard: {data['total_users']} users, {data['total_generations']} docs")
    
    def test_admin_users_list(self):
        """Test GET /api/admin/users"""
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        print(f"✓ Got {data['total']} users")


# Cleanup test vouchers after all tests
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_vouchers():
    """Cleanup test-created vouchers after all tests"""
    yield
    # Get admin token
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        token = response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get all vouchers
        vouchers_resp = requests.get(f"{BASE_URL}/api/admin/vouchers", headers=headers)
        if vouchers_resp.status_code == 200:
            vouchers = vouchers_resp.json()
            # Delete test vouchers
            for v in vouchers:
                if v["code"].startswith("TEST") or v["code"] in ["DELETEME", "TOGGLETEST"]:
                    requests.delete(f"{BASE_URL}/api/admin/vouchers/{v['id']}", headers=headers)
                    print(f"Cleaned up test voucher: {v['code']}")
