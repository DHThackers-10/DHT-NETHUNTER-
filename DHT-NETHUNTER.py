#!/usr/bin/env python3

import os
import time
import subprocess
import requests
import glob
import re
import shutil
from pathlib import Path

from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.progress import SpinnerColumn, TextColumn
console = Console()

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def show_banner(text, style="bold red"):
    from pyfiglet import figlet_format
    banner = figlet_format(text)
    console.print(Align.center(f"[{style}]{banner}[/{style}]"))

def banner():
    from pyfiglet import figlet_format
    clear()
    console.print(Align.center(f"[bold red]{figlet_format('TEAM-DHT')}[/bold red]"))
    console.print(
        Panel.fit(
            "[green]This tool is for ethical hacking education only.\n"
            "[cyan]Watch full tutorial:[/cyan] [bold blue]https://youtube.com/@dht-hackers_10[/bold blue]",
            title="[bold yellow]DHT Hackers Tool[/bold yellow]",
            border_style="magenta",
            padding=(1, 2),
        )
    )
    time.sleep(2)
    os.system("termux-open-url https://youtube.com/@dht-hackers_10")
    Prompt.ask("[yellow]Press Enter after subscribing to continue...[/yellow]")
    clear()

def Kali_tool_banner():
    show_banner("KALI", "bold blue")
    console.print(
        Align.center(
            Panel.fit(
                "[cyan]KALI NETHUNTER INSTALLER\n"
                "[magenta]Made by:[/magenta] [bold green]DHT Team[/bold green]",
                title="[bold green]Welcome[/bold green]",
                border_style="cyan",
                padding=(1, 2),
            )
        )
    )

def get_arch():
    result = subprocess.check_output("getprop ro.product.cpu.abi", shell=True).decode().strip()
    if "arm64" in result:
        arch = "arm64"
    elif "armeabi" in result:
        arch = "armhf"
    else:
        console.print("[bold red]Unsupported Architecture[/bold red]")
        exit(1)

    table = Table(title="Device Architecture", box=None)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("CPU ABI", result)
    table.add_row("Architecture", arch)
    console.print(table)
    return arch

def get_latest_rootfs_url(arch):
    base_url = "https://image-nethunter.kali.org/nethunter-fs/kali-weekly/"
    res = requests.get(base_url)
    if res.status_code != 200:
        console.print(f"[red]Could not access: {base_url}[/red]")
        exit(1)

    matches = re.findall(rf'href="(kali-nethunter-.*?-rootfs-full-{arch}.tar.xz)"', res.text)
    if not matches:
        console.print(f"[red]No matching rootfs for architecture: {arch}[/red]")
        exit(1)

    latest_file = sorted(matches)[-1]
    return base_url + latest_file

def find_existing_tarxz(arch):
    for file in glob.glob("*.tar.xz"):
        if arch in file:
            return file
    return None

def check_existing_rootfs(arch):
    folder = f"kali-{arch}"
    if os.path.exists(folder):
        console.print(f"[bold yellow][!] '{folder}' directory already exists.[/bold yellow]")
        if Confirm.ask("[red]Do you want to delete it and reinstall?[/red]"):
            console.print(f"[blue][*] Removing '{folder}'...[/blue]")
            subprocess.run(f"rm -rf {folder}", shell=True)
        else:
            console.print("[green][+] Skipping installation steps.[/green]")
            final_instructions()
            exit(0)

def check_dependencies():
    console.print("[blue][*] Checking and installing dependencies...[/blue]")
    subprocess.run("apt update -y", shell=True)
    deps = ["proot", "tar", "wget"]
    table = Table(title="Dependencies", show_lines=True)
    table.add_column("Package", style="cyan")
    table.add_column("Status", style="green")
    for pkg in deps:
        path = f"{os.environ['PREFIX']}/bin/{pkg}"
        if not os.path.exists(path):
            subprocess.run(f"apt install -y {pkg}", shell=True)
            table.add_row(pkg, "Installed")
        else:
            table.add_row(pkg, "Present")
    console.print(table)

def task_table(title):
    table = Table(title=title, show_lines=True)
    table.add_column("Task", style="cyan", width=30)
    table.add_column("Status", style="yellow")
    return table

