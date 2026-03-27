# Walkthrough

## Arhitectură
Sistemul funcționează conform planului inițial folosind o arhitectură *Master-Worker*:
* **Master Node ([master.py](file:///Users/adrianboscanici/Documents/proiect_apd/master.py))**: Coordonează distribuția datelor, primește interogările de la clienți, partiționează numele în `chunk`-uri și le trimite worker-ilor conectați (`Round-Robin`). Reasamblează și sortează rezultatele.
* **Worker Node ([worker.py](file:///Users/adrianboscanici/Documents/proiect_apd/worker.py))**: Se conectează la master, așteaptă job-uri conținând un text țintă, o limită de similaritate (threshold) și un set de date (un chunk). Calculează [jaccard_similarity](file:///Users/adrianboscanici/Documents/proiect_apd/utils.py#6-21) și trimite back listele filtrate.
* **Client Node ([client.py](file:///Users/adrianboscanici/Documents/proiect_apd/client.py))**: Trimite un payload JSON conținând ținta, limita, și parametrul esențial pentru throughput: `chunk_size`.

## Analiza de Performanță (Speedup & Throughput)

Am rulat benchmarkul pe un set generat de 1,000,000 de nume (probabilitate middle-name = 0.8 la generare). Outputul esențial al rulării:

```
Generating 1000000 names into names.txt (middle name probability=0.8)...
Generated 100000 names...
...Generated 900000 names...
Generation complete.
```
Master a încărcat names.txt:
```
Loaded 1000000 records.
```

### 1. Speedup (scalabilitate vs Număr Noduri)
Testul a folosit `chunk_size=50000`, `target='Ion'`, `threshold=0.2`. Rezultatele observate:

| Număr Workeri | Timp Execuție (s) | Matches |
|---------------:|------------------:|--------:|
| 1 | 3.5918 | 6645 |
| 2 | 1.8086 | 6645 |
| 4 | 0.9746 | 6645 |

Calcul rapid: speedup față de 1 worker → 2 workers ≈ 1.99x, 4 workers ≈ 3.68x.

**Concluzie**: Adăugarea de workeri reduce semnificativ timpul (eficiență aproape liniară până la 4 noduri în acest test).

### 2. Throughput (Impactul `chunk_size`)
Testul a rulat cu 4 workeri activi și aceiași parametri `target='Ion'`, `threshold=0.2`. Rezultate:

| Chunk Size | Timp Execuție (s) | Matches |
|-----------:|------------------:|--------:|
| 10000 | 0.9260 | 6645 |
| 25000 | 0.9208 | 6645 |
| 50000 | 0.9233 | 6645 |
| 100000 | 1.1155 | 6645 |

Observație: pentru acest dataset de 1M, chunk sizes între 10k–50k oferă timpi asemănători; `100k` scade utilizarea paralelismului (timp mai mare).

**Recomandare practică**: Alege `chunk_size` astfel încât numărul de chunk-uri ≥ număr_workeri × câteva (2–4) pentru a asigura balanță și reutilizare.

## Cod și Testare

Fișiere relevante:
- [master.py](master.py)
- [worker.py](worker.py)
- [client.py](client.py)
- [generate_data.py](generate_data.py)
- [benchmark.py](benchmark.py)

Comenzi de rulare folosite:
```bash
python3 generate_data.py 1000000 0.8
python3 master.py names.txt
python3 worker.py   # (pornit în N terminale)
python3 client.py --target Ion --threshold 0.2 --chunk-size 50000
python3 benchmark.py   # rulează teste automate (speedup + throughput)
```

Această analiză respectă cerința: paralelizare Master–Worker prin socketuri, distribuire pe chunk-uri, parametrizare pe `chunk_size` și `număr noduri`, și evaluarea `speedup` și `throughput`.
