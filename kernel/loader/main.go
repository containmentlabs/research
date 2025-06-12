package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"syscall"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	blockedSyscalls = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "lock_blocked_syscalls_total",
			Help: "Total number of blocked syscalls by type",
		},
		[]string{"syscall"},
	)
	
	kernelUptime = prometheus.NewGauge(
		prometheus.GaugeOpts{
			Name: "lock_kernel_uptime_seconds",
			Help: "Time since kernel was started",
		},
	)
)

func init() {
	prometheus.MustRegister(blockedSyscalls)
	prometheus.MustRegister(kernelUptime)
}

type Loader struct {
	kernelPath string
	metricsPort int
	startTime time.Time
	cmd *exec.Cmd
}

func NewLoader(kernelPath string, metricsPort int) *Loader {
	return &Loader{
		kernelPath: kernelPath,
		metricsPort: metricsPort,
	}
}

func (l *Loader) Start(ctx context.Context) error {
	args := []string{
		"--enable-syscall-block",
		"--enable-network-block",
	}
	
	l.cmd = exec.CommandContext(ctx, l.kernelPath, args...)
	l.cmd.Stdout = os.Stdout
	l.cmd.Stderr = os.Stderr
	
	if err := l.cmd.Start(); err != nil {
		return fmt.Errorf("failed to start kernel: %w", err)
	}
	
	l.startTime = time.Now()
	log.Printf("L.O.C.K. kernel started with PID %d", l.cmd.Process.Pid)
	
	go l.updateMetrics(ctx)
	
	return nil
}

func (l *Loader) Stop() error {
	if l.cmd == nil || l.cmd.Process == nil {
		return nil
	}
	
	if err := l.cmd.Process.Signal(syscall.SIGTERM); err != nil {
		return fmt.Errorf("failed to send SIGTERM: %w", err)
	}
	
	done := make(chan error, 1)
	go func() {
		done <- l.cmd.Wait()
	}()
	
	select {
	case <-done:
		log.Println("L.O.C.K. kernel stopped gracefully")
		return nil
	case <-time.After(5 * time.Second):
		if err := l.cmd.Process.Kill(); err != nil {
			return fmt.Errorf("failed to kill kernel: %w", err)
		}
		log.Println("L.O.C.K. kernel killed")
		return nil
	}
}

func (l *Loader) updateMetrics(ctx context.Context) {
	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			kernelUptime.Set(time.Since(l.startTime).Seconds())
		}
	}
}

func (l *Loader) ServeMetrics() {
	http.Handle("/metrics", promhttp.Handler())
	addr := fmt.Sprintf(":%d", l.metricsPort)
	log.Printf("Serving metrics on http://localhost%s/metrics", addr)
	if err := http.ListenAndServe(addr, nil); err != nil {
		log.Printf("Failed to serve metrics: %v", err)
	}
}

func main() {
	var (
		kernelPath = flag.String("kernel", "/usr/local/bin/lock", "Path to L.O.C.K. kernel binary")
		metricsPort = flag.Int("port", 9090, "Port for Prometheus metrics")
	)
	flag.Parse()
	
	loader := NewLoader(*kernelPath, *metricsPort)
	
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
	
	if err := loader.Start(ctx); err != nil {
		log.Fatalf("Failed to start loader: %v", err)
	}
	
	go loader.ServeMetrics()
	
	<-sigCh
	log.Println("Received shutdown signal")
	
	cancel()
	if err := loader.Stop(); err != nil {
		log.Printf("Error stopping kernel: %v", err)
	}
} 