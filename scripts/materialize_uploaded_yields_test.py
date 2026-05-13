from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / 'data' / 'raw' / 'yields'

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print('placeholder')

if __name__ == '__main__':
    main()
