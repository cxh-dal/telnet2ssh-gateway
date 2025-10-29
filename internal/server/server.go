package server

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"errors"
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"time"

	glssh "github.com/gliderlabs/ssh"
	"golang.org/x/crypto/ssh"

	"github.com/ritts-labs/tts-proxy/internal/config"
	"github.com/ritts-labs/tts-proxy/internal/health"
	"github.com/ritts-labs/tts-proxy/internal/tn"
)

func Run(initialCfg *config.Config) error {
	// Start health HTTP
	health.StartHTTP()

	ports := initialCfg.ListenPortsList()
	health.SetListenersCount(len(ports))

	// Prepare host key
	signer, err := loadOrCreateHostKey(defaultHostKeyPath())
	if err != nil {
		return fmt.Errorf("加载/生成主机密钥失败: %w", err)
	}

	// Shared auth settings
	user := envOr("SSH_USERNAME", "ritts")
	pass := envOr("SSH_PASSWORD", "ritts")

	wg := &sync.WaitGroup{}
	for _, port := range ports {
		p := port
		wg.Add(1)
		go func() {
			defer wg.Done()
			addr := fmt.Sprintf(":%d", p)
			for {
				s := &glssh.Server{
					Addr: addr,
					Version: "SSH-2.0-tts-proxy",
					PasswordHandler: func(ctx glssh.Context, password string) bool {
						return ctx.User() == user && password == pass
					},
					Handler: func(sess glssh.Session) {
						defer func() { _ = sess.Close() }()
						// 动态读取最新配置，支持运行时变更
						cfg, err := config.LoadOrCreate(config.PathFromEnv())
						if err != nil {
							io.WriteString(sess, fmt.Sprintf("加载配置失败: %v\n", err))
							return
						}
						local := sess.Context().LocalAddr()
						lport := portFromAddr(local)
						target := cfg.Lookup(lport)
						if target == "" {
							io.WriteString(sess, fmt.Sprintf("端口 %d 未配置Telnet地址。请使用 CLI: tts-proxy map set %d <host:port>\n", lport, lport))
							return
						}
						// 连接Telnet
						conn, err := tn.Dial(target, 5*time.Second)
						if err != nil {
							io.WriteString(sess, fmt.Sprintf("连接 Telnet 后端失败: %v\n", err))
							return
						}
						defer conn.Close()
						health.IncActiveSessions()
						defer health.DecActiveSessions()

						// 建立双向转发
						cw := tn.NewConnWriter(conn)
						inFilter := tn.NewInputFilter(conn, cw)
						outEsc := tn.NewOutputEscaper(cw)

						// sess -> telnet (bytes up)
						clientToSrvDone := make(chan struct{})
						go func() {
							_, _ = copyWithCount(outEsc, sess, health.AddBytesUp)
							close(clientToSrvDone)
						}()
						// telnet -> sess (bytes down)
						_, _ = copyWithCount(sess, inFilter, health.AddBytesDown)
						// 等待对向结束
						<-clientToSrvDone
					},
				}
				s.AddHostKey(signer)

				// Run and supervise
				if err := s.ListenAndServe(); err != nil {
					if errors.Is(err, glssh.ErrServerClosed) {
						return
					}
					log.Printf("监听 %s 失败: %v，5秒后重试", addr, err)
					time.Sleep(5 * time.Second)
					continue
				}
				return
			}
		}()
	}
	wg.Wait()
	return nil
}

func portFromAddr(a net.Addr) int {
	if a == nil { return 0 }
	// Expect format ip:port
	_, portStr, err := net.SplitHostPort(a.String())
	if err != nil { return 0 }
	p, _ := strconv.Atoi(portStr)
	return p
}

func defaultHostKeyPath() string {
	if v := os.Getenv("HOST_KEY_PATH"); v != "" {
		return v
	}
	return "/data/ssh_host_rsa_key"
}

func loadOrCreateHostKey(path string) (ssh.Signer, error) {
	if _, err := os.Stat(path); errors.Is(err, os.ErrNotExist) {
		if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
			return nil, err
		}
		if err := generateRSAKey(path, 2048); err != nil {
			return nil, err
		}
	}
	pemBytes, err := os.ReadFile(path)
	if err != nil { return nil, err }
	priv, err := ssh.ParseRawPrivateKey(pemBytes)
	if err != nil { return nil, err }
	signer, err := ssh.NewSignerFromKey(priv)
	if err != nil { return nil, err }
	return signer, nil
}

func generateRSAKey(path string, bits int) error {
	key, err := rsa.GenerateKey(rand.Reader, bits)
	if err != nil { return err }
	pemBlock := &pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(key)}
	pemBytes := pem.EncodeToMemory(pemBlock)
	return os.WriteFile(path, pemBytes, 0o600)
}

func envOr(k, def string) string { if v := strings.TrimSpace(os.Getenv(k)); v != "" { return v }; return def }

func copyWithCount(dst io.Writer, src io.Reader, onCount func(n int)) (int64, error) {
	buf := make([]byte, 32*1024)
	var written int64
	for {
		nr, er := src.Read(buf)
		if nr > 0 {
			nw, ew := dst.Write(buf[0:nr])
			if nw > 0 {
				written += int64(nw)
				onCount(nw)
			}
			if ew != nil {
				return written, ew
			}
			if nr != nw {
				return written, io.ErrShortWrite
			}
		}
		if er != nil {
			if er == io.EOF { break }
			return written, er
		}
	}
	return written, nil
}

func TestDial(target string) error {
	c, err := tn.Dial(target, 3*time.Second)
	if err != nil { return err }
	_ = c.Close()
	return nil
}
