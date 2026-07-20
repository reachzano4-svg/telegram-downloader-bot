import sys
import asyncio
from telethon import TelegramClient

# Force UTF-8 stdout/stderr for Windows console Khmer support
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 🔴 ត្រូវប្រាកដថា API_ID និង API_HASH នេះត្រូវគ្នានឹងកូដក្នុង main.py
API_ID = 35511201          # ដាក់ api_id របស់អ្នក (ជាលេខ)
API_HASH = '1cc2b5a851cad8cbe06f9e7cb8f019cc'  # ដាក់ api_hash របស់អ្នក (ជាអក្សរ)

async def main():
    client = TelegramClient('my_telegram_session', API_ID, API_HASH)
    print("កំពុងភ្ជាប់ទៅកាន់ Telegram...")
    
    # បញ្ជាឱ្យចាប់ផ្តើម Log in (វានឹងសួរលេខទូរស័ព្ទ និងលេខកូដក្នុង Terminal នេះ)
    await client.start()
    
    print("\n[✓] Log in ជោគជ័យហើយ!")
    print("[✓] File 'my_telegram_session.session' ត្រូវបានបង្កើតរួចរាល់។")
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())