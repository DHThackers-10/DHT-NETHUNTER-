#!/usr/bin/env python3

import os
import time
import subprocess
import requests
import pyfiglet

from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich.table import Table
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

console = Console()

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def show_banner(text, style="bold red"):
    banner = pyfiglet.figlet_format(text)
    console.print(Align.center(f"[{style}]{banner}[/{style}]"))

def dht_hackers_banner():
    clear()
    show_banner("DHT-HACKERS", "bold red")
    console.print(Panel.fit(
        "[green]This tool is for ethical hacking education only.\n"
        "[cyan]Watch full tutorial:[/cyan] [bold blue]https://youtube.com/@dht-hackers_10[/bold blue]",
        title="[bold yellow]DHT Hackers Tool[/bold yellow]",
        border_style="magenta",
        padding=(1, 2)
    ))
    time.sleep(2)
    if os.name == "posix":
        os.system("termux-open-url https://youtube.com/@dht-hackers_10")
    Prompt.ask("[yellow]Press Enter after subscribing to continue...[/yellow]")
    clear()

def Kali_tool_banner():
    show_banner("KALI", "bold blue")
    console.print(Align.center(
        Panel.fit(
            "[cyan]KALI NETHUNTER INSTALLER\n"
            "[magenta]Made by:[/magenta] [bold green]DHT Hackers Team[/bold green]",
            title="[bold green]Welcome[/bold green]",
            border_style="cyan",
            padding=(1, 2)
        )
    ))

def ask(question, default="N"):
    return Confirm.ask(f"[cyan]{question}[/cyan]", default=default.upper() == "Y")

def unsupported_arch():
    console.print("[bold red]Unsupported Architecture[/bold red]")
    exit(1)

def get_arch():
    result = subprocess.check_output("getprop ro.product.cpu.abi", shell=True).decode().strip()
    arch = None
    if "arm64" in result:
        arch = "arm64"
    elif "armeabi" in result:
        arch = "armhf"
    else:
        unsupported_arch()

    table = Table(title="Device Architecture", box=None)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("CPU ABI", result)
    table.add_row("Architecture", arch)
    console.print(table)

    return arch

def set_strings(arch):
    return (
        f"kali-{arch}",
        f"kali-nethunter-rootfs-full-{arch}.tar.xz"
    )

def prepare_fs(chroot):
    if os.path.isdir(chroot):
        if ask("Existing rootfs directory found. Delete and create a new one?", "N"):
            subprocess.run(["rm", "-rf", chroot])
        else:
            return True
    return False

def check_dependencies():
    console.print("\n[bold blue][*] Checking and installing dependencies...[/bold blue]")
    subprocess.run("apt update -y", shell=True)
    deps = ["proot", "tar", "wget"]
    table = Table(title="Dependencies", show_lines=True)
    table.add_column("Package", style="cyan")
    table.add_column("Status", style="green")

    for pkg in deps:
        if not os.path.exists(f"{os.environ['PREFIX']}/bin/{pkg}"):
            subprocess.run(f"apt install -y {pkg}", shell=True)
            table.add_row(pkg, "Installed")
        else:
            table.add_row(pkg, "Present")

    console.print(table)

def get_rootfs(image_name, url):
    if os.path.exists(image_name):
        if ask("Existing image file found. Delete and download a new one?", "N"):
            os.remove(image_name)
        else:
            return

    table = Table(title="Progress", show_lines=True)
    table.add_column("Task", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_row("Downloading Rootfs", "Starting...")

    console.print(table)

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("Downloading", filename=image_name, total=0)

        with requests.get(url, stream=True) as r:
            total = int(r.headers.get("Content-Length", 0))
            progress.update(task, total=total)

            with open(image_name, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))

def extract_rootfs(image_name, keep_chroot):
    table = Table(title="Progress", show_lines=True)
    table.add_column("Task", style="cyan")
    table.add_column("Status", style="yellow")

    if not keep_chroot:
        table.add_row("Extracting Rootfs", "In Progress...")
        console.print(table)
        subprocess.run(f"proot --link2symlink tar -xf {image_name}", shell=True)
    else:
        table.add_row("Extracting Rootfs", "Skipped (Already Exists)")
        console.print(table)

