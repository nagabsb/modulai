import { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { formatRupiah, DOC_TYPE_LABELS, formatShortDate } from "../utils/constants";
import api from "../utils/api";
import { 
  BookOpen, 
  FileText, 
  Coins, 
  Plus, 
  History, 
  Settings, 
  LogOut, 
  ChevronRight,
  Zap,
  Menu,
  X,
  Home,
  ShoppingCart,
  LayoutDashboard
} from "lucide-react";

const Dashboard = () => {
  const { user, logout, refreshUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [recentGenerations, setRecentGenerations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      await refreshUser();
      const response = await api.get("/generations?limit=5");
      setRecentGenerations(response.data.generations);
    } catch (error) {
      console.error("Failed to fetch data", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const sidebarItems = [
    { icon: <Home className="w-5 h-5" />, label: "Dashboard", path: "/dashboard" },
    { icon: <Plus className="w-5 h-5" />, label: "Buat Dokumen", path: "/generate" },
    { icon: <History className="w-5 h-5" />, label: "Riwayat", path: "/history" },
    { icon: <ShoppingCart className="w-5 h-5" />, label: "Top Up Token", path: "/checkout" },
  ];

  const docTypes = [
    { type: "modul", label: "Modul Ajar", icon: <BookOpen className="w-6 h-6" />, color: "bg-blue-500" },
    { type: "rpp", label: "RPP", icon: <FileText className="w-6 h-6" />, color: "bg-green-500" },
    { type: "lkpd", label: "LKPD", icon: <FileText className="w-6 h-6" />, color: "bg-purple-500" },
    { type: "soal", label: "Bank Soal", icon: <FileText className="w-6 h-6" />, color: "bg-orange-500" },
    { type: "rubrik", label: "Rubrik", icon: <FileText className="w-6 h-6" />, color: "bg-pink-500" },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#1E3A5F] transform transition-transform duration-200 ease-in-out ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } md:translate-x-0 md:static`}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center gap-2 p-6 border-b border-white/10">
            <div className="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-white">ModulAI</span>
            <button 
              className="ml-auto md:hidden text-white"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Token Balance */}
          <div className="p-4 mx-4 mt-4 bg-white/10 rounded-xl">
            <div className="flex items-center gap-2 text-white/70 text-sm mb-1">
              <Coins className="w-4 h-4" />
              Saldo Token
            </div>
            <div className="text-2xl font-bold text-white">{user?.token_balance || 0}</div>
            <Button 
              size="sm" 
              className="w-full mt-3 bg-[#F4820A] hover:bg-[#D66E00] text-white"
              onClick={() => navigate("/checkout")}
            >
              <Plus className="w-4 h-4 mr-1" />
              Top Up
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1">
            {sidebarItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  location.pathname === item.path 
                    ? 'bg-white/10 text-white' 
                    : 'text-white/70 hover:bg-white/5 hover:text-white'
                }`}
                onClick={() => setSidebarOpen(false)}
              >
                {item.icon}
                {item.label}
              </Link>
            ))}
          </nav>

          {/* User & Logout */}
          <div className="p-4 border-t border-white/10">
            <div className="flex items-center gap-3 px-4 py-2 mb-2">
              <div className="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center text-white font-medium">
                {user?.name?.charAt(0)?.toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium truncate">{user?.name}</p>
                <p className="text-white/50 text-sm truncate">{user?.email}</p>
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

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <main className="flex-1 min-h-screen">
        {/* Mobile Header */}
        <header className="sticky top-0 z-30 bg-white border-b border-slate-200 md:hidden">
          <div className="flex items-center justify-between p-4">
            <button onClick={() => setSidebarOpen(true)}>
              <Menu className="w-6 h-6 text-slate-600" />
            </button>
            <div className="flex items-center gap-2">
              <Coins className="w-5 h-5 text-[#F4820A]" />
              <span className="font-bold">{user?.token_balance}</span>
            </div>
          </div>
        </header>

        <div className="p-4 md:p-8" data-testid="dashboard-content">
          {/* Welcome */}
          <div className="mb-8">
            <h1 className="text-2xl md:text-3xl font-bold text-[#1E3A5F] mb-2">
              Selamat Datang, {user?.name?.split(' ')[0]}!
            </h1>
            <p className="text-slate-600">
              Mulai buat perangkat ajar dengan AI. Anda memiliki <strong>{user?.token_balance} token</strong>.
            </p>
          </div>

          {/* Quick Actions */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Buat Dokumen Baru</h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {docTypes.map((doc) => (
                <Card 
                  key={doc.type}
                  className="cursor-pointer hover:shadow-lg transition-all border-2 border-transparent hover:border-[#1E3A5F]/20"
                  onClick={() => navigate(`/generate?type=${doc.type}`)}
                  data-testid={`quick-action-${doc.type}`}
                >
                  <CardContent className="p-4 text-center">
                    <div className={`w-12 h-12 ${doc.color} rounded-xl flex items-center justify-center mx-auto mb-3 text-white`}>
                      {doc.icon}
                    </div>
                    <p className="font-medium text-slate-900 text-sm">{doc.label}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            <Card className="bg-gradient-to-br from-[#1E3A5F] to-[#2D4A6F] text-white">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white/70 text-sm">Saldo Token</p>
                    <p className="text-3xl font-bold mt-1">{user?.token_balance || 0}</p>
                  </div>
                  <Coins className="w-10 h-10 text-white/30" />
                </div>
                <Button 
                  size="sm" 
                  className="mt-4 bg-white/20 hover:bg-white/30 text-white w-full"
                  onClick={() => navigate("/checkout")}
                >
                  Top Up Token
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-slate-500 text-sm">Dokumen Dibuat</p>
                    <p className="text-3xl font-bold text-slate-900 mt-1">{recentGenerations.length}</p>
                  </div>
                  <FileText className="w-10 h-10 text-slate-200" />
                </div>
                <Button 
                  variant="outline"
                  size="sm" 
                  className="mt-4 w-full"
                  onClick={() => navigate("/history")}
                >
                  Lihat Riwayat
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-[#F4820A] to-[#FF9A2E] text-white">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white/70 text-sm">Aksi Cepat</p>
                    <p className="text-xl font-bold mt-1">Generate dengan AI</p>
                  </div>
                  <Zap className="w-10 h-10 text-white/30" />
                </div>
                <Button 
                  size="sm" 
                  className="mt-4 bg-white/20 hover:bg-white/30 text-white w-full"
                  onClick={() => navigate("/generate")}
                >
                  Mulai Generate
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Recent Generations */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-900">Dokumen Terbaru</h2>
              <Link to="/history" className="text-[#F4820A] text-sm font-medium hover:underline flex items-center gap-1">
                Lihat Semua <ChevronRight className="w-4 h-4" />
              </Link>
            </div>

            {loading ? (
              <div className="text-center py-8 text-slate-500">Memuat...</div>
            ) : recentGenerations.length > 0 ? (
              <div className="space-y-3">
                {recentGenerations.map((gen) => (
                  <Card 
                    key={gen.id} 
                    className="cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => navigate(`/history/${gen.id}`)}
                  >
                    <CardContent className="p-4 flex items-center gap-4">
                      <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
                        <FileText className="w-5 h-5 text-slate-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-slate-900 truncate">
                          {gen.form_data?.topik || "Dokumen"}
                        </p>
                        <p className="text-sm text-slate-500">
                          {gen.form_data?.mata_pelajaran} - {gen.form_data?.kelas}
                        </p>
                      </div>
                      <Badge variant="outline">{DOC_TYPE_LABELS[gen.doc_type]}</Badge>
                      <span className="text-sm text-slate-400">{formatShortDate(gen.created_at)}</span>
                      <ChevronRight className="w-5 h-5 text-slate-300" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <FileText className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                  <p className="text-slate-500 mb-4">Belum ada dokumen yang dibuat</p>
                  <Button onClick={() => navigate("/generate")} className="bg-[#1E3A5F] hover:bg-[#162B47]">
                    <Plus className="w-4 h-4 mr-2" />
                    Buat Dokumen Pertama
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
