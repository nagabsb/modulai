/**
 * Export HTML content to PDF using html2pdf.js
 * Handles tables, KaTeX math formulas, and styled content
 */

/**
 * Create a temporary container with proper styling for PDF rendering
 * @param {string} html - HTML content
 * @returns {HTMLElement} - Styled container element
 */
const createPdfContainer = (html) => {
  const container = document.createElement('div');
  container.innerHTML = html;
  container.style.cssText = `
    font-family: 'Times New Roman', serif;
    font-size: 12px;
    line-height: 1.6;
    color: #000;
    padding: 0;
    width: 210mm;
    max-width: 210mm;
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

  // Fix h2 styling
  const h2s = container.querySelectorAll('h2');
  h2s.forEach(h2 => {
    h2.style.pageBreakAfter = 'avoid';
  });

  // Remove diagram tags
  container.innerHTML = container.innerHTML.replace(
    /\[DIAGRAM:[^\]]+\]/g, 
    '<em>[Lihat Diagram di Aplikasi]</em>'
  );

  return container;
};

/**
 * Export HTML content to PDF
 * @param {string} htmlContent - HTML content to export
 * @param {string} filename - Filename without extension
 * @param {Object} options - Optional settings
 */
export const exportToPdf = async (htmlContent, filename, options = {}) => {
  // Dynamic import to avoid SSR issues
  const html2pdf = (await import('html2pdf.js')).default;

  const container = createPdfContainer(htmlContent);
  document.body.appendChild(container);

  const pdfOptions = {
    margin: [10, 10, 10, 10],
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
