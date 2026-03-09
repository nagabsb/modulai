/**
 * Export HTML content to Word (.doc) file
 * Uses the Blob approach with Word-compatible HTML wrapper
 */

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
    mso-background-themecolor: text2;
  }
  td { 
    border: 1pt solid #ccc; 
    padding: 6pt 8pt; 
    vertical-align: top;
  }
  tr:nth-child(even) td { background-color: #F8FAFC; }
  p { margin: 4pt 0; }
  strong { font-weight: bold; }
  em { font-style: italic; }
  hr { border: 1pt solid #1E3A5F; margin: 12pt 0; }
  .katex { font-family: 'Times New Roman', serif; }
`;

/**
 * Clean HTML for Word compatibility
 * @param {string} html - HTML content
 * @returns {string} - Cleaned HTML
 */
const cleanHtmlForWord = (html) => {
  let cleaned = html;

  // Remove diagram tags (not supported in Word)
  cleaned = cleaned.replace(/\[DIAGRAM:[^\]]+\]/g, '[Lihat Diagram di Aplikasi]');

  // Convert KaTeX rendered spans to plain text for Word
  // KaTeX renders to complex nested spans that Word can't handle
  const parser = new DOMParser();
  const doc = parser.parseFromString(cleaned, 'text/html');

  // Replace KaTeX elements with their text content
  const katexElements = doc.querySelectorAll('.katex');
  katexElements.forEach(el => {
    const annotation = el.querySelector('annotation');
    if (annotation) {
      const textNode = doc.createTextNode(` ${annotation.textContent} `);
      el.replaceWith(textNode);
    }
  });

  // Remove SVG elements (not supported in Word)
  const svgs = doc.querySelectorAll('svg');
  svgs.forEach(svg => svg.remove());

  return doc.body.innerHTML;
};

/**
 * Export HTML content to Word document
 * @param {string} htmlContent - HTML content
 * @param {string} filename - Filename without extension
 * @param {string} title - Document title
 */
export const exportToWord = (htmlContent, filename, title = '') => {
  const cleanedHtml = cleanHtmlForWord(htmlContent);

  const wordDoc = `
    <html xmlns:o='urn:schemas-microsoft-com:office:office' 
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
    </html>
  `;

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
