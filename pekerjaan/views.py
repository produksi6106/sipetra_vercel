from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import PekerjaanMitra, Mitra, TimKegiatan, BebanHonor
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField, Sum, FloatField
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from collections import defaultdict
import json

# Daftar bulan dan satuan
bulan_list = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
              "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

satuan_list = sorted([
    "Dokumen", "Rumah Tangga", "Unit Usaha", "Blok Sensus", "SLS", "Peta"
])

def build_maps():
    tim_kegiatan_map = {}
    for tim, kegiatan in TimKegiatan.objects.values_list('nama_tim', 'nama_kegiatan'):
        tim_kegiatan_map.setdefault(tim, []).append(kegiatan)
    for tim in tim_kegiatan_map:
        tim_kegiatan_map[tim] = sorted(set(tim_kegiatan_map[tim]))

    rincian_map = defaultdict(list)
    rincian_beban_map = {}
    for obj in BebanHonor.objects.all():
        rincian_map[obj.tim].append(obj.rincian)
        rincian_beban_map[f"{obj.tim}||{obj.rincian}"] = obj.beban

    tim_beban_map = {}
    for tim, beban in BebanHonor.objects.values_list('tim', 'beban').distinct():
        tim_beban_map.setdefault(tim, []).append(beban)
    for tim in tim_beban_map:
        tim_beban_map[tim] = sorted(set(tim_beban_map[tim]))

    return tim_kegiatan_map, tim_beban_map, rincian_map, rincian_beban_map

@login_required(login_url='/login/')
def input_pekerjaan(request):
    if request.method == 'POST':
        total_rows = int(request.POST.get('total_rows', 0))
        errors = 0
        for i in range(total_rows):
            try:
                volume_str = request.POST.get(f'volume_{i}', '').strip()
                if not volume_str.isdigit() or int(volume_str) < 1:
                    messages.error(request, f"Baris {i+1}: Volume harus bilangan bulat positif.")
                    errors += 1
                    continue
                volume = int(volume_str)
                honor = int(request.POST.get(f'honor_{i}', 0))
                nilai = volume * honor

                PekerjaanMitra.objects.create(
                    bulan_kegiatan=request.POST.get(f'bulan_kegiatan_{i}'),
                    nama_mitra=request.POST.get(f'nama_mitra_{i}'),
                    tim_kerja=request.POST.get(f'tim_kerja_{i}'),
                    kegiatan=request.POST.get(f'kegiatan_{i}'),
                    volume=volume,
                    satuan=request.POST.get(f'satuan_{i}'),
                    honor_per_satuan=honor,
                    nilai_pekerjaan=nilai,
                    mulai_kegiatan=request.POST.get(f'mulai_{i}'),
                    selesai_kegiatan=request.POST.get(f'selesai_{i}'),
                    beban_anggaran=request.POST.get(f'beban_{i}')
                )
            except Exception as e:
                messages.error(request, f"Baris {i+1}: Gagal disimpan ({e})")
                errors += 1

        if errors == 0:
            messages.success(request, "Semua data berhasil disimpan.")
            return redirect('view_data')

    mitra_list = list(Mitra.objects.values_list('nama', flat=True).order_by('nama'))
    tim_kegiatan_map, tim_beban_map, rincian_map, rincian_beban_map = build_maps()

    return render(request, 'pekerjaan/input.html', {
        'bulan_list': bulan_list,
        'mitra_list': mitra_list,
        'tim_list': sorted(tim_kegiatan_map.keys()),
        'tim_kegiatan_json': json.dumps(tim_kegiatan_map),
        'tim_beban_json': json.dumps(tim_beban_map),
        'rincian_map': json.dumps(rincian_map),
        'rincian_beban_map': json.dumps(rincian_beban_map),
        'satuan_list': satuan_list,
    })

@login_required(login_url='/login/')
def view_data(request):
    queryset = PekerjaanMitra.objects.all()
    bulan = request.GET.get('bulan')
    mitra = request.GET.get('mitra')
    tim = request.GET.get('tim')
    kegiatan = request.GET.get('kegiatan')

    if bulan:
        queryset = queryset.filter(bulan_kegiatan=bulan)
    if mitra:
        queryset = queryset.filter(nama_mitra__icontains=mitra)
    if tim:
        queryset = queryset.filter(tim_kerja=tim)
    if kegiatan:
        queryset = queryset.filter(kegiatan__icontains=kegiatan)

    bulan_case = Case(
        *[When(bulan_kegiatan=nama_bulan, then=Value(i)) for i, nama_bulan in enumerate(bulan_list)],
        output_field=IntegerField()
    )
    queryset = queryset.order_by(bulan_case, 'nama_mitra')

    total_volume = queryset.aggregate(Sum('volume'))['volume__sum'] or 0
    total_nilai = queryset.aggregate(Sum('nilai_pekerjaan'))['nilai_pekerjaan__sum'] or 0

    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    bulan_unik = list(PekerjaanMitra.objects.values_list('bulan_kegiatan', flat=True).distinct())
    urut_bulan = [b for b in bulan_list if b in bulan_unik]
    mitra_list = sorted(set(PekerjaanMitra.objects.values_list('nama_mitra', flat=True).distinct()))
    tim_list = sorted(set(PekerjaanMitra.objects.values_list('tim_kerja', flat=True).distinct()))
    kegiatan_list = sorted(set(PekerjaanMitra.objects.values_list('kegiatan', flat=True).distinct()))

    context = {
        'data': page_obj,
        'page_obj': page_obj,
        'bulan_list': urut_bulan,
        'tim_list': tim_list,
        'mitra_list': mitra_list,
        'kegiatan_list': kegiatan_list,
        'total_volume': total_volume,
        'total_nilai': total_nilai,
    }
    return render(request, 'pekerjaan/view.html', context)