def download_rootfs(arch, url, max_retries=3):
    existing_file = find_existing_tarxz(arch)
    filename = url.split("/")[-1]

    if existing_file:
        console.print(f"[yellow][!] Found existing file: {existing_file}[/yellow]")
        if Confirm.ask("[red]Use this file instead of downloading again?[/red]"):
            return existing_file
        else:
            os.remove(existing_file)

    progress = Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        transient=True,
    )

    task_table_ui = Table(title="Downloading Rootfs", show_lines=True)
    task_table_ui.add_column("Task", style="cyan", width=30)
    task_table_ui.add_column("Status", style="yellow")
    task_table_ui.add_row("Download Rootfs", "In Progress...")

    layout = Table.grid()
    layout.add_row(progress)
    layout.add_row(task_table_ui)

    for attempt in range(max_retries):
        try:
            with Live(layout, refresh_per_second=10):
                task = progress.add_task("Downloading", filename=filename, total=0)
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    total = int(r.headers.get("Content-Length", 0))
                    progress.update(task, total=total)

                    with open(filename, "wb") as f:
                        for chunk in r.iter_content(1024 * 1024):
                            if chunk:
                                f.write(chunk)
                                progress.update(task, advance=len(chunk))

                task_table_ui.columns[1]._cells[0] = Text("Completed", style="bold green")
                return filename

        except Exception as e:
            console.print(f"[red]Download failed (Attempt {attempt + 1}/{max_retries}): {e}[/red]")
            if attempt + 1 == max_retries:
                console.print("[bold red]Maximum retries reached. Exiting.[/bold red]")
                exit(1)
            else:
                console.print("[yellow]Retrying in 5 seconds...[/yellow]")
                time.sleep(5)

def extract_rootfs(image_name):
    # Keep tasks and their statuses here
    tasks = [
        ("Extract rootfs archive", "In Progress...")
    ]

    # Create and show initial table
    table = Table(title="Extracting rootfs")
    table.add_column("Task")
    table.add_column("Status")

    for task, status in tasks:
        table.add_row(task, status)

    console.clear()
    console.print(table)

    try:
        # Run the extraction command
        subprocess.run(
            ["proot", "--link2symlink", "tar", "-xf", image_name],
            stderr=subprocess.DEVNULL,
            check=True,
        )
        # If successful, update status
        tasks[0] = ("Extract rootfs archive", "[green]Done[/green]")

    except subprocess.CalledProcessError:
        # On failure, update status
        tasks[0] = ("Extract rootfs archive", "[red]Failed but continuing[/red]")

    # Rebuild and print updated table
    table = Table(title="Extracting rootfs")
    table.add_column("Task")
    table.add_column("Status")
    for task, status in tasks:
        table.add_row(task, status)

    console.clear()
    console.print(table)

def create_launcher(prefix, chroot, username):
    console.print(Panel("[bold cyan]Creating nethunter launcher[/bold cyan]", title="Step"))
    nh_launcher = Path(prefix) / "bin" / "nethunter"
    nh_shortcut = Path(prefix) / "bin" / "nh"

    script = f"""#!/data/data/com.termux/files/usr/bin/bash -e
cd ${{HOME}}
unset LD_PRELOAD
if [ ! -f {chroot}/root/.version ]; then
    touch {chroot}/root/.version
fi

user="{username}"
home="/home/$user"
start="sudo -u kali /bin/bash"

if grep -q "kali" {chroot}/etc/passwd; then
    KALIUSR="1";
else
    KALIUSR="0";
fi
if [[ $KALIUSR == "0" || ("$#" != "0" && ("$1" == "-r" || "$1" == "-R")) ]]; then
    user="root"
    home="/$user"
    start="/bin/bash --login"
    if [[ "$#" != "0" && ("$1" == "-r" || "$1" == "-R") ]]; then
        shift
    fi
fi

cmdline="proot \\
        --link2symlink \\
        -0 \\
        -r {chroot} \\
        -b /dev \\
        -b /proc \\
        -b /sdcard \\
        -b {chroot}$home:/dev/shm \\
        -w $home \\
           /usr/bin/env -i \\
           HOME=$home \\
           PATH=/usr/local/sbin:/usr/local/bin:/bin:/usr/bin:/sbin:/usr/sbin \\
           TERM=$TERM \\
           LANG=C.UTF-8 \\
           $start"

cmd="$@"
if [ "$#" == "0" ]; then
    exec $cmdline
else
    $cmdline -c "$cmd"
fi
"""

    table = Table(show_header=True, header_style="bold green")
    table.add_column("File")
    table.add_column("Action")

    table.add_row(str(nh_launcher), "Writing launcher script")
    nh_launcher.write_text(script)
    nh_launcher.chmod(0o700)

    if nh_shortcut.is_symlink():
        nh_shortcut.unlink()
        table.add_row(str(nh_shortcut), "Removed old shortcut symlink")

    if not nh_shortcut.exists():
        nh_shortcut.symlink_to(nh_launcher)
        table.add_row(str(nh_shortcut), "Created shortcut symlink")

    console.print(table)

