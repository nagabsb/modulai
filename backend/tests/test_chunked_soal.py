"""
Test suite for Chunked Soal Generation Feature

Tests the fix for:
1. PG chunking for large question sets (>15 questions)
2. is_chunk flag for intermediate API calls (no token deduction, no save)
3. /api/generate/save endpoint for saving merged results
4. Non-chunked flow still works correctly

Author: Testing Agent
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    raise ValueError("REACT_APP_BACKEND_URL environment variable is not set")


class TestHealthEndpoint:
    """Verify API is accessible"""
    
    def test_health_endpoint(self):
        """Test /api/health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ Health endpoint working")


class TestAuthentication:
    """Authentication tests to get token for subsequent tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for super admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "ipankpaul107@gmail.com",
            "password": "Kakiku5."
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        print(f"✓ Login successful, token_balance: {data.get('user', {}).get('token_balance')}")
        return data["token"]
    
    def test_login_and_get_token(self, auth_token):
        """Verify login works"""
        assert auth_token is not None
        assert len(auth_token) > 0


class TestChunkedSoalGeneration:
    """Test chunked soal generation endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authentication headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "ipankpaul107@gmail.com",
            "password": "Kakiku5."
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    @pytest.fixture(scope="class")
    def initial_token_balance(self, auth_headers):
        """Get initial token balance before tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "ipankpaul107@gmail.com",
            "password": "Kakiku5."
        })
        return response.json()["user"]["token_balance"]
    
    def test_chunk_call_returns_only_result_html(self, auth_headers):
        """Test that is_chunk=true returns only result_html without id or tokens_used"""
        print("\n--- Testing is_chunk=true API call ---")
        
        # Make a chunk call with small PG to speed up test
        response = requests.post(
            f"{BASE_URL}/api/generate",
            headers=auth_headers,
            json={
                "doc_type": "soal",
                "jenjang": "SMA",
                "kelas": "10",
                "kurikulum": "Merdeka",
                "semester": "Ganjil",
                "fase": "E",
                "mata_pelajaran": "Matematika",
                "topik": "Persamaan Linear",
                "alokasi_waktu": 60,
                "tingkat_kesulitan": "Mudah",
                "soal_section": "pg",
                "jumlah_pg": 3,
                "jumlah_isian": 0,
                "jumlah_essay": 0,
                "pg_numbering_start": 1,
                "is_chunk": True,  # This is the key flag
                "sertakan_pembahasan": False
            },
            timeout=180
        )
        
        assert response.status_code == 200, f"Chunk call failed: {response.text}"
        data = response.json()
        
        # Verify chunk response structure
        assert "result_html" in data, "result_html not in response"
        assert "id" not in data, "id should NOT be in chunk response"
        assert "tokens_used" not in data, "tokens_used should NOT be in chunk response"
        assert "remaining_tokens" not in data, "remaining_tokens should NOT be in chunk response"
        
        # Verify HTML content was generated
        assert len(data["result_html"]) > 100, "Generated HTML seems too short"
        assert "<" in data["result_html"], "Response should be HTML"
        
        print(f"✓ Chunk call returned only result_html ({len(data['result_html'])} chars)")
        print("✓ No id, tokens_used, or remaining_tokens in response")
    
    def test_chunk_call_does_not_deduct_tokens(self, auth_headers):
        """Test that is_chunk=true calls do not deduct tokens"""
        print("\n--- Testing token non-deduction for chunk calls ---")
        
        # Get initial balance
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "ipankpaul107@gmail.com",
            "password": "Kakiku5."
        })
        initial_balance = login_resp.json()["user"]["token_balance"]
        print(f"Initial token balance: {initial_balance}")
        
        # Make a chunk call
        response = requests.post(
            f"{BASE_URL}/api/generate",
            headers=auth_headers,
            json={
                "doc_type": "soal",
                "jenjang": "SMA",
                "kelas": "10",
                "kurikulum": "Merdeka",
                "semester": "Ganjil",
                "fase": "E",
                "mata_pelajaran": "Matematika",
                "topik": "Persamaan Kuadrat",
                "alokasi_waktu": 60,
                "tingkat_kesulitan": "Mudah",
                "soal_section": "pg",
                "jumlah_pg": 2,
                "jumlah_isian": 0,
                "jumlah_essay": 0,
                "pg_numbering_start": 1,
                "is_chunk": True,
                "sertakan_pembahasan": False
            },
            timeout=180
        )
        
        assert response.status_code == 200, f"Chunk call failed: {response.text}"
        
        # Verify balance unchanged
        login_resp2 = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "ipankpaul107@gmail.com",
            "password": "Kakiku5."
        })
        final_balance = login_resp2.json()["user"]["token_balance"]
        print(f"Token balance after chunk call: {final_balance}")
        
        assert final_balance == initial_balance, f"Token balance changed from {initial_balance} to {final_balance} - chunk calls should NOT deduct tokens"
        print("✓ Token balance unchanged after chunk call")
    
    def test_save_endpoint_deducts_one_token(self, auth_headers):
        """Test that /api/generate/save deducts exactly 1 token"""
        print("\n--- Testing /api/generate/save endpoint ---")
        
        # Get initial balance
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "ipankpaul107@gmail.com",
            "password": "Kakiku5."
        })
        initial_balance = login_resp.json()["user"]["token_balance"]
        print(f"Initial token balance: {initial_balance}")
        
        if initial_balance < 1:
            pytest.skip("Not enough tokens to test save endpoint")
        
        # Call save endpoint with merged HTML
        response = requests.post(
            f"{BASE_URL}/api/generate/save",
            headers=auth_headers,
            json={
                "doc_type": "soal",
                "form_data": {
                    "doc_type": "soal",
                    "jenjang": "SMA",
                    "kelas": "10",
                    "kurikulum": "Merdeka",
                    "semester": "Ganjil",
                    "mata_pelajaran": "Matematika",
                    "topik": "TEST_ChunkedSoal_SaveEndpoint",
                    "jumlah_pg": 20,
                    "jumlah_isian": 5,
                    "jumlah_essay": 3
                },
                "result_html": "<h2>TEST MERGED HTML</h2><p>This is a test merged result from chunked generation.</p>"
            },
            timeout=30
        )
        
        assert response.status_code == 200, f"Save failed: {response.text}"
        data = response.json()
        
        # Verify save response structure
        assert "id" in data, "id should be in save response"
        assert "result_html" in data, "result_html should be in save response"
        assert "tokens_used" in data, "tokens_used should be in save response"
        assert "remaining_tokens" in data, "remaining_tokens should be in save response"
        
        # Verify exactly 1 token was deducted
        assert data["tokens_used"] == 1, f"tokens_used should be 1, got {data['tokens_used']}"
        assert data["remaining_tokens"] == initial_balance - 1, f"Expected remaining_tokens to be {initial_balance - 1}, got {data['remaining_tokens']}"
        
        print(f"✓ Save response has id: {data['id']}")
        print(f"✓ tokens_used: {data['tokens_used']}")
        print(f"✓ remaining_tokens: {data['remaining_tokens']} (was {initial_balance})")
        print("✓ Exactly 1 token deducted")
    
    def test_non_pg_chunk_section(self, auth_headers):
        """Test non-PG chunk section (isian + essay)"""
        print("\n--- Testing non-PG chunk section (isian + essay) ---")
        
        response = requests.post(
            f"{BASE_URL}/api/generate",
            headers=auth_headers,
            json={
                "doc_type": "soal",
                "jenjang": "SMA",
                "kelas": "10",
                "kurikulum": "Merdeka",
                "semester": "Ganjil",
                "fase": "E",
                "mata_pelajaran": "Matematika",
                "topik": "Persamaan Linear",
                "alokasi_waktu": 60,
                "tingkat_kesulitan": "Sedang",
                "soal_section": "non_pg",  # Only isian + essay
                "jumlah_pg": 0,
                "jumlah_isian": 2,
                "jumlah_essay": 1,
                "is_chunk": True,
                "sertakan_pembahasan": True
            },
            timeout=180
        )
        
        assert response.status_code == 200, f"Non-PG chunk failed: {response.text}"
        data = response.json()
        
        # Verify only result_html returned
        assert "result_html" in data
        assert "id" not in data
        assert "tokens_used" not in data
        
        # Verify HTML contains isian/essay sections
        html = data["result_html"].lower()
        assert "isian" in html or "essay" in html, "HTML should contain isian or essay content"
        
        print(f"✓ Non-PG chunk returned HTML ({len(data['result_html'])} chars)")
    
    def test_pg_numbering_start(self, auth_headers):
        """Test that pg_numbering_start affects question numbering"""
        print("\n--- Testing pg_numbering_start parameter ---")
        
        # Generate PG starting from number 16
        response = requests.post(
            f"{BASE_URL}/api/generate",
            headers=auth_headers,
            json={
                "doc_type": "soal",
                "jenjang": "SMA",
                "kelas": "10",
                "kurikulum": "Merdeka",
                "semester": "Ganjil",
                "fase": "E",
                "mata_pelajaran": "Matematika",
                "topik": "Aljabar",
                "alokasi_waktu": 60,
                "tingkat_kesulitan": "Mudah",
                "soal_section": "pg",
                "jumlah_pg": 3,
                "jumlah_isian": 0,
                "jumlah_essay": 0,
                "pg_numbering_start": 16,  # Start numbering from 16
                "is_chunk": True,
                "sertakan_pembahasan": False
            },
            timeout=180
        )
        
        assert response.status_code == 200, f"PG chunk with start=16 failed: {response.text}"
        data = response.json()
        
        html = data["result_html"]
        # Check if numbering starts from 16
        assert "16" in html, "HTML should contain question number 16"
        
        print(f"✓ PG chunk with pg_numbering_start=16 generated successfully")
        print(f"  HTML contains '16': {'16' in html}")


class TestNonChunkedGeneration:
    """Test that normal (non-chunked) generation still works"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authentication headers"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "ipankpaul107@gmail.com",
            "password": "Kakiku5."
        })
        assert response.status_code == 200
        token = response.json()["token"]
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_small_pg_does_not_use_chunking(self, auth_headers):
        """Test that small PG counts (<= 15) use normal generation"""
        print("\n--- Testing non-chunked generation (small PG) ---")
        
        # Get initial balance
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "ipankpaul107@gmail.com",
            "password": "Kakiku5."
        })
        initial_balance = login_resp.json()["user"]["token_balance"]
        print(f"Initial token balance: {initial_balance}")
        
        if initial_balance < 1:
            pytest.skip("Not enough tokens")
        
        # Normal generation with small PG count (no is_chunk flag)
        response = requests.post(
            f"{BASE_URL}/api/generate",
            headers=auth_headers,
            json={
                "doc_type": "soal",
                "jenjang": "SMA",
                "kelas": "10",
                "kurikulum": "Merdeka",
                "semester": "Ganjil",
                "fase": "E",
                "mata_pelajaran": "Matematika",
                "topik": "TEST_NonChunked_SmallPG",
                "alokasi_waktu": 60,
                "tingkat_kesulitan": "Mudah",
                "jumlah_pg": 3,  # Small count, no chunking needed
                "jumlah_isian": 1,
                "jumlah_essay": 1,
                "sertakan_pembahasan": False
                # Note: is_chunk is NOT set, defaults to False
            },
            timeout=180
        )
        
        assert response.status_code == 200, f"Non-chunked generation failed: {response.text}"
        data = response.json()
        
        # Verify normal response structure (has id, tokens_used, remaining_tokens)
        assert "id" in data, "id should be in non-chunked response"
        assert "result_html" in data, "result_html should be in response"
        assert "tokens_used" in data, "tokens_used should be in non-chunked response"
        assert "remaining_tokens" in data, "remaining_tokens should be in non-chunked response"
        
        # Verify 1 token deducted
        assert data["tokens_used"] == 1
        assert data["remaining_tokens"] == initial_balance - 1
        
        print(f"✓ Non-chunked generation successful")
        print(f"  id: {data['id']}")
        print(f"  tokens_used: {data['tokens_used']}")
        print(f"  remaining_tokens: {data['remaining_tokens']}")
    
    def test_modul_generation_works(self, auth_headers):
        """Test that non-soal documents (modul) still generate normally"""
        print("\n--- Testing modul generation (non-soal) ---")
        
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "ipankpaul107@gmail.com",
            "password": "Kakiku5."
        })
        initial_balance = login_resp.json()["user"]["token_balance"]
        
        if initial_balance < 1:
            pytest.skip("Not enough tokens")
        
        response = requests.post(
            f"{BASE_URL}/api/generate",
            headers=auth_headers,
            json={
                "doc_type": "modul",  # Not soal, should use normal generation
                "jenjang": "SMA",
                "kelas": "10",
                "kurikulum": "Merdeka",
                "semester": "Ganjil",
                "fase": "E",
                "mata_pelajaran": "Matematika",
                "topik": "TEST_NonChunked_Modul",
                "alokasi_waktu": 90
            },
            timeout=180
        )
        
        assert response.status_code == 200, f"Modul generation failed: {response.text}"
        data = response.json()
        
        # Verify normal response structure
        assert "id" in data
        assert "result_html" in data
        assert "tokens_used" in data
        assert data["tokens_used"] == 1
        
        # Verify it's modul content
        html = data["result_html"].lower()
        assert "modul" in html or "pembelajaran" in html or "tujuan" in html
        
        print(f"✓ Modul generation successful")
        print(f"  id: {data['id']}")


