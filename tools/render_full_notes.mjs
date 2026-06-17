import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, "..");

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function inlineMarkdown(value) {
  let escaped = escapeHtml(value);
  escaped = escaped.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_match, text, href) => {
    return `<a href="${href}">${text}</a>`;
  });
  escaped = escaped.replace(/`([^`]+)`/g, "<code>$1</code>");
  return escaped;
}

function isTableSeparator(line) {
  return /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line);
}

function isTableLine(line) {
  return /^\s*\|.*\|\s*$/.test(line);
}

function splitTableRow(line) {
  let trimmed = line.trim();
  if (trimmed.startsWith("|")) trimmed = trimmed.slice(1);
  if (trimmed.endsWith("|")) trimmed = trimmed.slice(0, -1);
  return trimmed.split("|").map((cell) => cell.trim());
}

function isSpecialStart(line, nextLine = "") {
  const trimmed = line.trim();
  return (
    trimmed === "" ||
    /^```/.test(trimmed) ||
    /^#{1,6}\s+/.test(trimmed) ||
    /^---+$/.test(trimmed) ||
    /^>\s?/.test(trimmed) ||
    /^\s*-\s+/.test(line) ||
    (isTableLine(line) && isTableSeparator(nextLine))
  );
}

function markdownToHtml(markdown) {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  const out = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();
    const next = lines[i + 1] ?? "";

    if (trimmed === "") {
      i += 1;
      continue;
    }

    if (/^```/.test(trimmed)) {
      const lang = trimmed.replace(/^```/, "").trim();
      const code = [];
      i += 1;
      while (i < lines.length && !/^```/.test(lines[i].trim())) {
        code.push(lines[i]);
        i += 1;
      }
      if (i < lines.length) i += 1;
      const className = lang ? ` class="language-${escapeHtml(lang)}"` : "";
      out.push(`<pre><code${className}>${escapeHtml(code.join("\n"))}</code></pre>`);
      continue;
    }

    if (isTableLine(line) && isTableSeparator(next)) {
      const header = splitTableRow(line);
      i += 2;
      const rows = [];
      while (i < lines.length && isTableLine(lines[i])) {
        rows.push(splitTableRow(lines[i]));
        i += 1;
      }
      out.push(
        [
          '<div class="table-wrap"><table>',
          "<thead><tr>" + header.map((cell) => `<th>${inlineMarkdown(cell)}</th>`).join("") + "</tr></thead>",
          "<tbody>",
          rows.map((row) => "<tr>" + row.map((cell) => `<td>${inlineMarkdown(cell)}</td>`).join("") + "</tr>").join("\n"),
          "</tbody></table></div>",
        ].join("\n"),
      );
      continue;
    }

    const heading = /^(#{1,6})\s+(.*)$/.exec(trimmed);
    if (heading) {
      const level = Math.min(6, heading[1].length + 2);
      out.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`);
      i += 1;
      continue;
    }

    if (/^---+$/.test(trimmed)) {
      out.push("<hr />");
      i += 1;
      continue;
    }

    if (/^>\s?/.test(trimmed)) {
      const quote = [];
      while (i < lines.length && /^>\s?/.test(lines[i].trim())) {
        quote.push(lines[i].trim().replace(/^>\s?/, ""));
        i += 1;
      }
      out.push(`<blockquote><p>${quote.map(inlineMarkdown).join("<br />")}</p></blockquote>`);
      continue;
    }

    if (/^\s*-\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*-\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*-\s+/, ""));
        i += 1;
      }
      out.push("<ul>" + items.map((item) => `<li>${inlineMarkdown(item)}</li>`).join("") + "</ul>");
      continue;
    }

    const paragraph = [];
    while (i < lines.length && !isSpecialStart(lines[i], lines[i + 1] ?? "")) {
      paragraph.push(lines[i].trim());
      i += 1;
    }
    if (paragraph.length > 0) {
      out.push(`<p>${paragraph.map(inlineMarkdown).join("<br />")}</p>`);
    }
  }

  return out.join("\n");
}

function slugFor(filePath) {
  return filePath.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

async function buildFullNotes(pagePath, entries, title, note) {
  const pageAbs = path.join(root, pagePath);
  const pageDir = path.dirname(pagePath);
  const articles = [];

  for (const entry of entries) {
    const mdAbs = path.join(root, entry.path);
    const markdown = await readFile(mdAbs, "utf8");
    const relativeBase = pageDir === "." ? "" : pageDir;
    const link = path.relative(relativeBase, entry.path).replaceAll(path.sep, "/");
    const converted = markdownToHtml(markdown)
      .split("\n")
      .map((line) => `              ${line}`)
      .join("\n");

    articles.push(`          <article class="source-panel markdown-source" id="full-${slugFor(entry.path)}">
            <div class="markdown-source-header">
              <h3>${escapeHtml(entry.title)}</h3>
              <a href="${escapeHtml(link)}">원본 Markdown</a>
            </div>
            <div class="markdown-content">
${converted}
            </div>
          </article>`);
  }

  const section = `      <!-- full-notes:start -->
      <section class="section" id="full-notes" aria-labelledby="full-notes-title">
        <div class="section-header">
          <div>
            <p class="section-kicker">Full Notes</p>
            <h2 id="full-notes-title">${escapeHtml(title)}</h2>
          </div>
          <p class="section-note">${escapeHtml(note)}</p>
        </div>
        <div class="full-notes">
${articles.join("\n")}
        </div>
      </section>
      <!-- full-notes:end -->`;

  let html = await readFile(pageAbs, "utf8");
  if (html.includes("<!-- full-notes:start -->")) {
    html = html.replace(/\s*<!-- full-notes:start -->[\s\S]*?<!-- full-notes:end -->/, `\n${section}`);
  } else {
    html = html.replace(/\n\s*<\/main>/, `\n${section}\n    </main>`);
  }
  await writeFile(pageAbs, html, "utf8");
}

await buildFullNotes(
  "index.html",
  [{ path: "README.md", title: "README.md" }],
  "루트 README 전체",
  "아래 내용은 루트 README.md의 모든 Markdown 내용을 HTML로 변환한 것입니다.",
);

await buildFullNotes(
  "Day1/index.html",
  [
    { path: "Day1/README.md", title: "Day1/README.md" },
    { path: "Day1/Hour0930.md", title: "Hour0930.md" },
    { path: "Day1/Hour1030.md", title: "Hour1030.md" },
    { path: "Day1/Hour1130.md", title: "Hour1130.md" },
    { path: "Day1/Hour1330.md", title: "Hour1330.md" },
    { path: "Day1/Hour1430.md", title: "Hour1430.md" },
    { path: "Day1/Hour1600.md", title: "Hour1600.md" },
  ],
  "Day 1 Markdown 전체",
  "아래 내용은 Day1의 README와 시간대별 Markdown 원문 전체를 HTML로 변환한 것입니다.",
);

await buildFullNotes(
  "Day2/index.html",
  [
    { path: "Day2/README.md", title: "Day2/README.md" },
    { path: "Day2/Hour0930.md", title: "Hour0930.md" },
    { path: "Day2/Hour1030.md", title: "Hour1030.md" },
    { path: "Day2/Hour1130.md", title: "Hour1130.md" },
  ],
  "Day 2 Markdown 전체",
  "아래 내용은 Day2의 README와 시간대별 Markdown 원문 전체를 HTML로 변환한 것입니다.",
);

console.log("Rendered full-note sections.");
