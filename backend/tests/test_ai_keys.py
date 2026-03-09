"""
Test suite for Multi-Key Multi-Provider AI System
Tests AI providers endpoint and admin AI key CRUD operations
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_EMAIL = "ipankpaul107@gmail.com"
ADMIN_PASSWORD = "Kakiku5."


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    token = response.json().get("token")
    assert token, "No token in response"
    return token


@pytest.fixture(scope="module")
def authenticated_client(api_client, admin_token):
    """Session with admin auth header"""
    api_client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return api_client


class TestAIProviders:
    """Test GET /api/ai-providers endpoint"""
    
    def test_get_providers_returns_all_providers(self, api_client):
        """Verify providers endpoint returns Gemini, Kimi, and OpenAI"""
        response = api_client.get(f"{BASE_URL}/api/ai-providers")
        assert response.status_code == 200
        
        data = response.json()
        # Verify all 3 providers
        assert "gemini" in data, "Missing gemini provider"
        assert "kimi" in data, "Missing kimi provider"
        assert "openai" in data, "Missing openai provider"
    
    def test_gemini_provider_has_correct_models(self, api_client):
        """Verify Gemini has 4 models with pricing"""
        response = api_client.get(f"{BASE_URL}/api/ai-providers")
        data = response.json()
        
        gemini = data["gemini"]
        assert gemini["name"] == "Google Gemini"
        assert "key_url" in gemini
        
        models = gemini["models"]
        assert len(models) == 4, f"Expected 4 Gemini models, got {len(models)}"
        
        # Check gemini-2.5-flash model
        assert "gemini-2.5-flash" in models
        flash = models["gemini-2.5-flash"]
        assert flash["input_price"] == 0.30
        assert flash["output_price"] == 2.50
    
    def test_kimi_provider_has_correct_models(self, api_client):
        """Verify Kimi has 2 models"""
        response = api_client.get(f"{BASE_URL}/api/ai-providers")
        data = response.json()
        
        kimi = data["kimi"]
        assert kimi["name"] == "Kimi (Moonshot)"
        
        models = kimi["models"]
        assert len(models) == 2, f"Expected 2 Kimi models, got {len(models)}"
        assert "kimi-k2.5" in models
        assert "kimi-k2.5-instant" in models
    
    def test_openai_provider_has_correct_models(self, api_client):
        """Verify OpenAI has 2 models"""
        response = api_client.get(f"{BASE_URL}/api/ai-providers")
        data = response.json()
        
        openai = data["openai"]
        assert openai["name"] == "OpenAI"
        
        models = openai["models"]
        assert len(models) == 2, f"Expected 2 OpenAI models, got {len(models)}"
        assert "gpt-4o-mini" in models
        assert "gpt-4o" in models


class TestAdminAIKeys:
    """Test admin AI key CRUD operations"""
    
    def test_get_ai_keys_requires_auth(self, api_client):
        """GET /api/admin/ai-keys requires authentication"""
        # Create fresh session without auth
        fresh_session = requests.Session()
        response = fresh_session.get(f"{BASE_URL}/api/admin/ai-keys")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
    
    def test_get_ai_keys_returns_list(self, authenticated_client):
        """Admin can get AI keys list"""
        response = authenticated_client.get(f"{BASE_URL}/api/admin/ai-keys")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
    
    def test_ai_keys_are_masked(self, authenticated_client):
        """API keys should be masked in response"""
        response = authenticated_client.get(f"{BASE_URL}/api/admin/ai-keys")
        assert response.status_code == 200
        
        data = response.json()
        for key in data:
            assert "api_key_masked" in key, "Key should have masked API key"
            assert "api_key" not in key, "Raw API key should not be exposed"
    
    def test_ai_keys_sorted_by_priority(self, authenticated_client):
        """Keys should be sorted by priority"""
        response = authenticated_client.get(f"{BASE_URL}/api/admin/ai-keys")
        assert response.status_code == 200
        
        data = response.json()
        if len(data) >= 2:
            priorities = [k.get("priority", 0) for k in data]
            assert priorities == sorted(priorities), "Keys not sorted by priority"


class TestAdminCreateKey:
    """Test POST /api/admin/ai-keys"""
    
    created_key_id = None
    
    def test_create_key_with_valid_data(self, authenticated_client):
        """Admin can create a new AI key"""
        payload = {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "api_key": "sk-test123456789012345678901234567890",
            "label": "TEST_OpenAI Key"
        }
        response = authenticated_client.post(f"{BASE_URL}/api/admin/ai-keys", json=payload)
        assert response.status_code == 200, f"Failed to create key: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should have id"
        assert data["provider"] == "openai"
        assert data["model"] == "gpt-4o-mini"
        assert data["label"] == "TEST_OpenAI Key"
        assert data["is_active"] == True
        assert "priority" in data
        assert "api_key_masked" in data
        
        # Store for later tests
        TestAdminCreateKey.created_key_id = data["id"]
    
    def test_create_key_validates_provider(self, authenticated_client):
        """Invalid provider should be rejected"""
        payload = {
            "provider": "invalid_provider",
            "model": "some-model",
            "api_key": "sk-test123",
            "label": "Test"
        }
        response = authenticated_client.post(f"{BASE_URL}/api/admin/ai-keys", json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    def test_create_key_validates_model(self, authenticated_client):
        """Invalid model for provider should be rejected"""
        payload = {
            "provider": "gemini",
            "model": "invalid-model",
            "api_key": "sk-test123",
            "label": "Test"
        }
        response = authenticated_client.post(f"{BASE_URL}/api/admin/ai-keys", json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    def test_key_appears_in_list_after_creation(self, authenticated_client):
        """Created key should appear in keys list"""
        if not TestAdminCreateKey.created_key_id:
            pytest.skip("No key created in previous test")
        
        response = authenticated_client.get(f"{BASE_URL}/api/admin/ai-keys")
        assert response.status_code == 200
        
        data = response.json()
        key_ids = [k["id"] for k in data]
        assert TestAdminCreateKey.created_key_id in key_ids, "Created key not found in list"


class TestAdminUpdateKey:
    """Test PUT /api/admin/ai-keys/{key_id}"""
    
    def test_toggle_key_active_status(self, authenticated_client):
        """Admin can toggle key active status"""
        if not TestAdminCreateKey.created_key_id:
            pytest.skip("No key created in previous test")
        
        key_id = TestAdminCreateKey.created_key_id
        
        # Toggle to inactive
        response = authenticated_client.put(
            f"{BASE_URL}/api/admin/ai-keys/{key_id}",
            json={"is_active": False}
        )
        assert response.status_code == 200, f"Failed to update key: {response.text}"
        
        # Verify change
        keys_response = authenticated_client.get(f"{BASE_URL}/api/admin/ai-keys")
        keys = keys_response.json()
        key = next((k for k in keys if k["id"] == key_id), None)
        assert key is not None, "Key not found"
        assert key["is_active"] == False, "Key should be inactive"
        
        # Toggle back to active
        response = authenticated_client.put(
            f"{BASE_URL}/api/admin/ai-keys/{key_id}",
            json={"is_active": True}
        )
        assert response.status_code == 200
    
    def test_update_nonexistent_key_returns_404(self, authenticated_client):
        """Updating non-existent key returns 404"""
        response = authenticated_client.put(
            f"{BASE_URL}/api/admin/ai-keys/nonexistent-id-12345",
            json={"is_active": False}
        )
        assert response.status_code == 404


class TestAdminReorderKeys:
    """Test PUT /api/admin/ai-keys/reorder"""
    
    def test_reorder_keys(self, authenticated_client):
        """Admin can reorder keys"""
        # Get current keys
        response = authenticated_client.get(f"{BASE_URL}/api/admin/ai-keys")
        keys = response.json()
        
        if len(keys) < 2:
            pytest.skip("Need at least 2 keys to test reorder")
        
        # Reverse order
        key_ids = [k["id"] for k in keys]
        reversed_ids = list(reversed(key_ids))
        
        # Use new API format with key_ids object
        response = authenticated_client.put(
            f"{BASE_URL}/api/admin/ai-keys/reorder",
            json={"key_ids": reversed_ids}
        )
        assert response.status_code == 200, f"Reorder failed: {response.text}"
        
        # Verify new order
        response = authenticated_client.get(f"{BASE_URL}/api/admin/ai-keys")
        new_keys = response.json()
        new_ids = [k["id"] for k in new_keys]
        
        # First key should be what was last
        assert new_ids[0] == reversed_ids[0], "Reorder did not work correctly"


class TestAdminDeleteKey:
    """Test DELETE /api/admin/ai-keys/{key_id}"""
    
    def test_delete_key(self, authenticated_client):
        """Admin can delete a key"""
        if not TestAdminCreateKey.created_key_id:
            pytest.skip("No key created in previous test")
        
        key_id = TestAdminCreateKey.created_key_id
        
        response = authenticated_client.delete(f"{BASE_URL}/api/admin/ai-keys/{key_id}")
        assert response.status_code == 200, f"Delete failed: {response.text}"
        
        # Verify deletion
        keys_response = authenticated_client.get(f"{BASE_URL}/api/admin/ai-keys")
        keys = keys_response.json()
        key_ids = [k["id"] for k in keys]
        assert key_id not in key_ids, "Key should be deleted"
    
    def test_delete_nonexistent_key_returns_404(self, authenticated_client):
        """Deleting non-existent key returns 404"""
        response = authenticated_client.delete(f"{BASE_URL}/api/admin/ai-keys/nonexistent-id-12345")
        assert response.status_code == 404


class TestGenerateWithFallback:
    """Test POST /api/generate uses multi-key fallback system"""
    
    @pytest.fixture
    def user_token(self, api_client):
        """Get a regular user token for testing generation"""
        # Use admin credentials as they have tokens
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def test_generate_endpoint_works(self, api_client, user_token):
        """Test that generate endpoint is functional with multi-key system"""
        if not user_token:
            pytest.skip("No user token available")
        
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Use rubrik doc_type as specified in requirements
        payload = {
            "doc_type": "rubrik",
            "jenjang": "sma",
            "kelas": "X",
            "kurikulum": "merdeka",
            "semester": "1",
            "fase": "E",
            "mata_pelajaran": "Matematika",
            "topik": "Persamaan Linear",
            "alokasi_waktu": 90  # Integer value in minutes
        }
        
        # Long timeout for AI generation (120s as specified)
        response = api_client.post(
            f"{BASE_URL}/api/generate",
            json=payload,
            headers=headers,
            timeout=120
        )
        
        # Either success or token issue (402) is acceptable
        assert response.status_code in [200, 402], f"Generate failed: {response.status_code} - {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "result_html" in data, "Response should have result_html"
            assert "id" in data, "Response should have generation id"
            print(f"Generation successful! ID: {data['id']}")


# Cleanup function to remove test data
def pytest_sessionfinish(session, exitstatus):
    """Cleanup test keys after all tests"""
    try:
        session_client = requests.Session()
        session_client.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = session_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            session_client.headers.update({"Authorization": f"Bearer {token}"})
            
            # Get and delete any TEST_ prefixed keys
            keys_response = session_client.get(f"{BASE_URL}/api/admin/ai-keys")
            if keys_response.status_code == 200:
                for key in keys_response.json():
                    if key.get("label", "").startswith("TEST_"):
                        session_client.delete(f"{BASE_URL}/api/admin/ai-keys/{key['id']}")
    except Exception as e:
        print(f"Cleanup error: {e}")
