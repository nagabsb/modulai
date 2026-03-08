import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { formatRupiah } from "../utils/constants";
import api from "../utils/api";
import { 
  FileText, 
  Zap, 
  Shield, 
  Clock, 
  Check, 
  ArrowRight, 
  Star,
  BookOpen,
  ClipboardList,
  PenTool,
  Award,
  Menu,
  X
} from "lucide-react";

const Landing = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [packages, setPackages] = useState([]);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    fetchPackages();
  }, []);

  const fetchPackages = async () => {
    try {
      const response = await api.get("/packages");
      setPackages(response.data);
    } catch (error) {
      console.error("Failed to fetch packages", error);
    }
  };

  const features = [
    {
      icon: <FileText className="w-6 h-6" />,
      title: "Modul Ajar Lengkap",
      description: "Generate modul ajar dengan CP, TP, ATP sesuai Kurikulum Merdeka dalam hitungan menit."
    },
    {
      icon: <ClipboardList className="w-6 h-6" />,
      title: "RPP & LKPD",
      description: "Buat RPP dan Lembar Kerja Peserta Didik yang terstruktur dan siap pakai."
    },
    {
      icon: <PenTool className="w-6 h-6" />,
      title: "Bank Soal dengan Pembahasan",
      description: "Generate soal PG, isian, essay lengkap dengan kunci dan pembahasan detail."
    },
    {
      icon: <Award className="w-6 h-6" />,
      title: "Rubrik Asesmen",
      description: "Rubrik penilaian profesional dengan kriteria yang jelas dan terukur."
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "AI Cerdas",
      description: "Didukung teknologi AI mutakhir untuk hasil yang akurat dan relevan."
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Sesuai Kurikulum",
      description: "Mendukung Kurikulum Merdeka dan K13 untuk semua jenjang pendidikan."
    }
  ];

  const testimonials = [
    {
      name: "Ibu Sri Wahyuni",
      role: "Guru Matematika SMA",
      avatar: "https://randomuser.me/api/portraits/women/44.jpg",
      text: "ModulAI sangat membantu pekerjaan saya. Dulu butuh berjam-jam untuk buat modul ajar, sekarang cuma beberapa menit!"
    },
    {
      name: "Bapak Ahmad Fauzi",
      role: "Guru IPA SMP",
      avatar: "https://randomuser.me/api/portraits/men/32.jpg",
      text: "Fitur bank soal dengan pembahasan sangat lengkap. Hemat waktu dan hasilnya berkualitas."
    },
    {
      name: "Ibu Dewi Kartika",
      role: "Guru SD",
      avatar: "https://randomuser.me/api/portraits/women/68.jpg",
      text: "Sangat membantu guru-guru di sekolah kami. LKPD yang dihasilkan menarik dan sesuai kurikulum."
    }
  ];

  const docTypes = [
    { icon: <BookOpen className="w-5 h-5" />, name: "Modul Ajar", color: "bg-blue-100 text-blue-700" },
    { icon: <FileText className="w-5 h-5" />, name: "RPP", color: "bg-green-100 text-green-700" },
    { icon: <ClipboardList className="w-5 h-5" />, name: "LKPD", color: "bg-purple-100 text-purple-700" },
    { icon: <PenTool className="w-5 h-5" />, name: "Bank Soal", color: "bg-orange-100 text-orange-700" },
    { icon: <Award className="w-5 h-5" />, name: "Rubrik", color: "bg-pink-100 text-pink-700" },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200">
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 bg-[#1E3A5F] rounded-lg flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-[#1E3A5F]">ModulAI</span>
            </Link>
            
            {/* Desktop Menu */}
            <div className="hidden md:flex items-center gap-6">
              <a href="#features" className="text-slate-600 hover:text-[#1E3A5F] transition-colors">Fitur</a>
              <a href="#pricing" className="text-slate-600 hover:text-[#1E3A5F] transition-colors">Harga</a>
              <a href="#testimonials" className="text-slate-600 hover:text-[#1E3A5F] transition-colors">Testimoni</a>
              {user ? (
                <Button onClick={() => navigate("/dashboard")} className="bg-[#1E3A5F] hover:bg-[#162B47]">
                  Dashboard
                </Button>
              ) : (
                <div className="flex items-center gap-3">
                  <Button variant="ghost" onClick={() => navigate("/login")}>Masuk</Button>
                  <Button onClick={() => navigate("/register")} className="bg-[#F4820A] hover:bg-[#D66E00]">
                    Daftar Gratis
                  </Button>
                </div>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button 
              className="md:hidden p-2"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-slate-200 py-4 px-4">
            <div className="flex flex-col gap-4">
              <a href="#features" className="text-slate-600 hover:text-[#1E3A5F]" onClick={() => setMobileMenuOpen(false)}>Fitur</a>
              <a href="#pricing" className="text-slate-600 hover:text-[#1E3A5F]" onClick={() => setMobileMenuOpen(false)}>Harga</a>
              <a href="#testimonials" className="text-slate-600 hover:text-[#1E3A5F]" onClick={() => setMobileMenuOpen(false)}>Testimoni</a>
              {user ? (
                <Button onClick={() => navigate("/dashboard")} className="bg-[#1E3A5F] hover:bg-[#162B47] w-full">
                  Dashboard
                </Button>
              ) : (
                <div className="flex flex-col gap-2">
                  <Button variant="outline" onClick={() => navigate("/login")} className="w-full">Masuk</Button>
                  <Button onClick={() => navigate("/register")} className="bg-[#F4820A] hover:bg-[#D66E00] w-full">
                    Daftar Gratis
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="pt-24 pb-16 md:pt-32 md:pb-24">
        <div className="container mx-auto px-4 md:px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="animate-slideUp">
              <Badge className="mb-4 bg-[#1E3A5F]/10 text-[#1E3A5F] hover:bg-[#1E3A5F]/20">
                AI-Powered Education Tools
              </Badge>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-[#1E3A5F] leading-tight mb-6">
                Buat Perangkat Ajar dalam Hitungan Menit
              </h1>
              <p className="text-lg text-slate-600 mb-8 leading-relaxed">
                ModulAI membantu guru Indonesia membuat modul ajar, RPP, LKPD, bank soal, dan rubrik asesmen berkualitas tinggi dengan teknologi AI.
              </p>
              
              <div className="flex flex-wrap gap-3 mb-8">
                {docTypes.map((doc, idx) => (
                  <div key={idx} className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${doc.color} text-sm font-medium`}>
                    {doc.icon}
                    {doc.name}
                  </div>
                ))}
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <Button 
                  size="lg"
                  onClick={() => navigate(user ? "/generate" : "/register")}
                  className="bg-[#F4820A] hover:bg-[#D66E00] text-white shadow-lg shadow-orange-500/25"
                  data-testid="cta-get-started"
                >
                  Mulai Gratis
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
                <Button 
                  size="lg"
                  variant="outline"
                  onClick={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })}
                >
                  Lihat Fitur
                </Button>
              </div>

              <div className="flex items-center gap-6 mt-8 text-sm text-slate-500">
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-500" />
                  5 Token Gratis
                </div>
                <div className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-green-500" />
                  Tanpa Kartu Kredit
                </div>
              </div>
            </div>

            <div className="relative animate-fadeIn">
              <div className="absolute -inset-4 bg-gradient-to-r from-[#1E3A5F]/10 to-[#F4820A]/10 rounded-3xl blur-3xl"></div>
              <img 
                src="https://images.unsplash.com/photo-1690861835418-64b46dd72d7b?crop=entropy&cs=srgb&fm=jpg&q=85&w=600"
                alt="Teacher using ModulAI"
                className="relative rounded-2xl shadow-2xl w-full"
              />
              <div className="absolute -bottom-6 -left-6 bg-white rounded-xl shadow-lg p-4 flex items-center gap-3">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <Clock className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <p className="font-semibold text-slate-900">Hemat 90% Waktu</p>
                  <p className="text-sm text-slate-500">Buat dokumen instan</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 md:py-24 bg-white">
        <div className="container mx-auto px-4 md:px-6">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-[#1E3A5F]/10 text-[#1E3A5F]">Fitur Unggulan</Badge>
            <h2 className="text-3xl md:text-4xl font-bold text-[#1E3A5F] mb-4">
              Semua yang Guru Butuhkan
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Lengkapi administrasi mengajar dengan cepat dan mudah menggunakan teknologi AI terdepan.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, idx) => (
              <Card key={idx} className="border border-slate-200 hover:border-[#1E3A5F]/30 hover:shadow-lg transition-all duration-300 group">
                <CardContent className="p-6">
                  <div className="w-12 h-12 bg-[#1E3A5F]/10 rounded-xl flex items-center justify-center mb-4 text-[#1E3A5F] group-hover:bg-[#1E3A5F] group-hover:text-white transition-colors">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-semibold text-slate-900 mb-2">{feature.title}</h3>
                  <p className="text-slate-600">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-16 md:py-24 bg-slate-50">
        <div className="container mx-auto px-4 md:px-6">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-[#F4820A]/10 text-[#F4820A]">Harga Terjangkau</Badge>
            <h2 className="text-3xl md:text-4xl font-bold text-[#1E3A5F] mb-4">
              Pilih Paket Sesuai Kebutuhan
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Token tidak expired. Beli sekali, gunakan kapanpun.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {packages.map((pkg, idx) => (
              <Card 
                key={pkg.id} 
                className={`relative border-2 transition-all duration-300 hover:shadow-xl ${
                  idx === 1 ? 'border-[#F4820A] shadow-lg scale-105 z-10' : 'border-slate-200 hover:border-[#1E3A5F]/30'
                }`}
              >
                {idx === 1 && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge className="bg-[#F4820A] text-white">Populer</Badge>
                  </div>
                )}
                <CardContent className="p-6">
                  <h3 className="text-xl font-bold text-[#1E3A5F] mb-2">{pkg.name}</h3>
                  <div className="mb-4">
                    <span className="text-3xl font-bold text-slate-900">{formatRupiah(pkg.price)}</span>
                  </div>
                  <div className="space-y-3 mb-6">
                    <div className="flex items-center gap-2 text-slate-600">
                      <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
                      <span><strong>{pkg.tokens}</strong> token</span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-600">
                      <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
                      <span>~{pkg.documents_estimate} dokumen</span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-600">
                      <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
                      <span>Token tidak expired</span>
                    </div>
                    <div className="flex items-center gap-2 text-slate-600">
                      <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
                      <span>Semua jenis dokumen</span>
                    </div>
                  </div>
                  <Button 
                    className={`w-full ${idx === 1 ? 'bg-[#F4820A] hover:bg-[#D66E00]' : 'bg-[#1E3A5F] hover:bg-[#162B47]'}`}
                    onClick={() => navigate(user ? `/checkout/${pkg.id}` : '/register')}
                    data-testid={`pricing-${pkg.id}`}
                  >
                    Pilih Paket
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-16 md:py-24 bg-white">
        <div className="container mx-auto px-4 md:px-6">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-[#1E3A5F]/10 text-[#1E3A5F]">Testimoni</Badge>
            <h2 className="text-3xl md:text-4xl font-bold text-[#1E3A5F] mb-4">
              Dipercaya Guru Indonesia
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, idx) => (
              <Card key={idx} className="border border-slate-200">
                <CardContent className="p-6">
                  <div className="flex items-center gap-1 mb-4">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-slate-600 mb-6 italic">"{testimonial.text}"</p>
                  <div className="flex items-center gap-3">
                    <img 
                      src={testimonial.avatar} 
                      alt={testimonial.name}
                      className="w-12 h-12 rounded-full object-cover"
                    />
                    <div>
                      <p className="font-semibold text-slate-900">{testimonial.name}</p>
                      <p className="text-sm text-slate-500">{testimonial.role}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 md:py-24 bg-[#1E3A5F]">
        <div className="container mx-auto px-4 md:px-6 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Siap Hemat Waktu?
          </h2>
          <p className="text-lg text-slate-300 mb-8 max-w-2xl mx-auto">
            Bergabung dengan ribuan guru Indonesia yang sudah menggunakan ModulAI untuk membuat perangkat ajar berkualitas.
          </p>
          <Button 
            size="lg"
            onClick={() => navigate(user ? "/generate" : "/register")}
            className="bg-[#F4820A] hover:bg-[#D66E00] text-white shadow-lg"
            data-testid="cta-bottom"
          >
            Mulai Sekarang - Gratis!
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-slate-900 text-slate-400">
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-[#1E3A5F] rounded-lg flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-white" />
              </div>
              <span className="text-white font-bold">ModulAI</span>
            </div>
            <p className="text-sm">
              2024 ModulAI. Generator Perangkat Ajar AI untuk Guru Indonesia.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
