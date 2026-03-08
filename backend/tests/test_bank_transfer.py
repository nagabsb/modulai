"""
Bank Transfer Feature Tests
Tests dual payment method (Bank Transfer + E-Wallet via Midtrans)
- Bank transfer endpoints
- Admin verify/reject functionality
- File upload for proof of payment
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "ipankpaul107@gmail.com"
ADMIN_PASSWORD = "Kakiku5."

class TestBankTransferEndpoints:
    """Tests for bank transfer payment flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: get admin auth token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin to get token
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("token")  # Fixed: field is 'token' not 'access_token'
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            pytest.skip(f"Authentication failed: {response.status_code}")
    
    # Test 1: GET /api/payment/bank-accounts - returns BCA account details
    def test_get_bank_accounts(self):
        """GET /api/payment/bank-accounts - should return BCA account details"""
        response = self.session.get(f"{BASE_URL}/api/payment/bank-accounts")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Expected list of bank accounts"
        assert len(data) > 0, "Expected at least one bank account"
        
        # Verify BCA account details
        bca_account = data[0]
        assert bca_account.get("bank") == "BCA", "Expected BCA bank"
        assert bca_account.get("account_number") == "2470230889", "Expected BCA account number 2470230889"
        assert bca_account.get("account_name") == "NAJMI ABUBAKAR BASUMBUL", "Expected account name NAJMI ABUBAKAR BASUMBUL"
        
        print(f"✓ Bank accounts endpoint returns correct BCA details: {bca_account}")
    
    # Test 2: POST /api/payment/bank-transfer - creates bank transfer transaction
    def test_create_bank_transfer_transaction(self):
        """POST /api/payment/bank-transfer with package_id=starter - should create bank transfer transaction with unique code"""
        response = self.session.post(f"{BASE_URL}/api/payment/bank-transfer", json={
            "package_id": "starter",
            "name": "TEST Bank Transfer User",
            "email": "test_bt@example.com",
            "phone": "08123456789"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
        
        data = response.json()
        
        # Verify response fields
        assert "order_id" in data, "Expected order_id in response"
        assert data["order_id"].startswith("BT-"), f"Order ID should start with BT-, got {data['order_id']}"
        
        assert "amount" in data, "Expected amount in response"
        assert "unique_code" in data, "Expected unique_code in response"
        assert 1 <= data["unique_code"] <= 999, f"Unique code should be 1-999, got {data['unique_code']}"
        
        assert "bank_account" in data, "Expected bank_account in response"
        assert data["bank_account"]["bank"] == "BCA"
        assert data["bank_account"]["account_number"] == "2470230889"
        
        assert "package" in data, "Expected package in response"
        
        print(f"✓ Bank transfer transaction created: order_id={data['order_id']}, amount={data['amount']}, unique_code={data['unique_code']}")
        
        # Store order_id for subsequent tests
        self.__class__.test_order_id = data["order_id"]
        return data
    
    # Test 3: GET /api/payment/bank-transfer/{order_id} - returns transaction details
    def test_get_bank_transfer_status(self):
        """GET /api/payment/bank-transfer/{order_id} - should return transaction details"""
        # First create a transaction
        create_response = self.session.post(f"{BASE_URL}/api/payment/bank-transfer", json={
            "package_id": "starter",
            "name": "TEST Status Check User",
            "email": "test_status@example.com",
            "phone": "08123456789"
        })
        assert create_response.status_code == 200
        order_id = create_response.json()["order_id"]
        
        # Get transaction status
        response = self.session.get(f"{BASE_URL}/api/payment/bank-transfer/{order_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["order_id"] == order_id
        assert data["status"] == "pending", f"Expected status 'pending', got {data['status']}"
        assert data["payment_type"] == "bank_transfer"
        assert "gross_amount" in data
        assert "unique_code" in data
        assert "bank_account" in data
        
        print(f"✓ Bank transfer status retrieved: order_id={order_id}, status={data['status']}")
    
    # Test 4: Admin GET /api/admin/transactions - shows bank transfer transactions
    def test_admin_get_transactions_with_bank_transfer(self):
        """Admin: GET /api/admin/transactions - should show bank transfer transactions with payment_type=bank_transfer"""
        response = self.session.get(f"{BASE_URL}/api/admin/transactions")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "transactions" in data
        assert "total" in data
        
        # Find bank transfer transactions
        bank_transfers = [tx for tx in data["transactions"] if tx.get("payment_type") == "bank_transfer"]
        
        if len(bank_transfers) > 0:
            tx = bank_transfers[0]
            assert tx.get("payment_type") == "bank_transfer"
            assert "order_id" in tx
            assert tx["order_id"].startswith("BT-")
            print(f"✓ Found {len(bank_transfers)} bank transfer transactions. Sample: {tx['order_id']}")
        else:
            print("✓ No bank transfer transactions found yet (may need to create first)")
    
    # Test 5: Admin verify transaction - marks as success and adds tokens
    def test_admin_verify_transaction(self):
        """Admin: PUT /api/admin/transactions/{id}/verify - should mark transaction as success and add tokens to user"""
        # First create a bank transfer transaction
        create_response = self.session.post(f"{BASE_URL}/api/payment/bank-transfer", json={
            "package_id": "starter",
            "name": "TEST Verify User",
            "email": "test_verify@example.com",
            "phone": "08123456789"
        })
        assert create_response.status_code == 200
        order_id = create_response.json()["order_id"]
        
        # Get the transaction to find its ID
        # First get all transactions and find by order_id
        txns_response = self.session.get(f"{BASE_URL}/api/admin/transactions")
        assert txns_response.status_code == 200
        
        transactions = txns_response.json()["transactions"]
        test_tx = next((tx for tx in transactions if tx["order_id"] == order_id), None)
        
        assert test_tx is not None, f"Transaction with order_id {order_id} not found"
        transaction_id = test_tx["id"]
        
        # Verify the transaction
        verify_response = self.session.put(f"{BASE_URL}/api/admin/transactions/{transaction_id}/verify")
        
        assert verify_response.status_code == 200, f"Expected 200, got {verify_response.status_code}. Response: {verify_response.text}"
        
        verify_data = verify_response.json()
        assert "message" in verify_data
        assert "token" in verify_data["message"].lower() or "dikonfirmasi" in verify_data["message"].lower()
        
        # Verify transaction status changed to success
        check_response = self.session.get(f"{BASE_URL}/api/admin/transactions")
        transactions = check_response.json()["transactions"]
        verified_tx = next((tx for tx in transactions if tx["id"] == transaction_id), None)
        
        assert verified_tx is not None
        assert verified_tx["status"] == "success", f"Expected status 'success', got {verified_tx['status']}"
        
        print(f"✓ Transaction {order_id} verified successfully. Status: {verified_tx['status']}")
    
    # Test 6: Admin reject transaction - marks as rejected
    def test_admin_reject_transaction(self):
        """Admin: PUT /api/admin/transactions/{id}/reject - should mark transaction as rejected"""
        # First create a bank transfer transaction
        create_response = self.session.post(f"{BASE_URL}/api/payment/bank-transfer", json={
            "package_id": "starter",
            "name": "TEST Reject User",
            "email": "test_reject@example.com",
            "phone": "08123456789"
        })
        assert create_response.status_code == 200
        order_id = create_response.json()["order_id"]
        
        # Get the transaction to find its ID
        txns_response = self.session.get(f"{BASE_URL}/api/admin/transactions")
        assert txns_response.status_code == 200
        
        transactions = txns_response.json()["transactions"]
        test_tx = next((tx for tx in transactions if tx["order_id"] == order_id), None)
        
        assert test_tx is not None, f"Transaction with order_id {order_id} not found"
        transaction_id = test_tx["id"]
        
        # Reject the transaction
        reject_response = self.session.put(f"{BASE_URL}/api/admin/transactions/{transaction_id}/reject")
        
        assert reject_response.status_code == 200, f"Expected 200, got {reject_response.status_code}. Response: {reject_response.text}"
        
        reject_data = reject_response.json()
        assert "message" in reject_data
        
        # Verify transaction status changed to rejected
        check_response = self.session.get(f"{BASE_URL}/api/admin/transactions")
        transactions = check_response.json()["transactions"]
        rejected_tx = next((tx for tx in transactions if tx["id"] == transaction_id), None)
        
        assert rejected_tx is not None
        assert rejected_tx["status"] == "rejected", f"Expected status 'rejected', got {rejected_tx['status']}"
        
        print(f"✓ Transaction {order_id} rejected successfully. Status: {rejected_tx['status']}")
    
    # Test 7: Admin filter transactions by waiting_verification status
    def test_admin_filter_transactions_by_status(self):
        """Admin can filter transactions by 'waiting_verification' status"""
        # Test various status filters
        statuses_to_test = ["pending", "success", "waiting_verification", "rejected"]
        
        for status in statuses_to_test:
            response = self.session.get(f"{BASE_URL}/api/admin/transactions?status={status}")
            
            assert response.status_code == 200, f"Expected 200 for status={status}, got {response.status_code}"
            
            data = response.json()
            assert "transactions" in data
            
            # Verify all returned transactions have the correct status
            for tx in data["transactions"]:
                assert tx["status"] == status, f"Expected status '{status}', got '{tx['status']}'"
            
            print(f"✓ Filter by status='{status}' returned {len(data['transactions'])} transactions")
    
    # Test 8: Verify cannot verify already successful transaction
    def test_cannot_verify_success_transaction(self):
        """Should not be able to verify an already successful transaction"""
        # Create and verify a transaction first
        create_response = self.session.post(f"{BASE_URL}/api/payment/bank-transfer", json={
            "package_id": "starter",
            "name": "TEST Double Verify User",
            "email": "test_double@example.com",
            "phone": "08123456789"
        })
        assert create_response.status_code == 200
        order_id = create_response.json()["order_id"]
        
        # Get transaction ID
        txns_response = self.session.get(f"{BASE_URL}/api/admin/transactions")
        transactions = txns_response.json()["transactions"]
        test_tx = next((tx for tx in transactions if tx["order_id"] == order_id), None)
        transaction_id = test_tx["id"]
        
        # First verify
        first_verify = self.session.put(f"{BASE_URL}/api/admin/transactions/{transaction_id}/verify")
        assert first_verify.status_code == 200
        
        # Try to verify again - should fail
        second_verify = self.session.put(f"{BASE_URL}/api/admin/transactions/{transaction_id}/verify")
        assert second_verify.status_code == 400, f"Expected 400 for double verify, got {second_verify.status_code}"
        
        print(f"✓ Double verify correctly rejected with status 400")
    
    # Test 9: Verify cannot reject successful transaction
    def test_cannot_reject_success_transaction(self):
        """Should not be able to reject an already successful transaction"""
        # Create and verify a transaction first
        create_response = self.session.post(f"{BASE_URL}/api/payment/bank-transfer", json={
            "package_id": "starter",
            "name": "TEST Reject After Success",
            "email": "test_reject_success@example.com",
            "phone": "08123456789"
        })
        assert create_response.status_code == 200
        order_id = create_response.json()["order_id"]
        
        # Get transaction ID
        txns_response = self.session.get(f"{BASE_URL}/api/admin/transactions")
        transactions = txns_response.json()["transactions"]
        test_tx = next((tx for tx in transactions if tx["order_id"] == order_id), None)
        transaction_id = test_tx["id"]
        
        # First verify
        verify_response = self.session.put(f"{BASE_URL}/api/admin/transactions/{transaction_id}/verify")
        assert verify_response.status_code == 200
        
        # Try to reject - should fail
        reject_response = self.session.put(f"{BASE_URL}/api/admin/transactions/{transaction_id}/reject")
        assert reject_response.status_code == 400, f"Expected 400 for reject after success, got {reject_response.status_code}"
        
        print(f"✓ Reject after success correctly rejected with status 400")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
