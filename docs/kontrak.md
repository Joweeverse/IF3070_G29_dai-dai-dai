## state
- List of dict: {vehicle_id, on_board, x, y, orientation}
- x,y = pojok kiri atas; x ke kanan, y ke bawah
- orientasi => H: width->x, length->y. V: dibalik

## constraint
- kalau ada yang melanggar constraint maka pakai penalty (bkn lgsg ditolak)
- overlap 1000/cell, keluar batas kapal 1000/cell, overweight 1000/unit

## move
- swap: tukar posisi & orientasi dua kendaraan. hasil boleh tdk feasible
  (dianggap penalty)
- relocate: koordinat random baru dalam range geladak
- rotate: flip H<->V, anchor tetap kiri atas
- toggle: kendaraan keluar/masuk kapal

## kontrak interface
- evaluate(state, vehicles, ship) -> float
- semua algoritma nge return {initial_state, final_state, history,
  duration, metrics}
  
  "initial_state":	state |	state awal
  "final_state":	state	| solusi terbaik yang ditemukan
  "history":	list of float	| nilai objective terbaik per iterasi/generasi
  "history_avg":	list of float	| (opsional, GA) rata-rata objective populasi per generasi
  "duration":	float	| waktu eksekusi (detik)
  "metrics":	dict	| bebas per algoritma (SA: temperature akhir; GA: pop_size, dll.)
  "state_history":	list of state	| (opsional) snapshot state tiap improvement

## format input
- JSON: {ship: {width, length, max_weight}, vehicles: [{ id, width, length, weight, shipping_fee }, ...]}
