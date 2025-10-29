package main

import (
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/ritts-labs/tts-proxy/internal/config"
	"github.com/ritts-labs/tts-proxy/internal/server"
)

func main() {
	args := os.Args[1:]
	if len(args) == 0 {
		printHelp()
		os.Exit(1)
	}

	switch args[0] {
	case "serve":
		runServe(args[1:])
	case "map":
		runMap(args[1:])
	case "test":
		runTest(args[1:])
	case "help", "-h", "--help":
		printHelp()
	default:
		fmt.Printf("未知命令: %s\n\n", args[0])
		printHelp()
		os.Exit(1)
	}
}

func printHelp() {
	fmt.Println("tts-proxy - Telnet 转 SSH 代理服务")
	fmt.Println()
	fmt.Println("用法:")
	fmt.Println("  tts-proxy serve                       启动服务 (读取/创建 /data/config.json)")
	fmt.Println("  tts-proxy map list                    列出端口映射")
	fmt.Println("  tts-proxy map set <port> <host:port>  设置映射")
	fmt.Println("  tts-proxy map delete <port>           删除映射")
	fmt.Println("  tts-proxy test <port>                 测试映射连通性")
	fmt.Println()
	fmt.Println("环境变量:")
	fmt.Println("  CONFIG_PATH                 配置文件路径，默认 /data/config.json")
	fmt.Println("  SSH_USERNAME / SSH_PASSWORD SSH 登录用户名/密码，默认均为 ritts")
	fmt.Println("  HEALTH_ADDR                 健康检查HTTP地址，默认 :8080")
	fmt.Println()
}

func runServe(args []string) {
	cfgPath := config.PathFromEnv()
	cfg, err := config.LoadOrCreate(cfgPath)
	if err != nil {
		log.Fatalf("加载配置失败: %v", err)
	}

	if err := server.Run(cfg); err != nil {
		log.Fatalf("服务运行失败: %v", err)
	}
}

func runMap(args []string) {
	if len(args) == 0 {
		fmt.Println("用法: tts-proxy map [list|set|delete]")
		os.Exit(1)
	}
	cfgPath := config.PathFromEnv()
	cfg, err := config.LoadOrCreate(cfgPath)
	if err != nil {
		log.Fatalf("加载配置失败: %v", err)
	}

	sub := args[0]
	switch sub {
	case "list":
		pairs := cfg.SortedPairs()
		if len(pairs) == 0 {
			fmt.Println("无端口映射，使用 'tts-proxy map set <port> <host:port>' 添加")
			return
		}
		for _, p := range pairs {
			fmt.Printf("%d -> %s\n", p.Port, p.Target)
		}
	case "set":
		if len(args) != 3 {
			fmt.Println("用法: tts-proxy map set <port> <host:port>")
			os.Exit(1)
		}
		port, err := config.ParsePort(args[1])
		if err != nil {
			log.Fatalf("端口无效: %v", err)
		}
		target := strings.TrimSpace(args[2])
		if err := cfg.SetMapping(port, target); err != nil {
			log.Fatalf("设置失败: %v", err)
		}
		if err := config.SaveAtomic(cfgPath, cfg); err != nil {
			log.Fatalf("保存失败: %v", err)
		}
		fmt.Printf("已设置: %d -> %s\n", port, target)
	case "delete":
		if len(args) != 2 {
			fmt.Println("用法: tts-proxy map delete <port>")
			os.Exit(1)
		}
		port, err := config.ParsePort(args[1])
		if err != nil {
			log.Fatalf("端口无效: %v", err)
		}
		cfg.DeleteMapping(port)
		if err := config.SaveAtomic(cfgPath, cfg); err != nil {
			log.Fatalf("保存失败: %v", err)
		}
		fmt.Printf("已删除: %d\n", port)
	default:
		fmt.Println("用法: tts-proxy map [list|set|delete]")
		os.Exit(1)
	}
}

func runTest(args []string) {
	if len(args) != 1 {
		fmt.Println("用法: tts-proxy test <port>")
		os.Exit(1)
	}
	cfgPath := config.PathFromEnv()
	cfg, err := config.LoadOrCreate(cfgPath)
	if err != nil {
		log.Fatalf("加载配置失败: %v", err)
	}
	port, err := config.ParsePort(args[0])
	if err != nil {
		log.Fatalf("端口无效: %v", err)
	}
	target := cfg.Lookup(port)
	if target == "" {
		log.Fatalf("端口 %d 未映射，请先设置。", port)
	}
	if err := server.TestDial(target); err != nil {
		log.Fatalf("连通性失败: %v", err)
	}
	fmt.Printf("OK: %d -> %s 可连接\n", port, target)
}
