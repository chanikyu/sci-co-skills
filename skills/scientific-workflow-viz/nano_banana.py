#!/usr/bin/env python3
"""
nano_banana.py — render a scientific-workflow-viz prompt to an IMAGE with Google's
"Nano Banana" (Gemini image API). No third-party dependencies (stdlib only).

The API key is a secret: pass it via the GEMINI_API_KEY (or GOOGLE_API_KEY) environment
variable, or --api-key. NEVER hardcode it in a file or commit it.

Setup:
  1. Get a key at https://aistudio.google.com/apikey
  2. export GEMINI_API_KEY="your-key"        # in the session; not saved to disk

Usage:
  python nano_banana.py --prompt-file prompt.txt --out figure.png
  python nano_banana.py --prompt "A high-quality BioRender-style ..." --out figure.png --aspect 16:9

Models (Nano Banana family): gemini-2.5-flash-image (default) or a newer image model
via --model.
"""
import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error

DEFAULT_MODEL = "gemini-2.5-flash-image"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def generate(prompt, out, model=DEFAULT_MODEL, api_key=None, aspect=None, timeout=180):
    """Call the Gemini image API and write the returned image to `out`."""
    api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        sys.exit("No API key. Get one at https://aistudio.google.com/apikey and run "
                 "`export GEMINI_API_KEY=...` (or pass --api-key). Never commit the key.")

    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}}
    if aspect:
        body["generationConfig"]["imageConfig"] = {"aspectRatio": aspect}

    req = urllib.request.Request(
        ENDPOINT.format(model=model),
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            resp = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Gemini API error {e.code}: {e.read().decode(errors='replace')[:600]}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error contacting Gemini API: {e}")

    parts = (resp.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
    img_b64, texts = None, []
    for p in parts:
        inline = p.get("inlineData") or p.get("inline_data")
        if inline and inline.get("data"):
            img_b64 = inline["data"]
        elif p.get("text"):
            texts.append(p["text"])
    if not img_b64:
        note = " ".join(texts)[:600] or json.dumps(resp)[:600]
        sys.exit(f"No image was returned. Model response: {note}")

    with open(out, "wb") as f:
        f.write(base64.b64decode(img_b64))
    print(f"saved {out}  (model: {model})")
    return out


def main():
    ap = argparse.ArgumentParser(description="Render a figure prompt via Google Nano Banana (Gemini image API).")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt", help="the prompt text")
    src.add_argument("--prompt-file", help="path to a file containing the prompt")
    ap.add_argument("--out", default="figure.png", help="output image path (default figure.png)")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"image model (default {DEFAULT_MODEL})")
    ap.add_argument("--api-key", default=None, help="API key (else GEMINI_API_KEY / GOOGLE_API_KEY)")
    ap.add_argument("--aspect", default=None, help="aspect ratio, e.g. 16:9, 1:1, 4:3")
    a = ap.parse_args()
    prompt = a.prompt if a.prompt else open(a.prompt_file, encoding="utf-8").read()
    generate(prompt, a.out, model=a.model, api_key=a.api_key, aspect=a.aspect)


if __name__ == "__main__":
    main()
