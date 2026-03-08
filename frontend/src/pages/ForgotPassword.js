import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { toast } from "sonner";
import api from "../utils/api";
import { BookOpen, Mail, Loader2, ArrowLeft, CheckCircle } from "lucide-react";

const ForgotPassword = () => {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await api.post("/auth/forgot-password", { email });
      setSubmitted(true);
      toast.success("Link reset password telah dikirim ke email Anda");
    } catch (error) {
      // Still show success for security (don't reveal if email exists)
      setSubmitted(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <Link to="/" className="flex items-center justify-center gap-2 mb-8">
          <div className="w-12 h-12 bg-[#1E3A5F] rounded-xl flex items-center justify-center">
            <BookOpen className="w-7 h-7 text-white" />
          </div>
          <span className="text-2xl font-bold text-[#1E3A5F]">ModulAI</span>
        </Link>

        <Card className="border-0 shadow-xl">
          <CardHeader className="text-center pb-2">
            <CardTitle className="text-2xl text-[#1E3A5F]">Lupa Password</CardTitle>
            <CardDescription>
              {submitted 
                ? "Cek email Anda untuk link reset password" 
                : "Masukkan email untuk reset password"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {submitted ? (
              <div className="text-center py-6">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <p className="text-slate-600 mb-6">
                  Jika email <strong>{email}</strong> terdaftar, Anda akan menerima link untuk reset password.
                </p>
                <Link to="/login">
                  <Button variant="outline" className="w-full">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Kembali ke Login
                  </Button>
                </Link>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="email@sekolah.sch.id"
                      className="pl-10 h-11"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      data-testid="forgot-email"
                    />
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full h-11 bg-[#1E3A5F] hover:bg-[#162B47]"
                  disabled={loading}
                  data-testid="forgot-submit"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Mengirim...
                    </>
                  ) : (
                    "Kirim Link Reset"
                  )}
                </Button>

                <Link to="/login" className="block">
                  <Button variant="ghost" className="w-full">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Kembali ke Login
                  </Button>
                </Link>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ForgotPassword;
