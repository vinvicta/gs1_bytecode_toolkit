# GS1 Bytecode Toolkit

**Disclaimer: Written as a consequence after reverse engineering cheats that were made for the game, this script was thrown together by Gemini 1.5 Pro. Always double check your information. Thanks!**

**A robust, bidirectional Compiler, Decompiler, and Disassembler for the GraalScript 1 (GS1) container format.**

This repository contains a standalone toolkit designed to analyze and modify scripts stored in the "Tokenized" format common to GS1 engines (often found in `.nw` levels or legacy weapon files). Unlike GS2 (which is a true compiled bytecode), GS1 is stored as a sequence of readable tokens separated by binary delimiters.

## ⚡ Features

* **Decompiler (`-D`):** Reconstructs readable source code from binary containers. It extracts string tokens and applies heuristic formatting (indentation, spacing) to restore code structure.
* **Disassembler (`-d`):** Generates a view of the raw token stream, showing the binary "gaps" (opcodes) and the string values.
* **Assembler (`-a`):** Compiles text source code into the binary container format, injecting the standard `16F0` delimiters used by the engine.
* **Smart Header Detection:** Automatically skips container headers (e.g., `weapon,-Playerlist...`) to locate the actual script start.

## 🚀 Usage Guide

### 1. Decompiling (Binary -> Source Code)

To reconstruct a script from a binary file:

```bash
python gs1_tool.py -D script.bin -o source.gs
