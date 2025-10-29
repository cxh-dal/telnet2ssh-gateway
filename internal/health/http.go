package health

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"sync/atomic"
)

var (
	listenersCount    atomic.Int64
	activeSessions    atomic.Int64
	sessionsTotal     atomic.Int64
	bytesUpTotal      atomic.Int64 // SSH->Telnet
	bytesDownTotal    atomic.Int64 // Telnet->SSH
)

type snapshot struct {
	OK              bool   `json:"ok"`
	Message         string `json:"message"`
	Listeners       int64  `json:"listeners"`
	ActiveSessions  int64  `json:"active_sessions"`
	SessionsTotal   int64  `json:"sessions_total"`
	BytesUpTotal    int64  `json:"bytes_up_total"`
	BytesDownTotal  int64  `json:"bytes_down_total"`
}

func SetListenersCount(n int) {
	listenersCount.Store(int64(n))
}

func IncActiveSessions() { activeSessions.Add(1); sessionsTotal.Add(1) }
func DecActiveSessions() { activeSessions.Add(-1) }
func AddBytesUp(n int)   { bytesUpTotal.Add(int64(n)) }
func AddBytesDown(n int) { bytesDownTotal.Add(int64(n)) }

func addrFromEnv() string {
	if v := os.Getenv("HEALTH_ADDR"); v != "" {
		return v
	}
	return ":8080"
}

func StartHTTP() {
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		snap := snapshot{
			OK:             true,
			Message:        "ok",
			Listeners:      listenersCount.Load(),
			ActiveSessions: activeSessions.Load(),
			SessionsTotal:  sessionsTotal.Load(),
			BytesUpTotal:   bytesUpTotal.Load(),
			BytesDownTotal: bytesDownTotal.Load(),
		}
		_ = json.NewEncoder(w).Encode(snap)
	})
	mux.HandleFunc("/metrics", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		snap := map[string]any{
			"listeners":       listenersCount.Load(),
			"active_sessions": activeSessions.Load(),
			"sessions_total":  sessionsTotal.Load(),
			"bytes_up_total":  bytesUpTotal.Load(),
			"bytes_down_total": bytesDownTotal.Load(),
		}
		_ = json.NewEncoder(w).Encode(snap)
	})

	addr := addrFromEnv()
	go func() {
		if err := http.ListenAndServe(addr, mux); err != nil {
			log.Printf("健康检查HTTP服务退出: %v", err)
		}
	}()
}
