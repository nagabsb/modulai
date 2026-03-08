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
  Zap
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
            <SelectItem value="failed">Gagal</SelectItem>
          </SelectContent>
        </Select>
      </div>

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
                <TableHead>Tanggal</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {transactions.map((tx) => (
                <TableRow key={tx.order_id}>
                  <TableCell className="font-mono text-sm">{tx.order_id}</TableCell>
                  <TableCell className="capitalize">{tx.package_id}</TableCell>
                  <TableCell>{formatRupiah(tx.gross_amount)}</TableCell>
                  <TableCell>{tx.tokens_to_add}</TableCell>
                  <TableCell>
                    <Badge className={
                      tx.status === "success" ? "bg-green-100 text-green-700" :
                      tx.status === "pending" ? "bg-yellow-100 text-yellow-700" :
                      "bg-red-100 text-red-700"
                    }>
                      {tx.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{tx.payment_type || "-"}</TableCell>
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

// Admin Vouchers Component
const AdminVouchers = () => {
  const [vouchers, setVouchers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
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
          <div className="flex gap-4 items-end">
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
            <Button onClick={createVoucher} disabled={creating}>
              {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : "Buat"}
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
                    <Badge className={v.is_active ? "bg-green-100 text-green-700" : "bg-slate-100"}>
                      {v.is_active ? "Aktif" : "Nonaktif"}
                    </Badge>
                  </TableCell>
                  <TableCell>{formatShortDate(v.created_at)}</TableCell>
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
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    provider: "gemini_flash_lite",
    gemini_api_key: ""
  });
  const [showKey, setShowKey] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await api.get("/admin/ai-settings");
      setSettings(response.data);
      setFormData({
        provider: response.data.provider || "gemini_flash_lite",
        gemini_api_key: ""
      });
    } catch (error) {
      console.error("Failed to fetch AI settings", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put("/admin/ai-settings", {
        provider: formData.provider,
        gemini_api_key: formData.gemini_api_key || null
      });
      toast.success("AI Settings berhasil disimpan!");
      fetchSettings();
    } catch (error) {
      toast.error("Gagal menyimpan settings");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-8 text-center">Memuat...</div>;

  return (
    <div className="p-6 space-y-6" data-testid="admin-ai-settings">
      <h1 className="text-2xl font-bold text-[#1E3A5F]">AI Settings</h1>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="w-5 h-5" />
            Konfigurasi AI Provider
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Current Settings */}
          <div className="p-4 bg-slate-50 rounded-xl">
            <h3 className="font-medium mb-3">Settings Aktif</h3>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-slate-500">Provider:</span>
                <p className="font-medium">
                  {settings?.provider === "gemini_pro" ? "Gemini Pro" : "Gemini Flash-Lite"}
                </p>
              </div>
              <div>
                <span className="text-slate-500">Model:</span>
                <p className="font-medium">{settings?.model || "gemini-2.0-flash-lite"}</p>
              </div>
              <div>
                <span className="text-slate-500">API Key:</span>
                <p className="font-medium font-mono text-xs">{settings?.gemini_api_key_masked || "***"}</p>
              </div>
            </div>
          </div>

          {/* Provider Selection */}
          <div className="space-y-2">
            <Label>AI Provider</Label>
            <Select value={formData.provider} onValueChange={(v) => setFormData({ ...formData, provider: v })}>
              <SelectTrigger data-testid="select-ai-provider">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="gemini_flash_lite">
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-yellow-500" />
                    Gemini 2.0 Flash-Lite (Cepat & Hemat)
                  </div>
                </SelectItem>
                <SelectItem value="gemini_pro">
                  <div className="flex items-center gap-2">
                    <Bot className="w-4 h-4 text-blue-500" />
                    Gemini 2.0 Pro (Kualitas Tinggi)
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-slate-500">
              Flash-Lite: Respon cepat, cocok untuk dokumen standar. Pro: Kualitas lebih baik untuk konten kompleks.
            </p>
          </div>

          {/* API Key */}
          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <Key className="w-4 h-4" />
              Gemini API Key (Opsional)
            </Label>
            <div className="flex gap-2">
              <Input
                type={showKey ? "text" : "password"}
                placeholder="Masukkan API key baru (kosongkan jika tidak ingin mengubah)"
                value={formData.gemini_api_key}
                onChange={(e) => setFormData({ ...formData, gemini_api_key: e.target.value })}
                className="font-mono"
                data-testid="input-gemini-key"
              />
              <Button variant="outline" onClick={() => setShowKey(!showKey)}>
                <Eye className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-xs text-slate-500">
              Dapatkan API key di: <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google AI Studio</a>
            </p>
          </div>

          {/* Provider Info */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 border border-slate-200 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="w-5 h-5 text-yellow-500" />
                <span className="font-medium">Flash-Lite</span>
              </div>
              <ul className="text-sm text-slate-600 space-y-1">
                <li>Respon dalam 2-5 detik</li>
                <li>Cocok untuk dokumen standar</li>
                <li>Hemat kuota API</li>
              </ul>
            </div>
            <div className="p-4 border border-slate-200 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <Bot className="w-5 h-5 text-blue-500" />
                <span className="font-medium">Pro</span>
              </div>
              <ul className="text-sm text-slate-600 space-y-1">
                <li>Respon 5-15 detik</li>
                <li>Kualitas output lebih detail</li>
                <li>Cocok untuk soal kompleks</li>
              </ul>
            </div>
          </div>

          <Button onClick={handleSave} disabled={saving} className="w-full bg-[#1E3A5F] hover:bg-[#162B47]">
            {saving ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Menyimpan...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Simpan Settings
              </>
            )}
          </Button>
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
