# Batimetri

Python tabanlı, tek ışın (singlebeam) batimetri işlemlerine özel hafif bir araç seti. CSV formatında ham derinlik verilerini okuyabilir, özet istatistikler çıkarabilir, basit ASCII grid üretimi yapabilir ve derinlik aralıklarına göre filtrelenmiş çıktı alabilirsiniz.

## Kurulum
Proje dış bağımlılık kullanmaz. Sistemde Python 3.11+ yüklüyse aşağıdaki komutla CLI'ı çalıştırabilirsiniz:

```bash
python -m batimetri.cli --help
```

## Veri formatı
CSV dosyası şu başlıkları içermelidir:
- `latitude` (ondalık derece)
- `longitude` (ondalık derece)
- `depth` (metre, aşağı doğru pozitif)
- `timestamp` (isteğe bağlı, ISO-8601)

Örnek veri için `data/sample_soundings.csv` dosyasına bakabilirsiniz.

## Komutlar
### Özet
Ham verinin istatistiklerini hesaplar:
```bash
python -m batimetri.cli summary data/sample_soundings.csv
```

### ASCII grid üretimi
Basit bir ortalama derinlik grid'i (ESRI ASCII grid uyumlu) oluşturur:
```bash
python -m batimetri.cli export-grid data/sample_soundings.csv output.asc --cell-size 0.0005 --min-depth 12 --max-depth 14
```

### Filtrelenmiş CSV
Belirli bir derinlik aralığında kayıtları dışarı aktarır:
```bash
python -m batimetri.cli filter data/sample_soundings.csv filtered.csv --max-depth 14
```

## Sonraki adımlar
Uygulama, daha gelişmiş QC, tid/NMEA entegrasyonları ve görselleştirmeler gibi ek özellikler için genişletilmeye hazır basit bir temel sunar.
