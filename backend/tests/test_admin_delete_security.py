"""
ModulAI Admin DELETE & Security Tests
Tests for:
- Admin DELETE user (cannot delete super_admin)
- Admin DELETE generation
- Admin DELETE all generations
- Admin DELETE transaction
- Admin DELETE AI key
- Security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, CSP, etc.)
- XSS sanitization in registration
- Auth bypass check (unauthenticated admin requests return 401)
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "ipankpaul107@gmail.com"
ADMIN_PASSWORD = "Kakiku5."


@pytest.fixture(scope="module")
def admin_token():
    """Get admin token for authenticated tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json()["token"]
    pytest.skip("Admin authentication failed")


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    """Get headers with admin auth"""
    return {"Authorization": f"Bearer {admin_token}"}


# ====================
# Security Headers Tests
# ====================
class TestSecurityHeaders:
    """Test security headers on API responses"""
    
    def test_security_headers_on_health(self):
        """Test security headers are present on /api/health"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        # Check all required security headers
        headers = response.headers
        
        assert headers.get("X-Content-Type-Options") == "nosniff", "X-Content-Type-Options header missing or incorrect"
        print("✓ X-Content-Type-Options: nosniff")
        
        assert headers.get("X-Frame-Options") == "DENY", "X-Frame-Options header missing or incorrect"
        print("✓ X-Frame-Options: DENY")
        
        assert "1; mode=block" in headers.get("X-XSS-Protection", ""), "X-XSS-Protection header missing or incorrect"
        print("✓ X-XSS-Protection: 1; mode=block")
        
        assert "strict-origin-when-cross-origin" in headers.get("Referrer-Policy", ""), "Referrer-Policy header missing"
        print("✓ Referrer-Policy: strict-origin-when-cross-origin")
        
        assert "camera=()" in headers.get("Permissions-Policy", ""), "Permissions-Policy header missing"
        print("✓ Permissions-Policy present")
        
        assert "no-store" in headers.get("Cache-Control", ""), "Cache-Control header missing"
        print("✓ Cache-Control: no-store")
        
        assert headers.get("Content-Security-Policy") is not None, "Content-Security-Policy header missing"
        print("✓ Content-Security-Policy present")
    
    def test_security_headers_on_admin_endpoint(self, admin_headers):
        """Test security headers on admin protected endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/dashboard", headers=admin_headers)
        assert response.status_code == 200
        
        headers = response.headers
        assert headers.get("X-Content-Type-Options") == "nosniff"
        assert headers.get("X-Frame-Options") == "DENY"
        print("✓ Security headers present on admin endpoints")


# ====================
# XSS Sanitization Tests
# ====================
class TestXSSSanitization:
    """Test XSS sanitization on user input"""
    
    def test_xss_in_registration_name(self, admin_headers):
        """Test that script tags in name are sanitized during registration"""
        test_email = f"test_xss_{uuid.uuid4().hex[:8]}@test.com"
        xss_payload = '<script>alert("XSS")</script>MaliciousUser'
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPassword123!",
            "name": xss_payload,
            "phone": "081234567890",
            "school_name": "Test School"
        })
        
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        
        # The name should be sanitized - no script tags
        user_name = data["user"]["name"]
        assert "<script>" not in user_name.lower(), f"XSS not sanitized! Name: {user_name}"
        assert "alert(" not in user_name.lower(), f"XSS not sanitized! Name: {user_name}"
        print(f"✓ XSS sanitized: Original: '{xss_payload}' -> Sanitized: '{user_name}'")
        
        # Cleanup - delete the test user
        users_resp = requests.get(f"{BASE_URL}/api/admin/users", headers=admin_headers)
        if users_resp.status_code == 200:
            users = users_resp.json()["users"]
            test_user = next((u for u in users if u["email"] == test_email), None)
            if test_user:
                requests.delete(f"{BASE_URL}/api/admin/users/{test_user['id']}", headers=admin_headers)
                print(f"✓ Cleaned up test user: {test_email}")


