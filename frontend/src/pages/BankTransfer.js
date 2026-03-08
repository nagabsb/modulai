import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { toast } from "sonner";
import api from "../utils/api";
import { formatRupiah } from "../utils/constants";
import { 
  ArrowLeft, 
  Copy, 
  Upload, 
  Check, 
  Clock, 
  Loader2,
  ImageIcon,
  CheckCircle2
} from "lucide-react";

const BankTransfer = () => {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [transaction, setTransaction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    fetchTransaction();
    const interval = setInterval(fetchTransaction, 15000);
    return () => clearInterval(interval);
  }, [orderId]);

  const fetchTransaction = async () => {
    try {
      const response = await api.get(`/payment/bank-transfer/${orderId}`);
      setTransaction(response.data);
      if (response.data.status === "success") {
        toast.success("Pembayaran sudah dikonfirmasi!");
        await refreshUser();
      }
    } catch (error) {
      console.error("Failed to fetch transaction", error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} berhasil disalin`);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
      toast.error("Ukuran file maksimal 5MB");
      return;
    }
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", selectedFile);
      await api.post(`/payment/upload-proof/${orderId}`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      toast.success("Bukti pembayaran berhasil diupload!");
      setSelectedFile(null);
      setPreviewUrl(null);
      fetchTransaction();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Gagal upload bukti pembayaran");
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="w-8 h-8 animate-spin text-[#1E3A5F]" />
      </div>
    );
  }

  if (!transaction) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <p>Transaksi tidak ditemukan</p>
      </div>
    );
  }

  const isSuccess = transaction.status === "success";
  const isWaiting = transaction.status === "waiting_verification";
  const hasProof = !!transaction.proof_of_payment;

  return (
    <div className="min-h-screen bg-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Button variant="ghost" onClick={() => navigate("/dashboard")} data-testid="btn-back">
            <ArrowLeft className="w-5 h-5 mr-2" />
            Kembali
          </Button>
          <span className="font-bold text-[#1E3A5F]">Transfer Bank</span>
          <div className="w-24" />
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-lg">
        {/* Success State */}
        {isSuccess && (
          <Card className="mb-6 border-green-200 bg-green-50">
            <CardContent className="p-6 text-center">
              <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-green-700 mb-2">Pembayaran Dikonfirmasi!</h2>
              <p className="text-green-600 mb-4">
                {transaction.tokens_to_add} token telah ditambahkan ke akun Anda.
              </p>
              <Button className="bg-[#1E3A5F] hover:bg-[#162B47]" onClick={() => navigate("/dashboard")}>
                Ke Dashboard
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Order Info */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-slate-500 text-sm">Order ID</span>
              <span className="font-mono text-sm">{transaction.order_id}</span>
            </div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-slate-500 text-sm">Paket</span>
              <span className="capitalize font-medium">{transaction.package_id}</span>
            </div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-500 text-sm">Status</span>
              <Badge className={
                isSuccess ? "bg-green-100 text-green-700" :
                isWaiting ? "bg-blue-100 text-blue-700" :
                transaction.status === "rejected" ? "bg-red-100 text-red-700" :
                "bg-yellow-100 text-yellow-700"
              } data-testid="transfer-status">
                {isSuccess ? "Dikonfirmasi" :
                 isWaiting ? "Menunggu Verifikasi" :
                 transaction.status === "rejected" ? "Ditolak" :
                 "Menunggu Pembayaran"}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Amount */}
        {!isSuccess && (
          <>
            <Card className="mb-6">
              <CardContent className="p-6 text-center">
                <p className="text-slate-500 text-sm mb-2">Untuk menyelesaikan order, silahkan transfer sejumlah</p>
                <p className="text-3xl font-bold text-[#10B981] mb-3" data-testid="transfer-amount">
                  {formatRupiah(transaction.gross_amount)}
                </p>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => copyToClipboard(String(transaction.gross_amount), "Jumlah")}
                  data-testid="btn-copy-amount"
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Salin Jumlah
                </Button>
                {transaction.unique_code > 0 && (
                  <p className="text-xs text-slate-400 mt-3">
                    *Termasuk kode unik Rp {transaction.unique_code.toLocaleString("id-ID")} untuk verifikasi otomatis
                  </p>
                )}

                <div className="mt-6 text-left">
                  <p className="text-slate-500 text-sm mb-4 text-center">ke rekening bank berikut:</p>
                  
                  {/* BCA Card */}
                  <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center">
                    <img 
                      src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Bank_Central_Asia.svg/200px-Bank_Central_Asia.svg.png" 
                      alt="BCA" 
                      className="h-10 mx-auto mb-4 object-contain" 
                    />
                    <p className="text-2xl font-mono font-bold tracking-wider mb-2" data-testid="account-number">
                      {transaction.bank_account?.account_number}
                    </p>
                    <p className="text-slate-600 mb-4">
                      Atas Nama: <strong>{transaction.bank_account?.account_name}</strong>
                    </p>
                    <Button 
                      variant="outline"
                      onClick={() => copyToClipboard(transaction.bank_account?.account_number, "No. Rekening")}
                      data-testid="btn-copy-rekening"
                    >
                      <Copy className="w-4 h-4 mr-2" />
                      Salin No. Rek.
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Upload Proof */}
            <Card className="mb-6">
              <CardContent className="p-6">
                <h3 className="font-semibold text-lg mb-4">Konfirmasi Pembayaran</h3>
                
                {hasProof && !selectedFile ? (
                  <div className="text-center space-y-3">
                    <div className="flex items-center justify-center gap-2 text-blue-600">
                      <Check className="w-5 h-5" />
                      <span className="font-medium">Bukti pembayaran sudah diupload</span>
                    </div>
                    <img 
                      src={`${process.env.REACT_APP_BACKEND_URL}/api/uploads/${transaction.proof_of_payment}`}
                      alt="Bukti pembayaran"
                      className="max-w-full h-48 object-contain mx-auto rounded-lg border"
                    />
                    {isWaiting && (
                      <div className="flex items-center justify-center gap-2 text-amber-600 bg-amber-50 p-3 rounded-lg">
                        <Clock className="w-5 h-5" />
                        <span className="text-sm">Admin sedang memverifikasi pembayaran Anda</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    <p className="text-sm text-slate-500">
                      Upload bukti transfer untuk mempercepat proses verifikasi.
                    </p>

                    {/* File Preview */}
                    {previewUrl && (
                      <div className="relative">
                        <img 
                          src={previewUrl} 
                          alt="Preview" 
                          className="max-w-full h-48 object-contain mx-auto rounded-lg border" 
                        />
                        <button 
                          onClick={() => { setSelectedFile(null); setPreviewUrl(null); }}
                          className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs"
                        >
                          x
                        </button>
                      </div>
                    )}

                    {/* Upload Button */}
                    <div className="flex gap-3">
                      <label className="flex-1 cursor-pointer">
                        <div className="border-2 border-dashed border-slate-300 rounded-xl p-4 text-center hover:border-[#1E3A5F] transition-colors">
                          <ImageIcon className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                          <p className="text-sm text-slate-500">
                            {selectedFile ? selectedFile.name : "Pilih foto bukti transfer"}
                          </p>
                        </div>
                        <input 
                          type="file" 
                          className="hidden" 
                          accept="image/*"
                          onChange={handleFileSelect}
                          data-testid="input-proof"
                        />
                      </label>
                    </div>

                    {selectedFile && (
                      <Button 
                        className="w-full bg-[#10B981] hover:bg-[#059669]"
                        onClick={handleUpload}
                        disabled={uploading}
                        data-testid="btn-upload-proof"
                      >
                        {uploading ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Mengupload...
                          </>
                        ) : (
                          <>
                            <Upload className="w-4 h-4 mr-2" />
                            Upload Bukti Pembayaran
                          </>
                        )}
                      </Button>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        )}

        {/* Auto refresh note */}
        {!isSuccess && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-center">
            <p className="text-sm text-amber-700">
              Mohon tunggu sebentar, halaman ini akan refresh otomatis apabila pembayaran sudah terkonfirmasi.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BankTransfer;
