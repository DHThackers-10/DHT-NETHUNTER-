#!/usr/bin/env python3

import os, time, subprocess, requests
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

console = Console()

def clear(): os.system("clear" if os.name == "posix" else "cls")

def show_banner(text, style="bold red"):
    from pyfiglet import figlet_format
    banner = figlet_format(text)
    console.print(Align.center(f"[{style}]{banner}[/{style}]"))

def banner():
    from pyfiglet import figlet_format
    clear()
    console.print(Align.center(f"[bold red]{figlet_format('TEAM-DHT')}[/bold red]"))
    console.print(Panel.fit(
        "[green]This tool is for ethical hacking education only.\n"
        "[cyan]Watch full tutorial:[/cyan] [bold blue]https://youtube.com/@dht-hackers_10[/bold blue]",
        title="[bold yellow]DHT Hackers Tool[/bold yellow]", border_style="magenta", padding=(1, 2)
    ))
    time.sleep(2)
    os.system("termux-open-url https://youtube.com/@dht-hackers_10")
    Prompt.ask("[yellow]Press Enter after subscribing to continue...[/yellow]")
    clear()

def Kali_tool_banner():
    show_banner("KALI", "bold blue")
    console.print(Align.center(
        Panel.fit(
            "[cyan]KALI NETHUNTER INSTALLER\n"
            "[magenta]Made by:[/magenta] [bold green]DHT Team[/bold green]",
            title="[bold green]Welcome[/bold green]",
            border_style="cyan",
            padding=(1, 2)
        )
    ))

def get_arch():
    result = subprocess.check_output("getprop ro.product.cpu.abi", shell=True).decode().strip()
    if "arm64" in result: arch = "arm64"
    elif "armeabi" in result: arch = "armhf"
    else: console.print("[bold red]Unsupported Architecture[/bold red]"); exit(1)
    table = Table(title="Device Architecture", box=None)
    table.add_column("Property", style="cyan"); table.add_column("Value", style="green")
    table.add_row("CPU ABI", result); table.add_row("Architecture", arch)
    console.print(table)
    return arch
    
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
    table.add_column("Package", style="cyan"); table.add_column("Status", style="green")
    for pkg in deps:
        path = f"{os.environ['PREFIX']}/bin/{pkg}"
        if not os.path.exists(path):
            subprocess.run(f"apt install -y {pkg}", shell=True)
            table.add_row(pkg, "Installed")
        else: table.add_row(pkg, "Present")
    console.print(table)

def task_table(title):
    table = Table(title=title, show_lines=True)
    table.add_column("Task", style="cyan", width=30)
    table.add_column("Status", style="yellow")
    return table

def download_rootfs(image_name, url, max_retries=3):
    if os.path.exists(image_name):
        if Confirm.ask("[red]Existing Rootfs file found. Delete and redownload?[/red]"):
            os.remove(image_name)
        else:
            return

    progress = Progress(
        "[progress.description]{task.description}",
        BarColumn(), DownloadColumn(), TransferSpeedColumn(), TimeRemainingColumn(),
        transient=True,
    )

    task_table = Table(title="Downloading Rootfs", show_lines=True)
    task_table.add_column("Task", style="cyan", width=30)
    task_table.add_column("Status", style="yellow")
    task_table.add_row("Download Rootfs", "In Progress...")

    layout = Table.grid()
    layout.add_row(progress)
    layout.add_row(task_table)

    for attempt in range(max_retries):
        try:
            with Live(layout, refresh_per_second=10):
                headers = {}
                downloaded = 0
                if os.path.exists(image_name):
                    downloaded = os.path.getsize(image_name)
                    headers["Range"] = f"bytes={downloaded}-"

                task = progress.add_task("Downloading", filename=image_name, total=0)
                with requests.get(url, stream=True, headers=headers) as r:
                    r.raise_for_status()
                    total = int(r.headers.get("Content-Length", 0))
                    if "Content-Range" in r.headers:
                        total += downloaded
                    progress.update(task, total=total, completed=downloaded)

                    mode = "ab" if downloaded else "wb"
                    with open(image_name, mode) as f:
                        for chunk in r.iter_content(1024 * 1024):
                            if chunk:
                                f.write(chunk)
                                progress.update(task, advance=len(chunk))

                task_table.columns[1]._cells[0] = Text("Completed", style="bold green")
                return

        except Exception as e:
            console.print(f"[red]Download failed (Attempt {attempt + 1}/{max_retries}): {e}[/red]")
            if attempt + 1 == max_retries:
                console.print("[bold red]Maximum retries reached. Exiting.[/bold red]")
                exit(1)
            else:
                console.print("[yellow]Retrying in 5 seconds...[/yellow]")
                time.sleep(5)

def extract_rootfs(image_name, chroot):
    table = task_table("Extracting Rootfs")
    table.add_row("Extraction", "In Progress...")
    with Live(table, refresh_per_second=5):
        cmd = f"proot --link2symlink tar --exclude='dev/*' -xf {image_name}"
        subprocess.run(cmd, shell=True)
        table.columns[1]._cells[0] = Text("Completed", style="bold green")

def configure(chroot):
    table = task_table("Configuring NetHunter")
    table.add_row("Set permissions", "In Progress...")
    with Live(table, refresh_per_second=5):
        subprocess.run(f"chmod +s {chroot}/usr/bin/sudo", shell=True)
        subprocess.run(f"chmod +s {chroot}/usr/bin/su", shell=True)
        with open(f"{chroot}/etc/sudoers.d/kali", "w") as f:
            f.write("kali ALL=(ALL:ALL) ALL\n")
        table.columns[1]._cells[0] = Text("Completed", style="bold green")

def fix_uid_gid():
    table = task_table("Fix UID/GID")
    table.add_row("UID/GID Sync", "In Progress...")
    with Live(table, refresh_per_second=5):
        uid, gid = os.getuid(), os.getgid()
        subprocess.run(f"nh -r usermod -u {uid} kali", shell=True)
        subprocess.run(f"nh -r groupmod -g {gid} kali", shell=True)
        table.columns[1]._cells[0] = Text("Done", style="bold green")

def create_launcher(chroot):
    launcher_path = f"{os.environ['PREFIX']}/bin/nethunter"
    with open(launcher_path, "w") as f:
        f.write(f"""#!/data/data/com.termux/files/usr/bin/bash -e
cd $HOME
unset LD_PRELOAD
cmd="proot --link2symlink -0 -r {chroot} -b /dev -b /proc -w /root /usr/bin/env -i HOME=/root TERM=$TERM LANG=C.UTF-8 /bin/bash --login"
if [ "$#" == "0" ]; then exec $cmd
else $cmd -c "$@"
fi""")
    os.chmod(launcher_path, 0o700)
    nh_path = f"{os.environ['PREFIX']}/bin/nh"
    if not os.path.exists(nh_path):
        os.symlink(launcher_path, nh_path)

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
    console.print("[green]echo "nameserver 8.8.8.8" > /etc/resolv.conf[/green]")
    
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
    chroot = f"kali-{arch}"
    image_name = f"kali-nethunter-rootfs-full-{arch}.tar.xz"
    url = f"https://kali.download/nethunter-images/current/rootfs/{image_name}"
    check_dependencies()
    download_rootfs(image_name, url)
    extract_rootfs(image_name, chroot)
    move_chroot_to_home(chroot)
    create_launcher(chroot)
    configure(chroot)
    fix_uid_gid()
    cleanup(image_name)
    final_instructions()

if __name__ == "__main__":
    main()
    
