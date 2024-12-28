import socket
from concurrent.futures import ThreadPoolExecutor
import ipaddress
import json
from tqdm import tqdm
import time
import argparse
from pathlib import Path

# 常见端口描述
PORT_DESCRIPTIONS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
}

def describe_port(port):
    """
    返回端口的服务名称
    """
    return PORT_DESCRIPTIONS.get(port, "未知服务")


def scan_port(host, port, timeout):
    """
    扫描单个端口，判断是否开放。
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # 设置超时时间
            s.settimeout(timeout)
            if s.connect_ex((host, port)) == 0:
                return port
    except:
        pass
    return None

def scan_host(host, start_port, end_port, timeout=0.5, max_threads=100, rate_limit=0):
    """
    扫描单个主机的端口范围。
    """
    print(f"\n扫描主机: {host}")

    # 使用线程池并显示进度条
    ports = range(start_port, end_port + 1)
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        def rate_limited_scan(port):
            result = scan_port(host, port, timeout)
            time.sleep(rate_limit)
            return result

        results = list(tqdm(executor.map(rate_limited_scan, ports), total=len(ports), desc=f"Scanning {host}"))

    # 收集开放端口
    open_ports = [port for port in results if port]

    # 输出扫描结果
    print(f"\n扫描结束: {host}")
    if open_ports:
        for port in open_ports:
            print(f"[+] 端口 {port} ({describe_port(port)}) 开放")
    else:
        print("未找到开放的端口")

    return open_ports


def scan_subnet(subnet, start_port, end_port, max_threads=100, rate_limit=0):
    """
    扫描子网中所有主机。
    """
    network = ipaddress.ip_network(subnet, strict=False)
    all_results = {}

    for host in network.hosts():
        open_ports = scan_host(str(host), start_port, end_port, max_threads, rate_limit)
        if open_ports:
            all_results[str(host)] = open_ports

    return all_results


def save_results(results, dire):
    """
    保存扫描结果到 JSON 文件中。
    """
    filename = f"scan_results_{time.time_ns()}.json"
    directory = Path(dire)
    if not directory.exists():
        directory.mkdir()
    filepath = directory / filename
    with open(filepath, "w") as f:
        json.dump(results, f, indent=4)
    print(f"\n结果保存至 {filepath}")


def main():
    """
    主程序入口。
    """

    parser = argparse.ArgumentParser(description='多线程端口扫描器')

    # 添加命令行参数
    parser.add_argument('target', type=str, help='目标（IP、域名或子网，例如：192.168.1.0/24）')
    parser.add_argument('--start-port', type=int, default=1, help='起始端口（默认 1）')
    parser.add_argument('--end-port', type=int, default=65535, help='结束端口（默认 65535）')
    parser.add_argument('--timeout', type=float, default=0.5, help='每次扫描的超时限制（秒，默认 0.5）')
    parser.add_argument('--max-threads', type=int, default=100, help='最大线程数（默认 100）')
    parser.add_argument('--rate-limit', type=float, default=0, help='速率限制（秒，默认 0，无限制）')
    parser.add_argument('--result-dir', type=str, default='./', help='扫描结果JSON文件保存目录（默认 当前目录）')

    # 解析命令行参数
    args = parser.parse_args()

    try:
        # 获取参数
        target = args.target
        start_port = args.start_port
        end_port = args.end_port
        timeout = args.timeout
        max_threads = args.max_threads
        rate_limit = args.rate_limit
        dire = args.result_dir

        if start_port < 0 or end_port > 65535 or start_port > end_port:
            raise ValueError("Invalid port range.")

        if max_threads <= 0:
            raise ValueError("Number of threads must be a positive integer.")

        if rate_limit < 0:
            raise ValueError("Rate limit must be non-negative.")

        # 判断是单个主机还是子网
        if "/" in target:  # 子网扫描
            results = scan_subnet(target, start_port, end_port, max_threads, rate_limit)
        else:  # 单个主机扫描
            results = {target: scan_host(target, start_port, end_port, timeout, max_threads, rate_limit)}

        # 保存结果
        save_results(results, dire)

    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()