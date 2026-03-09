import katex from "katex";

/**
 * Process HTML string to render LaTeX math expressions
 * Handles both inline ($...$) and display ($$...$$) math
 */
export function renderLatexInHtml(html) {
  if (!html) return html;

  // First handle display math ($$...$$)
  let processed = html.replace(/\$\$([\s\S]*?)\$\$/g, (match, tex) => {
    try {
      return katex.renderToString(tex.trim(), {
        displayMode: true,
        throwOnError: false,
        strict: false,
      });
    } catch (e) {
      return match;
    }
  });

  // Then handle inline math ($...$) - but not already processed ones
  processed = processed.replace(/\$([^\$\n]+?)\$/g, (match, tex) => {
    try {
      return katex.renderToString(tex.trim(), {
        displayMode: false,
        throwOnError: false,
        strict: false,
      });
    } catch (e) {
      return match;
    }
  });

  return processed;
}

/**
 * Convert LaTeX expression to plain Unicode text for Word/PDF export
 * Handles common math expressions used in Indonesian education
 * Uses iterative approach to handle nested braces (e.g. \frac{-b \pm \sqrt{x}}{2a})
 */
export function latexToPlainText(tex) {
  if (!tex) return tex;
  let t = tex.trim();

  // Matrix/pmatrix → bracket notation (do this first, it's self-contained)
  t = t.replace(/\\begin\{[pbvBV]?matrix\}([\s\S]*?)\\end\{[pbvBV]?matrix\}/g, (_, content) => {
    const rows = content.split('\\\\').map(row =>
      row.split('&').map(cell => cell.trim()).join('  ')
    );
    return '(' + rows.join(' ; ') + ')';
  });

  // Replace symbols FIRST (before processing structural commands)
  // This prevents \pm inside \frac from confusing the brace matching
  const symbolMap = {
    '\\times': '×', '\\div': '÷', '\\cdot': '·', '\\pm': '±',
    '\\mp': '∓', '\\leq': '≤', '\\geq': '≥', '\\neq': '≠',
    '\\approx': '≈', '\\equiv': '≡', '\\infty': '∞',
    '\\Rightarrow': '⇒', '\\rightarrow': '→', '\\Leftarrow': '⇐',
    '\\leftarrow': '←', '\\leftrightarrow': '↔',
    '\\therefore': '∴', '\\because': '∵',
    '\\in': '∈', '\\notin': '∉', '\\subset': '⊂', '\\cup': '∪', '\\cap': '∩',
    '\\sum': 'Σ', '\\prod': 'Π', '\\int': '∫',
    '\\partial': '∂', '\\nabla': '∇',
    '\\angle': '∠', '\\perp': '⊥', '\\parallel': '∥',
    '\\triangle': '△',
    '\\ldots': '…', '\\cdots': '⋯', '\\dots': '…',
    '\\quad': '  ', '\\qquad': '    ',
    '\\left': '', '\\right': '', '\\Big': '', '\\big': '', '\\bigg': '',
    '\\,': ' ', '\\;': ' ', '\\:': ' ', '\\ ': ' ',
  };
  for (const [latex, unicode] of Object.entries(symbolMap)) {
    t = t.replaceAll(latex, unicode);
  }

  // Greek letters
  const greekMap = {
    '\\alpha': 'α', '\\beta': 'β', '\\gamma': 'γ', '\\delta': 'δ',
    '\\epsilon': 'ε', '\\theta': 'θ', '\\lambda': 'λ', '\\mu': 'μ',
    '\\pi': 'π', '\\sigma': 'σ', '\\omega': 'ω', '\\phi': 'φ',
    '\\Delta': 'Δ', '\\Sigma': 'Σ', '\\Omega': 'Ω',
  };
  for (const [latex, unicode] of Object.entries(greekMap)) {
    t = t.replaceAll(latex, unicode);
  }

  // Text commands: \text{...}, \mathrm{...}, \mathbf{...}, \textbf{...}
  t = t.replace(/\\(?:text|mathrm|mathbf|textbf|mathit|textit|operatorname)\{([^{}]*)\}/g, '$1');

  // Iteratively resolve nested structures from innermost to outermost
  // Each pass resolves one level of nesting. Repeat until stable.
  let prevT;
  let iterations = 0;
  do {
    prevT = t;

    // 1. Square root (innermost first)
    t = t.replace(/\\sqrt\[(\d+)\]\{([^{}]*)\}/g, '$1√($2)');
    t = t.replace(/\\sqrt\{([^{}]*)\}/g, '√($1)');

    // 2. Fractions (after sqrt is resolved, braces inside become plain)
    t = t.replace(/\\d?frac\{([^{}]*)\}\{([^{}]*)\}/g, '($1)/($2)');

    // 3. Superscripts
    t = t.replace(/\^\{([^{}]*)\}/g, (_, content) => {
      // Common superscripts to unicode
      if (content === '2') return '²';
      if (content === '3') return '³';
      if (content === '0') return '⁰';
      if (content === '1') return '¹';
      if (content === 'n') return 'ⁿ';
      return '^(' + content + ')';
    });

    // 4. Subscripts
    t = t.replace(/_\{([^{}]*)\}/g, (_, content) => {
      if (content === '0') return '₀';
      if (content === '1') return '₁';
      if (content === '2') return '₂';
      if (content === '3') return '₃';
      if (content === 'n') return 'ₙ';
      if (content === 'k') return 'ₖ';
      return '_(' + content + ')';
    });

    // 5. \overline, \underline, \hat, \bar, \vec
    t = t.replace(/\\(?:overline|bar)\{([^{}]*)\}/g, '$1̄');
    t = t.replace(/\\(?:underline)\{([^{}]*)\}/g, '$1');
    t = t.replace(/\\hat\{([^{}]*)\}/g, '$1̂');
    t = t.replace(/\\vec\{([^{}]*)\}/g, '$1⃗');

    // 6. Remove remaining single-level braces
    t = t.replace(/\{([^{}]*)\}/g, '$1');

    iterations++;
  } while (t !== prevT && iterations < 10);

  // Simple superscripts without braces
  t = t.replace(/\^2(?![0-9])/g, '²');
  t = t.replace(/\^3(?![0-9])/g, '³');
  t = t.replace(/\^n(?![a-z])/g, 'ⁿ');

  // Simple subscripts without braces
  t = t.replace(/_1(?![0-9])/g, '₁');
  t = t.replace(/_2(?![0-9])/g, '₂');
  t = t.replace(/_0(?![0-9])/g, '₀');
  t = t.replace(/_n(?![a-z])/g, 'ₙ');

  // Clean up any remaining backslash commands
  t = t.replace(/\\[a-zA-Z]+/g, '');

  return t.trim();
}

