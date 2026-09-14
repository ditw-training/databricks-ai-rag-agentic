import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import PDFDocument from "pdfkit";
import { PDFDocument as PdfLibDocument } from "pdf-lib";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const moduleDirectory = path.resolve(scriptDirectory, "..");
const documentsDirectory = path.join(moduleDirectory, "documents");
const illustrationsDirectory = path.join(moduleDirectory, "assets", "illustrations");

const articles = [
  {
    slug: "01_everyday_robotics",
    title: "Everyday Robotics: Quiet Helpers in Familiar Places",
    subtitle: "A fictional course sample about robots that support small routines.",
    image: "01_everyday_robotics.png",
    accent: "#D97745",
    overview: "Robots are no longer limited to factories or science-fiction films. In this fictional learning scenario, compact machines help people carry objects, water plants, tidy shared rooms, or guide visitors through a building. The useful part is not the shiny shell: it is the careful way a robot senses its surroundings and chooses a safe next action.",
    story: "Imagine a home assistant named Luma. It checks whether a watering can is full, rolls around a chair instead of bumping into it, and stops when a person enters its path. Luma does not understand a household like a person does. It combines simple maps, distance readings, and a short list of permitted tasks. That limited focus is exactly what makes it dependable.",
    detail: "Everyday robots work best when their job is narrow, repeatable, and easy to pause. A friendly experience also includes visible status lights, a clear stop button, and a predictable route. These design choices make a machine feel less mysterious and make it easier for people to decide when to trust it.",
    tableTitle: "Fictional helper-robot task comparison",
    table: [["Task", "Main input", "Useful behaviour"], ["Plant care", "Moisture + camera", "Moves slowly near pots"], ["Item delivery", "Map + distance sensor", "Chooses clear paths"], ["Visitor guidance", "Touch screen + map", "Stops for questions"]],
    chartTitle: "Fictional weekly task completion (%)",
    chart: [58, 66, 74, 81, 88],
    labels: ["Mon", "Tue", "Wed", "Thu", "Fri"],
    terms: [["Autonomy", "Making limited decisions without a person controlling each move."], ["Obstacle detection", "Noticing objects and people before a collision."], ["Human-centred design", "Designing technology around real human needs."]]
  },
  {
    slug: "02_robot_senses",
    title: "Robot Senses: Cameras, Distance, and Touch",
    subtitle: "A fictional course sample about how robots build a useful picture of a room.",
    image: "02_robot_senses.png",
    accent: "#2F8B87",
    overview: "A robot cannot rely on intuition. It gathers small clues from sensors and combines them into an estimate of what is nearby. A camera may notice a door, a depth sensor may estimate the door's distance, and a bumper may confirm that something is closer than expected. Each sensor has strengths and blind spots.",
    story: "In a fictional greenhouse, a rover named Fern checks plant beds. Its camera helps it recognize large leaves, while a short-range sensor helps it avoid the glass wall. If sunlight creates a confusing reflection, the rover compares several readings instead of trusting one picture. That is called sensor fusion: using multiple partial observations to make a safer decision.",
    detail: "Good sensor design is not about collecting every possible measurement. It is about selecting inputs that answer a task-specific question. Is the corridor clear? Is the tray full? Has the robot reached its charging station? Clear questions produce simpler systems and clearer ways to test them.",
    tableTitle: "Fictional sensor roles in a greenhouse rover",
    table: [["Sensor", "Sees best", "Common limitation"], ["Camera", "Shape and colour", "Lighting changes"], ["Depth sensor", "Distance to surfaces", "Reflective materials"], ["Bumper", "Direct contact", "Acts only at close range"]],
    chartTitle: "Fictional confidence after combining sensors (%)",
    chart: [42, 56, 69, 78, 91],
    labels: ["1", "2", "3", "4", "5"],
    terms: [["Sensor fusion", "Combining sensor readings into one stronger estimate."], ["Calibration", "Checking that a sensor's measurements are accurate."], ["Field of view", "The area a sensor can observe at one time."]]
  },
  {
    slug: "03_motion_and_actuators",
    title: "Motion and Actuators: Turning Plans into Movement",
    subtitle: "A fictional course sample about motors, feedback, and deliberate motion.",
    image: "03_motion_actuators.png",
    accent: "#B26E32",
    overview: "Actuators are the parts that turn electrical commands into physical movement. Motors spin wheels, lift a small arm, or open a gripper. A robot must do more than send a command such as move forward. It also needs feedback that tells it whether the intended motion actually happened.",
    story: "Consider a tabletop sorting arm called Orbit. It picks up a wooden block, rotates its wrist, and gently lowers the block into a tray. Encoders report how far each joint moved, while a controller compares the current position with the target. If the arm moves too far, the controller corrects the next command instead of repeating the same error.",
    detail: "Smooth motion is often more valuable than maximum speed. Sudden starts can shift an object or surprise a nearby person. In learning projects, a useful rule is to set modest speed limits first, then tune the motion after watching the robot perform its full task safely.",
    tableTitle: "Fictional actuator choices for a sorting arm",
    table: [["Component", "Job", "Feedback signal"], ["Joint motor", "Rotates an arm section", "Encoder angle"], ["Gripper motor", "Opens and closes fingers", "Position or current"], ["Wheel motor", "Moves a mobile base", "Wheel rotation"]],
    chartTitle: "Fictional placement accuracy as tuning improves (%)",
    chart: [35, 49, 63, 77, 89],
    labels: ["Trial 1", "2", "3", "4", "5"],
    terms: [["Actuator", "A component that creates movement."], ["Encoder", "A sensor that reports position or rotation."], ["Feedback loop", "A cycle of measuring, comparing, and correcting."]]
  },
  {
    slug: "04_mobile_robots",
    title: "Mobile Robots: Finding a Clear Route",
    subtitle: "A fictional course sample about robots that move through shared spaces.",
    image: "04_mobile_robots.png",
    accent: "#4B85AE",
    overview: "Mobile robots must answer two related questions: where am I, and how can I reach the next safe point? A map gives a broad plan, but a live sensor view matters just as much because people, chairs, and deliveries can change a hallway in seconds.",
    story: "A fictional campus delivery robot named Piko travels from a library desk to a study room. It follows a route that avoids stairs and busy entrances. When a group of students crosses its path, Piko slows down and waits. The robot does not need to predict every human choice; it needs a cautious rule for uncertain moments.",
    detail: "Navigation becomes easier when the environment has clear landmarks and well-defined allowed zones. Visual markers, charging bays, and gently curved paths can improve a system more than an overly complex algorithm. This is why robotics design includes both software and the design of the physical place.",
    tableTitle: "Fictional navigation decisions",
    table: [["Situation", "Robot signal", "Safe response"], ["Clear hallway", "Map agrees with sensors", "Continue at normal speed"], ["Person nearby", "Distance reduces", "Slow and yield"], ["Blocked route", "Path is unavailable", "Choose a permitted detour"]],
    chartTitle: "Fictional route completion with map updates (%)",
    chart: [50, 61, 70, 83, 90],
    labels: ["Map A", "B", "C", "D", "E"],
    terms: [["Localization", "Estimating a robot's position on a map."], ["Path planning", "Choosing a route from start to goal."], ["Dynamic obstacle", "Something that can move, such as a person."]]
  },
  {
    slug: "05_collaborative_robots",
    title: "Collaborative Robots: Sharing the Worktable",
    subtitle: "A fictional course sample about predictable human–robot collaboration.",
    image: "05_collaborative_robots.png",
    accent: "#7A7BB8",
    overview: "Collaborative robots, often called cobots, are designed for tasks where people and machines work close to one another. The goal is not to make the robot seem human. The goal is to make its movement, limits, and hand-off points easy for a person to understand.",
    story: "In a fictional community workshop, a cobot named Nori holds a part while a technician tightens two screws. The technician starts the cycle using a clear control, and Nori moves only inside a marked area. When the technician reaches in, the cobot pauses. The workflow is calm because both partners have clear roles.",
    detail: "A collaborative setup needs more than a friendly-looking robot. It needs task limits, speed limits, emergency stops, training, and a routine for unusual situations. These layers of care are more important than a dramatic demonstration of speed or strength.",
    tableTitle: "Fictional roles at a shared worktable",
    table: [["Step", "Person", "Cobot"], ["Prepare", "Checks the part", "Holds position"], ["Assemble", "Completes detailed work", "Stabilizes the part"], ["Review", "Confirms quality", "Waits for next cycle"]],
    chartTitle: "Fictional comfort rating after practice sessions (%)",
    chart: [46, 58, 67, 79, 87],
    labels: ["Day 1", "2", "3", "4", "5"],
    terms: [["Cobot", "A robot intended to work near people in a controlled task."], ["Hand-off", "A planned transfer of an object or responsibility."], ["Safeguard", "A design feature that reduces a possible harm."]]
  },
  {
    slug: "06_warehouse_robotics",
    title: "Warehouse Robotics: Moving the Right Item at the Right Time",
    subtitle: "A fictional course sample about coordinated logistics robots.",
    image: "06_warehouse_robotics.png",
    accent: "#466B9F",
    overview: "Warehouse robots often move shelves, bins, or carts instead of handling every object directly. The central challenge is coordination. A system must know what is moving, which aisle is available, and when a person needs to enter the same area.",
    story: "In a fictional fulfilment centre, compact robots carry shelf pods to packing stations. A simple dispatcher assigns each robot a destination and prevents two robots from claiming the same narrow space. Workers still make decisions about exceptions, fragile goods, and quality checks.",
    detail: "The most useful metric is not just speed. A healthy logistics system balances accuracy, clear traffic rules, battery planning, and safe shared zones. Small delays can be better than a traffic jam that affects the entire floor.",
    tableTitle: "Fictional warehouse robot signals",
    table: [["Signal", "Meaning", "Operational response"], ["Pod ready", "Shelf is available", "Assign a pickup robot"], ["Aisle busy", "Route has traffic", "Delay or reroute"], ["Battery low", "Charge is needed soon", "Schedule a charging stop"]],
    chartTitle: "Fictional on-time deliveries by shift (%)",
    chart: [62, 70, 76, 84, 92],
    labels: ["Shift 1", "2", "3", "4", "5"],
    terms: [["Fleet", "A group of robots managed together."], ["Dispatcher", "Software that assigns tasks or routes."], ["Throughput", "How much useful work is completed in a period."]]
  },
  {
    slug: "07_robotics_and_ai",
    title: "Robotics and AI: Learning from Patterns, Acting with Limits",
    subtitle: "A fictional course sample about pairing machine learning with safe rules.",
    image: "07_robotics_and_ai.png",
    accent: "#5866A4",
    overview: "Artificial intelligence can help a robot recognize patterns in images, sounds, or sensor readings. It does not replace every other part of robotics. A robot still needs physical limits, clear task boundaries, and a way to pause when a prediction is uncertain.",
    story: "A fictional lab robot named Miro learns to distinguish a reusable cup from a paper cup. A model suggests a category based on a camera image. Before the robot moves, simple rules check whether the object is inside the permitted pickup area and whether the gripper has a safe route.",
    detail: "This combination is practical: AI can make a perception step more flexible, while deterministic rules guard the action. Learners should test both parts. A high recognition score is not enough if the robot still tries to move when the workspace is blocked.",
    tableTitle: "Fictional division of work between AI and rules",
    table: [["Question", "AI pattern model", "Safety rule"], ["What is this object?", "Suggests a label", "Does not move yet"], ["Can I pick it up?", "Provides confidence", "Checks permitted zone"], ["What if uncertain?", "Reports low confidence", "Pauses for a person"]],
    chartTitle: "Fictional recognition confidence after examples (%)",
    chart: [40, 55, 68, 80, 86],
    labels: ["10", "20", "30", "40", "50"],
    terms: [["Model", "A learned pattern-making system."], ["Confidence", "A score showing how certain a prediction is."], ["Guardrail", "A rule that restricts an action to a safe boundary."]]
  },
  {
    slug: "08_robot_arms",
    title: "Robot Arms: Reach, Grip, and Place",
    subtitle: "A fictional course sample about deliberate manipulation tasks.",
    image: "08_robot_arms.png",
    accent: "#2B8D94",
    overview: "A robot arm is a chain of joints and links that positions a tool in space. The tool might be a gripper, a suction cup, or a camera. A useful arm task is often described in simple stages: find an item, approach it, grip it, move carefully, and release it.",
    story: "A fictional learning arm named Sol sorts wooden tokens by colour. It starts above the tray, lowers at a gentle speed, closes its gripper, and checks whether it has lifted an object. The small check is important: it avoids carrying an empty gripper across the table as if the pickup succeeded.",
    detail: "Reach and grip are linked decisions. An arm can reach an object but still fail if the angle is awkward or the gripper is unsuitable. Early prototypes should use large, forgiving objects because they make errors easier to observe and correct.",
    tableTitle: "Fictional pick-and-place checkpoints",
    table: [["Checkpoint", "Question", "Evidence"], ["Approach", "Is the tool aligned?", "Camera or joint position"], ["Grip", "Did the item make contact?", "Gripper position"], ["Place", "Is the target clear?", "Map of the tray"]],
    chartTitle: "Fictional successful picks per practice round (%)",
    chart: [38, 52, 66, 75, 90],
    labels: ["Round 1", "2", "3", "4", "5"],
    terms: [["End effector", "The tool at the end of a robot arm."], ["Gripper", "A tool used to hold an object."], ["Workspace", "The area the arm can safely reach."]]
  },
  {
    slug: "09_safety_and_ethics",
    title: "Safety and Ethics: Building Trustworthy Robot Experiences",
    subtitle: "A fictional course sample about practical safeguards and thoughtful choices.",
    image: "09_safety_and_ethics.png",
    accent: "#B56856",
    overview: "A robot project is successful only when people can use it safely and understand what it is allowed to do. Safety concerns physical movement, but it also includes privacy, clear communication, and a way to report problems. Ethical questions make those design choices visible instead of treating them as an afterthought.",
    story: "In a fictional school workshop, a robot pauses at a marked boundary before approaching a shared table. A facilitator can stop the activity with one button. The team also explains which sensor data is stored and which is discarded. These small choices show respect for the people around the machine.",
    detail: "Good questions are concrete. Who can activate the robot? What happens if a sensor disagrees? Can someone opt out of being recorded? How will the team notice an unfair or confusing result? The answers should be tested in the same calm way as the robot's motion.",
    tableTitle: "Fictional trust checklist",
    table: [["Area", "Question", "Example safeguard"], ["Physical safety", "Can motion stop quickly?", "Accessible stop control"], ["Privacy", "Is data necessary?", "Collect only task data"], ["Transparency", "Can people understand it?", "Visible status and plain language"]],
    chartTitle: "Fictional checklist completion before a demo (%)",
    chart: [45, 60, 71, 83, 95],
    labels: ["Plan", "Build", "Test", "Review", "Demo"],
    terms: [["Risk assessment", "A structured look at possible harms and controls."], ["Transparency", "Making a system's purpose and limits understandable."], ["Consent", "A person's informed agreement to take part."]]
  },
  {
    slug: "10_future_robotics",
    title: "Future Robotics: Useful, Gentle, and Connected to Real Needs",
    subtitle: "A fictional course sample about imagining responsible next steps.",
    image: "10_future_robotics.png",
    accent: "#775FA6",
    overview: "The future of robotics is not one giant leap. It is a collection of small, useful improvements in sensing, energy use, accessibility, and human collaboration. The most interesting question is not whether a robot looks futuristic. It is whether it helps with a real task while fitting gracefully into a real place.",
    story: "Imagine a rooftop garden where a rover checks soil moisture, a drone takes a distant overview, and a small arm assists with light maintenance. The machines share simple updates, but a gardener decides the goal for the day. This fictional scene keeps the person in charge of the purpose and lets each robot contribute a narrow skill.",
    detail: "Future-ready systems should be repairable, explainable, and mindful of resources. A robot that needs less power, exposes clear controls, and can be maintained locally may be more valuable than one that simply adds more features.",
    tableTitle: "Fictional future-robot design priorities",
    table: [["Priority", "Why it matters", "Simple example"], ["Accessibility", "More people can use it", "Clear controls and feedback"], ["Repairability", "Longer useful life", "Replaceable module"], ["Efficiency", "Lower resource use", "Smart charging plan"]],
    chartTitle: "Fictional learner priority score (%)",
    chart: [54, 66, 73, 82, 93],
    labels: ["Access", "Repair", "Energy", "Safety", "Usefulness"],
    terms: [["Human oversight", "People remain responsible for the purpose and limits."], ["Sustainability", "Considering long-term environmental and social impact."], ["Interoperability", "Systems sharing information through clear interfaces."]]
  }
];

