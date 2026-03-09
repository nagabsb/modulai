import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import api from "../utils/api";
import { exportToExcel } from "../utils/exportExcel";
import { exportToPdf } from "../utils/exportPdf";
import { parseDiagramsInContent, hasDiagrams } from "../utils/diagramParser";
import { processGeneratedContent } from "../utils/latexRenderer";
import { DOC_TYPE_LABELS, formatDate } from "../utils/constants";
import { 
  ArrowLeft, 
  Printer, 
  Download,
  RefreshCw,
  FileText,
  Calendar,
  BookOpen,
  Loader2,
  FileSpreadsheet,
  FileDown
} from "lucide-react";

const HistoryDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [generation, setGeneration] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGeneration();
  }, [id]);

  const fetchGeneration = async () => {
    try {
      const response = await api.get(`/generations/${id}`);
      setGeneration(response.data);
    } catch (error) {
      console.error("Failed to fetch generation", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>${DOC_TYPE_LABELS[generation.doc_type]} - ${generation.form_data?.topik}</title>
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
      <body>${generation.result_html.replace(/\[DIAGRAM:[^\]]+\]/g, '[Lihat Diagram di Aplikasi]')}</body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  const handleExportExcel = () => {
    try {
      const filename = `${DOC_TYPE_LABELS[generation.doc_type]}_${generation.form_data?.mata_pelajaran}_Kelas${generation.form_data?.kelas}`.replace(/\s+/g, '_');
      exportToExcel(generation.result_html, filename, generation.doc_type);
    } catch (error) {
      console.error("Export failed", error);
    }
  };

  const handleExportWord = async () => {
    try {
      toast.info("Membuat file Word...");
      const response = await api.get(`/export/docx/${id}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const filename = `${DOC_TYPE_LABELS[generation.doc_type]}_${generation.form_data?.mata_pelajaran}_Kelas${generation.form_data?.kelas}`.replace(/\s+/g, '_');
      link.download = `${filename}.docx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success("File Word berhasil didownload!");
    } catch (error) {
      console.error("Word export failed", error);
      toast.error("Gagal export ke Word");
    }
  };

  const handleExportPdf = async () => {
    try {
      const filename = `${DOC_TYPE_LABELS[generation.doc_type]}_${generation.form_data?.mata_pelajaran}_Kelas${generation.form_data?.kelas}`.replace(/\s+/g, '_');
      await exportToPdf(generation.result_html, filename);
    } catch (error) {
      console.error("PDF export failed", error);
    }
  };

  const renderContent = () => {
    const processedHtml = processGeneratedContent(generation.result_html);
    if (hasDiagrams(processedHtml)) {
      return (
        <div className="document-result prose max-w-none">
          {parseDiagramsInContent(processedHtml)}
        </div>
      );
    }
    return (
      <div 
        className="document-result prose max-w-none"
        dangerouslySetInnerHTML={{ __html: processedHtml }}
      />
    );
  };

  const handleRegenerate = () => {
    const params = new URLSearchParams({
      type: generation.doc_type
    });
    navigate(`/generate?${params.toString()}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-[#1E3A5F]" />
      </div>
    );
  }

  if (!generation) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500 mb-4">Dokumen tidak ditemukan</p>
            <Button onClick={() => navigate("/history")}>
              Kembali ke Riwayat
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate("/history")}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-xl font-bold text-[#1E3A5F]">Detail Dokumen</h1>
              <p className="text-sm text-slate-500">{DOC_TYPE_LABELS[generation.doc_type]}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={handleRegenerate} data-testid="btn-regenerate">
              <RefreshCw className="w-4 h-4 mr-2" />
              Buat Ulang
            </Button>
            <Button variant="outline" onClick={handleExportWord} data-testid="btn-export-word-detail">
              <FileDown className="w-4 h-4 mr-2" />
              Word
            </Button>
            <Button variant="outline" onClick={handleExportPdf} data-testid="btn-export-pdf-detail">
              <FileText className="w-4 h-4 mr-2" />
              PDF
            </Button>
            <Button variant="outline" onClick={handleExportExcel} data-testid="btn-export-excel-detail">
              <FileSpreadsheet className="w-4 h-4 mr-2" />
              Excel
            </Button>
            <Button variant="outline" onClick={handlePrint} data-testid="btn-print-detail">
              <Printer className="w-4 h-4 mr-2" />
              Cetak
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Meta Info */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-wrap gap-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-slate-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-500">Jenis Dokumen</p>
                  <p className="font-medium">{DOC_TYPE_LABELS[generation.doc_type]}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-slate-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-500">Mata Pelajaran</p>
                  <p className="font-medium">{generation.form_data?.mata_pelajaran}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-slate-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-500">Dibuat</p>
                  <p className="font-medium">{formatDate(generation.created_at)}</p>
                </div>
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t">
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline">{generation.form_data?.jenjang} Kelas {generation.form_data?.kelas}</Badge>
                <Badge variant="outline">{generation.form_data?.kurikulum}</Badge>
                <Badge variant="outline">Semester {generation.form_data?.semester}</Badge>
                <Badge variant="outline">Fase {generation.form_data?.fase}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Document Content */}
        <Card>
          <CardHeader className="border-b">
            <CardTitle>{generation.form_data?.topik}</CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            {renderContent()}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default HistoryDetail;