def check_kex(wimg):
    console.print(Panel("[bold cyan]Checking KeX dependencies[/bold cyan]", title="Step"))
    table = Table(show_header=True)
    table.add_column("Action")
    table.add_column("Status")

    if wimg in ("nano", "minimal"):
        table.add_row("Running apt update", "In Progress...")
        console.print(table)
        with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
            task1 = progress.add_task("Updating apt repositories...", start=False)
            progress.start_task(task1)
            subprocess.run(["nh", "sudo", "apt", "update"])
            table.rows[-1].cells[1].text = "[green]Done[/green]"
            console.print(table)

            task2 = progress.add_task("Installing tightvncserver and kali-desktop-xfce...", start=False)
            progress.start_task(task2)
            subprocess.run(["nh", "sudo", "apt", "install", "-y", "tightvncserver", "kali-desktop-xfce"])
            table.add_row("Install packages", "[green]Done[/green]")
            console.print(table)
    else:
        table.add_row("KeX dependencies", "[yellow]Not required for this image[/yellow]")
        console.print(table)

def create_kex_launcher(chroot):
    console.print(Panel("[bold cyan]Creating KeX launcher script[/bold cyan]", title="Step"))
    kex_launcher = Path(chroot) / "usr" / "bin" / "kex"

    script = """#!/bin/bash

function start-kex() {
    if [ ! -f ~/.vnc/passwd ]; then
        passwd-kex
    fi
    USR=$(whoami)
    if [ $USR == "root" ]; then
        SCREEN=":2"
    else
        SCREEN=":1"
    fi 
    export MOZ_FAKE_NO_SANDBOX=1; export HOME=${HOME}; export USER=${USR}; LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgcc_s.so.1 nohup vncserver $SCREEN >/dev/null 2>&1 </dev/null
    starting_kex=1
    return 0
}

function stop-kex() {
    vncserver -kill :1 | sed s/"Xtigervnc"/"NetHunter KeX"/
    vncserver -kill :2 | sed s/"Xtigervnc"/"NetHunter KeX"/
    return $?
}

function passwd-kex() {
    vncpasswd
    return $?
}

function status-kex() {
    sessions=$(vncserver -list | sed s/"TigerVNC"/"NetHunter KeX"/)
    if [[ $sessions == *"590"* ]]; then
        printf "\\n${sessions}\\n"
        printf "\\nYou can use the KeX client to connect to any of these displays.\\n\\n"
    else
        if [ ! -z $starting_kex ]; then
            printf '\\nError starting the KeX server.\\nPlease try "nethunter kex kill" or restart your termux session and try again.\\n\\n'
        fi
    fi
    return 0
}

function kill-kex() {
    pkill Xtigervnc
    return $?
}

case $1 in
    start)
        start-kex
        ;;
    stop)
        stop-kex
        ;;
    status)
        status-kex
        ;;
    passwd)
        passwd-kex
        ;;
    kill)
        kill-kex
        ;;
    *)
        stop-kex
        start-kex
        status-kex
        ;;
esac
"""
    table = Table(show_header=True)
    table.add_column("File")
    table.add_column("Action")

    table.add_row(str(kex_launcher), "Writing KeX launcher script")
    kex_launcher.write_text(script)
    kex_launcher.chmod(0o700)
    console.print(table)

def fix_profile_bash(chroot):
    console.print(Panel("[bold cyan]Fixing .bash_profile[/bold cyan]", title="Step"))
    bash_profile = Path(chroot) / "root" / ".bash_profile"
    if bash_profile.exists():
        lines = bash_profile.read_text().splitlines()
        new_lines = []
        skip = False
        for line in lines:
            if line.strip().startswith("if") and not skip:
                skip = True
                continue
            if line.strip().startswith("fi") and skip:
                skip = False
                continue
            if not skip:
                new_lines.append(line)
        bash_profile.write_text("\n".join(new_lines))
        console.print("[green]Removed conditional blocks from .bash_profile[/green]")
    else:
        console.print("[yellow].bash_profile not found, skipping[/yellow]")