# ====================
# Auth Bypass Tests
# ====================
class TestAuthBypass:
    """Test that admin endpoints require authentication"""
    
    def test_unauthenticated_dashboard_returns_401(self):
        """Admin dashboard should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/admin/dashboard")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ /api/admin/dashboard returns 401 without auth")
    
    def test_unauthenticated_users_returns_401(self):
        """Admin users endpoint should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ /api/admin/users returns 401 without auth")
    
    def test_unauthenticated_generations_returns_401(self):
        """Admin generations endpoint should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/admin/generations")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ /api/admin/generations returns 401 without auth")
    
    def test_unauthenticated_transactions_returns_401(self):
        """Admin transactions endpoint should return 401 without token"""
        response = requests.get(f"{BASE_URL}/api/admin/transactions")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ /api/admin/transactions returns 401 without auth")
    
    def test_unauthenticated_delete_user_returns_401(self):
        """Admin delete user should return 401 without token"""
        response = requests.delete(f"{BASE_URL}/api/admin/users/some-user-id")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ DELETE /api/admin/users/{id} returns 401 without auth")
    
    def test_unauthenticated_delete_ai_key_returns_401(self):
        """Admin delete AI key should return 401 without token"""
        response = requests.delete(f"{BASE_URL}/api/admin/ai-keys/some-key-id")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ DELETE /api/admin/ai-keys/{id} returns 401 without auth")


# ====================
# Admin DELETE User Tests
# ====================
class TestAdminDeleteUser:
    """Test admin delete user functionality"""
    
    def test_delete_user_and_related_data(self, admin_headers):
        """Test DELETE /api/admin/users/{id} - deletes user and related data"""
        # First create a test user
        test_email = f"test_delete_{uuid.uuid4().hex[:8]}@test.com"
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": "TestPassword123!",
            "name": "TEST_DeleteUser",
            "phone": "081234567890",
            "school_name": "Test School"
        })
        assert reg_resp.status_code == 200, f"Failed to create test user: {reg_resp.text}"
        user_id = reg_resp.json()["user"]["id"]
        print(f"✓ Created test user: {test_email} (id: {user_id})")
        
        # Delete the user
        del_resp = requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=admin_headers)
        assert del_resp.status_code == 200, f"Delete user failed: {del_resp.text}"
        data = del_resp.json()
        assert "message" in data
        print(f"✓ DELETE /api/admin/users/{user_id} returned 200")
        
        # Verify user is deleted (GET users should not find them)
        users_resp = requests.get(f"{BASE_URL}/api/admin/users", headers=admin_headers)
        users = users_resp.json()["users"]
        deleted_user = next((u for u in users if u["id"] == user_id), None)
        assert deleted_user is None, "User should be deleted"
        print("✓ User verified as deleted from database")
    
    def test_cannot_delete_super_admin(self, admin_headers):
        """Test DELETE /api/admin/users/{id} - cannot delete super_admin"""
        # Get list of users and find super_admin
        users_resp = requests.get(f"{BASE_URL}/api/admin/users", headers=admin_headers)
        users = users_resp.json()["users"]
        super_admin = next((u for u in users if u["role"] == "super_admin"), None)
        
        assert super_admin is not None, "Super admin should exist"
        
        # Try to delete super_admin
        del_resp = requests.delete(f"{BASE_URL}/api/admin/users/{super_admin['id']}", headers=admin_headers)
        assert del_resp.status_code == 403, f"Expected 403 Forbidden, got {del_resp.status_code}"
        print("✓ Cannot delete super_admin (returns 403)")
    
    def test_delete_nonexistent_user_returns_404(self, admin_headers):
        """Test DELETE /api/admin/users/{id} with non-existent ID returns 404"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/users/nonexistent-id-12345",
            headers=admin_headers
        )
        assert response.status_code == 404
        print("✓ Delete non-existent user correctly returns 404")


