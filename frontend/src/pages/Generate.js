import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Checkbox } from "../components/ui/checkbox";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { toast } from "sonner";
import api from "../utils/api";
import { exportToExcel, exportMultipleToExcel } from "../utils/exportExcel";
import { parseDiagramsInContent, hasDiagrams } from "../utils/diagramParser";
import { 
  JENJANG_OPTIONS, 
  KELAS_OPTIONS, 
  KURIKULUM_OPTIONS, 
  SEMESTER_OPTIONS, 
  MAPEL_OPTIONS,
  DIFFICULTY_OPTIONS,
  DOC_TYPE_LABELS,
  getFase 
} from "../utils/constants";
import { 
  BookOpen, 
  FileText, 
  ArrowLeft, 
  ArrowRight, 
  Loader2, 
  Coins,
  Printer,
  RefreshCw,
  Check,
  ClipboardList,
  PenTool,
  Award,
  FileSpreadsheet,
  Zap,
  Layers
} from "lucide-react";

import "katex/dist/katex.min.css";

const Generate = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, refreshUser } = useAuth();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [multiResults, setMultiResults] = useState(null);
  const [activeTab, setActiveTab] = useState("");
  const [generatingProgress, setGeneratingProgress] = useState("");
  
  // Multi-select mode
  const [isMultiMode, setIsMultiMode] = useState(false);
  const [selectedDocTypes, setSelectedDocTypes] = useState([]);
  
  const [formData, setFormData] = useState({
    doc_type: searchParams.get("type") || "modul",
    jenjang: "SMA",
    kelas: "10",
    kurikulum: "Merdeka",
    semester: "Ganjil",
    fase: "E",
    mata_pelajaran: "Matematika",
    topik: "",
    alokasi_waktu: 90,
    tingkat_kesulitan: "Sedang",
    jumlah_pg: 10,
    jumlah_isian: 5,
    jumlah_essay: 3,
    sertakan_pembahasan: true,
    use_custom_values: false,
    resistor1: "",
    resistor2: "",
    voltage: ""
  });

  const isPhysicsSubject = ["Fisika", "IPA"].includes(formData.mata_pelajaran);

  useEffect(() => {
    const newFase = getFase(formData.jenjang, formData.kelas);
    setFormData(prev => ({ ...prev, fase: newFase }));
  }, [formData.jenjang, formData.kelas]);

  useEffect(() => {
    const kelasOptions = KELAS_OPTIONS[formData.jenjang];
    if (kelasOptions?.length > 0) {
      setFormData(prev => ({ ...prev, kelas: kelasOptions[0].value }));
    }
  }, [formData.jenjang]);

  const docTypes = [
    { type: "modul", label: "Modul Ajar", icon: <BookOpen className="w-5 h-5" />, desc: "Modul lengkap dengan CP/TP/ATP" },
    { type: "rpp", label: "RPP", icon: <FileText className="w-5 h-5" />, desc: "Rencana Pelaksanaan Pembelajaran" },
    { type: "lkpd", label: "LKPD", icon: <ClipboardList className="w-5 h-5" />, desc: "Lembar Kerja Peserta Didik" },
    { type: "soal", label: "Bank Soal", icon: <PenTool className="w-5 h-5" />, desc: "PG + Isian + Essay + Pembahasan" },
    { type: "rubrik", label: "Rubrik Asesmen", icon: <Award className="w-5 h-5" />, desc: "Rubrik penilaian terstruktur" },
  ];

  const toggleDocType = (type) => {
    if (isMultiMode) {
      setSelectedDocTypes(prev => 
        prev.includes(type) 
          ? prev.filter(t => t !== type)
          : [...prev, type]
      );
    } else {
      setFormData({ ...formData, doc_type: type });
    }
  };

  const getTokenCost = () => {
    if (isMultiMode) {
      return selectedDocTypes.length;
    }
    return 1;
  };

  const handleGenerate = async () => {
    if (!formData.topik.trim()) {
      toast.error("Mohon isi topik/materi pembelajaran");
      return;
    }

    const tokenCost = getTokenCost();
    if (user.token_balance < tokenCost) {
      toast.error(`Token tidak mencukupi. Butuh ${tokenCost} token.`);
      navigate("/checkout");
      return;
    }

    if (isMultiMode && selectedDocTypes.length === 0) {
      toast.error("Pilih minimal 1 jenis dokumen");
      return;
    }

    setLoading(true);
    
    try {
      if (isMultiMode && selectedDocTypes.length > 1) {
        // Multi-document generation
        setGeneratingProgress(`Generating 0/${selectedDocTypes.length}...`);
        
        const requestData = {
          doc_types: selectedDocTypes,
          jenjang: formData.jenjang,
          kelas: formData.kelas,
          kurikulum: formData.kurikulum,
          semester: formData.semester,
          fase: formData.fase,
          mata_pelajaran: formData.mata_pelajaran,
          topik: formData.topik,
          alokasi_waktu: formData.alokasi_waktu,
          tingkat_kesulitan: formData.tingkat_kesulitan,
          jumlah_pg: formData.jumlah_pg,
          jumlah_isian: formData.jumlah_isian,
          jumlah_essay: formData.jumlah_essay,
          sertakan_pembahasan: formData.sertakan_pembahasan,
          use_custom_values: formData.use_custom_values,
          resistor1: formData.use_custom_values && formData.resistor1 ? parseFloat(formData.resistor1) : null,
          resistor2: formData.use_custom_values && formData.resistor2 ? parseFloat(formData.resistor2) : null,
          voltage: formData.use_custom_values && formData.voltage ? parseFloat(formData.voltage) : null,
        };
        
        const response = await api.post("/generate/multi", requestData);
        setMultiResults(response.data);
        setActiveTab(response.data.results[0]?.doc_type || "");
        await refreshUser();
        setStep(3);
        toast.success(`${selectedDocTypes.length} dokumen berhasil dibuat!`);
      } else {
        // Single document generation
        const docType = isMultiMode ? selectedDocTypes[0] : formData.doc_type;
        const requestData = {
          ...formData,
          doc_type: docType,
          resistor1: formData.use_custom_values && formData.resistor1 ? parseFloat(formData.resistor1) : null,
          resistor2: formData.use_custom_values && formData.resistor2 ? parseFloat(formData.resistor2) : null,
          voltage: formData.use_custom_values && formData.voltage ? parseFloat(formData.voltage) : null,
        };
        
        const response = await api.post("/generate", requestData);
        setResult(response.data);
        await refreshUser();
        setStep(3);
        toast.success("Dokumen berhasil dibuat!");
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Gagal generate dokumen");
    } finally {
      setLoading(false);
      setGeneratingProgress("");
    }
  };

  const handlePrint = (html, docType, topik) => {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>${DOC_TYPE_LABELS[docType]} - ${topik}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
        <style>
          body { font-family: 'Times New Roman', serif; line-height: 1.6; padding: 40px; }
          table { border-collapse: collapse; width: 100%; margin: 16px 0; }
          th { background-color: #1E3A5F !important; color: white !important; padding: 10px; text-align: left; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
          td { border: 1px solid #ccc; padding: 8px; }
          h1, h2, h3 { color: #1E3A5F; }
          @media print { body { padding: 0; } }
        </style>
      </head>
      <body>${html.replace(/\[DIAGRAM:[^\]]+\]/g, '[Lihat Diagram di Aplikasi]')}</body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  const handleExportExcel = (html, docType) => {
    try {
      const filename = `${DOC_TYPE_LABELS[docType]}_${formData.mata_pelajaran}_Kelas${formData.kelas}`.replace(/\s+/g, '_');
      exportToExcel(html, filename, docType);
      toast.success("File Excel berhasil didownload!");
    } catch (error) {
      toast.error("Gagal export ke Excel");
      console.error(error);
    }
  };

  const handleExportAllExcel = () => {
    if (!multiResults) return;
    try {
      const documents = multiResults.results.map(r => ({
        html: r.result_html,
        name: DOC_TYPE_LABELS[r.doc_type],
        type: r.doc_type
      }));
      const filename = `Paket_${formData.mata_pelajaran}_Kelas${formData.kelas}`.replace(/\s+/g, '_');
      exportMultipleToExcel(documents, filename);
      toast.success("File Excel berhasil didownload!");
    } catch (error) {
      toast.error("Gagal export ke Excel");
      console.error(error);
    }
  };

  const renderResultContent = (html) => {
    if (!html) return null;
    
    if (hasDiagrams(html)) {
      return (
        <div className="document-result prose max-w-none">
          {parseDiagramsInContent(html)}
        </div>
      );
    }
    
    return (
      <div 
        className="document-result prose max-w-none"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate("/dashboard")}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-xl font-bold text-[#1E3A5F]">Buat Dokumen</h1>
              <p className="text-sm text-slate-500">Langkah {step} dari 3</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 rounded-lg">
            <Coins className="w-4 h-4 text-[#F4820A]" />
            <span className="font-medium">{user?.token_balance} Token</span>
          </div>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="bg-white border-b border-slate-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-center gap-4">
            {[
              { num: 1, label: "Identitas" },
              { num: 2, label: "Konfigurasi" },
              { num: 3, label: "Hasil" }
            ].map((s, idx) => (
              <div key={s.num} className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-medium ${
                  step >= s.num 
                    ? 'bg-[#1E3A5F] text-white' 
                    : 'bg-slate-200 text-slate-500'
                }`}>
                  {step > s.num ? <Check className="w-4 h-4" /> : s.num}
                </div>
                <span className={`text-sm ${step >= s.num ? 'text-[#1E3A5F] font-medium' : 'text-slate-400'}`}>
                  {s.label}
                </span>
                {idx < 2 && <div className={`w-12 h-0.5 ${step > s.num ? 'bg-[#1E3A5F]' : 'bg-slate-200'}`} />}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Step 1: Identity */}
        {step === 1 && (
          <Card className="animate-fadeIn">
            <CardHeader>
              <CardTitle>Identitas Pembelajaran</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Multi-mode toggle */}
              <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-xl border border-blue-200">
                <Checkbox
                  id="multiMode"
                  checked={isMultiMode}
                  onCheckedChange={(checked) => {
                    setIsMultiMode(checked);
                    if (!checked) setSelectedDocTypes([]);
                  }}
                  data-testid="checkbox-multi-mode"
                />
                <Label htmlFor="multiMode" className="cursor-pointer flex items-center gap-2">
                  <Layers className="w-4 h-4 text-blue-600" />
                  <span className="font-medium text-blue-800">Generate Beberapa Dokumen Sekaligus</span>
                </Label>
              </div>

              {/* Doc Type Selection */}
              <div>
                <Label className="mb-3 block">
                  {isMultiMode ? "Pilih Dokumen (bisa lebih dari 1)" : "Jenis Dokumen"}
                </Label>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {docTypes.map((doc) => {
                    const isSelected = isMultiMode 
                      ? selectedDocTypes.includes(doc.type)
                      : formData.doc_type === doc.type;
                    
                    return (
                      <div
                        key={doc.type}
                        onClick={() => toggleDocType(doc.type)}
                        className={`cursor-pointer p-4 rounded-xl border-2 transition-all relative ${
                          isSelected
                            ? 'border-[#1E3A5F] bg-[#1E3A5F]/5'
                            : 'border-slate-200 hover:border-slate-300'
                        }`}
                        data-testid={`doc-type-${doc.type}`}
                      >
                        {isMultiMode && isSelected && (
                          <div className="absolute top-2 right-2 w-5 h-5 bg-[#1E3A5F] rounded-full flex items-center justify-center">
                            <Check className="w-3 h-3 text-white" />
                          </div>
                        )}
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-2 ${
                          isSelected ? 'bg-[#1E3A5F] text-white' : 'bg-slate-100 text-slate-600'
                        }`}>
                          {doc.icon}
                        </div>
                        <p className="font-medium text-sm">{doc.label}</p>
                      </div>
                    );
                  })}
                </div>
                {isMultiMode && selectedDocTypes.length > 0 && (
                  <p className="mt-2 text-sm text-slate-500">
                    {selectedDocTypes.length} dokumen dipilih = {selectedDocTypes.length} token
                  </p>
                )}
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Jenjang</Label>
                  <Select value={formData.jenjang} onValueChange={(v) => setFormData({ ...formData, jenjang: v })}>
                    <SelectTrigger data-testid="select-jenjang">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {JENJANG_OPTIONS.map((opt) => (
                        <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Kelas</Label>
                  <Select value={formData.kelas} onValueChange={(v) => setFormData({ ...formData, kelas: v })}>
                    <SelectTrigger data-testid="select-kelas">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {KELAS_OPTIONS[formData.jenjang]?.map((opt) => (
                        <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Kurikulum</Label>
                  <Select value={formData.kurikulum} onValueChange={(v) => setFormData({ ...formData, kurikulum: v })}>
                    <SelectTrigger data-testid="select-kurikulum">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {KURIKULUM_OPTIONS.map((opt) => (
                        <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Semester</Label>
                  <Select value={formData.semester} onValueChange={(v) => setFormData({ ...formData, semester: v })}>
                    <SelectTrigger data-testid="select-semester">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {SEMESTER_OPTIONS.map((opt) => (
                        <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Fase</Label>
                  <Input value={formData.fase} disabled className="bg-slate-50" data-testid="input-fase" />
                </div>

                <div className="space-y-2">
                  <Label>Mata Pelajaran</Label>
                  <Select value={formData.mata_pelajaran} onValueChange={(v) => setFormData({ ...formData, mata_pelajaran: v })}>
                    <SelectTrigger data-testid="select-mapel">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {MAPEL_OPTIONS.map((mapel) => (
                        <SelectItem key={mapel} value={mapel}>{mapel}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Topik / Materi Pembelajaran *</Label>
                <Input
                  placeholder="Contoh: Persamaan Kuadrat, Hukum Newton, Rangkaian Listrik"
                  value={formData.topik}
                  onChange={(e) => setFormData({ ...formData, topik: e.target.value })}
                  data-testid="input-topik"
                />
              </div>

              <div className="space-y-2">
                <Label>Alokasi Waktu (menit)</Label>
                <Input
                  type="number"
                  value={formData.alokasi_waktu}
                  onChange={(e) => setFormData({ ...formData, alokasi_waktu: parseInt(e.target.value) || 90 })}
                  data-testid="input-waktu"
                />
              </div>

              <div className="flex justify-end">
                <Button 
                  onClick={() => setStep(2)} 
                  className="bg-[#1E3A5F] hover:bg-[#162B47]"
                  disabled={!formData.topik.trim() || (isMultiMode && selectedDocTypes.length === 0)}
                  data-testid="btn-next-step1"
                >
                  Lanjutkan
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Configuration */}
        {step === 2 && (
          <Card className="animate-fadeIn">
            <CardHeader>
              <CardTitle>
                Konfigurasi {isMultiMode ? `${selectedDocTypes.length} Dokumen` : DOC_TYPE_LABELS[formData.doc_type]}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Summary */}
              <div className="p-4 bg-slate-50 rounded-xl">
                <h3 className="font-medium mb-2">Ringkasan</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-slate-500">Jenjang:</span>
                    <p className="font-medium">{formData.jenjang} Kelas {formData.kelas}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Kurikulum:</span>
                    <p className="font-medium">{formData.kurikulum}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Mata Pelajaran:</span>
                    <p className="font-medium">{formData.mata_pelajaran}</p>
                  </div>
                  <div>
                    <span className="text-slate-500">Topik:</span>
                    <p className="font-medium truncate">{formData.topik}</p>
                  </div>
                </div>
                {isMultiMode && (
                  <div className="mt-3 pt-3 border-t">
                    <span className="text-slate-500">Dokumen yang akan dibuat:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {selectedDocTypes.map(type => (
                        <Badge key={type} variant="outline">{DOC_TYPE_LABELS[type]}</Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Soal-specific config - show if soal is selected */}
              {(formData.doc_type === "soal" || selectedDocTypes.includes("soal")) && (
                <div className="space-y-4 p-4 bg-slate-50 rounded-xl">
                  <h3 className="font-medium">Konfigurasi Bank Soal</h3>
                  
                  <div className="space-y-2">
                    <Label>Tingkat Kesulitan</Label>
                    <Select value={formData.tingkat_kesulitan} onValueChange={(v) => setFormData({ ...formData, tingkat_kesulitan: v })}>
                      <SelectTrigger data-testid="select-difficulty">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {DIFFICULTY_OPTIONS.map((opt) => (
                          <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label>Jumlah Soal Pilihan Ganda</Label>
                      <Input
                        type="number"
                        min="0"
                        max="50"
                        value={formData.jumlah_pg}
                        onChange={(e) => setFormData({ ...formData, jumlah_pg: parseInt(e.target.value) || 0 })}
                        data-testid="input-pg"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Jumlah Soal Isian Singkat</Label>
                      <Input
                        type="number"
                        min="0"
                        max="20"
                        value={formData.jumlah_isian}
                        onChange={(e) => setFormData({ ...formData, jumlah_isian: parseInt(e.target.value) || 0 })}
                        data-testid="input-isian"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Jumlah Soal Essay</Label>
                      <Input
                        type="number"
                        min="0"
                        max="10"
                        value={formData.jumlah_essay}
                        onChange={(e) => setFormData({ ...formData, jumlah_essay: parseInt(e.target.value) || 0 })}
                        data-testid="input-essay"
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Checkbox
                      id="pembahasan"
                      checked={formData.sertakan_pembahasan}
                      onCheckedChange={(checked) => setFormData({ ...formData, sertakan_pembahasan: checked })}
                      data-testid="checkbox-pembahasan"
                    />
                    <Label htmlFor="pembahasan" className="cursor-pointer">
                      Sertakan Kunci Jawaban dan Pembahasan Detail
                    </Label>
                  </div>

                  {/* Physics custom values */}
                  {isPhysicsSubject && (
                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl space-y-4">
                      <div className="flex items-center gap-2">
                        <Checkbox
                          id="customValues"
                          checked={formData.use_custom_values}
                          onCheckedChange={(checked) => setFormData({ ...formData, use_custom_values: checked })}
                          data-testid="checkbox-custom-values"
                        />
                        <Label htmlFor="customValues" className="cursor-pointer font-medium text-blue-800">
                          <Zap className="w-4 h-4 inline mr-1" />
                          Gunakan Nilai Custom untuk Soal Fisika
                        </Label>
                      </div>
                      
                      {formData.use_custom_values && (
                        <div className="grid md:grid-cols-3 gap-4 mt-3">
                          <div className="space-y-2">
                            <Label className="text-blue-700">Resistor 1 (Ohm)</Label>
                            <Input
                              type="number"
                              placeholder="Contoh: 2"
                              value={formData.resistor1}
                              onChange={(e) => setFormData({ ...formData, resistor1: e.target.value })}
                              className="bg-white"
                              data-testid="input-resistor1"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label className="text-blue-700">Resistor 2 (Ohm)</Label>
                            <Input
                              type="number"
                              placeholder="Contoh: 3"
                              value={formData.resistor2}
                              onChange={(e) => setFormData({ ...formData, resistor2: e.target.value })}
                              className="bg-white"
                              data-testid="input-resistor2"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label className="text-blue-700">Tegangan (Volt)</Label>
                            <Input
                              type="number"
                              placeholder="Contoh: 12"
                              value={formData.voltage}
                              onChange={(e) => setFormData({ ...formData, voltage: e.target.value })}
                              className="bg-white"
                              data-testid="input-voltage"
                            />
                          </div>
                        </div>
                      )}
                      
                      <p className="text-xs text-blue-600">
                        Jika tidak diisi, AI akan generate nilai random yang sesuai untuk soal fisika.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Token Info */}
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center gap-3">
                <Coins className="w-5 h-5 text-amber-600" />
                <div>
                  <p className="font-medium text-amber-800">Biaya: {getTokenCost()} Token</p>
                  <p className="text-sm text-amber-600">Saldo Anda: {user?.token_balance} token</p>
                </div>
              </div>

              <div className="flex justify-between">
                <Button variant="outline" onClick={() => setStep(1)} data-testid="btn-back-step2">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Kembali
                </Button>
                <Button 
                  onClick={handleGenerate} 
                  className="bg-[#F4820A] hover:bg-[#D66E00]"
                  disabled={loading || user?.token_balance < getTokenCost()}
                  data-testid="btn-generate"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      {generatingProgress || "Generating..."}
                    </>
                  ) : (
                    <>
                      Generate {isMultiMode && selectedDocTypes.length > 1 ? `${selectedDocTypes.length} Dokumen` : "Dokumen"}
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Result */}
        {step === 3 && (result || multiResults) && (
          <div className="animate-fadeIn space-y-4">
            {/* Actions */}
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <Badge className="bg-green-100 text-green-700">Berhasil</Badge>
                <span className="text-slate-500">
                  Sisa token: {multiResults?.remaining_tokens ?? result?.remaining_tokens}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <Button variant="outline" onClick={() => { 
                  setStep(1); 
                  setResult(null); 
                  setMultiResults(null);
                  setSelectedDocTypes([]);
                  setIsMultiMode(false);
                }} data-testid="btn-new-doc">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Buat Baru
                </Button>
                {multiResults && multiResults.results.length > 1 && (
                  <Button variant="outline" onClick={handleExportAllExcel} data-testid="btn-export-all-excel">
                    <FileSpreadsheet className="w-4 h-4 mr-2" />
                    Export Semua (Excel)
                  </Button>
                )}
                <Button 
                  className="bg-[#1E3A5F] hover:bg-[#162B47]"
                  onClick={() => navigate("/history")}
                  data-testid="btn-view-history"
                >
                  Lihat Riwayat
                </Button>
              </div>
            </div>

            {/* Single Result */}
            {result && !multiResults && (
              <Card>
                <CardHeader className="border-b flex flex-row items-center justify-between">
                  <CardTitle>{DOC_TYPE_LABELS[formData.doc_type]}: {formData.topik}</CardTitle>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleExportExcel(result.result_html, formData.doc_type)}>
                      <FileSpreadsheet className="w-4 h-4 mr-1" />
                      Excel
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handlePrint(result.result_html, formData.doc_type, formData.topik)}>
                      <Printer className="w-4 h-4 mr-1" />
                      Cetak
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="p-6">
                  {renderResultContent(result.result_html)}
                </CardContent>
              </Card>
            )}

            {/* Multi Results with Tabs */}
            {multiResults && multiResults.results.length > 0 && (
              <Card>
                <CardContent className="p-0">
                  <Tabs value={activeTab} onValueChange={setActiveTab}>
                    <div className="border-b px-4">
                      <TabsList className="bg-transparent h-auto p-0 gap-0">
                        {multiResults.results.map((r) => (
                          <TabsTrigger 
                            key={r.doc_type} 
                            value={r.doc_type}
                            className="px-4 py-3 rounded-none border-b-2 border-transparent data-[state=active]:border-[#1E3A5F] data-[state=active]:bg-transparent"
                          >
                            {DOC_TYPE_LABELS[r.doc_type]}
                          </TabsTrigger>
                        ))}
                      </TabsList>
                    </div>
                    {multiResults.results.map((r) => (
                      <TabsContent key={r.doc_type} value={r.doc_type} className="p-0 m-0">
                        <div className="p-4 border-b bg-slate-50 flex items-center justify-between">
                          <h3 className="font-semibold">{DOC_TYPE_LABELS[r.doc_type]}: {formData.topik}</h3>
                          <div className="flex gap-2">
                            <Button variant="outline" size="sm" onClick={() => handleExportExcel(r.result_html, r.doc_type)}>
                              <FileSpreadsheet className="w-4 h-4 mr-1" />
                              Excel
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => handlePrint(r.result_html, r.doc_type, formData.topik)}>
                              <Printer className="w-4 h-4 mr-1" />
                              Cetak
                            </Button>
                          </div>
                        </div>
                        <div className="p-6">
                          {renderResultContent(r.result_html)}
                        </div>
                      </TabsContent>
                    ))}
                  </Tabs>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Generate;
