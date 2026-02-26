package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os/exec"
	"strconv"
)

type resQ struct {
	Status        string `json:"status"`
	RequestedBits int    `json:"requested_bits"`
	RawBitsUsed   int    `json:"raw_bits_used"`
	Hex           string `json:"hex"`
	Binary        string `json:"binary"`
	Message       string `json:"message,omitempty"`
}

func main() {
	mux := defaultMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		fmt.Printf("Server running healthy...")
	})
	mux.HandleFunc("/qrng", give_qrn)

	fmt.Printf("Starting server...")
	err := http.ListenAndServe("127.0.0.1:8890", mux)
	if err != nil {
		log.Printf("Can't run the defaultMux")
	}
	fmt.Printf("Server running successfully...")
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

	cmd := exec.Command("python3", "core/quantum_engine.py", "--bits", bits, "--oversample", "4")
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