/**
 * Convert HTML with LaTeX delimiters to plain text with Unicode math
 * Used for Word export where KaTeX HTML rendering is not supported
 */
export function convertLatexToPlainInHtml(html) {
  if (!html) return html;

  // Display math
  let processed = html.replace(/\$\$([\s\S]*?)\$\$/g, (_, tex) => {
    return latexToPlainText(tex);
  });

  // Inline math
  processed = processed.replace(/\$([^\$\n]+?)\$/g, (_, tex) => {
    return latexToPlainText(tex);
  });

  return processed;
}

/**
 * Post-process AI-generated content to fix common formatting issues:
 * - Convert plain text with numbered items into proper HTML
 * - Ensure line breaks are preserved
 * - Render LaTeX math expressions
 */
export function processGeneratedContent(html) {
  if (!html) return html;

  // If content is already well-structured HTML (has tags), just render LaTeX
  if (/<(table|div|ol|ul|h[1-6]|p)\b/i.test(html)) {
    return renderLatexInHtml(html);
  }

  // Content is plain text or poorly formatted - convert to structured HTML
  let lines = html.split("\n");
  let result = [];
  let inList = false;

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i].trim();
    if (!line) {
      if (inList) {
        result.push("</div>");
        inList = false;
      }
      result.push("<br/>");
      continue;
    }

    // Section headers (all caps or decorated lines)
    if (/^[═━─=]{3,}/.test(line)) {
      result.push('<hr class="my-4 border-[#1E3A5F]"/>');
      continue;
    }

    // Main section headers like "BANK SOAL", "KUNCI JAWABAN", "PEMBAHASAN"
    if (/^(BANK SOAL|I\.|II\.|III\.|IV\.|KUNCI JAWABAN|PEMBAHASAN|SOAL PILIHAN|SOAL ISIAN|SOAL ESSAY|CATATAN)/i.test(line)) {
      if (inList) {
        result.push("</div>");
        inList = false;
      }
      result.push(`<h3 class="font-bold text-lg text-[#1E3A5F] mt-6 mb-3">${line}</h3>`);
      continue;
    }

    // Numbered questions (1. 2. 3. etc)
    const questionMatch = line.match(/^(\d+)\.\s*(.*)/);
    if (questionMatch) {
      if (inList) {
        result.push("</div>");
      }
      inList = true;
      result.push(`<div class="mb-4 pl-2">`);
      result.push(`<p class="font-medium mb-2"><strong>${questionMatch[1]}.</strong> ${questionMatch[2]}</p>`);
      continue;
    }

    // Answer choices (A. B. C. D. E.)
    const choiceMatch = line.match(/^([A-E])\.\s*(.*)/);
    if (choiceMatch) {
      result.push(`<div class="pl-8 py-0.5">${choiceMatch[1]}. ${choiceMatch[2]}</div>`);
      continue;
    }

    // Regular text
    result.push(`<p class="mb-2">${line}</p>`);
  }

  if (inList) {
    result.push("</div>");
  }

  let processed = result.join("\n");
  return renderLatexInHtml(processed);
}
