import os
import re
import asyncio
from telethon import TelegramClient, events

# 🔴 ផ្លាស់ប្តូរព័ត៌មានពិតប្រាកដរបស់អ្នកនៅទីនេះ (គូកូដដែលធ្លាប់ដើរក្នុង main.py)
API_ID = 1234567                           # ដាក់ API ID ពិតរបស់អ្នក (ជាលេខ)
API_HASH = '1cc2b5a851cad8cbe06f9e7cb8f019cc'   # ដាក់ API HASH ពិតរបស់អ្នក

TMP_DIR = 'tmp_audio'
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

# 🟢 ប្រើប្រាស់ Client តែមួយគត់ ដើម្បីកុំឱ្យជាន់ប្រព័ន្ធគ្នា
bot = TelegramClient('my_telegram_session', API_ID, API_HASH)

print("[~] កំពុងចាប់ផ្តើមប្រព័ន្ធទាញយកស្វ័យប្រវត្តិតាម Group... សូមរង់ចាំ...")

TARGET_GROUP_TITLE = "My Audio Downloader Group"

# ចាប់យកលីងដែលផ្ញើនៅក្នុង Group "My Audio Downloader Group"
@bot.on(events.NewMessage())
async def download_handler(event):
    # ពិនិត្យមើលថាជា Group "My Audio Downloader Group" ឬទេ
    chat = await event.get_chat()
    chat_title = getattr(chat, 'title', '')
    if chat_title.strip() != TARGET_GROUP_TITLE:
        return

    link = event.text.strip() if event.text else ''
    
    # បើគ្មានលីង Telegram ទេ មិនបាច់ធ្វើការឡើយ
    if 't.me/' not in link:
        return

    status_message = await event.reply("[~] កំពុងពិនិត្យមើលលីង និងស្វែងរកសារ... ⏳")

    try:
        # បំបែកលីងស្វែងរក Group ID និង Message ID
        if 't.me/c/' in link:
            match = re.search(r't\.me/c/(\d+)/(\d+)', link)
            if not match:
                await status_message.edit("[X] ទម្រង់លីង Private មិនត្រឹមត្រូវ!")
                return
            group_id = int(f"-100{match.group(1)}")
            message_id = int(match.group(2))
        else:
            match = re.search(r't\.me/([^/]+)/(\d+)', link)
            if not match:
                await status_message.edit("[X] ទម្រង់លីង Public មិនត្រឹមត្រូវ!")
                return
            group_id = match.group(1)
            if '?' in group_id:
                group_id = group_id.split('?')[0]
            message_id = int(match.group(2))

        # ទាញយកសារពីលីង
        message = await bot.get_messages(group_id, ids=message_id)

        if not message:
            await status_message.edit("[X] រកមិនឃើញសារនេះទេ! សូមប្រាកដថាគណនីរបស់អ្នកនៅក្នុង Group នោះ។")
            return

        # ពិនិត្យមើលឯកសារ Audio/Voice
        if message.audio or message.voice:
            await status_message.edit("[~] រកឃើញឯកសារហើយ! កំពុងទាញយកចូលម៉ាស៊ីន... 📥")
            
            file_name = message.file.name if message.file.name else f"audio_{message.id}.mp3"
            path = os.path.join(TMP_DIR, file_name)

            # ទាញយក
            await bot.download_media(message, path)
            
            await status_message.edit("[~] កំពុងផ្ញើត្រឡប់ទៅកាន់លោកអ្នកវិញ... 📤")
            
            # ផ្ញើ File Audio នោះចូលទៅក្នុង Chat/Group ដែលអ្នកបានបោះលីងអម្បាញ់មិញ
            await bot.send_file(event.chat_id, path, caption=f"🎯 ទាញយកជោគជ័យ៖ `{file_name}`")
            
            # លុប File បណ្តោះអាសន្ន និងសារ Status
            if os.path.exists(path):
                os.remove(path)
            await status_message.delete()

            # លុបសារដើមរបស់អ្នកប្រើប្រាស់ (Past Link) ដើម្បីកុំឱ្យបង្ហាញ Link ទៅកាន់ Source Group ដើម
            try:
                await event.delete()
            except Exception:
                pass
        else:
            await status_message.edit("[X] សារតាមលីងនេះ មិនមែនជា File Audio ឬ Voice ឡើយ!")

    except Exception as e:
        await status_message.edit(f"[X] មានកំហុស៖ {str(e)}")

async def handle_http(reader, writer):
    try:
        # Read the incoming request and send a basic HTTP 200 OK response
        await reader.read(1024)
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 2\r\n\r\nOK"
        writer.write(response.encode('utf-8'))
        await writer.drain()
    except Exception:
        pass
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass

async def main():
    # ចាប់ផ្តើម HTTP Server សម្រាប់គាំទ្រការ Deploy នៅលើ Render (Free)
    port = int(os.environ.get("PORT", 10000))
    try:
        server = await asyncio.start_server(handle_http, '0.0.0.0', port)
        print(f"[✓] HTTP Server កំពុងរត់លើ Port {port} (សម្រាប់ Render/Cloud)")
    except Exception as e:
        print(f"[!] មិនអាចបើក HTTP Server បានទេ៖ {e}")
        server = None

    await bot.start()
    print("[✓] ប្រព័ន្ធដំណើរការជោគជ័យហើយ! លោកអ្នកអាចបង្កើត Group រួចបោះលីងចូលដើម្បីដោនឡូដបានភ្លាមៗ។")
    
    if server:
        async with server:
            await bot.run_until_disconnected()
    else:
        await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())