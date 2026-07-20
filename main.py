import sys
import os
import re
import asyncio
from PyQt6 import QtWidgets, uic
from telethon import TelegramClient
from qasync import QEventLoop, asyncSlot

# 🔴 ផ្លាស់ប្តូរព័ត៌មាន API របស់អ្នកនៅទីនេះ
API_ID = 35511201          # ដាក់ api_id របស់អ្នក (ជាលេខ)
API_HASH = '1cc2b5a851cad8cbe06f9e7cb8f019cc'  # ដាក់ api_hash របស់អ្នក

OUTPUT_DIR = 'downloaded_audio'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

class AppWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui_main.ui', self)
        
        # បង្កើត Telegram Client ទុកឱ្យហើយ (ប៉ុន្តែមិនទាន់ឱ្យវា Connect ទេ)
        self.client = TelegramClient('my_telegram_session', API_ID, API_HASH)
        
        # ភ្ជាប់ប៊ូតុងទៅនឹង Function ដំណើរការ
        self.download_btn.clicked.connect(self.start_download)
        
        # ហៅឱ្យបើក Connection ទៅកាន់ Telegram ភ្លាមៗពេលកម្មវិធីបើកឡើង
        asyncio.ensure_future(self.init_telegram())
        
    def log(self, text):
        self.log_output.append(text)
        self.log_output.ensureCursorVisible()

    async def init_telegram(self):
        self.download_btn.setEnabled(False)
        self.log("[~] កំពុងភ្ជាប់ទៅកាន់ប្រព័ន្ធ Telegram... សូមរង់ចាំ...")
        try:
            # ចាប់ផ្តើមទាក់ទងទៅ Telegram (ដោយសារមាន File session រួចហើយ វានឹងរត់ចូលស្វ័យប្រវត្តិ)
            await self.client.start()
            self.log("[✓] បានភ្ជាប់ទៅកាន់ Telegram រួចរាល់! កម្មវិធីរង់ចាំដោនឡូដ។\n")
            self.download_btn.setEnabled(True)
        except Exception as e:
            self.log(f"[X] មិនអាចភ្ជាប់ទៅ Telegram បានទេ៖ {str(e)}")

    @asyncSlot()
    async def start_download(self):
        link = self.link_input.text().strip()
        
        if not link:
            self.log("[X] សូមបញ្ចូល Link ជាមុនសិន!")
            return
            
        self.download_btn.setEnabled(False)
        
        try:
            if 't.me/c/' in link:
                match = re.search(r't\.me/c/(\d+)/(\d+)', link)
                if not match:
                    self.log("[X] ទម្រង់លីង Private មិនត្រឹមត្រូវ!")
                    self.download_btn.setEnabled(True)
                    return
                group_id = int(f"-100{match.group(1)}")
                message_id = int(match.group(2))
            else:
                match = re.search(r't\.me/([^/]+)/(\d+)', link)
                if not match:
                    self.log("[X] ទម្រង់លីងមិនត្រឹមត្រូវ! សូមពិនិត្យមើលលីងឡើងវិញ។")
                    self.download_btn.setEnabled(True)
                    return
                group_id = match.group(1)
                if '?' in group_id:
                    group_id = group_id.split('?')[0]
                message_id = int(match.group(2))
                
            self.log(f"[~] កំពុងស្វែងរកសារលេខ {message_id} ពីលីង...")
            
            message = await self.client.get_messages(group_id, ids=message_id)
            
            if not message:
                self.log("[X] រកមិនឃើញសារនេះទេ! សូមពិនិត្យមើលថាគណនីរបស់អ្នកបាន Join ក្នុង Group នោះហើយឬនៅ។")
                self.download_btn.setEnabled(True)
                return
                
            if message.audio or message.voice:
                file_name = message.file.name if message.file.name else f"audio_{message.id}.mp3"
                path = os.path.join(OUTPUT_DIR, file_name)
                
                file_size = round(message.file.size / (1024 * 1024), 2)
                self.log(f"[✓] ជោគជ័យ: រកឃើញឯកសារ '{file_name}' ({file_size} MB)")
                self.log("[~] កំពុងទាញយក... សូមរង់ចាំ...")
                
                await self.client.download_media(message, path)
                self.log(f"[✓] រួចរាល់! ឯកសាររក្សាទុកក្នុង Folder: {OUTPUT_DIR}")
            else:
                self.log("[X] សារតាម Link នេះមិនមែនជា File Audio ឬ Voice ឡើយ។")
                
        except Exception as e:
            self.log(f"[X] មានកំហុស: {str(e)}")
            
        self.download_btn.setEnabled(True)

def start_app():
    app = QtWidgets.QApplication(sys.argv)
    
    # បង្កើត និងកំណត់ Loop របស់ qasync ឱ្យច្បាស់លាស់
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # បើកផ្ទាំង UI ឡើងមកមុនគេ
    window = AppWindow()
    window.show()
    
    # រត់ផ្ទាំង UI ឱ្យដំណើរការរហូតដល់អ្នកប្រើចុចបិទ
    with loop:
        loop.run_forever()

if __name__ == '__main__':
    start_app()