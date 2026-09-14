import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const workspaceDirectory = path.resolve(scriptDirectory, "..");
const ragAgentDirectory = path.join(workspaceDirectory, "rag_agent");
const require = createRequire(path.join(ragAgentDirectory, "package.json"));
const PDFDocument = require("pdfkit");
const { PDFDocument: PdfLibDocument } = require("pdf-lib");

const outputPath = path.join(workspaceDirectory, "sprawozdanie_zbiorcze_v3.pdf");
const backgroundPath = path.join(ragAgentDirectory, "assets", "illustrations", "07_robotics_and_ai.png");
const regularFontPath = "C:\\Windows\\Fonts\\segoeui.ttf";
const boldFontPath = "C:\\Windows\\Fonts\\segoeuib.ttf";
const pageWidth = 595.28;
const pageHeight = 841.89;
const margin = 54;
const contentWidth = pageWidth - margin * 2;
const contentBottom = 770;

for (const requiredPath of [backgroundPath, regularFontPath, boldFontPath]) {
  if (!fs.existsSync(requiredPath)) throw new Error(`Missing report asset: ${requiredPath}`);
}

const doc = new PDFDocument({ autoFirstPage: false, size: "A4", margin: 0, bufferPages: true });
const output = fs.createWriteStream(outputPath);
doc.pipe(output);
doc.registerFont("Regular", regularFontPath);
doc.registerFont("Bold", boldFontPath);

function drawPage() {
  doc.addPage({ size: "A4", margin: 0 });
  const imageWidth = 1536;
  const imageHeight = 1024;
  const scale = Math.max(pageWidth / imageWidth, pageHeight / imageHeight);
  const width = imageWidth * scale;
  const height = imageHeight * scale;
  doc.save();
  doc.opacity(0.22).image(backgroundPath, (pageWidth - width) / 2, (pageHeight - height) / 2, { width, height });
  doc.restore();
  doc.save();
  doc.fillColor("#FFFFFF").opacity(0.82).roundedRect(35, 40, pageWidth - 70, pageHeight - 95, 12).fill();
  doc.restore();
  doc.strokeColor("#B6C0CD").lineWidth(0.8).moveTo(margin, 77).lineTo(pageWidth - margin, 77).stroke();
  doc.strokeColor("#CBD5E1").lineWidth(0.6).moveTo(margin, 790).lineTo(pageWidth - margin, 790).stroke();
  doc.y = 98;
}

function textHeight(text, options = {}) {
  return doc.font(options.bold ? "Bold" : "Regular").fontSize(options.size ?? 10)
    .heightOfString(text, { width: options.width ?? contentWidth, lineGap: options.lineGap ?? 2.7 });
}

function ensureSpace(height) {
  if (doc.y + height > contentBottom) drawPage();
}

function chapter(number, title) {
  drawPage();
  doc.font("Bold").fontSize(18).fillColor("#374151").text(`${number}. ${title}`, margin, doc.y, { width: contentWidth });
  doc.y += 14;
}

function subsection(title, firstText) {
  const titleHeight = textHeight(title, { bold: true, size: 11.5, lineGap: 2 });
  const firstHeight = textHeight(firstText, { size: 10, lineGap: 2.7 });
  ensureSpace(titleHeight + firstHeight + 22);
  doc.font("Bold").fontSize(11.5).fillColor("#374151").text(title, margin, doc.y, { width: contentWidth });
  doc.y += 5;
}

function paragraph(text) {
  const height = textHeight(text, { size: 10, lineGap: 2.7 });
  ensureSpace(height + 10);
  doc.font("Regular").fontSize(10).fillColor("#4B5563").text(text, margin, doc.y, { width: contentWidth, lineGap: 2.7 });
  doc.y += 7;
}

function bullet(text) {
  const indent = 15;
  const height = textHeight(text, { size: 10, width: contentWidth - indent, lineGap: 2.5 });
  ensureSpace(height + 8);
  const y = doc.y;
  doc.font("Regular").fontSize(10).fillColor("#71839A").text("•", margin, y);
  doc.font("Regular").fontSize(10).fillColor("#4B5563").text(text, margin + indent, y, { width: contentWidth - indent, lineGap: 2.5 });
  doc.y = y + height + 5;
}

function notebooks(items) {
  for (const [name, description] of items) bullet(`${name} — ${description}`);
}