def fix_resolv_conf(chroot):
    console.print(Panel("[bold cyan]Fixing resolv.conf[/bold cyan]", title="Step"))
    resolv_conf = Path(chroot) / "etc" / "resolv.conf"
    try:
        resolv_conf.write_text("nameserver 8.8.8.8\nnameserver 1.1.1.1\n")
        console.print("[green]DNS configured successfully[/green]")
    except Exception as e:
        console.print(f"[red]Failed to write resolv.conf: {e}[/red]")
        
def fix_sudo(chroot):
    console.print(Panel("[bold cyan]Fixing sudo and su permissions[/bold cyan]", title="Step"))
    sudo = Path(chroot) / "usr" / "bin" / "sudo"
    su = Path(chroot) / "usr" / "bin" / "su"
    sudo.chmod(sudo.stat().st_mode | 0o4000)
    su.chmod(su.stat().st_mode | 0o4000)

    sudoers_d = Path(chroot) / "etc" / "sudoers.d" / "kali"
    sudoers_d.write_text("kali    ALL=(ALL:ALL) ALL\n")

    sudo_conf = Path(chroot) / "etc" / "sudo.conf"
    sudo_conf.write_text("Set disable_coredump false\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File")
    table.add_column("Action")

    table.add_row(str(sudo), "Set SUID bit")
    table.add_row(str(su), "Set SUID bit")
    table.add_row(str(sudoers_d), "Configured sudoers for kali user")
    table.add_row(str(sudo_conf), "Configured sudo.conf")

    console.print(table)

def fix_uid(chroot):
    console.print(Panel("[bold cyan]Fixing UID and GID for kali user[/bold cyan]", title="Step"))
    uid = os.getuid()
    gid = os.getgid()
    
    console.print(f"Detected UID: [bold]{uid}[/bold], GID: [bold]{gid}[/bold]")
    
    try:
        subprocess.run(["nh", "-r", "usermod", "-u", str(uid), "kali"], check=True, stderr=subprocess.DEVNULL)
        subprocess.run(["nh", "-r", "groupmod", "-g", str(gid), "kali"], check=True, stderr=subprocess.DEVNULL)
        subprocess.run(["nh", "-r", "chown", "-R", "kali:kali", "/home/kali"], check=True, stderr=subprocess.DEVNULL)
        console.print("[green]UID and GID fix applied successfully.[/green]")
    except subprocess.CalledProcessError:
        console.print("[bold red]Failed to fix UID and GID. You may need to check permissions.[/bold red]")

def cleanup(image_name):
    if os.path.exists(image_name) and Confirm.ask("Delete downloaded rootfs file?"):
        os.remove(image_name)

def final_instructions():
    from pyfiglet import figlet_format
    console.print(f"[bold blue]{figlet_format('KALI')}[/bold blue]")
    table = Table(title="How to Use", show_lines=True)
    table.add_column("Command", style="green", no_wrap=True)
    table.add_column("Description", style="cyan")
    table.add_row("nethunter", "Start Kali NetHunter CLI")
    table.add_row("nh", "Shortcut command")
    table.add_row("nethunter -r", "Run as root")
    table.add_row("nethunter kex passwd", "Set KeX GUI password")
    table.add_row("nethunter kex &", "Start GUI")
    table.add_row("nethunter kex stop", "Stop GUI")
    console.print(table)
    console.print('[green]echo "nameserver 8.8.8.8" > /etc/resolv.conf[/green]')

def move_chroot_to_home(chroot):
    home = os.environ["HOME"]
    target = os.path.join(home, chroot)
    if os.path.abspath(os.getcwd()) != home:
        source = os.path.join(os.getcwd(), chroot)
        if os.path.exists(source):
            console.print(f"[blue][*] Moving {chroot} to home directory...[/blue]")
            subprocess.run(f"mv {source} {home}", shell=True)
        else:
            console.print(f"[red]Error: {source} does not exist[/red]")
            exit(1)
    os.chdir(home)
    console.print(f"[green][+] Changed directory to {home}[/green]")

def main():
    banner()
    Kali_tool_banner()
    arch = get_arch()
    check_existing_rootfs(arch)
    check_dependencies()
    rootfs_url = get_latest_rootfs_url(arch)
    image_name = download_rootfs(arch, rootfs_url)
    extract_rootfs(image_name)
    chroot = f"kali-{arch}"
    create_launcher(os.environ["PREFIX"], chroot, "kali")
    check_kex("full")  # or pass based on image name detection
    create_kex_launcher(chroot)
    fix_profile_bash(chroot)
    fix_resolv_conf(chroot)
    shutil.move("kali-arm64", os.path.expanduser("~"))
    clear()
    final_instructions()
if __name__ == "__main__":
    main()
    
