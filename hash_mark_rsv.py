import argparse
import hashlib
from sha256_impl import sha256_hex
from text_extractor import fetch_html, extract_visible_text, clean_scripture_text

def compute_hashes(raw_bytes: bytes):
    our_hex = sha256_hex(raw_bytes)
    lib_hex = hashlib.sha256(raw_bytes).hexdigest()
    return our_hex, lib_hex

def save_text_and_digest(text: str, digest_hex: str, text_filename: str, digest_filename: str):
    with open(text_filename, "wb") as f:
        f.write(text.encode("utf-8"))
    with open(digest_filename, "w", encoding="utf-8") as f:
        f.write(digest_hex + "\n")

def main():
    parser = argparse.ArgumentParser(description="Fetch Book of Mark (RSV) and compute SHA-256 (raw & clean).")
    parser.add_argument("--no-clean", action="store_true", help="Do not produce CLEAN version (only RAW).")
    parser.add_argument("--out-prefix", default="mark_rsv", help="Prefix for output files (default: mark_rsv)")
    args = parser.parse_args()

    print("Fetching HTML page...")
    html = fetch_html()

    print("Extracting RAW visible text...")
    raw_text = extract_visible_text(html)
    raw_bytes = raw_text.encode("utf-8")

    print("Computing hash for RAW text...")
    our_raw, lib_raw = compute_hashes(raw_bytes)
    print("RAW SHA-256 (our impl):", our_raw)
    print("RAW SHA-256 (hashlib)  :", lib_raw)
    print("Match? ", "YES" if our_raw == lib_raw else "NO")
    save_text_and_digest(raw_text, our_raw, f"{args.out_prefix}_raw.txt", f"{args.out_prefix}_raw_sha256.txt")
    print(f"Wrote {args.out_prefix}_raw.txt and {args.out_prefix}_raw_sha256.txt")

    if not args.no_clean:
        print("\nProducing CLEAN scripture text (heuristic)...")
        clean_text = clean_scripture_text(raw_text)
        clean_bytes = clean_text.encode("utf-8")
        print("Computing hash for CLEAN text...")
        our_clean, lib_clean = compute_hashes(clean_bytes)
        print("CLEAN SHA-256 (our impl):", our_clean)
        print("CLEAN SHA-256 (hashlib)  :", lib_clean)
        print("Match? ", "YES" if our_clean == lib_clean else "NO")
        save_text_and_digest(clean_text, our_clean, f"{args.out_prefix}_clean.txt", f"{args.out_prefix}_clean_sha256.txt")
        print(f"Wrote {args.out_prefix}_clean.txt and {args.out_prefix}_clean_sha256.txt")

if __name__ == "__main__":
    main()