# ====================
# Admin DELETE AI Key Tests
# ====================
class TestAdminDeleteAIKey:
    """Test admin delete AI key functionality"""
    
    def test_delete_ai_key(self, admin_headers):
        """Test DELETE /api/admin/ai-keys/{id}"""
        # First create a test AI key
        create_resp = requests.post(
            f"{BASE_URL}/api/admin/ai-keys",
            headers=admin_headers,
            json={
                "provider": "gemini",
                "model": "gemini-2.5-flash",
                "api_key": "test_api_key_to_delete_12345",
                "label": "TEST_DeleteKey"
            }
        )
        assert create_resp.status_code == 200, f"Failed to create test AI key: {create_resp.text}"
        key_id = create_resp.json()["id"]
        print(f"✓ Created test AI key (id: {key_id})")
        
        # Delete the key
        del_resp = requests.delete(f"{BASE_URL}/api/admin/ai-keys/{key_id}", headers=admin_headers)
        assert del_resp.status_code == 200, f"Delete AI key failed: {del_resp.text}"
        data = del_resp.json()
        assert "message" in data
        print(f"✓ DELETE /api/admin/ai-keys/{key_id} returned 200")
        
        # Verify key is deleted
        keys_resp = requests.get(f"{BASE_URL}/api/admin/ai-keys", headers=admin_headers)
        keys = keys_resp.json()
        deleted_key = next((k for k in keys if k["id"] == key_id), None)
        assert deleted_key is None, "AI key should be deleted"
        print("✓ AI key verified as deleted from database")
    
    def test_delete_nonexistent_ai_key_returns_404(self, admin_headers):
        """Test DELETE /api/admin/ai-keys/{id} with non-existent ID returns 404"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/ai-keys/nonexistent-key-12345",
            headers=admin_headers
        )
        assert response.status_code == 404
        print("✓ Delete non-existent AI key correctly returns 404")


# ====================
# Admin DELETE Transaction Tests
# ====================
class TestAdminDeleteTransaction:
    """Test admin delete transaction functionality"""
    
    def test_delete_transaction(self, admin_headers):
        """Test DELETE /api/admin/transactions/{id}"""
        # First get existing transactions
        txs_resp = requests.get(f"{BASE_URL}/api/admin/transactions", headers=admin_headers)
        transactions = txs_resp.json()["transactions"]
        
        if len(transactions) == 0:
            pytest.skip("No transactions to test delete on")
        
        # Get first transaction to delete
        tx_id = transactions[0]["id"]
        
        # Delete the transaction
        del_resp = requests.delete(f"{BASE_URL}/api/admin/transactions/{tx_id}", headers=admin_headers)
        assert del_resp.status_code == 200, f"Delete transaction failed: {del_resp.text}"
        data = del_resp.json()
        assert "message" in data
        print(f"✓ DELETE /api/admin/transactions/{tx_id} returned 200")
        
        # Verify transaction is deleted
        txs_resp2 = requests.get(f"{BASE_URL}/api/admin/transactions", headers=admin_headers)
        transactions2 = txs_resp2.json()["transactions"]
        deleted_tx = next((t for t in transactions2 if t["id"] == tx_id), None)
        assert deleted_tx is None, "Transaction should be deleted"
        print("✓ Transaction verified as deleted from database")
    
    def test_delete_nonexistent_transaction_returns_404(self, admin_headers):
        """Test DELETE /api/admin/transactions/{id} with non-existent ID returns 404"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/transactions/nonexistent-tx-12345",
            headers=admin_headers
        )
        assert response.status_code == 404
        print("✓ Delete non-existent transaction correctly returns 404")