chapter("1", "Wstęp");
paragraph("Dokument podsumowuje cztery moduły szkoleniowe przygotowane w środowisku Databricks: rag_agent, single_agent_app, genai_eval_and_monitor oraz genai_deploy_and_monitor. Materiały, notebooki, dane testowe i instrukcje zostały wygenerowane przez AI na podstawie celów dydaktycznych kursów Databricks, a nie przepisane z ich materiałów źródłowych.");
paragraph("Zakres obejmuje pełny przepływ od dokumentów i RAG, przez pojedynczego agenta z narzędziami Unity Catalog, po guardrails, ewaluację, batch inference, wdrażanie oraz monitoring. Raport rozdziela etapy zweryfikowane w Databricks Free Edition od etapów przygotowanych, lecz zablokowanych ograniczeniami Model Serving, AI Gateway lub dostępnych endpointów.");
paragraph("Cztery moduły tworzą jeden ciąg praktycznych ćwiczeń: rag_agent buduje RAG na dokumentach, single_agent_app pokazuje agenta pracującego z funkcjami Unity Catalog, genai_eval_and_monitor dodaje guardrails i ewaluację, a genai_deploy_and_monitor opisuje batch scoring, wdrożenie oraz monitoring. Zestaw zawiera dane testowe, notebooki, instrukcje i odtwarzalne raporty.");
paragraph("Największym ograniczeniem okazała się rozbieżność między materiałami kursowymi a możliwościami Databricks Free Edition: zmienna dostępność modeli, limit endpointów, brak możliwości utworzenia części endpointów oraz brak external storage wymaganego przez AI Gateway. Z tego powodu raport nie przedstawia niezweryfikowanych etapów jako działających. Największą wartością materiałów jest przejrzyste pokazanie pełnych przepływów oraz rzeczywistych wymagań platformy, wraz z rozróżnieniem kodu, konfiguracji UI i ograniczeń środowiska.");

chapter("2", "rag_agent");
subsection("Wstęp", "Moduł jest inspirowany kursem „Building Retrieval Agents On Databricks”. Pokazuje drogę od testowych dokumentów PDF do systemu RAG, który wyszukuje fragmenty materiałów i używa ich jako kontekstu odpowiedzi. Moduł oraz instrukcja zostały zweryfikowane 22.07.2026.");
paragraph("Moduł jest inspirowany kursem „Building Retrieval Agents On Databricks”. Pokazuje drogę od testowych dokumentów PDF do systemu RAG, który wyszukuje fragmenty materiałów i używa ich jako kontekstu odpowiedzi. Moduł oraz instrukcja zostały zweryfikowane 22.07.2026.");
subsection("Notebooki", "01_parse_robotics_documents — parsowanie dziesięciu testowych PDF-ów przez Python i SQL z ai_parse_document, zapis Pythonowego wyniku do Delta, metadane oraz wizualizacja dokumentu.");
notebooks([
  ["01_parse_robotics_documents", "parsowanie dziesięciu testowych PDF-ów przez Python i SQL z ai_parse_document, zapis Pythonowego wyniku do Delta, metadane oraz wizualizacja dokumentu."],
  ["02_chunking", "konwersja sparsowanego JSON do Markdown i zwykłego tekstu, chunking LangChain oraz zapis chunków do Delta."],
  ["03_vector_search", "embeddingi, Change Data Feed, indeks AI Search Delta Sync oraz semantic, hybrid, full-text i filtrowane wyszukiwanie."],
  ["04_building_and_logging", "AI Playground, agent LangChain oparty na AI Search, MLflow tracing oraz rejestracja modelu w Unity Catalog."],
  ["05_building_assistant", "wczytanie PDF-ów z Volume i instrukcja utworzenia Knowledge Assistant oraz Examples / Guidelines w UI."],
]);
subsection("Ograniczenia", "Reranking z ostatniego bloku notebooka 03 nie był dostępny w Free Edition bez dodatkowej konfiguracji workspace.");
bullet("Reranking z ostatniego bloku notebooka 03 nie był dostępny w Free Edition bez dodatkowej konfiguracji workspace.");
bullet("Dostępność AI Search, Knowledge Assistant i modeli zależy od regionu oraz workspace. GPT zwracały timeouty, a Inkling był dostępny tylko przez krótki czas, po czym przestał być widoczny.");
bullet("Knowledge Assistant nie został potwierdzony end-to-end w Free Edition, mimo że instrukcja UI i źródło Volume zostały przygotowane.");
subsection("Wnioski", "Przygotowano dziesięć fikcyjnych artykułów o robotyce. Każdy zawiera mockowy tekst edukacyjny, ilustrację, tabelę porównawczą i wykres z fikcyjnymi danymi, dzięki czemu nadaje się do testowania parsowania.");
paragraph("Przygotowano dziesięć fikcyjnych artykułów o robotyce. Każdy zawiera mockowy tekst edukacyjny, ilustrację, tabelę porównawczą i wykres z fikcyjnymi danymi, dzięki czemu nadaje się do testowania parsowania. Materiały kursu „Building Retrieval Agents On Databricks” były praktyczne i dobrze uzasadniały kolejne kroki, na przykład zasady tworzenia promptów. Najwięcej problemów wynikało z konfiguracji usług zależnych od workspace, a nie z samego przepływu RAG.");

