import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { toast } from "sonner";
import { BookOpen, Mail, Lock, Loader2 } from "lucide-react";

const Login = () => {
  const navigate = useNavigate();
  const { login, user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: ""
  });

  // Redirect if already logged in
  if (user) {
    navigate(user.role === "super_admin" ? "/super-admin" : "/dashboard");
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const data = await login(formData.email, formData.password);
      toast.success("Login berhasil!");
      navigate(data.user.role === "super_admin" ? "/super-admin" : "/dashboard");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Email atau password salah");
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
            <CardTitle className="text-2xl text-[#1E3A5F]">Selamat Datang</CardTitle>
            <CardDescription>Masuk ke akun ModulAI Anda</CardDescription>
          </CardHeader>
          <CardContent>
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
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                    data-testid="login-email"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password">Password</Label>
                  <Link to="/forgot-password" className="text-sm text-[#F4820A] hover:underline">
                    Lupa Password?
                  </Link>
                </div>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="Masukkan password"
                    className="pl-10 h-11"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required
                    data-testid="login-password"
                  />
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full h-11 bg-[#1E3A5F] hover:bg-[#162B47]"
                disabled={loading}
                data-testid="login-submit"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Memproses...
                  </>
                ) : (
                  "Masuk"
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-slate-600">
                Belum punya akun?{" "}
                <Link to="/register" className="text-[#F4820A] font-medium hover:underline">
                  Daftar Gratis
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;
