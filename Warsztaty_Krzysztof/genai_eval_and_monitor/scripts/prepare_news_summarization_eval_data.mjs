import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const moduleDirectory = path.resolve(scriptDirectory, "..");
const dataDirectory = path.join(moduleDirectory, "data");
const sourceUrl = "https://raw.githubusercontent.com/Tiiiger/benchmark_llm_summarization/main/writer_summaries.json";
const sourcePath = path.join(dataDirectory, "writer_summaries.json");
const outputPath = path.join(dataDirectory, "news-summarization.csv");

function escapeCsv(value) {
  const text = String(value ?? "").replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  return `"${text.replaceAll('"', '""')}"`;
}

const response = await fetch(sourceUrl);
if (!response.ok) {
  throw new Error(`Could not download the source data: ${response.status} ${response.statusText}`);
}

const sourceText = await response.text();
const records = JSON.parse(sourceText);
if (!Array.isArray(records)) {
  throw new Error("Expected writer_summaries.json to contain a JSON array.");
}

const evaluationRows = records
  .filter((record) => typeof record.article === "string" && typeof record.summary === "string")
  .map((record) => ({ input: record.article.trim(), output: record.summary.trim() }))
  .filter((record) => record.input && record.output);

if (evaluationRows.length === 0) {
  throw new Error("The source file did not contain usable article/summary pairs.");
}

fs.mkdirSync(dataDirectory, { recursive: true });
fs.writeFileSync(sourcePath, sourceText, "utf8");
fs.writeFileSync(
  outputPath,
  ["input,output", ...evaluationRows.map((row) => `${escapeCsv(row.input)},${escapeCsv(row.output)}`)].join("\n") + "\n",
  "utf8",
);

console.log(`Saved source JSON: ${sourcePath}`);
console.log(`Created evaluation CSV with ${evaluationRows.length} rows: ${outputPath}`);
