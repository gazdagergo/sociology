# Study Resources Guide: study_schedule_<semester>.md vs. Lernpfad.pdf

## Overview

This workspace contains two complementary resources for tracking course progress through **Kurs 25501 B1: Einführung in den Studiengang**:

1. **study_schedule_<semester>.md** - A markdown-formatted, human-editable study guide
2. **Lernpfad.pdf** (pvs.b1.verlauf.2023.24.pdf) - The official university course structure document

Both documents describe the same course structure but serve different purposes. This guide helps LLMs understand what information is in each.

---

## Document 1: study_schedule_<semester>.md

### What It Is
A markdown file created for easy note-taking, progress tracking, and integration with the Claude Code learning environment.

### Content Structure
- **Week-by-week breakdown** (Week 1/2, 3/4, 5/6, etc.)
- Each week includes:
  - **Theme**: Main focus of the week
  - **Learning Materials**: List of LE I/II/III/IV chapters and articles to cover
  - **Exercises**: Which Übung (exercise) to work on
  - **Tasks**: Checkboxes for tracking completion

### Format Benefits
- **Markdown format**: Easy to edit, version control, and integrate with note-taking
- **Checkboxes**: Can toggle items as you complete them (using `[ ]` for empty, `[x]` for done)
- **Hierarchical**: Clear structure with weeks, materials, exercises, and tasks
- **LLM-friendly**: Easy for Claude to parse, understand, and help update progress

### Example Content
```
## Week 1/2
**Theme**: Orientation + Introduction to Political Science...

### Learning Materials:
- **LE I Chapters 1-3**
- **Lecture 1**: Susanne Lütz - "Was ist Politikwissenschaft?"
- **Article 1**: Elisabeth Töller/Alix Weigel - "Circular Cities"

### Tasks:
- [ ] Read LE I Chapters 1-3
- [ ] Watch Lecture 1
- [ ] Read Article 1
```

### When to Use
- As your **main working document** for progress tracking
- When **updating Claude about your progress**
- When you want to **toggle items as you complete them**
- For **planning your study sessions** with Claude

### How LLMs Use It
- Claude can **read your progress** from checked/unchecked items
- Claude can **update items** as you report completion
- Claude can **create study summaries** based on content
- Claude can **generate review questions** based on what you've covered

---

## Document 2: Lernpfad.pdf (pvs.b1.verlauf.2023.24.pdf)

### What It Is
The official course structure document published by FernUniversität Hagen showing the semester's learning path.

### Content Structure
A detailed table with multiple columns across 2 pages:

**Columns:**
1. **SW (Semesterwoche)** - Semester week number (1, 2, 3... through ~15)
2. **Lerneinheiten I & IV (Studienbriefe)** - Learning unit chapters and topics
3. **Lerneinheit II (Vorlesungen)** - Lecture titles and instructors
4. **Lerneinheit III (Multimedia)** - Article/contribution titles and authors
5. **Übungen/Übungsblöcke** - Exercise blocks assigned to each week
6. **Ziele** - Specific learning goals and outcomes for each week

### Example Content
From the PDF table:
```
Week 1-2:
| Lerneinheit I & IV | Lerneinheit II | Lerneinheit III | Übungen | Ziele |
|---|---|---|---|---|
| Lerneinheit I: Studienbrief, Kapitel 1 S. 1-2 | LE I Lütz: Was ist Politikwissenschaft? | LE I Töller / Weigel: Circular Cities | A | Fachlich: Fragestellung erkennen, Disziplinarische Ansätze... |
```

### Detailed Information
- **More granular week-by-week breakdown** than study_schedule_<semester>.md
- **Specific learning goals (Ziele)** for each week's work
- **More detailed descriptions** of what each material covers
- **Official university source** - authoritative reference

### Format
- **PDF table format**: Official, formal document
- **Not editable** (in this context) - reference document
- **Comprehensive** - includes all materials and goals
- **Visual layout** - designed for printing/reviewing

### When to Use
- As your **authoritative reference** for what should be covered
- When you need **specific learning goals (Ziele)** for motivation
- To **verify you're covering the right materials** at the right time
- When Claude needs to understand the **official course structure**

### How LLMs Use It
- Claude can **extract learning goals** to create study questions
- Claude can **verify materials** match the official curriculum
- Claude can **summarize** what should be covered in each week
- Claude can **provide context** for why materials are in a particular order

---

## Key Differences

| Aspect | study_schedule_<semester>.md | Lernpfad.pdf |
|--------|------------------|--------------|
| **Format** | Markdown (editable) | PDF (reference) |
| **Purpose** | Progress tracking & study planning | Official course structure |
| **Editability** | Yes - update as you progress | No - reference document |
| **Checkboxes** | Yes - toggle completion | No - static content |
| **Learning Goals** | Basic theme descriptions | Detailed specific goals (Ziele) |
| **Detail Level** | Week-based summary | Week-based detailed breakdown |
| **Best For** | Working document | Reference & verification |
| **LLM Integration** | Easy to update in chat | Easy to reference & extract info |

---

## How These Documents Work Together

### Workflow

1. **Reference the PDF** to understand what materials should be covered in a week
2. **Update study_schedule_<semester>.md** as you work through the materials
3. **Check off tasks** in study_schedule_<semester>.md as you complete them
4. **Refer back to PDF** for specific learning goals and motivations
5. **Ask Claude to verify** your progress matches the PDF's expectations

### Example Interaction

**You**: "I finished Week 1/2 materials. What should I focus on next?"

**Claude reads:**
- Checks study_schedule_<semester>.md for what you completed
- Verifies against PDF that Week 1/2 is complete
- Looks at Ziele (goals) from PDF for Week 1/2
- Proposes Week 3/4 with specific goals from the PDF

---

## Content Mapping

### What's in BOTH Documents (same info, different format)
- Week numbers (1/2, 3/4, 5/6, 7, 8/9, 10/11, 12/13, 14/15)
- Learning Unit chapters (LE I, LE II, LE III, LE IV)
- Lectures (3 total - Lütz, Holtkamp, Hillebrandt)
- Articles (7 total - Töller/Weigel, Wiechmann/Garske, etc.)
- Exercises (8 total - Übung A through G, plus X)

### What's ONLY in the PDF
- **Detailed learning goals (Ziele)** for each week
- **More specific descriptions** of content within each material
- **Official university formatting** and structure
- **Rationale** for material sequencing

### What's ONLY in study_schedule_<semester>.md
- **Checkboxes** for tracking completion
- **Markdown formatting** for easy editing
- **Simplified layout** for working sessions
- **Notes section** for your observations
- **Integration** with learning-progress.md

---

## Using With Claude

### When Referencing the PDF
```
"According to the Lernpfad PDF, the learning goals for Week 1/2 (Ziele column) are..."
```

### When Updating Progress
```
"I've completed the following from study_schedule_<semester>.md Week 1/2:
- [x] Read LE I Chapters 1-3
- [x] Watch Lecture 1
- [ ] Read Article 1
```

### Best Practices for LLMs
1. **Always check the PDF** for authoritative learning goals
2. **Use study_schedule_<semester>.md** to track what you've actually done
3. **Compare the two** to ensure you're on track
4. **Extract Ziele (goals)** from PDF when planning reviews
5. **Update study_schedule_<semester>.md** as the working progress document

---

## File Locations

In this workspace:
