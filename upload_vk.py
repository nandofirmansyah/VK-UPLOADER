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
        
        video_url = f"https://vk.com/video{video['owner_id']}_{video['video_id']}"
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