def create_launcher(chroot, username="kali"):
    launcher_path = f"{os.environ['PREFIX']}/bin/nethunter"
    shortcut_path = f"{os.environ['PREFIX']}/bin/nh"
    with open(launcher_path, "w") as f:
        f.write(f"""#!/data/data/com.termux/files/usr/bin/bash -e
cd $HOME
unset LD_PRELOAD
if [ ! -f {chroot}/root/.version ]; then
  touch {chroot}/root/.version
fi
user="{username}"
home="/home/$user"
start="sudo -u kali /bin/bash"
if grep -q "kali" {chroot}/etc/passwd; then
  KALIUSR="1"
else
  KALIUSR="0"
fi
if [[ $KALIUSR == "0" || ("$#" != "0" && ("$1" == "-r" || "$1" == "-R")) ]]; then
  user="root"
  home="/$user"
  start="/bin/bash --login"
  if [[ "$#" != "0" && ("$1" == "-r" || "$1" == "-R") ]]; then
    shift
  fi
fi
cmdline="proot --link2symlink -0 -r {chroot} -b /dev -b /proc -b {chroot}$home:/dev/shm -w $home /usr/bin/env -i HOME=$home PATH=/usr/local/sbin:/usr/local/bin:/bin:/usr/bin:/sbin:/usr/sbin TERM=$TERM LANG=C.UTF-8 $start"
cmd="$@"
if [ "$#" == "0" ]; then
  exec $cmdline
else
  $cmdline -c "$cmd"
fi
""")
    os.chmod(launcher_path, 0o700)
    if os.path.islink(shortcut_path):
        os.remove(shortcut_path)
    if not os.path.exists(shortcut_path):
        os.symlink(launcher_path, shortcut_path)

def configure_nethunter(chroot):
    subprocess.run(f"sed -i '/if/,/fi/d' {chroot}/root/.bash_profile", shell=True)
    subprocess.run(f"chmod +s {chroot}/usr/bin/sudo", shell=True)
    subprocess.run(f"chmod +s {chroot}/usr/bin/su", shell=True)
    with open(f"{chroot}/etc/sudoers.d/kali", "w") as f:
        f.write("kali    ALL=(ALL:ALL) ALL\n")
    with open(f"{chroot}/etc/sudo.conf", "w") as f:
        f.write("Set disable_coredump false\n")

def fix_uid():
    uid = os.getuid()
    gid = os.getgid()
    subprocess.run(f"nh -r usermod -u {uid} kali", shell=True)
    subprocess.run(f"nh -r groupmod -g {gid} kali", shell=True)

def cleanup(image_name):
    if os.path.exists(image_name):
        if ask("Delete downloaded rootfs file?", "N"):
            os.remove(image_name)

def final_instructions():
    show_banner("NetHunter", "blue")
    table = Table(title="How to Use", show_lines=True)
    table.add_column("Command", style="green", no_wrap=True)
    table.add_column("Description", style="cyan")

    table.add_row("nethunter", "Start Kali NetHunter CLI")
    table.add_row("nethunter kex passwd", "Set KeX password")
    table.add_row("nethunter kex &", "Start GUI session")
    table.add_row("nethunter kex stop", "Stop GUI session")
    table.add_row("nethunter -r", "Run as root")
    table.add_row("nh", "Shortcut")

    console.print(table)

# === Main ===

def main():
    dht_hackers_banner()
    Kali_tool_banner()
    arch = get_arch()
    chroot, image_name = set_strings(arch)
    keep_chroot = prepare_fs(chroot)
    check_dependencies()
    url = f"https://kali.download/nethunter-images/current/rootfs/{image_name}"
    get_rootfs(image_name, url)
    extract_rootfs(image_name, keep_chroot)
    create_launcher(chroot)
    cleanup(image_name)
    console.print("[blue][*] Configuring NetHunter...[/blue]")
    configure_nethunter(chroot)
    fix_uid()
    final_instructions()

if __name__ == "__main__":
    main()
    
