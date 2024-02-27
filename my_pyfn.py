import builtins
import aiohttp
from tqdm import tqdm
import subprocess
import platform
import sys
import os

# --------------------------修改全局 print -------------------------------------

# 保存原始的print函数，以便在自定义print函数中可以调用
original_print = builtins.print

# 定义一个新的print函数，这个函数将覆盖原始的print
def custom_print(*args, **kwargs):
    # 在这里可以添加任何你希望执行的代码
    
    # 调用原始的print函数
    original_print(*args, **kwargs)

def init_builtins_print():
    # 将全局的print函数替换为自定义的print函数
    builtins.print = custom_print

# --------------------------检测是否存在ffmpeg-------------------------------------
def add_ffmpeg_to_path():
    # 获取当前操作系统
    os_name = platform.system()
    current_directory = os.getcwd()
    # 根据操作系统确定ffmpeg文件名
    if os_name == "Windows":
        ffmpeg_filename = "ffmpeg.exe"
    elif os_name == "Darwin":  # macOS的系统名称
        ffmpeg_filename = "ffmpeg"
    else:
        print("此脚本仅支持Mac和Windows")
        sys.exit(1)

    ffmpeg_full_path = os.path.join(current_directory, ffmpeg_filename)
    target_path = "/usr/local/bin"

    # 检查ffmpeg文件是否存在于当前目录
    if os.path.isfile(ffmpeg_full_path):
        if os_name == "Windows":
            try:
                # Windows: 使用setx命令永久添加到PATH
                subprocess.run(["setx", "PATH", f"%PATH%;{current_directory}"], check=True)
                print(f"已将{ffmpeg_filename}的目录添加到Windows环境变量PATH。")
            except subprocess.CalledProcessError as e:
                print(f"添加环境变量失败: {e}")
        elif os_name == "Darwin":
            try:
                # macOS: 尝试移动ffmpeg到/usr/local/bin
                # 构建AppleScript命令
                applescript_command = f'''
                do shell script "mv \\"{ffmpeg_full_path}\\" \\"{target_path}\\"" with administrator privileges
                '''
                try:
                    # 使用osascript运行AppleScript
                    subprocess.run(["osascript", "-e", applescript_command], check=True)
                    print(f"文件已成功移动到 {target_path}")
                except subprocess.CalledProcessError:
                    print("需要管理员权限来执行此操作。")
            except subprocess.CalledProcessError:
                print(f"移动{ffmpeg_filename}时需要管理员权限。请尝试手动运行以下命令：")
                print(f"sudo mv {ffmpeg_full_path} {os.path.join(target_path, ffmpeg_filename)}")
    else:
        print(f"{ffmpeg_filename}不存在于{current_directory}")

def is_ffmpeg_executable():
    """尝试运行ffmpeg命令来检测其是否可执行。"""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
  

async def download_file(url, dest_path):
    """
    异步下载文件并显示进度条。
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            chunk_size = 1024
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
            with open(dest_path, 'wb') as file:
                async for data in response.content.iter_chunked(chunk_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()

async def install_ffmpeg():
    """
    异步下载FFmpeg到当前执行目录下，并显示下载进度。
    """
    os_name = os.name
    ffmpeg_filename = "ffmpeg.exe" if os_name == "nt" else "ffmpeg"
    ffmpeg_url = f"https://gitee.com/gao-ling-feng/echo-fetch-assets/releases/download/v1.0.0/{ffmpeg_filename}"
    await download_file(ffmpeg_url, ffmpeg_filename)
    if os_name != "nt":  # 如果不是Windows，设置执行权限
        os.chmod(ffmpeg_filename, 0o755)
    print(f"Downloaded {ffmpeg_filename} successfully.")
    add_ffmpeg_to_path()