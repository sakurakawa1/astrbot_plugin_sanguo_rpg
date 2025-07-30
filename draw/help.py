import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def draw_help_image():
    # 画布尺寸
    width, height = 800, 2400

    # 1. 创建渐变背景
    def create_vertical_gradient(w, h, top_color, bottom_color):
        base = Image.new('RGB', (w, h), top_color)
        top_r, top_g, top_b = top_color
        bot_r, bot_g, bot_b = bottom_color
        draw = ImageDraw.Draw(base)
        for y in range(h):
            ratio = y / (h - 1)
            r = int(top_r + (bot_r - top_r) * ratio)
            g = int(top_g + (bot_g - top_g) * ratio)
            b = int(top_b + (bot_b - top_b) * ratio)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
        return base

    bg_top = (255, 235, 205)  # 暖黄色
    bg_bot = (255, 255, 255)  # 白
    image = create_vertical_gradient(width, height, bg_top, bg_bot)
    draw = ImageDraw.Draw(image)

    # 2. 加载字体
    def load_font(name, size):
        path = os.path.join(os.path.dirname(__file__), "resource", name)
        try:
            return ImageFont.truetype(path, size)
        except:
            return ImageFont.load_default()

    title_font = load_font("DouyinSansBold.otf", 32)
    subtitle_font = load_font("DouyinSansBold.otf", 28)
    section_font = load_font("DouyinSansBold.otf", 24)
    cmd_font = load_font("DouyinSansBold.otf", 18)
    desc_font = load_font("DouyinSansBold.otf", 16)

    # 3. 颜色定义
    title_color = (139, 69, 19)  # 棕色
    cmd_color = (40, 40, 40)
    card_bg = (255, 255, 255)
    line_color = (200, 200, 200)
    shadow_color = (0, 0, 0, 80)

    # 4. 获取文本尺寸的辅助函数
    def get_text_size(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    # 5. 处理logo背景色的函数
    def replace_white_background(img, new_bg_color=bg_top, threshold=240):
        """将图片的白色背景替换为指定颜色"""
        img = img.convert("RGBA")
        data = img.getdata()
        new_data = []

        for item in data:
            r, g, b = item[:3]
            alpha = item[3] if len(item) > 3 else 255

            # 如果像素接近白色，就替换为新背景色
            if r >= threshold and g >= threshold and b >= threshold:
                new_data.append((*new_bg_color, alpha))
            else:
                new_data.append(item)

        img.putdata(new_data)
        return img

    # 6. 绘制 Logo 和 标题
    logo_size = 160
    logo_x = 30
    logo_y = 25

    try:
        logo = Image.open(os.path.join(os.path.dirname(__file__), "resource", "astrbot_logo.jpg"))

        # 将白色背景替换为与画布背景一致的颜色
        logo = replace_white_background(logo, bg_top)

        # 保持纵横比调整大小
        logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

        # 创建圆角遮罩
        mask = Image.new("L", logo.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, logo.size[0], logo.size[1]], 20, fill=255)

        # 应用圆角遮罩
        output = Image.new("RGBA", logo.size, (0, 0, 0, 0))
        output.paste(logo, (0, 0))
        output.putalpha(mask)

        # 贴到主图上
        image.paste(output, (logo_x, logo_y), output)

    except Exception as e:
        print(f"Logo加载失败: {e}")
        # 如果没有logo文件，绘制一个圆角占位符
        draw.rounded_rectangle((logo_x, logo_y, logo_x + logo_size, logo_y + logo_size),
                               20, fill=bg_top, outline=(180, 180, 180), width=2)
        draw.text((logo_x + logo_size // 2, logo_y + logo_size // 2), "三国",
                  fill=(120, 120, 120), font=subtitle_font, anchor="mm")

    # 主标题居中显示，调整位置避免与logo重叠
    title_y = logo_y + logo_size // 2
    draw.text((width // 2, title_y), "三国文字RPG 帮助", fill=title_color, font=title_font, anchor="mm")

    # 7. 圆角矩形＋阴影 helper
    def draw_card(x0, y0, x1, y1, radius=12):
        # 简化阴影效果
        shadow_offset = 3
        # 绘制阴影
        draw.rounded_rectangle([x0 + shadow_offset, y0 + shadow_offset, x1 + shadow_offset, y1 + shadow_offset],
                               radius, fill=(220, 220, 220))
        # 白色卡片
        draw.rounded_rectangle([x0, y0, x1, y1], radius, fill=card_bg, outline=line_color, width=1)

    # 8. 绘制章节和命令
    def draw_section(title, cmds, y_start, cols=3):
        # 章节标题左对齐
        title_x = 50
        draw.text((title_x, y_start), title, fill=title_color, font=section_font, anchor="lm")
        w, h = get_text_size(title, section_font)

        # 标题下划线
        underline_y = y_start + h // 2 + 8
        draw.line([(title_x, underline_y), (title_x + w, underline_y)],
                  fill=title_color, width=3)

        y = y_start + h // 2 + 25

        card_w = (width - 60) // cols
        card_h = 85
        pad = 15

        for idx, (cmd, desc) in enumerate(cmds):
            col = idx % cols
            row = idx // cols
            x0 = 30 + col * card_w
            y0 = y + row * (card_h + pad)
            x1 = x0 + card_w - 10
            y1 = y0 + card_h

            draw_card(x0, y0, x1, y1)

            # 文本居中显示
            cx = (x0 + x1) // 2
            # 命令文本
            draw.text((cx, y0 + 18), cmd, fill=cmd_color, font=cmd_font, anchor="mt")
            # 描述文本 - 支持多行
            desc_lines = desc.split('\n') if '\n' in desc else [desc]
            for i, line in enumerate(desc_lines):
                draw.text((cx, y0 + 45 + i * 18), line, fill=(100, 100, 100), font=desc_font, anchor="mt")

        rows = math.ceil(len(cmds) / cols)
        return y + rows * (card_h + pad) + 35

    # 9. 各段命令数据
    basic = [
        ("注册", "注册用户"),
        ("签到", "每日签到"),
        ("我的信息", "查看个人\n信息"),
        ("三国帮助", "显示帮助\n信息")
    ]

    general = [
        ("我的武将", "查看拥有\n的武将"),
        ("招募", "招募新武将\n(消耗元宝)"),
        ("闯关", "派遣武将\n进行闯关")
    ]

    game_features = [
        ("🏆 武将系统", "收集三国名将\n包含蜀魏吴群四大阵营"),
        ("⭐ 稀有度", "武将分2-5星稀有度\n高星武将属性更强"),
        ("💎 招募", "消耗元宝招募武将\n有概率获得传说武将"),
        ("⚔️ 闯关", "派遣武将挑战关卡\n获得铜钱和经验奖励"),
        ("🎯 战力计算", "根据武将四维属性\n计算队伍总战力"),
        ("⏰ 冷却机制", "招募和闯关都有\n冷却时间限制")
    ]

    # 10. 绘制各个部分 - 调整起始位置给logo留足空间
    y0 = logo_y + logo_size + 30
    y0 = draw_section("⚡ 基础功能", basic, y0, cols=2)
    y0 = draw_section("🏺 武将系统", general, y0, cols=3)
    y0 = draw_section("🎮 游戏特色", game_features, y0, cols=2)

    # 添加玩法说明
    guide_y = y0 + 20
    guide_title = "🎯 游戏玩法说明"
    draw.text((50, guide_y), guide_title, fill=title_color, font=section_font, anchor="lm")
    w, h = get_text_size(guide_title, section_font)
    underline_y = guide_y + h // 2 + 8
    draw.line([(50, underline_y), (50 + w, underline_y)], fill=title_color, width=3)

    # 玩法说明文本
    guide_text = [
        "1. 首先使用 /注册 命令注册账户，获得初始铜钱和元宝",
        "2. 使用 /招募 命令消耗元宝招募武将，有机会获得传说武将",
        "3. 使用 /我的武将 查看已拥有的武将及其属性",
        "4. 使用 /闯关 派遣武将挑战关卡，获得铜钱奖励",
        "5. 使用 /签到 每日获得资源，不要忘记哦！",
        "",
        "💡 提示：武将等级会影响属性，高等级武将战力更强！",
        "🎲 概率：5星(1%), 4星(9%), 3星(20%), 2星(70%)"
    ]

    text_y = guide_y + h // 2 + 35
    for line in guide_text:
        if line:  # 非空行
            draw.text((70, text_y), line, fill=(60, 60, 60), font=desc_font, anchor="lm")
        text_y += 22

    # 添加底部信息
    footer_y = text_y + 20
    draw.text((width // 2, footer_y), "🏛️ 纵横三国，招贤纳士，成就霸业！",
              fill=(120, 120, 120), font=desc_font, anchor="mm")

    # 11. 裁剪图像到实际内容高度并保存
    final_height = footer_y + 30
    image = image.crop((0, 0, width, min(final_height, height)))

    output_path = "sanguo_rpg_help.png"
    image.save(output_path, quality=95)
    return output_path