# ====================
# Admin DELETE Generation Tests
# ====================
class TestAdminDeleteGeneration:
    """Test admin delete generation functionality"""
    
    def test_delete_single_generation(self, admin_headers, admin_token):
        """Test DELETE /api/admin/generations/{id}"""
        # First get existing generations
        gens_resp = requests.get(f"{BASE_URL}/api/admin/generations", headers=admin_headers)
        generations = gens_resp.json()["generations"]
        
        if len(generations) == 0:
            # Create a test generation if none exist
            gen_resp = requests.post(
                f"{BASE_URL}/api/generate",
                headers=admin_headers,
                json={
                    "doc_type": "rubrik",
                    "jenjang": "SMA",
                    "kelas": "10",
                    "kurikulum": "Merdeka",
                    "semester": "Ganjil",
                    "fase": "E",
                    "mata_pelajaran": "Matematika",
                    "topik": "TEST_DeleteGeneration",
                    "alokasi_waktu": 45
                },
                timeout=120
            )
            if gen_resp.status_code != 200:
                pytest.skip(f"Could not create test generation: {gen_resp.text}")
            
            # Refetch generations
            gens_resp = requests.get(f"{BASE_URL}/api/admin/generations", headers=admin_headers)
            generations = gens_resp.json()["generations"]
        
        if len(generations) == 0:
            pytest.skip("No generations to test delete on")
        
        # Get first generation to delete
        gen_id = generations[0]["id"]
        
        # Delete the generation
        del_resp = requests.delete(f"{BASE_URL}/api/admin/generations/{gen_id}", headers=admin_headers)
        assert del_resp.status_code == 200, f"Delete generation failed: {del_resp.text}"
        data = del_resp.json()
        assert "message" in data
        print(f"✓ DELETE /api/admin/generations/{gen_id} returned 200")
        
        # Verify generation is deleted
        gens_resp2 = requests.get(f"{BASE_URL}/api/admin/generations", headers=admin_headers)
        generations2 = gens_resp2.json()["generations"]
        deleted_gen = next((g for g in generations2 if g["id"] == gen_id), None)
        assert deleted_gen is None, "Generation should be deleted"
        print("✓ Generation verified as deleted from database")
    
    def test_delete_all_generations(self, admin_headers):
        """Test DELETE /api/admin/generations - deletes all generations"""
        # First check if there are any generations
        gens_resp = requests.get(f"{BASE_URL}/api/admin/generations", headers=admin_headers)
        initial_count = len(gens_resp.json()["generations"])
        
        # Delete all generations
        del_resp = requests.delete(f"{BASE_URL}/api/admin/generations", headers=admin_headers)
        assert del_resp.status_code == 200, f"Delete all generations failed: {del_resp.text}"
        data = del_resp.json()
        assert "message" in data
        print(f"✓ DELETE /api/admin/generations returned 200: {data['message']}")
        
        # Verify all generations are deleted
        gens_resp2 = requests.get(f"{BASE_URL}/api/admin/generations", headers=admin_headers)
        final_count = len(gens_resp2.json()["generations"])
        assert final_count == 0, f"Expected 0 generations, got {final_count}"
        print(f"✓ All generations deleted (was {initial_count}, now {final_count})")
    
    def test_delete_nonexistent_generation_returns_404(self, admin_headers):
        """Test DELETE /api/admin/generations/{id} with non-existent ID returns 404"""
        response = requests.delete(
            f"{BASE_URL}/api/admin/generations/nonexistent-gen-12345",
            headers=admin_headers
        )
        assert response.status_code == 404
        print("✓ Delete non-existent generation correctly returns 404")


# ====================
# Admin List Endpoints Tests (for verification)
# ====================
class TestAdminListEndpoints:
    """Test admin list endpoints work correctly"""
    
    def test_admin_generations_list(self, admin_headers):
        """Test GET /api/admin/generations"""
        response = requests.get(f"{BASE_URL}/api/admin/generations", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "generations" in data
        assert "total" in data
        print(f"✓ GET /api/admin/generations: {data['total']} total")
    
    def test_admin_transactions_list(self, admin_headers):
        """Test GET /api/admin/transactions"""
        response = requests.get(f"{BASE_URL}/api/admin/transactions", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert "total" in data
        print(f"✓ GET /api/admin/transactions: {data['total']} total")
    
    def test_admin_ai_keys_list(self, admin_headers):
        """Test GET /api/admin/ai-keys"""
        response = requests.get(f"{BASE_URL}/api/admin/ai-keys", headers=admin_headers)
        assert response.status_code == 200
        keys = response.json()
        assert isinstance(keys, list)
        print(f"✓ GET /api/admin/ai-keys: {len(keys)} keys")
