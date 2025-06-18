# Script Upload Video ke VK.com via Terminal Linux

Repositori ini berisi script Python yang memungkinkan Anda untuk mengunggah video ke situs jejaring sosial VK.com langsung dari terminal Linux. Script ini menggunakan API resmi VK dan dirancang untuk otomatisasi dan kemudahan penggunaan.

## Fitur

-   Mengunggah file video dari path lokal.
-   Menambahkan judul dan deskripsi kustom untuk video.
-   Opsi untuk langsung memposting video yang diunggah ke *wall* (dinding) profil Anda.
-   Menggunakan *environment variable* untuk menyimpan *access token* secara aman.
-   Memberikan output berupa URL langsung ke video yang telah diunggah.

## Persiapan (Wajib)

Sebelum menggunakan script, ada beberapa hal yang perlu Anda siapkan terlebih dahulu.

### 1. Kebutuhan Sistem
Pastikan sistem Linux Anda telah terpasang:
-   Python 3
-   PIP (Package Installer for Python)

Anda bisa mengeceknya dengan perintah:
```bash
python3 --version
pip3 --version
```

### 2. Dapatkan Access Token VK
*Access token* adalah kunci otorisasi yang memberikan izin kepada script untuk mengakses akun VK Anda.

1.  Login ke akun VK Anda di browser.
2.  Kunjungi halaman manajemen aplikasi: [https://vk.com/apps?act=manage](https://vk.com/apps?act=manage).
3.  Klik **"Create an app"**.
4.  Pilih platform **"Standalone app"**, beri nama aplikasi (misalnya "My Video Uploader"), dan selesaikan proses verifikasi.
5.  Setelah aplikasi dibuat, buka tab **"Settings"** dan salin **`App ID`** Anda.
6.  Untuk mendapatkan *user access token* yang diperlukan, buat URL otorisasi dengan mengganti `MASUKKAN_APP_ID_ANDA` dengan App ID yang baru saja Anda salin.

    ```
    [https://oauth.vk.com/authorize?client_id=MASUKKAN_APP_ID_ANDA&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=video,wall&response_type=token&v=5.199](https://oauth.vk.com/authorize?client_id=MASUKKAN_APP_ID_ANDA&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=video,wall&response_type=token&v=5.199)
    ```

7.  Buka URL yang sudah dimodifikasi tersebut di browser.
8.  Klik **"Allow"** untuk memberikan izin akses.
9.  Anda akan diarahkan ke halaman kosong (`blank.html`). Lihat address bar browser Anda. Salin string panjang yang ada di antara `access_token=` dan `&`. Itulah *access token* Anda.

    **Contoh URL:** `https://oauth.vk.com/blank.html#access_token=vk1.a.ABC...123&expires_in=0&user_id=123456789`

    **Simpan token ini di tempat yang aman dan jangan bagikan ke siapa pun!**

## Instalasi

Kloning repositori ini atau cukup salin script di bawah. Kemudian, instal pustaka Python yang dibutuhkan.

Buka terminal dan jalankan:
```bash
pip3 install vk-api
```

## Konfigurasi

Untuk alasan keamanan, script ini dirancang untuk membaca *access token* dari *environment variable*.

Buka terminal Anda dan atur variabel `VK_ACCESS_TOKEN`.
```bash
# Perintah ini hanya berlaku untuk sesi terminal saat ini
export VK_ACCESS_TOKEN='ganti_dengan_access_token_anda'
```

Untuk membuatnya permanen, tambahkan baris `export` di atas ke file konfigurasi shell Anda (misalnya `~/.bashrc` atau `~/.zshrc`) dan restart terminal Anda.

## Kode Script (`upload_vk.py`)

Simpan kode berikut ke dalam file bernama `upload_vk.py`.

```python
#!/usr/bin/env python3
import os
import argparse
import vk_api
from vk_api.upload import VkUpload
from vk_api.exceptions import ApiError, AuthError

def main():
    """
    Script utama untuk mengunggah video ke VK.com.
    """
    # --- Konfigurasi Argumen Terminal ---
    parser = argparse.ArgumentParser(
        description="Unggah video ke VK.com melalui terminal.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--file', type=str, required=True, help="Path lengkap ke file video. (Contoh: /home/user/video.mp4)")
    parser.add_argument('--title', type=str, default="Video Baru", help="Judul video.")
    parser.add_argument('--description', type=str, default="", help="Deskripsi video.")
    parser.add_argument('--wallpost', action='store_true', help="Sertakan flag ini untuk memposting video ke wall/dinding Anda.")
    
    args = parser.parse_args()

    # --- Validasi File ---
    if not os.path.exists(args.file):
        print(f"❌ Error: File tidak ditemukan di path '{args.file}'")
        return

    # --- Ambil Access Token dari Environment Variable (Lebih Aman) ---
    access_token = os.getenv('VK_ACCESS_TOKEN')
    if not access_token:
        print("❌ Error: Environment variable 'VK_ACCESS_TOKEN' tidak diatur.")
        print("Jalankan 'export VK_ACCESS_TOKEN=\"token_anda_disini\"' sebelum menjalankan script.")
        return

    print("🚀 Memulai proses upload...")

    try:
        # --- Inisialisasi API VK ---
        vk_session = vk_api.VkApi(token=access_token)
        vk = vk_session.get_api()
        upload = VkUpload(vk_session)

        # --- Proses Upload Video ---
        print(f"Mengunggah file: {args.file}...")
        video = upload.video(
            video_file=args.file,
            name=args.title,
            description=args.description
        )
        
        video_url = f"[https://vk.com/video](https://vk.com/video){video['owner_id']}_{video['video_id']}"
        print(f"✅ Video berhasil diunggah!")
        print(f"   URL: {video_url}")

        # --- Posting ke Wall jika diminta ---
        if args.wallpost:
            print("Memposting video ke wall...")
            attachment = f"video{video['owner_id']}_{video['video_id']}"
            vk.wall.post(
                message=f"{args.title}\n\n{args.description}",
                attachments=attachment
            )
            print("✅ Berhasil diposting ke wall!")

    except AuthError as error_msg:
        print(f"❌ Error Otentikasi: {error_msg}")
        print("   Pastikan access token Anda valid dan memiliki scope 'video' dan 'wall'.")
    except ApiError as error_msg:
        print(f"❌ Error API VK: {error_msg}")
    except Exception as e:
        print(f"Terjadi kesalahan yang tidak terduga: {e}")

if __name__ == '__main__':
    main()
```

## Cara Penggunaan

Pastikan Anda berada di direktori yang sama dengan file `upload_vk.py` atau panggil script dengan path lengkapnya.

**Contoh 1: Upload video dengan judul kustom**
```bash
python3 upload_vk.py --file "/home/user/videos/liburan.mp4" --title "Video Liburan di Bali"
```

**Contoh 2: Upload video, beri deskripsi, dan langsung post ke wall**
```bash
python3 upload_vk.py \
--file "./acara.mov" \
--title "Dokumentasi Acara Kantor 2025" \
--description "Momen seru dari acara tahunan kita." \
--wallpost
```

**Melihat Opsi Bantuan**
```bash
python3 upload_vk.py --help
```
