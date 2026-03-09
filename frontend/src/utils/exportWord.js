/**
 * Export HTML content to Word (.doc) file
 * Uses the Blob approach with Word-compatible HTML wrapper
 * Converts LaTeX math to Unicode plain text for Word compatibility
 */
import { convertLatexToPlainInHtml } from "./latexRenderer";

const WORD_STYLES = `
  @page { margin: 2cm; }
  body { 
    font-family: 'Times New Roman', serif; 
    font-size: 12pt; 
    line-height: 1.6; 
    color: #000;
  }
  h1 { font-size: 18pt; color: #1E3A5F; margin-top: 12pt; }
  h2 { font-size: 14pt; color: #1E3A5F; margin-top: 10pt; padding: 6pt 10pt; }
  h3 { font-size: 12pt; color: #1E3A5F; margin-top: 8pt; }
  table { border-collapse: collapse; width: 100%; margin: 8pt 0; }
  th { 
    background-color: #1E3A5F; 
    color: white; 
    padding: 6pt 8pt; 
    text-align: left; 
    font-weight: bold;
    border: 1pt solid #999;
  }
  td { 
    border: 1pt solid #ccc; 
    padding: 6pt 8pt; 
    vertical-align: top;
  }
  p { margin: 4pt 0; }
  strong { font-weight: bold; }
  em { font-style: italic; }
  hr { border: 1pt solid #1E3A5F; margin: 12pt 0; }
`;

/**
 * Export HTML content to Word document
 * @param {string} htmlContent - Raw HTML content (may contain $latex$ delimiters)
 * @param {string} filename - Filename without extension
 * @param {string} title - Document title
 */
export const exportToWord = (htmlContent, filename, title = '') => {
  // Convert LaTeX to plain Unicode text (Word can't render KaTeX)
  let cleanedHtml = convertLatexToPlainInHtml(htmlContent);

  // Remove diagram tags
  cleanedHtml = cleanedHtml.replace(/\[DIAGRAM:[^\]]+\]/g, '[Lihat Diagram di Aplikasi]');

  // Remove SVG tags
  cleanedHtml = cleanedHtml.replace(/<svg[\s\S]*?<\/svg>/gi, '');

  const wordDoc = `<html xmlns:o='urn:schemas-microsoft-com:office:office' 
        xmlns:w='urn:schemas-microsoft-com:office:word' 
        xmlns='http://www.w3.org/TR/REC-html40'>
  <head>
    <meta charset='utf-8'>
    <title>${title || filename}</title>
    <!--[if gte mso 9]>
    <xml>
      <w:WordDocument>
        <w:View>Print</w:View>
        <w:Zoom>100</w:Zoom>
        <w:DoNotOptimizeForBrowser/>
      </w:WordDocument>
    </xml>
    <![endif]-->
    <style>${WORD_STYLES}</style>
  </head>
  <body>
    ${cleanedHtml}
  </body>
  </html>`;

  const blob = new Blob(['\ufeff' + wordDoc], { type: 'application/msword' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.doc`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export default exportToWord;