class TestTokenBalanceVerification:
    """Verify token balance changes are correct"""
    
    def test_single_generation_deducts_one_token(self):
        """Verify single generation deducts exactly 1 token"""
        print("\n--- Verifying token deduction ---")
        
        # Login to get initial balance
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "ipankpaul107@gmail.com",
            "password": "Kakiku5."
        })
        initial_balance = login_resp.json()["user"]["token_balance"]
        token = login_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        print(f"Initial balance: {initial_balance}")
        
        if initial_balance < 1:
            pytest.skip("Not enough tokens")
        
        # Generate document
        response = requests.post(
            f"{BASE_URL}/api/generate",
            headers=headers,
            json={
                "doc_type": "rubrik",
                "jenjang": "SMA",
                "kelas": "10",
                "kurikulum": "Merdeka",
                "semester": "Ganjil",
                "fase": "E",
                "mata_pelajaran": "Matematika",
                "topik": "TEST_TokenBalance_Verification",
                "alokasi_waktu": 60
            },
            timeout=180
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify returned remaining_tokens
        assert data["remaining_tokens"] == initial_balance - 1
        
        # Double-check with login
        login_resp2 = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "ipankpaul107@gmail.com",
            "password": "Kakiku5."
        })
        final_balance = login_resp2.json()["user"]["token_balance"]
        
        assert final_balance == initial_balance - 1, f"Expected {initial_balance - 1}, got {final_balance}"
        print(f"✓ Token balance correctly decreased from {initial_balance} to {final_balance}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