@login_required(login_url='/login/')
def dashboard(request):
    bulan_filter = request.GET.get('bulan')
    mitra_filter = request.GET.get('mitra')

    data = PekerjaanMitra.objects.all()
    if bulan_filter:
        data = data.filter(bulan_kegiatan=bulan_filter)
    if mitra_filter:
        data = data.filter(nama_mitra=mitra_filter)

    total_volume = data.aggregate(
        total=Coalesce(Sum('volume'), 0, output_field=FloatField())
    )['total']

    total_honor = data.aggregate(
        total=Coalesce(Sum('nilai_pekerjaan'), 0, output_field=FloatField())
    )['total']

    bulan_order = Case(
        *[When(bulan_kegiatan=nama_bulan, then=Value(i)) for i, nama_bulan in enumerate(bulan_list)],
        output_field=IntegerField()
    )

    rekap_list = (
        data
        .values('bulan_kegiatan', 'nama_mitra')
        .annotate(total_honor=Sum('nilai_pekerjaan', output_field=FloatField()))
        .order_by(bulan_order, 'nama_mitra')
    )

    paginator = Paginator(rekap_list, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    dropdown_bulan_raw = list(PekerjaanMitra.objects.values_list('bulan_kegiatan', flat=True).distinct())
    dropdown_bulan = [b for b in bulan_list if b in dropdown_bulan_raw]
    dropdown_mitra = sorted(set(PekerjaanMitra.objects.values_list('nama_mitra', flat=True).distinct()))

    jumlah_mitra = data.values('nama_mitra').distinct().count()

    return render(request, 'pekerjaan/dashboard.html', {
        'total_volume': total_volume,
        'total_honor': total_honor,
        'rekap': page_obj,
        'jumlah_mitra': jumlah_mitra,
        'dropdown_bulan': dropdown_bulan,
        'dropdown_mitra': dropdown_mitra,
        'filter_bulan': bulan_filter,
        'filter_mitra': mitra_filter,
    })

@login_required(login_url='/login/')
def rincian_pekerjaan(request):
    bulan = request.GET.get('bulan')
    mitra = request.GET.get('mitra')
    data = list(PekerjaanMitra.objects.filter(
        bulan_kegiatan=bulan,
        nama_mitra=mitra
    ).values(
        'kegiatan', 'volume', 'satuan', 'honor_per_satuan',
        'nilai_pekerjaan', 'mulai_kegiatan', 'selesai_kegiatan'
    ))
    return JsonResponse({'status': 'ok', 'data': data})

@login_required(login_url='/login/')
def edit_data(request, id):
    data = get_object_or_404(PekerjaanMitra, pk=id)
    mitra_list = list(Mitra.objects.values_list('nama', flat=True).order_by('nama'))
    tim_kegiatan_map, tim_beban_map, rincian_map, rincian_beban_map = build_maps()

    if request.method == 'POST':
        try:
            volume_str = request.POST.get('volume', '').strip()
            if not volume_str.isdigit() or int(volume_str) < 1:
                messages.error(request, "Volume harus bilangan bulat positif.")
                return redirect('edit_data', id=id)

            volume = int(volume_str)
            honor = int(request.POST.get('honor', 0))

            data.bulan_kegiatan = request.POST.get('bulan_kegiatan')
            data.nama_mitra = request.POST.get('nama_mitra')
            data.tim_kerja = request.POST.get('tim_kerja')
            data.kegiatan = request.POST.get('kegiatan')
            data.volume = volume
            data.satuan = request.POST.get('satuan')
            data.honor_per_satuan = honor
            data.nilai_pekerjaan = volume * honor
            data.mulai_kegiatan = request.POST.get('mulai')
            data.selesai_kegiatan = request.POST.get('selesai')
            data.beban_anggaran = request.POST.get('beban')
            data.save()

            messages.success(request, "Data berhasil diperbarui.")
            return redirect('view_data')
        except Exception as e:
            messages.error(request, f"Gagal memperbarui data: {e}")

    return render(request, 'pekerjaan/edit.html', {
        'data': data,
        'bulan_list': bulan_list,
        'mitra_list': mitra_list,
        'tim_list': sorted(tim_kegiatan_map.keys()),
        'tim_kegiatan_map': json.dumps(tim_kegiatan_map),
        'tim_beban_map': json.dumps(tim_beban_map),
        'rincian_map': json.dumps(rincian_map),
        'rincian_beban_map': json.dumps(rincian_beban_map),
        'satuan_list': satuan_list,
    })

@login_required(login_url='/login/')
def delete_data(request, id):
    data = get_object_or_404(PekerjaanMitra, pk=id)
    data.delete()
    messages.success(request, "Data berhasil dihapus.")
    return redirect('view_data')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            return redirect(next_url) if next_url else redirect('dashboard')
        else:
            messages.error(request, 'Username atau password salah.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