// Convert a CSS hex colour to RGB values accepted by PDFKit.
function hexToRgb(hex) {
  const normalized = hex.replace("#", "");
  return [0, 2, 4].map((index) => Number.parseInt(normalized.slice(index, index + 2), 16));
}

// Draw a consistent coloured banner at the top of every course-sample page.
function writeHeader(doc, article, pageNumber) {
  const [r, g, b] = hexToRgb(article.accent);
  doc.save();
  doc.fillColor(r, g, b).rect(0, 0, 612, 26).fill();
  doc.fillColor("#FFFFFF").font("Helvetica-Bold").fontSize(8)
    .text("ROBOTICS COURSE SAMPLE", 42, 9, { width: 300, characterSpacing: 0.7 });
  doc.fillColor("#FFFFFF").font("Helvetica").fontSize(8)
    .text(`PAGE ${pageNumber} OF 3`, 445, 9, { width: 125, align: "right" });
  doc.restore();
}

// Add the fictional-data notice to the bottom of every page.
function writeFooter(doc) {
  doc.save();
  doc.strokeColor("#D7D1C9").lineWidth(0.5).moveTo(42, 750).lineTo(570, 750).stroke();
  doc.fillColor("#6B6863").font("Helvetica").fontSize(7.5)
    .text("Fictional course sample — illustrative content and invented learning data.", 42, 758, { width: 528, align: "center" });
  doc.restore();
}

