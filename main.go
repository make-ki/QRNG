package qrng

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os/exec"
	"strconv"
)

type resQ struct {
	Status string `json:"status"`
	Bits   int    `json:"bits"`
	Hex    string `json:"hex"`
	Binary string `json:"binary"`
}

func main() {
	mux := defaultMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		fmt.Printf("Server running healthy...")
	})
	mux.HandleFunc("/qrng", give_qrn)

	http.ListenAndServe("127.0.0.1:80", mux)
}

func defaultMux() *http.ServeMux {
	mux := http.NewServeMux()
	mux.HandleFunc("/", usage)
	return mux
}

func usage(w http.ResponseWriter, r *http.Request) {
	w.Write([]byte("Just go to /qrng?bits=<whatever you want>"))
}

func give_qrn(w http.ResponseWriter, r *http.Request) {
	bits := r.URL.Query().Get("bits")
	intBits, err := strconv.Atoi(bits)

	if err != nil || intBits < 0 || intBits > 1024 {
		http.Error(w, "Invalid bits value in query.", http.StatusBadRequest)
		return
	}

	cmd := exec.Command("python3 ./core/quantum_engine.py", "--bits", bits)
	stdout, err := cmd.Output()
	if err != nil {
		http.Error(w, "Error in displaying output", http.StatusInternalServerError)
		return
	}

	var res resQ
	if err := json.Unmarshal(stdout, &res); err != nil {
		http.Error(w, "Internal data corruption or incompatible json outputs.", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(res)
}
