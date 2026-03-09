import { useState, useEffect } from "react";
import { Routes, Route, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Badge } from "../components/ui/badge";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "../components/ui/table";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "../components/ui/select";
import { Switch } from "../components/ui/switch";
import { toast } from "sonner";
import api from "../utils/api";
import { formatRupiah, formatShortDate, DOC_TYPE_LABELS } from "../utils/constants";
import { 
  LayoutDashboard, 
  Users, 
  CreditCard, 
  FileText, 
  Settings, 
  BarChart3,
  BookOpen,
  LogOut,
  Menu,
  X,
  Coins,
  TrendingUp,
  DollarSign,
  FileCheck,
  Eye,
  Edit,
  Save,
  Loader2,
  Gift,
  Bot,
  Key,
  Zap,
  Trash2,
  Check,
  Plus,
  ChevronUp,
  ChevronDown
} from "lucide-react";

// Admin Dashboard Component
const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get("/admin/dashboard");
      setStats(response.data);
    } catch (error) {
      console.error("Failed to fetch stats", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8 text-center">Memuat...</div>;

  return (
    <div className="p-6 space-y-6" data-testid="admin-dashboard">
      <h1 className="text-2xl font-bold text-[#1E3A5F]">Dashboard Admin</h1>

      {/* Stats Cards */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-[#1E3A5F] to-[#2D4A6F] text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white/70 text-sm">Total Users</p>
                <p className="text-3xl font-bold">{stats?.total_users || 0}</p>
              </div>
              <Users className="w-10 h-10 text-white/30" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-[#10B981] to-[#059669] text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white/70 text-sm">Total Revenue</p>
                <p className="text-3xl font-bold">{formatRupiah(stats?.total_revenue || 0)}</p>
              </div>
              <DollarSign className="w-10 h-10 text-white/30" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-[#F4820A] to-[#D66E00] text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white/70 text-sm">Total Dokumen</p>
                <p className="text-3xl font-bold">{stats?.total_generations || 0}</p>
              </div>
              <FileText className="w-10 h-10 text-white/30" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-500 text-sm">Token Beredar</p>
                <p className="text-3xl font-bold text-slate-900">{stats?.total_tokens_circulation || 0}</p>
              </div>
              <Coins className="w-10 h-10 text-slate-200" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Document Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Dokumen per Jenis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-5 gap-4">
            {stats?.doc_breakdown && Object.entries(stats.doc_breakdown).map(([type, count]) => (
              <div key={type} className="text-center p-4 bg-slate-50 rounded-xl">
                <p className="text-2xl font-bold text-[#1E3A5F]">{count}</p>
                <p className="text-sm text-slate-500">{DOC_TYPE_LABELS[type]}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Transactions */}
      <Card>
        <CardHeader>
          <CardTitle>Transaksi Terbaru</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Order ID</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Tanggal</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {stats?.recent_transactions?.map((tx) => (
                <TableRow key={tx.order_id}>
                  <TableCell className="font-mono text-sm">{tx.order_id}</TableCell>
                  <TableCell>{formatRupiah(tx.gross_amount)}</TableCell>
                  <TableCell>
                    <Badge className={
                      tx.status === "success" ? "bg-green-100 text-green-700" :
                      tx.status === "pending" ? "bg-yellow-100 text-yellow-700" :
                      "bg-red-100 text-red-700"
                    }>
                      {tx.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{formatShortDate(tx.created_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

// Admin Users Component
const AdminUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingUser, setEditingUser] = useState(null);
  const [editTokens, setEditTokens] = useState(0);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await api.get("/admin/users");
      setUsers(response.data.users);
    } catch (error) {
      console.error("Failed to fetch users", error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async (userId) => {
    try {
      await api.put(`/admin/users/${userId}`, { token_balance: editTokens });
      toast.success("User berhasil diupdate");
      setEditingUser(null);
      fetchUsers();
    } catch (error) {
      toast.error("Gagal update user");
    }
  };

  const toggleUserStatus = async (userId, currentStatus) => {
    try {
      await api.put(`/admin/users/${userId}`, { is_active: !currentStatus });
      toast.success("Status user berhasil diubah");
      fetchUsers();
    } catch (error) {
      toast.error("Gagal mengubah status user");
    }
  };

  if (loading) return <div className="p-8 text-center">Memuat...</div>;

  return (
    <div className="p-6" data-testid="admin-users">
      <h1 className="text-2xl font-bold text-[#1E3A5F] mb-6">Manajemen User</h1>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nama</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Token</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Terdaftar</TableHead>
                <TableHead>Aksi</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="font-medium">{user.name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <Badge className={user.role === "super_admin" ? "bg-purple-100 text-purple-700" : "bg-slate-100"}>
                      {user.role}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {editingUser === user.id ? (
                      <div className="flex items-center gap-2">
                        <Input
                          type="number"
                          value={editTokens}
                          onChange={(e) => setEditTokens(parseInt(e.target.value))}
                          className="w-20 h-8"
                        />
                        <Button size="sm" onClick={() => handleUpdateUser(user.id)}>
                          <Save className="w-4 h-4" />
                        </Button>
                      </div>
                    ) : (
                      <span>{user.token_balance}</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Switch
                      checked={user.is_active !== false}
                      onCheckedChange={() => toggleUserStatus(user.id, user.is_active !== false)}
                    />
                  </TableCell>
                  <TableCell>{formatShortDate(user.created_at)}</TableCell>
                  <TableCell>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => { setEditingUser(user.id); setEditTokens(user.token_balance); }}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

// Admin Transactions Component
const AdminTransactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState("all");
  const [verifyingId, setVerifyingId] = useState(null);
  const [proofModal, setProofModal] = useState(null);

  useEffect(() => {
    fetchTransactions();
  }, [filterStatus]);

  const fetchTransactions = async () => {
    try {
      const params = filterStatus !== "all" ? `?status=${filterStatus}` : "";
      const response = await api.get(`/admin/transactions${params}`);
      setTransactions(response.data.transactions);
    } catch (error) {
      console.error("Failed to fetch transactions", error);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (transactionId) => {
    setVerifyingId(transactionId);
    try {
      await api.put(`/admin/transactions/${transactionId}/verify`);
      toast.success("Transaksi dikonfirmasi! Token ditambahkan ke user.");
      fetchTransactions();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Gagal konfirmasi transaksi");
    } finally {
      setVerifyingId(null);
    }
  };

  const handleReject = async (transactionId) => {
    try {
      await api.put(`/admin/transactions/${transactionId}/reject`);
      toast.success("Transaksi ditolak.");
      fetchTransactions();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Gagal menolak transaksi");
    }
  };

  const API_URL = process.env.REACT_APP_BACKEND_URL;

  if (loading) return <div className="p-8 text-center">Memuat...</div>;

  return (
    <div className="p-6" data-testid="admin-transactions">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-[#1E3A5F]">Transaksi</h1>
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Filter Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Semua</SelectItem>
            <SelectItem value="success">Sukses</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="waiting_verification">Menunggu Verifikasi</SelectItem>
            <SelectItem value="failed">Gagal</SelectItem>
            <SelectItem value="rejected">Ditolak</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Proof of payment modal */}
      {proofModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setProofModal(null)}>
          <div className="bg-white rounded-xl max-w-lg w-full p-4" onClick={e => e.stopPropagation()}>
            <h3 className="font-semibold mb-3">Bukti Pembayaran</h3>
            <img 
              src={`${API_URL}/api/uploads/${proofModal}`} 
              alt="Bukti pembayaran" 
              className="max-w-full max-h-96 object-contain mx-auto rounded-lg"
            />
            <Button variant="outline" className="w-full mt-3" onClick={() => setProofModal(null)}>Tutup</Button>
          </div>
        </div>
      )}

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Order ID</TableHead>
                <TableHead>Paket</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Token</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Payment</TableHead>
                <TableHead>Bukti TF</TableHead>
                <TableHead>Tanggal</TableHead>
                <TableHead>Aksi</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.map((tx) => (
                <TableRow key={tx.order_id}>
                  <TableCell className="font-mono text-xs">{tx.order_id}</TableCell>
                  <TableCell className="capitalize">{tx.package_id}</TableCell>
                  <TableCell>{formatRupiah(tx.gross_amount)}</TableCell>
                  <TableCell>{tx.tokens_to_add}</TableCell>
                  <TableCell>
                    <Badge className={
                      tx.status === "success" ? "bg-green-100 text-green-700" :
                      tx.status === "waiting_verification" ? "bg-blue-100 text-blue-700" :
                      tx.status === "pending" ? "bg-yellow-100 text-yellow-700" :
                      tx.status === "rejected" ? "bg-red-100 text-red-700" :
                      "bg-red-100 text-red-700"
                    }>
                      {tx.status === "waiting_verification" ? "Verifikasi" : tx.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <span className="text-xs">{tx.payment_type === "bank_transfer" ? "Bank TF" : tx.payment_type || "-"}</span>
                  </TableCell>
                  <TableCell>
                    {tx.proof_of_payment ? (
                      <button 
                        onClick={() => setProofModal(tx.proof_of_payment)}
                        className="text-blue-600 hover:text-blue-800"
                        data-testid={`view-proof-${tx.order_id}`}
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    ) : (
                      <span className="text-slate-300">-</span>
                    )}
                  </TableCell>
                  <TableCell className="text-xs">{formatShortDate(tx.created_at)}</TableCell>
                  <TableCell>
                    {(tx.status === "waiting_verification" || (tx.status === "pending" && tx.payment_type === "bank_transfer")) && (
                      <div className="flex gap-1">
                        <Button 
                          size="sm" 
                          className="bg-green-600 hover:bg-green-700 h-7 text-xs px-2"
                          onClick={() => handleVerify(tx.id)}
                          disabled={verifyingId === tx.id}
                          data-testid={`verify-${tx.order_id}`}
                        >
                          {verifyingId === tx.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <Check className="w-3 h-3" />}
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          className="h-7 text-xs px-2 text-red-600 border-red-200 hover:bg-red-50"
                          onClick={() => handleReject(tx.id)}
                          data-testid={`reject-${tx.order_id}`}
                        >
                          <X className="w-3 h-3" />
                        </Button>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

// Admin Vouchers Component
const AdminVouchers = () => {
  const [vouchers, setVouchers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [newVoucher, setNewVoucher] = useState({
    code: "",
    discount_type: "percentage",
    discount_value: 10
  });

  useEffect(() => {
    fetchVouchers();
  }, []);

  const fetchVouchers = async () => {
    try {
      const response = await api.get("/admin/vouchers");
      setVouchers(response.data);
    } catch (error) {
      console.error("Failed to fetch vouchers", error);
    } finally {
      setLoading(false);
    }
  };

  const createVoucher = async () => {
    if (!newVoucher.code) {
      toast.error("Kode voucher wajib diisi");
      return;
    }
    setCreating(true);
    try {
      await api.post(`/admin/vouchers?code=${newVoucher.code}&discount_type=${newVoucher.discount_type}&discount_value=${newVoucher.discount_value}`);
      toast.success("Voucher berhasil dibuat");
      setNewVoucher({ code: "", discount_type: "percentage", discount_value: 10 });
      fetchVouchers();
    } catch (error) {
      toast.error("Gagal membuat voucher");
    } finally {
      setCreating(false);
    }
  };

  const toggleVoucherStatus = async (voucherId, currentStatus) => {
    try {
      await api.put(`/admin/vouchers/${voucherId}`, { is_active: !currentStatus });
      toast.success(`Voucher ${!currentStatus ? 'diaktifkan' : 'dinonaktifkan'}`);
      fetchVouchers();
    } catch (error) {
      toast.error("Gagal mengubah status voucher");
    }
  };

  const deleteVoucher = async (voucherId) => {
    if (!window.confirm("Yakin ingin menghapus voucher ini? Tindakan ini tidak dapat dibatalkan.")) {
      return;
    }
    setDeletingId(voucherId);
    try {
      await api.delete(`/admin/vouchers/${voucherId}`);
      toast.success("Voucher berhasil dihapus");
      fetchVouchers();
    } catch (error) {
      toast.error("Gagal menghapus voucher");
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) return <div className="p-8 text-center">Memuat...</div>;

  return (
    <div className="p-6" data-testid="admin-vouchers">
      <h1 className="text-2xl font-bold text-[#1E3A5F] mb-6">Manajemen Voucher</h1>

      {/* Create Voucher */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Buat Voucher Baru</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-end flex-wrap">
            <div className="space-y-2">
              <Label>Kode Voucher</Label>
              <Input
                placeholder="KODE2024"
                value={newVoucher.code}
                onChange={(e) => setNewVoucher({ ...newVoucher, code: e.target.value.toUpperCase() })}
              />
            </div>
            <div className="space-y-2">
              <Label>Tipe Diskon</Label>
              <Select 
                value={newVoucher.discount_type} 
                onValueChange={(v) => setNewVoucher({ ...newVoucher, discount_type: v })}
              >
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="percentage">Persen (%)</SelectItem>
                  <SelectItem value="fixed">Nominal (Rp)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Nilai Diskon</Label>
              <Input
                type="number"
                value={newVoucher.discount_value}
                onChange={(e) => setNewVoucher({ ...newVoucher, discount_value: parseInt(e.target.value) })}
                className="w-24"
              />
            </div>
            <Button onClick={createVoucher} disabled={creating} className="bg-[#1E3A5F] hover:bg-[#162B47]">
              {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : "Buat Voucher"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Voucher List */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Kode</TableHead>
                <TableHead>Tipe</TableHead>
                <TableHead>Nilai</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Dibuat</TableHead>
                <TableHead>Aksi</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {vouchers.map((v) => (
                <TableRow key={v.id}>
                  <TableCell className="font-mono font-bold">{v.code}</TableCell>
                  <TableCell className="capitalize">{v.discount_type === "percentage" ? "Persen" : "Nominal"}</TableCell>
                  <TableCell>
                    {v.discount_type === "percentage" ? `${v.discount_value}%` : formatRupiah(v.discount_value)}
                  </TableCell>
                  <TableCell>
                    <Switch
                      checked={v.is_active}
                      onCheckedChange={() => toggleVoucherStatus(v.id, v.is_active)}
                    />
                  </TableCell>
                  <TableCell>{formatShortDate(v.created_at)}</TableCell>
                  <TableCell>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => deleteVoucher(v.id)}
                      disabled={deletingId === v.id}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      {deletingId === v.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

// Admin AI Settings Component
const AdminAISettings = () => {
  const [keys, setKeys] = useState([]);
  const [providers, setProviders] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showKey, setShowKey] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [newKey, setNewKey] = useState({
    provider: "gemini",
    model: "gemini-2.5-flash",
    api_key: "",
    label: ""
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [keysRes, providersRes] = await Promise.all([
        api.get("/admin/ai-keys"),
        api.get("/ai-providers")
      ]);
      setKeys(keysRes.data);
      setProviders(providersRes.data);
    } catch (error) {
      console.error("Failed to fetch AI settings", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddKey = async () => {
    if (!newKey.api_key) {
      toast.error("API key wajib diisi");
      return;
    }
    setSaving(true);
    try {
      await api.post("/admin/ai-keys", newKey);
      toast.success("API key berhasil ditambahkan!");
      setNewKey({ provider: "gemini", model: "gemini-2.5-flash", api_key: "", label: "" });
      setShowAddForm(false);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Gagal menambahkan key");
    } finally {
      setSaving(false);
    }
  };

  const toggleKey = async (keyId, currentStatus) => {
    try {
      await api.put(`/admin/ai-keys/${keyId}`, { is_active: !currentStatus });
      toast.success(`Key ${!currentStatus ? 'diaktifkan' : 'dinonaktifkan'}`);
      fetchData();
    } catch (error) {
      toast.error("Gagal mengubah status key");
    }
  };

  const deleteKey = async (keyId) => {
    if (!window.confirm("Yakin ingin menghapus key ini?")) return;
    setDeletingId(keyId);
    try {
      await api.delete(`/admin/ai-keys/${keyId}`);
      toast.success("Key berhasil dihapus");
      fetchData();
    } catch (error) {
      toast.error("Gagal menghapus key");
    } finally {
      setDeletingId(null);
    }
  };

  const moveKey = async (keyId, direction) => {
    const idx = keys.findIndex(k => k.id === keyId);
    if ((direction === "up" && idx === 0) || (direction === "down" && idx === keys.length - 1)) return;
    const newKeys = [...keys];
    const swapIdx = direction === "up" ? idx - 1 : idx + 1;
    [newKeys[idx], newKeys[swapIdx]] = [newKeys[swapIdx], newKeys[idx]];
    try {
      await api.put("/admin/ai-keys/reorder", { key_ids: newKeys.map(k => k.id) });
      fetchData();
    } catch (error) {
      toast.error("Gagal mengubah urutan");
    }
  };

  const availableModels = providers[newKey.provider]?.models || {};

  if (loading) return <div className="p-8 text-center">Memuat...</div>;

  return (
    <div className="p-6 space-y-6" data-testid="admin-ai-settings">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-[#1E3A5F]">AI Settings</h1>
        <Button 
          onClick={() => setShowAddForm(!showAddForm)} 
          className="bg-[#F4820A] hover:bg-[#D97008]"
          data-testid="btn-add-key"
        >
          <Plus className="w-4 h-4 mr-2" /> Tambah API Key
        </Button>
      </div>

      {/* Add Key Form */}
      {showAddForm && (
        <Card className="border-[#F4820A]/30 bg-orange-50/30">
          <CardHeader>
            <CardTitle className="text-lg">Tambah API Key Baru</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Provider</Label>
                <Select 
                  value={newKey.provider} 
                  onValueChange={(v) => {
                    const firstModel = Object.keys(providers[v]?.models || {})[0] || "";
                    setNewKey({ ...newKey, provider: v, model: firstModel });
                  }}
                >
                  <SelectTrigger data-testid="select-provider">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(providers).map(([key, p]) => (
                      <SelectItem key={key} value={key}>{p.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Model</Label>
                <Select value={newKey.model} onValueChange={(v) => setNewKey({ ...newKey, model: v })}>
                  <SelectTrigger data-testid="select-model">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(availableModels).map(([key, m]) => (
                      <SelectItem key={key} value={key}>
                        {m.name} — ${m.input_price}/${m.output_price} per 1M token
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label>API Key</Label>
              <div className="flex gap-2">
                <Input
                  type={showKey ? "text" : "password"}
                  placeholder="Masukkan API key..."
                  value={newKey.api_key}
                  onChange={(e) => setNewKey({ ...newKey, api_key: e.target.value })}
                  className="font-mono"
                  data-testid="input-api-key"
                />
                <Button variant="outline" onClick={() => setShowKey(!showKey)}>
                  <Eye className="w-4 h-4" />
                </Button>
              </div>
              {providers[newKey.provider]?.key_url && (
                <p className="text-xs text-slate-500">
                  Dapatkan key di: <a href={providers[newKey.provider].key_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">{providers[newKey.provider].key_url}</a>
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label>Label (opsional)</Label>
              <Input
                placeholder="Contoh: Gemini Key Utama"
                value={newKey.label}
                onChange={(e) => setNewKey({ ...newKey, label: e.target.value })}
                data-testid="input-key-label"
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleAddKey} disabled={saving} className="bg-[#1E3A5F] hover:bg-[#162B47]">
                {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Simpan Key
              </Button>
              <Button variant="outline" onClick={() => setShowAddForm(false)}>Batal</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Fallback Chain Visualization */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-500" />
            Fallback Chain (Urutan Prioritas)
          </CardTitle>
          <p className="text-sm text-slate-500">
            Sistem akan mencoba key dari atas ke bawah. Jika key pertama gagal, otomatis pindah ke key berikutnya.
          </p>
        </CardHeader>
        <CardContent>
          {keys.length === 0 ? (
            <div className="text-center py-8 text-slate-400">
              <Bot className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Belum ada API key. Klik "Tambah API Key" untuk memulai.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {keys.map((key, idx) => {
                const providerInfo = providers[key.provider];
                const modelInfo = providerInfo?.models?.[key.model];
                return (
                  <div 
                    key={key.id}
                    className={`flex items-center gap-3 p-4 rounded-xl border-2 transition-all ${
                      key.is_active 
                        ? key.last_error ? "border-amber-200 bg-amber-50/50" : "border-slate-200 bg-white"
                        : "border-slate-100 bg-slate-50 opacity-60"
                    }`}
                    data-testid={`ai-key-${key.id}`}
                  >
                    {/* Priority number */}
                    <div className="flex flex-col items-center gap-1">
                      <button onClick={() => moveKey(key.id, "up")} disabled={idx === 0} className="text-slate-400 hover:text-slate-600 disabled:opacity-30">
                        <ChevronUp className="w-4 h-4" />
                      </button>
                      <span className="text-lg font-bold text-[#1E3A5F] w-8 text-center">{idx + 1}</span>
                      <button onClick={() => moveKey(key.id, "down")} disabled={idx === keys.length - 1} className="text-slate-400 hover:text-slate-600 disabled:opacity-30">
                        <ChevronDown className="w-4 h-4" />
                      </button>
                    </div>

                    {/* Key Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold truncate">{key.label}</span>
                        <Badge variant="outline" className="text-xs shrink-0">
                          {providerInfo?.name || key.provider}
                        </Badge>
                        {idx === 0 && key.is_active && (
                          <Badge className="bg-[#F4820A] text-white text-xs shrink-0">Utama</Badge>
                        )}
                        {idx > 0 && key.is_active && (
                          <Badge variant="outline" className="text-xs text-slate-500 shrink-0">Fallback</Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-3 text-xs text-slate-500">
                        <span className="font-mono">{key.api_key_masked}</span>
                        <span>{modelInfo?.name || key.model}</span>
                        {modelInfo && (
                          <span className="text-green-600 font-medium">
                            ${modelInfo.input_price} / ${modelInfo.output_price} per 1M
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-3 text-xs mt-1">
                        {key.usage_count > 0 && (
                          <span className="text-slate-400">{key.usage_count}x dipakai</span>
                        )}
                        {key.last_error && (
                          <span className="text-amber-600 truncate max-w-xs" title={key.last_error}>
                            Error: {key.last_error}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 shrink-0">
                      <Switch
                        checked={key.is_active}
                        onCheckedChange={() => toggleKey(key.id, key.is_active)}
                      />
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="h-8 w-8 p-0 text-red-500 hover:bg-red-50"
                        onClick={() => deleteKey(key.id)}
                        disabled={deletingId === key.id}
                      >
                        {deletingId === key.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Provider Pricing Reference */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Harga per Provider (per 1M Token)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Provider</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>Input</TableHead>
                  <TableHead>Output</TableHead>
                  <TableHead>Catatan</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Object.entries(providers).map(([provKey, prov]) => 
                  Object.entries(prov.models).map(([modelKey, model], mIdx) => (
                    <TableRow key={modelKey}>
                      {mIdx === 0 && (
                        <TableCell rowSpan={Object.keys(prov.models).length} className="font-medium align-top">
                          {prov.name}
                        </TableCell>
                      )}
                      <TableCell className="text-sm">{model.name}</TableCell>
                      <TableCell className="font-mono text-sm text-green-600">${model.input_price}</TableCell>
                      <TableCell className="font-mono text-sm text-green-600">${model.output_price}</TableCell>
                      <TableCell className="text-xs text-slate-500">{model.desc}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Main SuperAdmin Component
const SuperAdmin = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const menuItems = [
    { icon: <LayoutDashboard className="w-5 h-5" />, label: "Dashboard", path: "/super-admin" },
    { icon: <Users className="w-5 h-5" />, label: "Users", path: "/super-admin/users" },
    { icon: <CreditCard className="w-5 h-5" />, label: "Transaksi", path: "/super-admin/transactions" },
    { icon: <Gift className="w-5 h-5" />, label: "Voucher", path: "/super-admin/vouchers" },
    { icon: <Bot className="w-5 h-5" />, label: "AI Settings", path: "/super-admin/ai-settings" },
  ];

  const isActive = (path) => {
    if (path === "/super-admin") return location.pathname === path;
    return location.pathname.startsWith(path);
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-slate-100 flex">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 transform transition-transform duration-200 ease-in-out ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } md:translate-x-0 md:static`}>
        <div className="flex flex-col h-full">
          <div className="flex items-center gap-2 p-6 border-b border-white/10">
            <div className="w-10 h-10 bg-[#F4820A] rounded-lg flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-white">Admin Panel</span>
            <button className="ml-auto md:hidden text-white" onClick={() => setSidebarOpen(false)}>
              <X className="w-6 h-6" />
            </button>
          </div>

          <nav className="flex-1 p-4 space-y-1">
            {menuItems.map((item) => (
              <button
                key={item.path}
                onClick={() => { navigate(item.path); setSidebarOpen(false); }}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors w-full text-left ${
                  isActive(item.path)
                    ? 'bg-[#F4820A] text-white' 
                    : 'text-white/70 hover:bg-white/5 hover:text-white'
                }`}
              >
                {item.icon}
                {item.label}
              </button>
            ))}
          </nav>

          <div className="p-4 border-t border-white/10">
            <div className="flex items-center gap-3 px-4 py-2 mb-2">
              <div className="w-10 h-10 bg-[#F4820A] rounded-full flex items-center justify-center text-white font-medium">
                {user?.name?.charAt(0)?.toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium truncate">{user?.name}</p>
                <p className="text-white/50 text-sm">Super Admin</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-4 py-3 w-full rounded-lg text-white/70 hover:bg-white/5 hover:text-white transition-colors"
            >
              <LogOut className="w-5 h-5" />
              Keluar
            </button>
          </div>
        </div>
      </aside>

      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 md:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main Content */}
      <main className="flex-1 min-h-screen">
        <header className="sticky top-0 z-30 bg-white border-b border-slate-200 md:hidden">
          <div className="flex items-center justify-between p-4">
            <button onClick={() => setSidebarOpen(true)}>
              <Menu className="w-6 h-6 text-slate-600" />
            </button>
            <span className="font-bold text-[#1E3A5F]">Admin Panel</span>
            <div className="w-6" />
          </div>
        </header>

        <Routes>
          <Route index element={<AdminDashboard />} />
          <Route path="users" element={<AdminUsers />} />
          <Route path="transactions" element={<AdminTransactions />} />
          <Route path="vouchers" element={<AdminVouchers />} />
          <Route path="ai-settings" element={<AdminAISettings />} />
        </Routes>
      </main>
    </div>
  );
};

export default SuperAdmin;