// Render a section heading with a short accent rule underneath.
function sectionTitle(doc, title, y, accent) {
  const [r, g, b] = hexToRgb(accent);
  doc.fillColor(r, g, b).font("Helvetica-Bold").fontSize(13).text(title, 42, y);
  doc.strokeColor(r, g, b).lineWidth(1.25).moveTo(42, y + 19).lineTo(178, y + 19).stroke();
}

// Place a bounded paragraph without changing the fixed three-page template.
function paragraph(doc, text, x, y, width, height = 120) {
  doc.fillColor("#303039").font("Helvetica").fontSize(10.3).lineGap(3.5)
    .text(text, x, y, { width, height, align: "left" });
}

// Draw the article-specific comparison table as selectable PDF text.
function drawTable(doc, article, x, y, width) {
  const rows = article.table;
  const columnWidths = [width * 0.27, width * 0.31, width * 0.42];
  const headerHeight = 28;
  const rowHeight = 45;
  const [r, g, b] = hexToRgb(article.accent);
  doc.fillColor("#303039").font("Helvetica-Bold").fontSize(10.8).text(article.tableTitle, x, y - 23);
  let currentY = y;
  rows.forEach((row, rowIndex) => {
    const height = rowIndex === 0 ? headerHeight : rowHeight;
    let currentX = x;
    row.forEach((cell, columnIndex) => {
      const cellWidth = columnWidths[columnIndex];
      if (rowIndex === 0) {
        doc.fillColor(r, g, b).rect(currentX, currentY, cellWidth, height).fill();
        doc.fillColor("#FFFFFF").font("Helvetica-Bold").fontSize(8.2)
          .text(cell, currentX + 6, currentY + 8, { width: cellWidth - 12, height: height - 10 });
      } else {
        doc.fillColor(rowIndex % 2 === 0 ? "#F5F1EB" : "#FBF9F5").rect(currentX, currentY, cellWidth, height).fill();
        doc.strokeColor("#DED8D0").lineWidth(0.5).rect(currentX, currentY, cellWidth, height).stroke();
        doc.fillColor("#34313A").font(columnIndex === 0 ? "Helvetica-Bold" : "Helvetica").fontSize(8.2)
          .text(cell, currentX + 6, currentY + 7, { width: cellWidth - 12, height: height - 9, lineGap: 1.5 });
      }
      currentX += cellWidth;
    });
    currentY += height;
  });
}

