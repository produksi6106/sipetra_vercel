from django.db import models

class PekerjaanMitra(models.Model):
    bulan_kegiatan = models.CharField(max_length=20)
    nama_mitra = models.CharField(max_length=100)
    tim_kerja = models.CharField(max_length=100)
    kegiatan = models.CharField(max_length=200)
    volume = models.FloatField()
    satuan = models.CharField(max_length=50)
    honor_per_satuan = models.IntegerField()
    nilai_pekerjaan = models.IntegerField()
    mulai_kegiatan = models.DateField()
    selesai_kegiatan = models.DateField()
    beban_anggaran = models.CharField(max_length=100)

# pekerjaan/models.py
class Mitra(models.Model):
    nama = models.CharField(max_length=100)
    alamat = models.TextField()
    no_hp = models.CharField(max_length=20)
    sobat_id = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return self.nama

class TimKegiatan(models.Model):
    nama_tim = models.CharField(max_length=100)
    nama_kegiatan = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nama_kegiatan} ({self.nama_tim})"

class BebanHonor(models.Model):
    tim = models.CharField(max_length=100)
    beban = models.CharField(max_length=100)
    rincian = models.TextField()
    honor = models.IntegerField()
    satuan = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.tim} - {self.rincian}"

