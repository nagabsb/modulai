import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import api from "../utils/api";
import { toast } from "sonner";
import { DOC_TYPE_LABELS, formatShortDate } from "../utils/constants";
import { 
  ArrowLeft, 
  FileText, 
  Search, 
  Filter,
  ChevronRight,
  BookOpen,
  Coins,
  Plus,
  History as HistoryIcon,
  Home,
  ShoppingCart,
  LogOut,
  Menu,
  X,
  Trash2,
  Loader2
} from "lucide-react";

const History = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [generations, setGenerations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    fetchGenerations();
  }, []);

  const fetchGenerations = async () => {
    try {
      const response = await api.get("/generations?limit=100");
      setGenerations(response.data.generations);
    } catch (error) {
      console.error("Failed to fetch generations", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (e, genId) => {
    e.stopPropagation();
    if (!window.confirm("Yakin ingin menghapus dokumen ini? Tindakan ini tidak dapat dibatalkan.")) return;
    setDeletingId(genId);
    try {
      await api.delete(`/generations/${genId}`);
      toast.success("Dokumen berhasil dihapus");
      setGenerations(prev => prev.filter(g => g.id !== genId));
    } catch (error) {
      toast.error(error.response?.data?.detail || "Gagal menghapus dokumen");
    } finally {
      setDeletingId(null);
    }
  };

  const filteredGenerations = generations.filter(gen => {
    const matchesSearch = gen.form_data?.topik?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         gen.form_data?.mata_pelajaran?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === "all" || gen.doc_type === filterType;
    return matchesSearch && matchesFilter;
  });

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const sidebarItems = [
    { icon: <Home className="w-5 h-5" />, label: "Dashboard", path: "/dashboard" },
    { icon: <Plus className="w-5 h-5" />, label: "Buat Dokumen", path: "/generate" },
    { icon: <HistoryIcon className="w-5 h-5" />, label: "Riwayat", path: "/history", active: true },
    { icon: <ShoppingCart className="w-5 h-5" />, label: "Top Up Token", path: "/checkout" },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#1E3A5F] transform transition-transform duration-200 ease-in-out ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } md:translate-x-0 md:static`}>
        <div className="flex flex-col h-full">
          <div className="flex items-center gap-2 p-6 border-b border-white/10">
            <div className="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-white">ModulAI</span>
            <button className="ml-auto md:hidden text-white" onClick={() => setSidebarOpen(false)}>
              <X className="w-6 h-6" />
            </button>
          </div>

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

          <nav className="flex-1 p-4 space-y-1">
            {sidebarItems.map((item) => (
              <button
                key={item.path}
                onClick={() => { navigate(item.path); setSidebarOpen(false); }}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors w-full text-left ${
                  item.active 
                    ? 'bg-white/10 text-white' 
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
            <div className="flex items-center gap-2">
              <Coins className="w-5 h-5 text-[#F4820A]" />
              <span className="font-bold">{user?.token_balance}</span>
            </div>
          </div>
        </header>

        <div className="p-4 md:p-8" data-testid="history-content">
          <div className="mb-8">
            <h1 className="text-2xl md:text-3xl font-bold text-[#1E3A5F] mb-2">Riwayat Dokumen</h1>
            <p className="text-slate-600">Semua dokumen yang pernah Anda generate</p>
          </div>

          {/* Filters */}
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <Input
                placeholder="Cari berdasarkan topik atau mata pelajaran..."
                className="pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                data-testid="history-search"
              />
            </div>
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-full md:w-48" data-testid="history-filter">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Semua Jenis" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Semua Jenis</SelectItem>
                {Object.entries(DOC_TYPE_LABELS).map(([key, label]) => (
                  <SelectItem key={key} value={key}>{label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Results */}
          {loading ? (
            <div className="text-center py-12 text-slate-500">Memuat...</div>
          ) : filteredGenerations.length > 0 ? (
            <div className="space-y-3">
              {filteredGenerations.map((gen) => (
                <Card 
                  key={gen.id} 
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => navigate(`/history/${gen.id}`)}
                  data-testid={`history-item-${gen.id}`}
                >
                  <CardContent className="p-4 flex items-center gap-4">
                    <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <FileText className="w-6 h-6 text-slate-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-slate-900 truncate">
                        {gen.form_data?.topik || "Dokumen"}
                      </p>
                      <p className="text-sm text-slate-500">
                        {gen.form_data?.mata_pelajaran} - {gen.form_data?.jenjang} Kelas {gen.form_data?.kelas}
                      </p>
                    </div>
                    <Badge variant="outline" className="hidden md:inline-flex">
                      {DOC_TYPE_LABELS[gen.doc_type]}
                    </Badge>
                    <span className="text-sm text-slate-400 hidden md:block">
                      {formatShortDate(gen.created_at)}
                    </span>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-slate-400 hover:text-red-600 hover:bg-red-50 h-8 w-8 shrink-0"
                      onClick={(e) => handleDelete(e, gen.id)}
                      disabled={deletingId === gen.id}
                      data-testid={`delete-history-${gen.id}`}
                    >
                      {deletingId === gen.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </Button>
                    <ChevronRight className="w-5 h-5 text-slate-300" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-500 mb-4">
                  {searchTerm || filterType !== "all" 
                    ? "Tidak ada dokumen yang sesuai filter" 
                    : "Belum ada dokumen yang dibuat"}
                </p>
                <Button onClick={() => navigate("/generate")} className="bg-[#1E3A5F] hover:bg-[#162B47]">
                  <Plus className="w-4 h-4 mr-2" />
                  Buat Dokumen Baru
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
};

export default History;
