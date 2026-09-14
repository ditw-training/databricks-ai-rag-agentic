import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { PDFDocument } from "pdf-lib";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const moduleDirectory = path.resolve(scriptDirectory, "..");
const documentsDirectory = path.join(moduleDirectory, "documents");
const illustrationsDirectory = path.join(moduleDirectory, "assets", "illustrations");
const notebookPath = path.join(moduleDirectory, "notebooks", "01_parse_robotics_documents.py");
const rendererPath = path.join(moduleDirectory, "notebooks", "includes", "document_renderer.py");
const chunkingNotebookPath = path.join(moduleDirectory, "notebooks", "02_chunking.py");

// Validate the generated binary assets and the required notebook workflow markers.
async function main() {
  const pdfs = fs.readdirSync(documentsDirectory).filter((name) => name.endsWith(".pdf")).sort();
  const illustrations = fs.readdirSync(illustrationsDirectory).filter((name) => name.endsWith(".png")).sort();
  if (pdfs.length !== 10 || illustrations.length !== 10) {
    throw new Error(`Expected 10 PDFs and 10 illustrations; found ${pdfs.length} PDFs and ${illustrations.length} illustrations.`);
  }
  for (const name of pdfs) {
    const pdfPath = path.join(documentsDirectory, name);
    const bytes = fs.readFileSync(pdfPath);
    if (!bytes.subarray(0, 4).equals(Buffer.from("%PDF"))) {
      throw new Error(`${name} is not a PDF file.`);
    }
    const pdf = await PDFDocument.load(bytes);
    if (pdf.getPageCount() !== 3) {
      throw new Error(`${name} has ${pdf.getPageCount()} pages; expected 3.`);
    }
    if (bytes.length < 100_000) {
      throw new Error(`${name} is unexpectedly small and may be missing an illustration.`);
    }
  }
  if (!fs.existsSync(rendererPath)) {
    throw new Error("The local document_renderer helper is missing.");
  }
  if (!fs.existsSync(chunkingNotebookPath)) {
    throw new Error("The chunking continuation notebook is missing.");
  }
  const notebook = fs.readFileSync(notebookPath, "utf8");
  const requiredMarkers = [
    "F.ai_parse_document",
    "%sql",
    "ai_parse_document(",
    "'/Volumes/workspace/default/robotics_files'",
    "write.format(\"delta\")",
    "saveAsTable(parsed_delta_table)",
    "variant_explode(parsed:document:pages)",
    "variant_explode(parsed:document:elements)",
    "render_ai_parse_output(sample_document",
  ];
  for (const marker of requiredMarkers) {
    if (!notebook.includes(marker)) {
      throw new Error(`Notebook is missing required marker: ${marker}`);
    }
  }
  const orderedMarkers = ["## 1. Parse documents with Python", "## 2. Parse documents with SQL", "## 3. Save parsed output to a Delta table", "## 4. Display parsed-document metadata", "## 5. Visualize one Python-parsed document"];
  const positions = orderedMarkers.map((marker) => notebook.indexOf(marker));
  if (positions.some((position) => position < 0) || positions.some((position, index) => index > 0 && position <= positions[index - 1])) {
    throw new Error("Notebook stages are missing or out of order.");
  }
  const chunkingNotebook = fs.readFileSync(chunkingNotebookPath, "utf8");
  const chunkingMarkers = [
    "## 1. Load previously parsed data as JSON",
    "databricks-gpt-oss-20b",
    "== page ==",
    "RecursiveCharacterTextSplitter",
    "chunk_size=2000",
    "chunk_overlap=200",
    "saveAsTable(chunked_delta_table)",
  ];
  for (const marker of chunkingMarkers) {
    if (!chunkingNotebook.includes(marker)) {
      throw new Error(`Chunking notebook is missing required marker: ${marker}`);
    }
  }
  console.log(`Validated ${pdfs.length} PDFs (three pages each), ${illustrations.length} illustrations, and notebook workflow markers.`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