// Draw a simple vector line chart from intentionally fictional learning data.
function drawChart(doc, article, x, y, width, height) {
  const [r, g, b] = hexToRgb(article.accent);
  const maxValue = 100;
  const bottom = y + height;
  doc.fillColor("#303039").font("Helvetica-Bold").fontSize(10.8).text(article.chartTitle, x, y - 23);
  doc.strokeColor("#BFB8AF").lineWidth(0.7).moveTo(x, y).lineTo(x, bottom).lineTo(x + width, bottom).stroke();
  [25, 50, 75, 100].forEach((value) => {
    const gridY = bottom - (value / maxValue) * height;
    doc.strokeColor("#E4DED7").lineWidth(0.5).moveTo(x, gridY).lineTo(x + width, gridY).stroke();
    doc.fillColor("#6B6863").font("Helvetica").fontSize(7).text(String(value), x - 26, gridY - 3, { width: 20, align: "right" });
  });
  const step = width / (article.chart.length - 1);
  const points = article.chart.map((value, index) => [x + index * step, bottom - (value / maxValue) * height]);
  doc.strokeColor(r, g, b).lineWidth(2.4).moveTo(points[0][0], points[0][1]);
  points.slice(1).forEach(([pointX, pointY]) => doc.lineTo(pointX, pointY));
  doc.stroke();
  points.forEach(([pointX, pointY], index) => {
    doc.fillColor("#FFFFFF").circle(pointX, pointY, 4.2).fill();
    doc.strokeColor(r, g, b).lineWidth(2).circle(pointX, pointY, 4.2).stroke();
    doc.fillColor("#3A3640").font("Helvetica-Bold").fontSize(7.2).text(String(article.chart[index]), pointX - 11, pointY - 17, { width: 22, align: "center" });
    doc.fillColor("#6B6863").font("Helvetica").fontSize(7).text(article.labels[index], pointX - 21, bottom + 8, { width: 42, align: "center" });
  });
}

