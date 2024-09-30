# Optimizing Indicar Analysis code with Polars (on going)

### Mengapa Optimisasi Kode dengan Polars Diperlukan?

![image](https://github.com/user-attachments/assets/e021810d-3ea8-40a1-a234-6f378ed2aac4)

Dalam analisis data dan pemrosesan data yang besar, waktu eksekusi dan efisiensi memori adalah faktor yang sangat penting. Seiring dengan pertumbuhan volume data dan kompleksitas pemrosesan data, alat analisis seperti Pandas yang umum digunakan menjadi terbatas kemampuannya. Dalam analisis data GPS kendaraan, data yang dianalisis biasanya berasal dari ribuan titik GPS yang dikumpulkan dari berbagai kendaraan selama periode waktu tertentu. Setiap titik data bisa mencakup atribut seperti `deviceid`, `waktu pengambilan data`, `longitude`, `latitude`, `kecepatan`, dan parameter lainnya. Pengolahan dan analisis data ini dapat menjadi sangat intensif, terutama ketika menyangkut:

1. **Proses Analisis Rute dan Perjalanan**
   - Dataset GPS biasanya mencakup informasi yang mendetail tentang perjalanan kendaraan, seperti waktu mulai dan berakhir, kecepatan rata-rata, jarak tempuh, dan pola perjalanan lainnya. Analisis ini mengharuskan **filtering**, **grouping**, **aggregation**, dan **perhitungan jarak** yang memerlukan banyak operasi komputasi.
   - Dengan menggunakan Pandas, analisis ini sering kali melibatkan iterasi berulang melalui data, membuat DataFrame baru, dan memodifikasi data. Karena pendekatan ini bekerja secara **eager evaluation**, eksekusi langsung dari setiap operasi sering menghabiskan waktu dan memori yang signifikan. 

2. **Peningkatan Volume Data dari GPS**
   - Setiap kendaraan menghasilkan data GPS secara terus-menerus (misalnya, setiap detik atau menit), yang berarti dataset GPS akan berkembang secara eksponensial seiring waktu. Penggunaan Pandas yang bekerja secara **single-threaded** dan memori-berat tidak dapat menangani volume data yang besar secara efisien.
   - Data GPS memiliki waktu dan koordinat geografis yang membutuhkan banyak manipulasi data, seperti **penyaringan** berdasarkan waktu, penghitungan jarak antara titik koordinat, dan penggabungan data berdasarkan `deviceid` dan `waktu`. Operasi-operasi ini sangat memerlukan optimisasi karena sifatnya yang computationally expensive.

3. **Polars sebagai Solusi untuk Analisis Data GPS yang Kompleks**
   - **Polars** dengan kemampuan **lazy evaluation** dan **multi-threaded execution** dapat menjalankan operasi data GPS ini dengan cara yang lebih efisien. Sebagai contoh, ketika menghitung jarak total perjalanan kendaraan dari dataset GPS, Polars dapat melakukan penggabungan dan penghitungan ini dengan lebih cepat melalui optimisasi otomatis dan pemrosesan paralel.
   - Ketika melakukan operasi seperti `concat`, `filter`, atau `groupby` pada dataset GPS besar, Polars akan meminimalkan penggunaan memori dengan menggabungkan beberapa operasi dalam satu langkah eksekusi yang dioptimalkan. Ini berbeda dengan Pandas yang akan mengalokasikan memori untuk setiap tahap operasi, menyebabkan beban memori yang besar.

4. **Mengurangi Waktu Pemrosesan Perjalanan**
   - Dalam analisis GPS kendaraan, misalnya, untuk mendeteksi perjalanan kendaraan, kita perlu menggabungkan titik-titik data berdasarkan waktu dan lokasi. Jika menggunakan Pandas, kita sering harus melakukan operasi iterasi melalui setiap baris data, yang bisa menjadi sangat lambat.
   - Dengan Polars, operasi ini dapat dilakukan dalam waktu yang jauh lebih singkat karena optimisasi **vectorized operations** dan **multi-threading**. Seperti pada contoh sebelumnya, Polars memungkinkan filtering data berdasarkan waktu dan penghitungan jarak antara titik-titik GPS dengan efisien, sehingga waktu eksekusi dapat berkurang secara drastis.

5. **Penggunaan Memori yang Efisien untuk Dataset GPS**
   - Dataset GPS kendaraan memiliki atribut waktu yang kompleks (`datetime` dengan zona waktu), yang sering kali menyebabkan overhead memori saat diolah dengan Pandas. Kesalahan seperti yang muncul sebelumnya (`failed to determine supertype of datetime[μs, Asia/Jakarta] and datetime[μs]`) adalah contoh bagaimana Polars dapat membantu dengan penanganan tipe data yang lebih baik.
   - Polars dapat menangani berbagai tipe data dengan lebih fleksibel dan efisien, terutama untuk `datetime`, yang menjadi salah satu elemen penting dalam analisis data GPS. Operasi yang memerlukan manipulasi waktu, seperti konversi zona waktu, dapat dilakukan lebih cepat dan dengan memori yang lebih rendah menggunakan Polars.

Beralih dari Pandas ke Polars dalam analisis data GPS kendaraan diperlukan untuk menangani volume data besar dengan operasi komputasi yang kompleks. Polars memberikan peningkatan performa signifikan melalui pemrosesan paralel, efisiensi memori, dan kemampuan **lazy evaluation**. Oleh karena itu, optimisasi kode dengan Polars memungkinkan pengolahan data GPS kendaraan dilakukan lebih cepat dan efisien, membantu dalam analisis rute, pola perjalanan, dan evaluasi kinerja kendaraan secara real-time dan pada skala besar.


### Indicar Analyis Pandas VS Polars

Aanalisis berikut hanya menampilkan bagian code dengan perbedaan waktu pemrosesan yang cukup signifikan, full code dapat dilihat di dokumentasi terlampir.

#### 1. Load Data

![image](https://github.com/user-attachments/assets/bc71b322-72fd-44f3-8ed7-9aa085e01e07)
![image](https://github.com/user-attachments/assets/3d6e579d-9c38-4c92-bdb2-cdecd0c90178)

- **Atas:** Menggunakan `pandas` untuk membaca CSV (`pd.read_csv()`). Eksekusi menggunakan Pandas membutuhkan waktu yang lebih lama (1,4 detik) untuk memproses data tanpa set timezone. Set timezone memerlukan waktu 0,6 detik lagi.
- **Bawah:** Menggunakan `polars` untuk membaca CSV (`pl.read_csv()`). Eksekusi menggunakan Polars jauh lebih cepat (0,1 detik) sudah termasuk set timezone, menunjukkan kinerja yang lebih baik dalam pemrosesan data.

#### 2. Null Coordinate

![image](https://github.com/user-attachments/assets/01dc7308-79f4-4e48-a6c4-a3955d40f1fd)

- **Kiri:** Menggunakan `pandas`. Eksekusi menggunakan Pandas membutuhkan waktu yang lebih lama (1,5 detik) untuk memproses data.
- **Kanan:** Menggunakan `polars`. Eksekusi menggunakan Polars jauh lebih cepat (0,1 detik).

#### 3. Distance-Speed-Acceleration

![image](https://github.com/user-attachments/assets/6264a247-8fee-40db-a3c7-b17a775477ca)

- **Kiri:** Menggunakan `pandas`. Eksekusi menggunakan Pandas membutuhkan waktu yang lebih lama (18,5 detik) untuk memproses data.
- **Kanan:** Menggunakan `polars`. Eksekusi menggunakan Polars jauh lebih cepat (16,1 detik).


### Kesimpulan
- Hasil yang didapat menunjukkan Polars memiliki kemampuan untuk memproses data lebih cepat daripada Pandas. Untuk bagian code lain tidak memiliki perbedaan waktu pemrosesan yang signifikan, namun hasil code Polars yang didapat selalu relatif lebih cepat daripada Pandas.
- Kelebihan Polars: Kecepatan yang sangat tinggi, optimasi memori, dan kemampuan untuk menangani operasi yang kompleks dengan waktu yang relatif singkat.
- Kelemahan Polars: Tidak seperti Pandas, Polars tidak mendukung konsep indexing pada DataFrame. Hal ini bisa menjadi kelemahan ketika bekerja dengan operasi yang membutuhkan pencarian data secara cepat menggunakan indeks. Di Pandas, penggunaan indeks memungkinkan akses dan manipulasi data yang lebih efisien ketika menangani dataset besar dan kompleks. Pengguna yang terbiasa dengan Pandas mungkin perlu waktu untuk menyesuaikan dengan sintaks dan API yang berbeda di Polars.
- Untuk analisis dataset GPS dengan jumlah data yang besar dan kompleks, penggunaan Polars terbukti lebih efisien. Waktu pemrosesan yang lebih cepat sangat membantu dalam pengolahan data yang membutuhkan iterasi dan manipulasi kolom besar, seperti pada analisis data GPS kendaraan. Meskipun Pandas masih banyak digunakan dan bermanfaat dalam data science, Polars menawarkan alternatif yang lebih efisien terutama ketika performa dan kecepatan menjadi faktor penting.

### What to Do Next
- Melanjutkan ke bagian Journey, Speed Analysis, Anomalies, dan Case Study.
- Optimisasi lebih lanjut code Polars yyang sudah dibuat.
- Melakukan evaluasi output yang dihasilkan oleh Pandas dan Polars (apakah ada yang berbeda).
- Melakukan komparasi waktu pemrosesan secara menyeluruh antara code Pandas dan code Polars.
