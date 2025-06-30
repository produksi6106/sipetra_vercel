import pandas as pd
import os
import django

# Set environment project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mitraproject.settings')
django.setup()

from pekerjaan.models import PekerjaanMitra  # Ganti sesuai app kamu

file_path = 'Form.xlsx'  # Ganti dengan path file Excel kamu

try:
    df = pd.read_excel(file_path)

    for index, row in df.iterrows():
        try:
            PekerjaanMitra.objects.create(
                bulan_kegiatan     = row['bulan_kegiatan'],
                nama_mitra         = row['nama_mitra'],
                tim_kerja          = row['tim_kerja'],
                kegiatan           = row['kegiatan'],
                volume             = row['volume'],
                satuan             = row['satuan'],
                honor_per_satuan   = row['honor_per_satuan'],
                nilai_pekerjaan    = row['nilai_pekerjaan'],
                mulai_kegiatan     = pd.to_datetime(row['mulai_kegiatan']).date(),
                selesai_kegiatan   = pd.to_datetime(row['selesai_kegiatan']).date(),
                beban_anggaran     = row['beban_anggaran']
            )
            print(f"✅ Baris {index+2} berhasil disimpan.")
        
        except KeyError as e:
            print(f"🚫 Kolom tidak ditemukan di baris {index+2}: {e}")
        except Exception as e:
            print(f"🚫 Gagal menyimpan baris {index+2}: {e}")

except Exception as e:
    print(f"🚫 Gagal membuka file: {e}")
