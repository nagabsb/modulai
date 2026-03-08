import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { RadioGroup, RadioGroupItem } from "../components/ui/radio-group";
import { toast } from "sonner";
import api from "../utils/api";
import { formatRupiah } from "../utils/constants";
import { 
  ArrowLeft, 
  ArrowRight, 
  Check, 
  Coins, 
  CreditCard, 
  Wallet, 
  Building2,
  QrCode,
  Loader2,
  Gift,
  Star,
  ChevronRight
} from "lucide-react";

const MIDTRANS_CLIENT_KEY = "SB-Mid-client-RlztC9s1e9UMUkE6";

const Checkout = () => {
  const { packageId } = useParams();
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [packages, setPackages] = useState([]);
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [voucherCode, setVoucherCode] = useState("");
  const [voucherApplied, setVoucherApplied] = useState(null);
  const [applyingVoucher, setApplyingVoucher] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState("bank");
  
  const [formData, setFormData] = useState({
    name: user?.name || "",
    email: user?.email || "",
    phone: user?.phone || ""
  });

  useEffect(() => {
    fetchPackages();
    loadMidtransScript();
  }, []);

  useEffect(() => {
    if (packages.length > 0 && packageId) {
      const pkg = packages.find(p => p.id === packageId);
      if (pkg) setSelectedPackage(pkg);
    }
  }, [packages, packageId]);

  const loadMidtransScript = () => {
    if (document.getElementById("midtrans-script")) return;
    
    const script = document.createElement("script");
    script.id = "midtrans-script";
    script.src = "https://app.sandbox.midtrans.com/snap/snap.js";
    script.setAttribute("data-client-key", MIDTRANS_CLIENT_KEY);
    document.head.appendChild(script);
  };

  const fetchPackages = async () => {
    try {
      const response = await api.get("/packages");
      setPackages(response.data);
      if (!packageId && response.data.length > 0) {
        setSelectedPackage(response.data[1]); // Default to Pro
      }
    } catch (error) {
      console.error("Failed to fetch packages", error);
    }
  };

  const applyVoucher = async () => {
    if (!voucherCode.trim() || !selectedPackage) return;
    
    setApplyingVoucher(true);
    try {
      const response = await api.post("/voucher/apply", {
        code: voucherCode,
        package_id: selectedPackage.id
      });
      setVoucherApplied(response.data);
      toast.success(response.data.message);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Kode voucher tidak valid");
      setVoucherApplied(null);
    } finally {
      setApplyingVoucher(false);
    }
  };

  const getFinalPrice = () => {
    if (!selectedPackage) return 0;
    if (voucherApplied) return voucherApplied.final_price;
    return selectedPackage.price;
  };

  const getDiscount = () => {
    if (voucherApplied) return voucherApplied.discount;
    return 0;
  };

  const handlePayment = async () => {
    if (!formData.name || !formData.email || !formData.phone) {
      toast.error("Mohon lengkapi data Anda");
      return;
    }

    setLoading(true);
    try {
      if (paymentMethod === "bank") {
        // Bank Transfer - create transaction and redirect to transfer page
        const response = await api.post("/payment/bank-transfer", {
          package_id: selectedPackage.id,
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
          voucher_code: voucherApplied ? voucherCode : null
        });
        navigate(`/bank-transfer/${response.data.order_id}`);
      } else {
        // E-Wallet / QRIS - use Midtrans
        const response = await api.post("/payment/create", {
          package_id: selectedPackage.id,
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
          voucher_code: voucherApplied ? voucherCode : null
        });

        window.snap.pay(response.data.token, {
          onSuccess: async function(result) {
            toast.success("Pembayaran berhasil!");
            await refreshUser();
            navigate("/dashboard");
          },
          onPending: function(result) {
            toast.info("Menunggu pembayaran...");
            navigate("/dashboard");
          },
          onError: function(result) {
            toast.error("Pembayaran gagal");
          },
          onClose: function() {
            toast.info("Popup pembayaran ditutup");
          }
        });
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Gagal memproses pembayaran");
    } finally {
      setLoading(false);
    }
  };

  const testimonials = [
    {
      name: "Ibu Sri Wahyuni",
      role: "Guru Matematika SMA",
      avatar: "https://randomuser.me/api/portraits/women/44.jpg",
      text: "ModulAI sangat membantu! Dokumen yang dihasilkan berkualitas dan sesuai kurikulum."
    },
    {
      name: "Bapak Ahmad Fauzi",
      role: "Guru IPA SMP",
      avatar: "https://randomuser.me/api/portraits/men/32.jpg",
      text: "Hemat waktu dan tenaga. Bank soal yang dihasilkan lengkap dengan pembahasan."
    },
    {
      name: "Ibu Dewi Kartika",
      role: "Guru SD",
      avatar: "https://randomuser.me/api/portraits/women/68.jpg",
      text: "LKPD yang dihasilkan menarik dan mudah dipahami siswa. Sangat recommended!"
    }
  ];

  return (
    <div className="min-h-screen bg-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Button variant="ghost" onClick={() => navigate(-1)}>
            <ArrowLeft className="w-5 h-5 mr-2" />
            Kembali
          </Button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#1E3A5F] rounded-lg flex items-center justify-center">
              <Coins className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-[#1E3A5F]">ModulAI</span>
          </div>
          <div className="w-24" />
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {/* Left Column - Info & Testimonials */}
          <div className="order-2 lg:order-1">
            <div className="sticky top-24">
              <div className="bg-[#1E3A5F] rounded-2xl p-8 text-white mb-6">
                <h2 className="text-2xl font-bold mb-2">Top Up Token ModulAI</h2>
                <p className="text-white/70">
                  Dapatkan akses ke semua fitur generator dokumen AI. Token tidak pernah kadaluarsa.
                </p>
              </div>

              {/* Package Selection (if not selected) */}
              {!packageId && (
                <div className="bg-white rounded-2xl p-6 mb-6">
                  <h3 className="font-semibold text-lg mb-4">Pilih Paket</h3>
                  <div className="space-y-3">
                    {packages.map((pkg, idx) => (
                      <div
                        key={pkg.id}
                        onClick={() => { setSelectedPackage(pkg); setVoucherApplied(null); }}
                        className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                          selectedPackage?.id === pkg.id 
                            ? 'border-[#10B981] bg-[#10B981]/5' 
                            : 'border-slate-200 hover:border-slate-300'
                        }`}
                        data-testid={`package-${pkg.id}`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-semibold">{pkg.name}</span>
                              {idx === 1 && <Badge className="bg-[#F4820A] text-white text-xs">Populer</Badge>}
                            </div>
                            <p className="text-sm text-slate-500">{pkg.tokens} token (~{pkg.documents_estimate} dokumen)</p>
                          </div>
                          <div className="text-right">
                            <p className="font-bold text-lg">{formatRupiah(pkg.price)}</p>
                            {selectedPackage?.id === pkg.id && (
                              <Check className="w-5 h-5 text-[#10B981] ml-auto" />
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Testimonials */}
              <div className="bg-white rounded-2xl p-6">
                <h3 className="font-semibold text-lg mb-4">Apa Kata Mereka?</h3>
                <div className="space-y-4">
                  {testimonials.map((t, idx) => (
                    <div key={idx} className="flex gap-4">
                      <img src={t.avatar} alt={t.name} className="w-12 h-12 rounded-full object-cover flex-shrink-0" />
                      <div>
                        <p className="text-slate-600 text-sm italic mb-2">"{t.text}"</p>
                        <p className="font-medium text-sm">{t.name}</p>
                        <p className="text-xs text-slate-500">{t.role}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Checkout Form */}
          <div className="order-1 lg:order-2">
            <Card className="border-0 shadow-xl">
              {/* Steps */}
              <div className="p-6 border-b">
                <div className="flex items-center justify-center gap-4">
                  <div className="flex items-center gap-2">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      step >= 1 ? 'bg-[#10B981] text-white' : 'bg-slate-200 text-slate-500'
                    }`}>
                      {step > 1 ? <Check className="w-4 h-4" /> : "1"}
                    </div>
                    <span className={`text-sm ${step >= 1 ? 'text-[#10B981] font-medium' : 'text-slate-400'}`}>
                      Detail Pemesan
                    </span>
                  </div>
                  <div className={`w-12 h-0.5 ${step > 1 ? 'bg-[#10B981]' : 'bg-slate-200'}`} />
                  <div className="flex items-center gap-2">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      step >= 2 ? 'bg-[#10B981] text-white' : 'bg-slate-200 text-slate-500'
                    }`}>
                      2
                    </div>
                    <span className={`text-sm ${step >= 2 ? 'text-[#10B981] font-medium' : 'text-slate-400'}`}>
                      Pembayaran
                    </span>
                  </div>
                </div>
              </div>

              <CardContent className="p-6">
                {/* Step 1: Customer Details */}
                {step === 1 && (
                  <div className="animate-fadeIn space-y-6">
                    <div>
                      <h3 className="font-semibold text-lg mb-1">Detail Pemesan</h3>
                      <p className="text-slate-500 text-sm">Pastikan data yang Anda masukkan sudah benar.</p>
                    </div>

                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label>Nama Lengkap</Label>
                        <Input
                          placeholder="Nama lengkap Anda"
                          value={formData.name}
                          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                          data-testid="checkout-name"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label>Alamat Email</Label>
                        <Input
                          type="email"
                          placeholder="email@example.com"
                          value={formData.email}
                          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                          data-testid="checkout-email"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label>Nomor WhatsApp</Label>
                        <Input
                          type="tel"
                          placeholder="08xxxxxxxxxx"
                          value={formData.phone}
                          onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                          data-testid="checkout-phone"
                        />
                      </div>
                    </div>

                    <Button 
                      className="w-full bg-[#10B981] hover:bg-[#059669]"
                      onClick={() => setStep(2)}
                      disabled={!formData.name || !formData.email || !formData.phone || !selectedPackage}
                      data-testid="checkout-continue"
                    >
                      Lanjutkan ke Pembayaran
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                )}

                {/* Step 2: Payment */}
                {step === 2 && (
                  <div className="animate-fadeIn space-y-6">
                    <div>
                      <h3 className="font-semibold text-lg mb-1">Pembayaran</h3>
                      <p className="text-slate-500 text-sm">Selesaikan pembayaran untuk mengaktifkan token.</p>
                    </div>

                    {/* Order Summary */}
                    <div className="bg-slate-50 rounded-xl p-4 space-y-3">
                      <div className="flex justify-between">
                        <span className="text-slate-600">Paket {selectedPackage?.name}</span>
                        <span>{formatRupiah(selectedPackage?.price)}</span>
                      </div>
                      {getDiscount() > 0 && (
                        <div className="flex justify-between text-[#10B981]">
                          <span>Diskon</span>
                          <span>- {formatRupiah(getDiscount())}</span>
                        </div>
                      )}
                      <div className="border-t pt-3 flex justify-between font-bold text-lg">
                        <span>Total</span>
                        <span className="text-[#10B981]">{formatRupiah(getFinalPrice())}</span>
                      </div>
                    </div>

                    {/* Voucher */}
                    <div className="border-2 border-dashed border-[#10B981] rounded-xl p-4 bg-[#10B981]/5">
                      <div className="flex items-center gap-2 mb-3">
                        <Gift className="w-5 h-5 text-[#10B981]" />
                        <span className="font-medium text-[#10B981]">Harga Spesial Untuk Anda!</span>
                      </div>
                      <p className="text-sm text-slate-600 mb-3">
                        Gunakan kode voucher di bawah ini untuk mendapatkan potongan harga spesial.
                      </p>
                      
                      {/* Sample Voucher Display */}
                      <div className="bg-white border border-dashed border-slate-300 rounded-lg p-3 text-center mb-3">
                        <code className="font-mono font-bold text-lg">GURU2024</code>
                      </div>
                      
                      <div className="flex gap-2">
                        <Input
                          placeholder="Masukkan kode voucher"
                          value={voucherCode}
                          onChange={(e) => setVoucherCode(e.target.value.toUpperCase())}
                          data-testid="voucher-input"
                        />
                        <Button 
                          onClick={applyVoucher}
                          disabled={applyingVoucher || !voucherCode}
                          className="bg-[#10B981] hover:bg-[#059669]"
                          data-testid="voucher-apply"
                        >
                          {applyingVoucher ? <Loader2 className="w-4 h-4 animate-spin" /> : "Apply"}
                        </Button>
                      </div>
                      {voucherApplied && (
                        <p className="text-sm text-[#10B981] mt-2 flex items-center gap-1">
                          <Check className="w-4 h-4" />
                          Voucher valid! Diskon {formatRupiah(voucherApplied.discount)}
                        </p>
                      )}
                    </div>

                    {/* Payment Method Selection */}
                    <div className="space-y-3">
                      <Label>Metode Pembayaran</Label>
                      <div className="grid grid-cols-2 gap-3">
                        <div 
                          onClick={() => setPaymentMethod("bank")}
                          className={`border-2 rounded-xl p-4 cursor-pointer transition-all ${
                            paymentMethod === "bank" 
                              ? "border-[#10B981] bg-[#10B981]/5" 
                              : "border-slate-200 hover:border-slate-300"
                          }`}
                          data-testid="payment-method-bank"
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <Building2 className="w-5 h-5 text-slate-600" />
                            <span className="font-medium">Bank Transfer</span>
                            {paymentMethod === "bank" && <Check className="w-4 h-4 text-[#10B981] ml-auto" />}
                          </div>
                          <div className="flex gap-2">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Bank_Central_Asia.svg/120px-Bank_Central_Asia.svg.png" alt="BCA" className="h-5 object-contain" />
                          </div>
                        </div>
                        <div 
                          onClick={() => setPaymentMethod("ewallet")}
                          className={`border-2 rounded-xl p-4 cursor-pointer transition-all ${
                            paymentMethod === "ewallet" 
                              ? "border-[#10B981] bg-[#10B981]/5" 
                              : "border-slate-200 hover:border-slate-300"
                          }`}
                          data-testid="payment-method-ewallet"
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <Wallet className="w-5 h-5 text-slate-600" />
                            <span className="font-medium">E-Wallet / QRIS</span>
                            {paymentMethod === "ewallet" && <Check className="w-4 h-4 text-[#10B981] ml-auto" />}
                          </div>
                          <div className="flex gap-2 text-xs text-slate-500">
                            GoPay, OVO, DANA, ShopeePay
                          </div>
                        </div>
                      </div>
                      <p className="text-xs text-slate-500">
                        {paymentMethod === "bank" 
                          ? "Transfer ke rekening BCA. Upload bukti transfer untuk verifikasi admin."
                          : "Pembayaran via Midtrans. Otomatis dikonfirmasi."
                        }
                      </p>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3">
                      <Button 
                        variant="outline" 
                        onClick={() => setStep(1)}
                        className="flex-1"
                        data-testid="checkout-back"
                      >
                        Kembali
                      </Button>
                      <Button 
                        className="flex-1 bg-[#10B981] hover:bg-[#059669]"
                        onClick={handlePayment}
                        disabled={loading}
                        data-testid="checkout-pay"
                      >
                        {loading ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Memproses...
                          </>
                        ) : paymentMethod === "bank" ? (
                          <>
                            <Building2 className="w-4 h-4 mr-2" />
                            Transfer Bank
                          </>
                        ) : (
                          <>
                            <CreditCard className="w-4 h-4 mr-2" />
                            Bayar via E-Wallet
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
