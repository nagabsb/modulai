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
    // Skip if it looks like currency (e.g. $100)
    if (/^\d+[.,]?\d*$/.test(tex.trim())) return match;
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
