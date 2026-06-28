"""
淘宝页面选择器集中管理
当淘宝页面结构变化时, 只需修改此文件
每个选择器是一个列表, 按优先级排列, 依次尝试
"""

# ==================== 商品详情页 ====================

# API端点模式
DETAIL_API_PATTERN = "mtop.taobao.detail.getdetail"
DESC_API_PATTERN = "mtop.taobao.detail.getdesc"

# 标题
TITLE_SELECTORS = [
    '[class*="mainTitle"]',
    '[class*="ItemHeader--mainTitle"]',
    '[class*="ItemHeader"] [class*="title"]',
    'h1[class*="title"]',
    '.tb-main-title',
    '[data-testid*="title"]',
    'h1',
]

# 价格
PRICE_SELECTORS = [
    '[class*="Price--priceText"]',
    '[class*="priceText"]',
    '[class*="Price"] [class*="text"]',
    '.tb-rmb-num',
    '[class*="price"] span[class*="text"]',
    'span[class*="Price"]',
    '[class*="price--current"]',
    '[class*="PriceBox"] span',
]

# 主图
MAIN_IMAGE_SELECTORS = [
    '[class*="PicGallery--thumbnails"] img',
    '[class*="thumbnail"] img',
    '#J_UlThumb img',
    '[class*="slider"] img',
    '[class*="PicGallery"] img',
    '[class*="main-pic"] img',
    '[class*="gallery"] img',
]

# SKU面板
SKU_PANEL_SELECTORS = [
    '[class*="SkuContent"]',
    '[class*="sku-wrapper"]',
    '.tb-sku',
    '[class*="sku"]',
]

# 属性面板
ATTRIBUTE_SELECTORS = [
    '[class*="Attr--attrs"] li',
    '[class*="attributes"] li',
    '#attributes li',
    '[class*="attr"] tr',
]

# 店铺名
SHOP_NAME_SELECTORS = [
    '[class*="ShopHeader--title"]',
    '[class*="shopTitle"]',
    '[class*="ShopHeader"] [class*="name"]',
    '.tb-shop-name a',
    '[class*="shop-name"]',
    '[class*="shopTitle"] a',
    '[class*="store"] [class*="name"]',
]

# 描述
DESCRIPTION_SELECTORS = [
    '[class*="desc"]',
    '[class*="RichContent"]',
    '#description',
    '[class*="content-detail"]',
]

# ==================== 卖家发布页 ====================

# 标题输入框
UPLOAD_TITLE_SELECTORS = [
    'textarea[name="title"]',
    'input[name="title"]',
    '[class*="title-input"] textarea',
    '[class*="title"] input',
]

# 价格输入框
UPLOAD_PRICE_SELECTORS = [
    'input[name="price"]',
    '[class*="price"] input[type="text"]',
    '[class*="PriceInput"] input',
]

# 图片上传区域
UPLOAD_IMAGE_SELECTORS = [
    'input[type="file"][accept*="image"]',
    '[class*="image-upload"] input[type="file"]',
    '[class*="upload"] input[type="file"]',
]

# 类目搜索框
UPLOAD_CATEGORY_SEARCH_SELECTORS = [
    'input[placeholder*="类目"]',
    'input[placeholder*="搜索"]',
    '[class*="category-search"] input',
    '[class*="CategorySearch"] input',
]

# 发布按钮
SUBMIT_BUTTON_SELECTORS = [
    'button:has-text("发布")',
    'button:has-text("提交")',
    '[class*="submit"] button',
    '[class*="publish"] button',
]

# ==================== 登录检测 ====================

# 已登录状态标识
LOGIN_CHECK_SELECTORS = [
    '.site-nav-user',
    '.J_UserName',
    '[class*="site-nav-user"]',
    '[class*="userName"]',
    '[class*="NickName"]',
]

# 登录页面标识
LOGIN_PAGE_SELECTORS = [
    'input[name="TPL_username"]',
    'input[id="fm-login-id"]',
    '[class*="login-form"]',
    '#login',
]
