import asyncio
import websockets
import threading
import builtins

# --------------------------重写 builtins.print 方法-------------------------------------
# 覆盖全局的print方法
original_print = builtins.print
connection = None  # 全局变量，用于存储websocket连接
server_loop = None  # 用于存储WebSocket服务器事件循环的全局变量

# 创建WebSocket服务端的逻辑
async def websocket_server_logic(websocket, path):
    global connection
    connection = websocket  # 存储websocket连接
    try:
        async for message in websocket:
            original_print(f"Message from client: {message}")  # 使用original_print以避免递归调用
    except websockets.exceptions.ConnectionClosed:
        original_print("Connection closed")  # 使用original_print以避免递归调用

# 启动WebSocket服务器的函数
def start_websocket_server():
    global server_loop
    loop = asyncio.new_event_loop()
    server_loop = loop  # 保存对事件循环的引用
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(websocket_server_logic, "localhost", 8765)
    loop.run_until_complete(start_server)
    loop.run_forever()

# 在新线程中启动WebSocket服务
threading.Thread(target=start_websocket_server, daemon=True).start()

def custom_print(*args, **kwargs):
    message = ' '.join(map(str, args))
    original_print(message, **kwargs)  # 保留原始print的行为
    if connection is not None and server_loop is not None:
        # 使用服务器事件循环来调度消息发送
        asyncio.run_coroutine_threadsafe(async_send(message), server_loop)
    
async def async_send(message):
    if connection is not None:
        await connection.send(message)

# 等待服务器线程启动并创建事件循环
while server_loop is None:
    pass

builtins.print = custom_print

# --------------------------重写 os.system 方法-------------------------------------
import os

# 保存原始的os.system
original_os_system = os.system

# 定义一个新的os.system行为
def custom_os_system(command):
    # 在这里调用原始的os.system执行命令
    result = original_os_system(command)
    
    # 发送消息到客户端
    # 注意: 这里需要根据你的实际WebSocket处理逻辑进行调整
    # 这里的调用假设你已经在其他地方建立了WebSocket连接
    asyncio.run_coroutine_threadsafe(async_send("CLEAR_GLINFEN"), server_loop)

    return result

# 覆盖os.system
os.system = custom_os_system
