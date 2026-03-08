// Format currency to Indonesian Rupiah
export const formatRupiah = (amount) => {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

// Format date to Indonesian locale
export const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString("id-ID", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// Format short date
export const formatShortDate = (dateString) => {
  return new Date(dateString).toLocaleDateString("id-ID", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
};

// Document type labels
export const DOC_TYPE_LABELS = {
  modul: "Modul Ajar",
  rpp: "RPP",
  lkpd: "LKPD",
  soal: "Bank Soal",
  rubrik: "Rubrik Asesmen",
};

// Jenjang options
export const JENJANG_OPTIONS = [
  { value: "TK", label: "TK" },
  { value: "SD", label: "SD" },
  { value: "SMP", label: "SMP" },
  { value: "SMA", label: "SMA" },
  { value: "SMK", label: "SMK" },
];

// Kelas based on jenjang
export const KELAS_OPTIONS = {
  TK: [
    { value: "A", label: "TK A" },
    { value: "B", label: "TK B" },
  ],
  SD: [
    { value: "1", label: "Kelas 1" },
    { value: "2", label: "Kelas 2" },
    { value: "3", label: "Kelas 3" },
    { value: "4", label: "Kelas 4" },
    { value: "5", label: "Kelas 5" },
    { value: "6", label: "Kelas 6" },
  ],
  SMP: [
    { value: "7", label: "Kelas 7" },
    { value: "8", label: "Kelas 8" },
    { value: "9", label: "Kelas 9" },
  ],
  SMA: [
    { value: "10", label: "Kelas 10" },
    { value: "11", label: "Kelas 11" },
    { value: "12", label: "Kelas 12" },
  ],
  SMK: [
    { value: "10", label: "Kelas 10" },
    { value: "11", label: "Kelas 11" },
    { value: "12", label: "Kelas 12" },
  ],
};

// Fase mapping
export const FASE_MAP = {
  TK: "Fondasi",
  SD: {
    1: "A",
    2: "A",
    3: "B",
    4: "B",
    5: "C",
    6: "C",
  },
  SMP: {
    7: "D",
    8: "D",
    9: "D",
  },
  SMA: {
    10: "E",
    11: "E",
    12: "F",
  },
  SMK: {
    10: "E",
    11: "E",
    12: "F",
  },
};

// Get fase based on jenjang and kelas
export const getFase = (jenjang, kelas) => {
  if (jenjang === "TK") return "Fondasi";
  const faseMap = FASE_MAP[jenjang];
  if (typeof faseMap === "object") {
    return faseMap[kelas] || "A";
  }
  return faseMap || "A";
};

// Mata pelajaran options
export const MAPEL_OPTIONS = [
  "Matematika",
  "Bahasa Indonesia",
  "Bahasa Inggris",
  "IPA",
  "IPS",
  "Fisika",
  "Kimia",
  "Biologi",
  "Ekonomi",
  "Geografi",
  "Sejarah",
  "Sosiologi",
  "PKN",
  "Pendidikan Agama",
  "Seni Budaya",
  "PJOK",
  "Informatika",
  "Prakarya",
];

// Kurikulum options
export const KURIKULUM_OPTIONS = [
  { value: "Merdeka", label: "Kurikulum Merdeka" },
  { value: "K13", label: "Kurikulum 2013" },
];

// Semester options
export const SEMESTER_OPTIONS = [
  { value: "Ganjil", label: "Ganjil" },
  { value: "Genap", label: "Genap" },
];

// Difficulty options
export const DIFFICULTY_OPTIONS = [
  { value: "Mudah", label: "Mudah" },
  { value: "Sedang", label: "Sedang" },
  { value: "Sulit", label: "Sulit" },
  { value: "Campuran", label: "Campuran" },
];
