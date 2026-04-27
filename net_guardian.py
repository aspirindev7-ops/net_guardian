import os
import time
import socket
import platform
import json
from datetime import datetime
import threading

class NetGuardian:
    def __init__(self, target_hosts):
        self.target_hosts = target_hosts
        self.stats = {host: {"status": "Unknown", "latency": "N/A", "last_check": ""} for host in target_hosts}
        self.is_running = True

    def ping_host(self, host):
        """Check host availability using ping."""
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = f"ping {param} 1 {host}"
        
        start_time = time.time()
        response = os.system(command + " > " + ("NUL" if platform.system().lower() == "windows" else "/dev/null"))
        end_time = time.time()
        
        latency = round((end_time - start_time) * 1000, 2)
        
        status = "UP" if response == 0 else "DOWN"
        return status, latency

    def check_critical_services(self, host, ports=[80, 443, 22]):
        """Verify if essential ports are reachable."""
        open_ports = []
        for port in ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                if s.connect_ex((host, port)) == 0:
                    open_ports.append(port)
        return open_ports

    def monitor_loop(self):
        """Main monitoring loop running in the background."""
        print(f"\n[+] NetGuardian Active. Monitoring {len(self.target_hosts)} hosts...")
        while self.is_running:
            for host in self.target_hosts:
                status, latency = self.ping_host(host)
                services = self.check_critical_services(host)
                
                self.stats[host] = {
                    "status": status,
                    "latency": f"{latency}ms" if status == "UP" else "N/A",
                    "open_services": services,
                    "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            self.display_dashboard()
            time.sleep(10) # Wait 10 seconds before next check

    def display_dashboard(self):
        """Clear screen and show live status."""
        os.system('cls' if platform.system().lower() == 'windows' else 'clear')
        print("="*60)
        print(f" NETGUARDIAN LIVE MONITOR - {datetime.now().strftime('%H:%M:%S')} ")
        print("="*60)
        print(f"{'HOST':<20} | {'STATUS':<8} | {'LATENCY':<10} | {'SERVICES'}")
        print("-"*60)
        for host, data in self.stats.items():
            status_color = "[+] " if data['status'] == "UP" else "[-] "
            print(f"{status_color}{host:<16} | {data['status']:<8} | {data['latency']:<10} | {data['open_services']}")
        print("\n[Press Ctrl+C to stop]")

if __name__ == "__main__":
    # Example hosts to monitor (Google DNS, Localhost, etc.)
    hosts = ["8.8.8.8", "google.com", "127.0.0.1"]
    guardian = NetGuardian(hosts)
    try:
        guardian.monitor_loop()
    except KeyboardInterrupt:
        guardian.is_running = False
        print("\n[!] Monitoring stopped by user.")