chapter("3", "single_agent_app");
subsection("Wstęp", "Moduł jest inspirowany kursem „Building Single-Agent Applications on Databricks”. Zamiast indeksu dokumentów wykorzystuje tabelę Delta z ofertami Airbnb w San Francisco oraz funkcje Unity Catalog, które agent może wywoływać jako narzędzia.");
paragraph("Moduł jest inspirowany kursem „Building Single-Agent Applications on Databricks”. Zamiast indeksu dokumentów wykorzystuje tabelę Delta z ofertami Airbnb w San Francisco oraz funkcje Unity Catalog, które agent może wywoływać jako narzędzia. Moduł i instrukcja zostały zweryfikowane 23.07.2026.");
subsection("Notebooki", "06_building_uc_functions — wczytanie pliku Airbnb CSV do Delta table, funkcje SQL i Python, testy ich działania oraz rejestracja funkcji w Unity Catalog.");
notebooks([
  ["06_building_uc_functions", "wczytanie pliku Airbnb CSV do Delta table, funkcje SQL i Python, testy ich działania oraz rejestracja funkcji w Unity Catalog."],
  ["07_building_agent", "agent LangChain z Unity Catalog Function Toolkit, konfiguracją JSON, endpointem databricks-meta-llama-3-3-70b-instruct i MLflow tracingiem."],
  ["08_mlflow_tracing", "lokalizacja eksperymentów MLflow, artefakty, testowe wywołanie agenta, eksploracja trace’ów oraz trace decorator."],
  ["09_tagging", "tagowanie trace’ów, walidacja promptów, eksport agenta, zapis modelu pyfunc i rejestracja modelu w Unity Catalog."],
]);
subsection("Ograniczenia", "Podstawowy przepływ modułu został wykonany w Free Edition.");
paragraph("Podstawowy przepływ modułu został wykonany w Free Edition. Nie wystąpiły trwałe blokady limitów, ponieważ scenariusz nie wymagał AI Search ani wielu synchronizowanych usług. Występowały natomiast przejściowe problemy zgodności LangChain i LangGraph, które wymagały aktualizacji kodu oraz właściwego doboru zależności.");
subsection("Wnioski", "Pobrany CSV Airbnb zapewnił prosty i realistyczny kontekst dla funkcji Unity Catalog oraz agenta.");
paragraph("Pobrany CSV Airbnb zapewnił prosty i realistyczny kontekst dla funkcji Unity Catalog oraz agenta. W tym module dostępny był model databricks-meta-llama-3-3-70b-instruct. Tworzenie notebooków było prostsze niż w rag_agent, a Codex lepiej niż Genie sprawdzał się w diagnozowaniu błędów zależności i naprawie kodu. Materiały teoretyczne kursu były jednak mało przystępne: zawierały dużo buzzwordów i nazw własnych, a część treści niewiele pomagała osobie bez wcześniejszej znajomości Databricks i agentów AI.");

chapter("4", "genai_eval_and_monitor");
subsection("Wstęp", "Moduł jest inspirowany kursem „Generative AI Application Evaluation and Governance”. Rozszerza wcześniejsze ćwiczenia o dane z Marketplace, guardrails, benchmarkowanie, klasyczną ewaluację w MLflow oraz LLM-as-a-judge.");
paragraph("Moduł jest inspirowany kursem „Generative AI Application Evaluation and Governance”. Rozszerza wcześniejsze ćwiczenia o dane z Marketplace, guardrails, benchmarkowanie, klasyczną ewaluację w MLflow oraz LLM-as-a-judge. Materiały zostały przygotowane i zaktualizowane 24.07.2026.");
subsection("Notebooki", "10_exploring_datasets — instrukcje znalezienia, sprawdzenia warunków i ręcznego importu danych Amazon Products od Bright Data oraz Personal Income od Rearc z Databricks Marketplace.");
notebooks([
  ["10_exploring_datasets", "instrukcje znalezienia, sprawdzenia warunków i ręcznego importu danych Amazon Products od Bright Data oraz Personal Income od Rearc z Databricks Marketplace."],
  ["11_guardrails", "przykłady odmowy niebezpiecznych próśb, ograniczenia domenowego i aktualne użycie AI Guardrails zamiast przestarzałego enable_safety_filter."],
  ["12_implementing_guardrails", "instrukcja Llama Guard z Marketplace, kategorie unsafe, ocena promptów i integracja z Llama Instruct."],
  ["13_benchmark_evaluation", "porównanie modeli na danych news summarization oraz klasyczna metryka ROUGE-1 w MLflow."],
  ["14_llm_as_a_judge", "własna metryka professionalism 1–5, przykłady EvaluationExample, mean i variance oraz analiza wyników eksperymentu."],
]);
subsection("Ograniczenia", "Notebook 12 wymaga endpointu Model Serving dla Llama Guard.");
bullet("Notebook 12 wymaga endpointu Model Serving dla Llama Guard. Free Edition nie pozwoliła utworzyć wymaganego endpointu, więc ten etap nie został zweryfikowany wykonawczo.");
bullet("Notebooki 13 i 14 wymagały licznych korekt z powodu zmian MLflow i SDK: legacy API mlflow.evaluate, struktury evaluator_config oraz różnego formatu odpowiedzi endpointów.");
subsection("Wnioski", "Utworzono dataset news-summarization.csv zawierający 302 pary tekst–referencyjne streszczenie.");
paragraph("Utworzono dataset news-summarization.csv zawierający 302 pary tekst–referencyjne streszczenie. Moduł pokazuje, że ocena aplikacji generatywnej wymaga danych referencyjnych, jawnej polityki bezpieczeństwa, porównywalnego benchmarku i kontroli jakości odpowiedzi. Parametr enable_safety_filter okazał się przestarzały i zwracał błędy, dlatego właściwym kierunkiem są AI Guardrails konfigurowane w ustawieniach endpointu.");

