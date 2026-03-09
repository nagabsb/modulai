/**
 * Export HTML content to PDF using html2pdf.js
 * Pre-renders LaTeX math via KaTeX before PDF generation
 */
import { renderLatexInHtml } from "./latexRenderer";

/**
 * Create a temporary container with KaTeX-rendered content for PDF
 * @param {string} html - Raw HTML (may contain $latex$ delimiters)
 * @returns {HTMLElement} - Styled container with rendered math
 */
const createPdfContainer = (html) => {
  // Pre-render LaTeX to KaTeX HTML
  const renderedHtml = renderLatexInHtml(html);

  const container = document.createElement('div');
  container.innerHTML = renderedHtml;
  container.style.cssText = `
    font-family: 'Times New Roman', serif;
    font-size: 12px;
    line-height: 1.6;
    color: #000;
    padding: 10px 20px;
    width: 190mm;
    max-width: 190mm;
    background: white;
  `;

  // Fix table styling for PDF
  const tables = container.querySelectorAll('table');
  tables.forEach(table => {
    table.style.borderCollapse = 'collapse';
    table.style.width = '100%';
    table.style.marginBottom = '10px';
    table.style.pageBreakInside = 'auto';
  });

  const ths = container.querySelectorAll('th');
  ths.forEach(th => {
    th.style.backgroundColor = '#1E3A5F';
    th.style.color = 'white';
    th.style.padding = '6px 8px';
    th.style.border = '1px solid #999';
    th.style.textAlign = 'left';
  });

  const tds = container.querySelectorAll('td');
  tds.forEach(td => {
    td.style.border = '1px solid #ccc';
    td.style.padding = '6px 8px';
  });

  // Ensure h2 sections don't break across pages
  const h2s = container.querySelectorAll('h2');
  h2s.forEach(h2 => {
    h2.style.pageBreakAfter = 'avoid';
  });

  // Replace diagram tags with placeholder text
  container.innerHTML = container.innerHTML.replace(
    /\[DIAGRAM:[^\]]+\]/g, 
    '<em style="color:#666;">[Lihat Diagram di Aplikasi]</em>'
  );

  return container;
};

/**
 * Export HTML content to PDF
 * @param {string} htmlContent - Raw HTML with $latex$ delimiters
 * @param {string} filename - Filename without extension
 * @param {Object} options - Optional settings
 */
export const exportToPdf = async (htmlContent, filename, options = {}) => {
  const html2pdf = (await import('html2pdf.js')).default;

  const container = createPdfContainer(htmlContent);
  
  // Must be in DOM for html2canvas to capture
  container.style.position = 'fixed';
  container.style.left = '-9999px';
  container.style.top = '0';
  document.body.appendChild(container);

  // Wait for KaTeX fonts to load
  await new Promise(resolve => setTimeout(resolve, 500));

  const pdfOptions = {
    margin: [10, 10, 15, 10],
    filename: `${filename}.pdf`,
    image: { type: 'jpeg', quality: 0.95 },
    html2canvas: { 
      scale: 2, 
      useCORS: true,
      letterRendering: true,
      logging: false,
    },
    jsPDF: { 
      unit: 'mm', 
      format: 'a4', 
      orientation: options.orientation || 'portrait' 
    },
    pagebreak: { mode: ['avoid-all', 'css', 'legacy'] },
  };

  try {
    await html2pdf().set(pdfOptions).from(container).save();
  } finally {
    document.body.removeChild(container);
  }
};

export default exportToPdf;
