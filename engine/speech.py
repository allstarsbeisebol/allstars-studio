#!/usr/bin/env python3
"""Síntese local grátis usando OHF Piper. É necessário baixar uma voz licenciada para o uso pretendido."""
import argparse, json, subprocess
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--episode", default="data/episode.json")
p.add_argument("--model", default="pt_BR-faber-medium")
p.add_argument("--data-dir", default="voice")
p.add_argument("--output", default="output/narracao.wav")
p.add_argument("--pace", type=float, default=1.14, help="Ritmo da fala: 1.0 normal; valores maiores falam mais devagar.")
args = p.parse_args()
if not 0.9 <= args.pace <= 1.45:
    raise SystemExit("Ritmo inválido: escolha entre 0.90 e 1.45.")
episode = json.loads(Path(args.episode).read_text(encoding="utf-8"))
out = Path(args.output)
out.parent.mkdir(parents=True, exist_ok=True)
text = episode["narration"].strip()
if not text:
    raise SystemExit("Narração vazia.")
subprocess.run(["python", "-m", "piper", "--data-dir", args.data_dir, "-m", args.model,
                "--length-scale", str(args.pace), "--sentence-silence", "0.22",
                "-f", str(out), "--", text], check=True)
print("Áudio salvo:", out, "| ritmo:", args.pace, "| pausas entre frases: 0.22s")
