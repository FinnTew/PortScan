# PortScan

## 介绍

操作系统期末作业，多线程端口扫描工具，使用线程池处理扫描任务，使用 `tqdm` 实现进度条显示。

## 使用

```plaintext
usage: scan.py [-h] [--start-port START_PORT] [--end-port END_PORT] [--timeout TIMEOUT]
               [--max-threads MAX_THREADS] [--rate-limit RATE_LIMIT] [--result-dir RESULT_DIR]
               target

多线程端口扫描器

positional arguments:
  target                目标（IP、域名或子网，例如：192.168.1.0/24）

options:
  -h, --help            show this help message and exit
  --start-port START_PORT
                        起始端口（默认 1）
  --end-port END_PORT   结束端口（默认 65535）
  --timeout TIMEOUT     每次扫描的超时限制（秒，默认 0.5）
  --max-threads MAX_THREADS
                        最大线程数（默认 100）
  --rate-limit RATE_LIMIT
                        速率限制（秒，默认 0，无限制）
  --result-dir RESULT_DIR
                        扫描结果JSON文件保存目录（默认 当前目录）
```