chapter("5", "genai_deploy_and_monitor");
subsection("Wstęp", "Moduł obejmuje batch inference, rejestrację modelu, wdrożenie łańcucha RAG w custom Model Serving oraz monitoring online.");
paragraph("Moduł obejmuje batch inference, rejestrację modelu, wdrożenie łańcucha RAG w custom Model Serving oraz monitoring online. Materiały przygotowano 28.07.2026. Notebook 15 może być używany niezależnie, natomiast notebooki 16–17 pozostają niesprawdzone end-to-end.");
subsection("Notebooki", "15_batch_inference — tabela Delta z tekstami XSum, pipeline Hugging Face T5-small, MLflow, Unity Catalog Model Registry, alias @champion oraz przykład batch inference przez ai_query.");
notebooks([
  ["15_batch_inference", "tabela Delta z tekstami XSum, pipeline Hugging Face T5-small, MLflow, Unity Catalog Model Registry, alias @champion oraz przykład batch inference przez ai_query."],
  ["16_deploying_llm_chain", "przygotowanie i rejestracja łańcucha RAG, sekrety endpointu, custom Model Serving, instrukcje UI i test inference."],
  ["17_online_monitoring", "rozpakowanie inference payloadów, metryki toxicity, perplexity i readability, Delta streaming oraz Data Quality Monitoring."],
]);
subsection("Ograniczenia", "Oryginalny kurs zakłada gotowego agenta RAG, ale nie wyjaśnia jego budowy.");
bullet("Oryginalny kurs zakłada gotowego agenta RAG, ale nie wyjaśnia jego budowy. Odtworzenie takiego agenta z użyciem Codex wymagało oddzielnej i czasochłonnej pracy.");
bullet("Dwie próby utworzenia endpointu notebooka 16 zakończyły się niepowodzeniem: provisioning długo pozostawał w stanie Not Ready / Updating, po czym przechodził w Failed.");
bullet("AI Gateway telemetry i inference tables nie mogą używać workspace.default, ponieważ jest to default storage. Usługa wymaga katalogu Unity Catalog opartego na external storage. Brak tabeli payload z notebooka 16 blokuje prawdziwy test notebooka 17.");
bullet("Cały kurs obejmujący cztery moduły potrzebuje więcej endpointów niż jest dostępnych równocześnie w Free Edition. Kontynuowanie ćwiczeń wymaga usuwania starszych endpointów.");
subsection("Wnioski", "Operacje wdrożeniowe i monitoringowe są długie, a troubleshooting jest mało wygodny.");
paragraph("Operacje wdrożeniowe i monitoringowe są długie, a troubleshooting jest mało wygodny: błąd może pojawić się dopiero po wielu minutach. W notebooku batch inference wystąpił też przypadek, w którym wykonanie nie zgłosiło błędu, ale tabela wynikowa zawierała wartości null. Materiały teoretyczne są mało pomocne dla początkujących, ponieważ wprowadzają wiele nazw i definicji bez dostatecznego wyjaśnienia przygotowania zasobów, zależności i częstych punktów awarii.");

const range = doc.bufferedPageRange();
for (let index = 0; index < range.count; index += 1) {
  doc.switchToPage(index);
  doc.font("Regular").fontSize(8).fillColor("#6B7280")
    .text(`Strona ${index + 1} z ${range.count}`, margin, 801, { width: contentWidth, align: "right" });
}

doc.end();
await new Promise((resolve, reject) => {
  output.on("finish", resolve);
  output.on("error", reject);
});

const report = await PdfLibDocument.load(fs.readFileSync(outputPath));
if (report.getPageCount() < 5) throw new Error("Expected at least five pages.");
console.log(`Generated ${report.getPageCount()}-page report: ${outputPath}`);
