package config

import (
	"encoding/json"
	"errors"
	"fmt"
	"net"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
)

const (
	defaultConfigPath = "/data/config.json"
)

type Config struct {
	// ListenPorts: 监听的SSH端口列表。为空则默认 4001-4032。
	ListenPorts []int            `json:"listen_ports"`
	// Mappings: 端口 -> Telnet 目标地址 host:port
	Mappings    map[int]string   `json:"mappings"`
}

type Pair struct {
	Port   int
	Target string
}

func PathFromEnv() string {
	if v := strings.TrimSpace(os.Getenv("CONFIG_PATH")); v != "" {
		return v
	}
	return defaultConfigPath
}

func defaultListenPorts() []int {
	ports := make([]int, 0, 32)
	for p := 4001; p <= 4032; p++ {
		ports = append(ports, p)
	}
	return ports
}

func defaultConfig() *Config {
	return &Config{
		ListenPorts: nil, // 空代表使用默认4001-4032
		Mappings:    map[int]string{},
	}
}

func ensureDir(path string) error {
	dir := filepath.Dir(path)
	return os.MkdirAll(dir, 0o755)
}

func LoadOrCreate(path string) (*Config, error) {
	if _, err := os.Stat(path); errors.Is(err, os.ErrNotExist) {
		cfg := defaultConfig()
		if err := SaveAtomic(path, cfg); err != nil {
			return nil, err
		}
		return cfg, nil
	}
	b, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	cfg := defaultConfig()
	if len(b) > 0 {
		if err := json.Unmarshal(b, cfg); err != nil {
			return nil, err
		}
	}
	if cfg.Mappings == nil {
		cfg.Mappings = map[int]string{}
	}
	return cfg, nil
}

func SaveAtomic(path string, cfg *Config) error {
	if err := ensureDir(path); err != nil {
		return err
	}
	tmp := path + ".tmp"
	b, err := json.MarshalIndent(cfg, "", "  ")
	if err != nil {
		return err
	}
	if err := os.WriteFile(tmp, b, 0o644); err != nil {
		return err
	}
	return os.Rename(tmp, path)
}

func (c *Config) ListenPortsList() []int {
	if len(c.ListenPorts) == 0 {
		return defaultListenPorts()
	}
	return append([]int(nil), c.ListenPorts...)
}

func (c *Config) Lookup(port int) string {
	return c.Mappings[port]
}

func (c *Config) SetMapping(port int, target string) error {
	if err := validatePort(port); err != nil {
		return err
	}
	if err := validateTarget(target); err != nil {
		return err
	}
	if c.Mappings == nil {
		c.Mappings = map[int]string{}
	}
	c.Mappings[port] = target
	return nil
}

func (c *Config) DeleteMapping(port int) {
	delete(c.Mappings, port)
}

func (c *Config) SortedPairs() []Pair {
	pairs := make([]Pair, 0, len(c.Mappings))
	for k, v := range c.Mappings {
		pairs = append(pairs, Pair{Port: k, Target: v})
	}
	sort.Slice(pairs, func(i, j int) bool { return pairs[i].Port < pairs[j].Port })
	return pairs
}

func ParsePort(s string) (int, error) {
	p, err := strconv.Atoi(strings.TrimSpace(s))
	if err != nil {
		return 0, fmt.Errorf("无法解析端口: %w", err)
	}
	return p, validatePort(p)
}

func validatePort(p int) error {
	if p < 1 || p > 65535 {
		return fmt.Errorf("端口超出范围: %d", p)
	}
	return nil
}

func validateTarget(target string) error {
	// 要求 host:port 形式
	host, port, err := net.SplitHostPort(target)
	if err != nil {
		return fmt.Errorf("目标地址无效(需要 host:port): %w", err)
	}
	if host == "" {
		return fmt.Errorf("目标主机为空")
	}
	if _, err := strconv.Atoi(port); err != nil {
		return fmt.Errorf("目标端口无效: %w", err)
	}
	return nil
}