// Render the final-page glossary with three parser-friendly text blocks.
function drawTerms(doc, article, x, y, width) {
  const [r, g, b] = hexToRgb(article.accent);
  doc.fillColor("#303039").font("Helvetica-Bold").fontSize(10.8).text("Key terms for discussion", x, y - 23);
  let currentY = y;
  article.terms.forEach(([term, definition]) => {
    doc.fillColor("#F6F2ED").roundedRect(x, currentY, width, 42, 5).fill();
    doc.fillColor(r, g, b).font("Helvetica-Bold").fontSize(8.5).text(term, x + 9, currentY + 8, { width: 110 });
    doc.fillColor("#3C3941").font("Helvetica").fontSize(8.2).lineGap(1.5)
      .text(definition, x + 122, currentY + 7, { width: width - 132, height: 29 });
    currentY += 49;
  });
}

// Generate the fixed three-page PDF layout for one fictional robotics article.
function renderArticle(article) {
  const outputPath = path.join(documentsDirectory, `${article.slug}.pdf`);
  const imagePath = path.join(illustrationsDirectory, article.image);
  if (!fs.existsSync(imagePath)) {
    throw new Error(`Missing illustration: ${imagePath}`);
  }
  // Use explicit positions throughout the template, so a narrow default margin cannot create implicit extra pages.
  const doc = new PDFDocument({ size: "LETTER", margin: 0, info: { Title: article.title, Author: "Databricks course sample", Subject: "Fictional robotics document for parsing practice" } });
  const outputStream = fs.createWriteStream(outputPath);
  doc.pipe(outputStream);

  writeHeader(doc, article, 1);
  doc.fillColor("#27242C").font("Helvetica-Bold").fontSize(24).lineGap(4).text(article.title, 42, 54, { width: 515 });
  doc.fillColor("#6B6863").font("Helvetica-Oblique").fontSize(10.2).lineGap(3).text(article.subtitle, 42, 117, { width: 490 });
  doc.image(imagePath, 42, 157, { fit: [528, 270], align: "center", valign: "center" });
  doc.fillColor("#6B6863").font("Helvetica-Oblique").fontSize(8).text("Figure 1. Original watercolor-style illustration created for this fictional course sample.", 42, 435, { width: 528, align: "center" });
  sectionTitle(doc, "Why this topic matters", 476, article.accent);
  paragraph(doc, article.overview, 42, 507, 528, 99);
  sectionTitle(doc, "A short fictional scene", 621, article.accent);
  paragraph(doc, article.story, 42, 652, 528, 78);
  writeFooter(doc);

  doc.addPage();
  writeHeader(doc, article, 2);
  sectionTitle(doc, "How the idea works", 55, article.accent);
  paragraph(doc, article.detail, 42, 86, 528, 105);
  sectionTitle(doc, "A practical way to observe it", 222, article.accent);
  paragraph(doc, `${article.story} In a classroom demonstration, learners can pause after each step and describe what information the robot needs before it continues. This turns a smooth-looking robot action into a sequence of visible decisions.`, 42, 253, 528, 118);
  drawTable(doc, article, 42, 425, 528);
  sectionTitle(doc, "Questions for a parsing exercise", 606, article.accent);
  paragraph(doc, "Can a document parser recognize the section headers, the rows and columns of the table, the page footer, and the figure caption? Compare the extracted structure with the visual layout before deciding whether an element was parsed correctly.", 42, 637, 528, 72);
  writeFooter(doc);

  doc.addPage();
  writeHeader(doc, article, 3);
  sectionTitle(doc, "Invented learning data", 55, article.accent);
  paragraph(doc, "The chart below uses deliberately fictional values. Its purpose is to give a document parser a distinct visual data element, not to represent a real benchmark or product claim.", 42, 86, 528, 56);
  drawChart(doc, article, 63, 184, 465, 255);
  doc.fillColor("#6B6863").font("Helvetica-Oblique").fontSize(8).text("Figure 2. Fictional data for visual parsing practice; values are not measured results.", 42, 462, { width: 528, align: "center" });
  drawTerms(doc, article, 42, 531, 528);
  writeFooter(doc);
  doc.end();
  return new Promise((resolve, reject) => {
    outputStream.on("finish", resolve);
    outputStream.on("error", reject);
    doc.on("error", reject);
  });
}

// Verify the exact page count after the PDF output stream has finished writing.
async function validatePageCount(pdfPath) {
  const bytes = fs.readFileSync(pdfPath);
  const pdf = await PdfLibDocument.load(bytes);
  if (pdf.getPageCount() !== 3) {
    throw new Error(`${path.basename(pdfPath)} has ${pdf.getPageCount()} pages; expected 3.`);
  }
}

// Generate every article and fail the process if any PDF is not exactly three pages.
async function main() {
  fs.mkdirSync(documentsDirectory, { recursive: true });
  for (const article of articles) {
    await renderArticle(article);
  }
  for (const article of articles) {
    await validatePageCount(path.join(documentsDirectory, `${article.slug}.pdf`));
  }
  console.log(`Created and validated ${articles.length} three-page PDFs in ${documentsDirectory}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
