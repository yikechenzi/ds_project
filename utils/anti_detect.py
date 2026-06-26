"""
反检测工具
注入JS隐藏自动化痕迹 + 模拟人类行为
"""
import asyncio
import random
import math


def get_stealth_init_script() -> str:
    """返回反检测初始化JS脚本"""
    return """
    // 隐藏 webdriver 属性
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });

    // 模拟插件列表
    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            const plugins = [
                { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                { name: 'Native Client', filename: 'internal-nacl-plugin' }
            ];
            plugins.length = 3;
            return plugins;
        }
    });

    // 设置语言
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-CN', 'zh', 'en']
    });

    // Canvas 指纹噪声
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type) {
        if (type === 'image/png') {
            const ctx = this.getContext('2d');
            if (ctx) {
                const imageData = ctx.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] = imageData.data[i] ^ 1;
                }
                ctx.putImageData(imageData, 0, 0);
            }
        }
        return originalToDataURL.apply(this, arguments);
    };

    // WebGL 指纹一致性
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return 'Intel Inc.';
        if (parameter === 37446) return 'Intel Iris OpenGL Engine';
        return getParameter.apply(this, arguments);
    };

    // 隐藏自动化相关属性
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;

    // Chrome runtime
    window.chrome = {
        runtime: {},
        loadTimes: function() {},
        csi: function() {},
        app: {}
    };

    // 权限查询模拟
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    """


async def human_delay(min_s: float = 0.5, max_s: float = 2.0):
    """随机人类延迟"""
    delay = random.uniform(min_s, max_s)
    await asyncio.sleep(delay)


async def simulate_mouse_move(page, x: int, y: int):
    """模拟贝塞尔曲线鼠标移动"""
    # 获取当前鼠标位置(如果有的话)
    viewport = page.viewport_size
    start_x = random.randint(0, viewport["width"])
    start_y = random.randint(0, viewport["height"])

    # 生成贝塞尔控制点
    cp1_x = start_x + (x - start_x) * random.uniform(0.2, 0.5)
    cp1_y = start_y + (y - start_y) * random.uniform(0.0, 0.3)
    cp2_x = start_x + (x - start_x) * random.uniform(0.5, 0.8)
    cp2_y = start_y + (y - start_y) * random.uniform(0.7, 1.0)

    steps = random.randint(15, 30)
    for i in range(steps + 1):
        t = i / steps
        # 三阶贝塞尔曲线
        tx = (
            (1 - t) ** 3 * start_x +
            3 * (1 - t) ** 2 * t * cp1_x +
            3 * (1 - t) * t ** 2 * cp2_x +
            t ** 3 * x
        )
        ty = (
            (1 - t) ** 3 * start_y +
            3 * (1 - t) ** 2 * t * cp1_y +
            3 * (1 - t) * t ** 2 * cp2_y +
            t ** 3 * y
        )
        await page.mouse.move(tx, ty)
        await asyncio.sleep(random.uniform(0.005, 0.02))


async def simulate_typing(page, selector: str, text: str):
    """模拟人类打字（逐字符输入）"""
    element = page.locator(selector).first
    await element.click()
    await asyncio.sleep(random.uniform(0.2, 0.5))

    for char in text:
        await page.keyboard.type(char, delay=random.randint(50, 150))
        # 偶尔暂停一下，像人在思考
        if random.random() < 0.1:
            await asyncio.sleep(random.uniform(0.3, 0.8))


async def simulate_scroll(page, distance: int = 300):
    """模拟人类滚动（带惯性）"""
    steps = random.randint(5, 15)
    for i in range(steps):
        delta = distance / steps * (1 - i / steps)  # 逐渐减速
        await page.mouse.wheel(0, delta)
        await asyncio.sleep(random.uniform(0.02, 0.08))
