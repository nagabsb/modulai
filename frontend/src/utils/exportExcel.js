import XLSX from '@redoper1/xlsx-js-style';

/**
 * Parse HTML tables to array of arrays
 * @param {string} html - HTML content containing tables
 * @returns {Array<Array<string>>} - 2D array of cell values
 */
const parseHTMLToArray = (html) => {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');
  const tables = doc.querySelectorAll('table');
  
  const result = [];
  
  tables.forEach((table, tableIndex) => {
    if (tableIndex > 0) {
      result.push([]); // Empty row between tables
    }
    
    const rows = table.querySelectorAll('tr');
    rows.forEach((row) => {
      const cells = row.querySelectorAll('th, td');
      const rowData = [];
      cells.forEach((cell) => {
        // Clean text content - remove extra whitespace
        let text = cell.textContent.trim().replace(/\s+/g, ' ');
        rowData.push(text);
      });
      if (rowData.length > 0) {
        result.push(rowData);
      }
    });
  });
  
  // If no tables found, parse other content
  if (tables.length === 0) {
    const lines = html
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<\/p>/gi, '\n')
      .replace(/<\/div>/gi, '\n')
      .replace(/<\/h[1-6]>/gi, '\n')
      .replace(/<[^>]*>/g, '')
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0);
    
    lines.forEach(line => {
      result.push([line]);
    });
  }
  
  return result;
};

/**
 * Apply styles to worksheet
 * @param {Object} ws - XLSX worksheet
 * @param {Array<Array<string>>} data - Data array
 */
const applyStyles = (ws, data) => {
  const headerStyle = {
    fill: {
      fgColor: { rgb: "1E3A5F" }
    },
    font: {
      color: { rgb: "FFFFFF" },
      bold: true,
      sz: 12
    },
    alignment: {
      horizontal: "center",
      vertical: "center",
      wrapText: true
    },
    border: {
      top: { style: "thin", color: { rgb: "000000" } },
      bottom: { style: "thin", color: { rgb: "000000" } },
      left: { style: "thin", color: { rgb: "000000" } },
      right: { style: "thin", color: { rgb: "000000" } }
    }
  };

  const bodyStyleEven = {
    fill: {
      fgColor: { rgb: "FFFFFF" }
    },
    font: {
      color: { rgb: "000000" },
      sz: 11
    },
    alignment: {
      horizontal: "left",
      vertical: "center",
      wrapText: true
    },
    border: {
      top: { style: "thin", color: { rgb: "CCCCCC" } },
      bottom: { style: "thin", color: { rgb: "CCCCCC" } },
      left: { style: "thin", color: { rgb: "CCCCCC" } },
      right: { style: "thin", color: { rgb: "CCCCCC" } }
    }
  };

  const bodyStyleOdd = {
    ...bodyStyleEven,
    fill: {
      fgColor: { rgb: "F8FAFC" }
    }
  };

  // Get range of cells
  const range = XLSX.utils.decode_range(ws['!ref']);
  
  // Apply styles to each cell
  for (let R = range.s.r; R <= range.e.r; ++R) {
    for (let C = range.s.c; C <= range.e.c; ++C) {
      const cellAddress = XLSX.utils.encode_cell({ r: R, c: C });
      if (!ws[cellAddress]) {
        ws[cellAddress] = { v: '', t: 's' };
      }
      
      // First row is header
      if (R === 0) {
        ws[cellAddress].s = headerStyle;
      } else {
        ws[cellAddress].s = R % 2 === 0 ? bodyStyleEven : bodyStyleOdd;
      }
    }
  }

  // Auto-fit column widths
  const colWidths = [];
  for (let C = range.s.c; C <= range.e.c; ++C) {
    let maxWidth = 10;
    for (let R = range.s.r; R <= range.e.r; ++R) {
      const cellAddress = XLSX.utils.encode_cell({ r: R, c: C });
      const cell = ws[cellAddress];
      if (cell && cell.v) {
        const width = String(cell.v).length;
        maxWidth = Math.max(maxWidth, Math.min(width + 2, 50));
      }
    }
    colWidths.push({ wch: maxWidth });
  }
  ws['!cols'] = colWidths;

  // Set row heights
  const rowHeights = [];
  for (let R = range.s.r; R <= range.e.r; ++R) {
    rowHeights.push({ hpt: R === 0 ? 25 : 20 });
  }
  ws['!rows'] = rowHeights;
};

/**
 * Export HTML content to Excel file
 * @param {string} htmlContent - HTML content from AI generation
 * @param {string} filename - Filename without extension
 * @param {string} docType - Document type (modul, rpp, lkpd, soal, rubrik)
 */
export const exportToExcel = (htmlContent, filename, docType) => {
  try {
    // Parse HTML to array
    const data = parseHTMLToArray(htmlContent);
    
    if (data.length === 0) {
      // If no tables, create single column from text
      const textContent = htmlContent
        .replace(/<br\s*\/?>/gi, '\n')
        .replace(/<\/p>/gi, '\n\n')
        .replace(/<\/div>/gi, '\n')
        .replace(/<\/h[1-6]>/gi, '\n\n')
        .replace(/<[^>]*>/g, '')
        .trim();
      
      textContent.split('\n').forEach(line => {
        if (line.trim()) {
          data.push([line.trim()]);
        }
      });
    }

    // Add header row if data doesn't look like it has one
    const docTypeLabels = {
      modul: 'MODUL AJAR',
      rpp: 'RENCANA PELAKSANAAN PEMBELAJARAN',
      lkpd: 'LEMBAR KERJA PESERTA DIDIK',
      soal: 'BANK SOAL',
      rubrik: 'RUBRIK ASESMEN'
    };

    // Create workbook
    const wb = XLSX.utils.book_new();
    
    // Create worksheet from data
    const ws = XLSX.utils.aoa_to_sheet(data);
    
    // Apply styles
    applyStyles(ws, data);
    
    // Add worksheet to workbook
    const sheetName = docTypeLabels[docType] || 'Sheet1';
    XLSX.utils.book_append_sheet(wb, ws, sheetName.substring(0, 31));
    
    // Generate and save file
    XLSX.writeFile(wb, `${filename}.xlsx`);
    
    return true;
  } catch (error) {
    console.error('Export to Excel failed:', error);
    throw error;
  }
};

/**
 * Export multiple documents to a single Excel workbook with multiple sheets
 * @param {Array<{html: string, name: string, type: string}>} documents - Array of document objects
 * @param {string} filename - Filename without extension
 */
export const exportMultipleToExcel = (documents, filename) => {
  try {
    const wb = XLSX.utils.book_new();
    
    documents.forEach((doc, index) => {
      const data = parseHTMLToArray(doc.html);
      
      if (data.length > 0) {
        const ws = XLSX.utils.aoa_to_sheet(data);
        applyStyles(ws, data);
        
        // Sheet name max 31 chars
        const sheetName = (doc.name || `Sheet${index + 1}`).substring(0, 31);
        XLSX.utils.book_append_sheet(wb, ws, sheetName);
      }
    });
    
    XLSX.writeFile(wb, `${filename}.xlsx`);
    return true;
  } catch (error) {
    console.error('Export multiple to Excel failed:', error);
    throw error;
  }
};

export default exportToExcel;
