"""
AI 写作引擎 (AI Writer)
通过 Claude API 实现真实的小说内容生成。
也支持离线模式下的启发式写作。
"""

import os
from typing import Dict, List, Optional
from datetime import datetime


class AIWriter:
    """AI 写作引擎 — 通过 Claude API 生成小说内容"""

    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.model = model
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self._client = None

    @property
    def client(self):
        """延迟初始化 Anthropic 客户端"""
        if self._client is None and self.api_key:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                pass
        return self._client

    @property
    def ai_available(self) -> bool:
        return self.client is not None

    def write_chapter(self, context: Dict, chapter_num: int,
                     tone: str = "auto", length: str = "medium",
                     pov: str = "third_person",
                     temperature: float = 0.8) -> str:
        """撰写完整章节

        Args:
            context: 项目上下文 (包含 title, genre, outline, characters, previous_chapters)
            chapter_num: 章节号
            tone: 语气
            length: 长度 (short=~1000字, medium=~3000字, long=~5000字, ultra_long=~10000字)
            pov: 视角
            temperature: 创意度 (0-1, 越高越有创意)

        Returns:
            章节正文 (Markdown 格式)
        """
        word_target = {
            "short": 1000, "medium": 3000, "long": 5000, "ultra_long": 10000
        }.get(length, 3000)

        system_prompt = self._build_system_prompt(context, tone, pov)

        user_prompt = self._build_chapter_prompt(context, chapter_num, word_target)

        if self.ai_available:
            return self._call_claude(system_prompt, user_prompt, temperature)
        else:
            return self._offline_chapter(context, chapter_num, word_target)

    def write_scene(self, context: Dict, scene_desc: str,
                   tone: str = "auto", length: str = "medium") -> str:
        """撰写一个场景"""
        word_target = {"short": 500, "medium": 1500, "long": 3000}.get(length, 1500)

        system_prompt = self._build_system_prompt(context, tone,
                                                  context.get("pov", "third_person"))
        user_prompt = f"""请撰写以下场景：

{scene_desc}

要求：
- 约 {word_target} 字
- 细腻的环境描写和人物刻画
- 自然流畅的对话
- 与前后章节情节衔接
- 使用中文写作"""

        if self.ai_available:
            return self._call_claude(system_prompt, user_prompt, 0.8)
        else:
            return self._offline_scene(scene_desc, word_target)

    def continue_writing(self, context: Dict, last_paragraph: str,
                        tone: str = "auto") -> str:
        """从上次中断处继续写作"""
        system_prompt = self._build_system_prompt(context, tone,
                                                  context.get("pov", "third_person"))
        user_prompt = f"""请从以下位置继续写作，保持连贯：

...{last_paragraph[-500:]}

请续写约 1500 字，保持相同的叙事风格和节奏。使用中文写作。"""

        if self.ai_available:
            return self._call_claude(system_prompt, user_prompt, 0.8)
        else:
            return self._offline_scene("继续写作", 1500)

    def rewrite_passage(self, passage: str, instructions: str,
                       tone: str = "auto") -> str:
        """重写选段"""
        system_prompt = f"你是一位专业的小说编辑。请按照以下指示重写文本。语气: {tone}"
        user_prompt = f"""原文：
---
{passage}
---

重写指示: {instructions}

请输出重写后的版本，保持原意但改进表达。"""

        if self.ai_available:
            return self._call_claude(system_prompt, user_prompt, 0.7)
        else:
            return f"[重写版本] {passage}"

    def expand_description(self, passage: str, focus: str) -> str:
        """扩展描写"""
        system_prompt = "你是一位擅长细腻描写的作家。请在不改变情节的前提下扩展描写。"
        user_prompt = f"""原文：
---
{passage}
---

请重点扩展"{focus}"方面的描写，增加约 500 字的细节。"""

        if self.ai_available:
            return self._call_claude(system_prompt, user_prompt, 0.7)
        else:
            return passage

    def polish_text(self, passage: str) -> str:
        """润色文字"""
        system_prompt = "你是一位资深文字编辑。请润色以下文本，使其更流畅优美，但不改变原意和风格。"
        user_prompt = f"请润色:\n\n{passage}"

        if self.ai_available:
            return self._call_claude(system_prompt, user_prompt, 0.5)
        else:
            return passage

    def brainstorm_ideas(self, genre: str, theme: str = "") -> List[str]:
        """生成故事创意"""
        user_prompt = f"请为{genre}类型的小说生成5个创新故事创意。{theme if theme else ''}"
        if self.ai_available:
            system_prompt = "你是一位创意写作顾问。请返回5个独特的故事创意，每个一两句话。"
            result = self._call_claude(system_prompt, user_prompt, 0.9)
            return [line.strip("- ") for line in result.split("\n") if line.strip().startswith(("-", "1", "2", "3", "4", "5"))]
        else:
            return [
                "一个普通人在平凡生活中发现自己拥有改变现实的能力，但每次使用都有代价",
                "在AI全面接管社会后，最后一个坚持人类创作的小说家面临抉择",
                "时间旅行者回到过去不是为了改变历史，而是为了收集失传的故事",
                "两个平行世界的同一人通过梦境交换人生经历，发现彼此世界的秘密",
                "一个被遗忘的神明在现代都市中寻找最后一位信徒",
            ]

    # ====== 内部方法 ======

    def _build_system_prompt(self, context: Dict, tone: str, pov: str) -> str:
        """构建系统 prompt"""
        title = context.get("title", "未命名作品")
        genre = context.get("genre", "小说")
        language = context.get("language", "zh")

        pov_desc = {
            "first_person": "第一人称叙事 ('我')",
            "third_person": "第三人称有限视角",
            "third_omniscient": "第三人称全知视角",
            "second_person": "第二人称叙事 ('你')",
        }.get(pov, "第三人称有限视角")

        tone_desc = {
            "auto": "根据情节自然变化",
            "serious": "严肃沉重",
            "humorous": "幽默风趣",
            "dark": "暗黑压抑",
            "light": "轻松温暖",
            "suspenseful": "悬疑紧张",
            "romantic": "浪漫温情",
            "epic": "史诗宏大",
            "casual": "随意自然",
        }.get(tone, "根据情节自然变化")

        return f"""你是一位专业的{genre}小说作家。

当前作品: 《{title}》
类型: {genre}
叙事视角: {pov_desc}
语气风格: {tone_desc}
写作语言: {'中文' if language == 'zh' else 'English' if language == 'en' else '日本語'}

写作要求:
1. 生动的描写 — 让读者身临其境
2. 自然的对话 — 符合角色性格
3. 紧凑的节奏 — 张弛有度
4. 合理的情节 — 前后逻辑自洽
5. 独特的文风 — 具有辨识度
6. 使用 Markdown 格式 — # 章标题, ## 场景, *** 分隔线"""

    def _build_chapter_prompt(self, context: Dict, chapter_num: int,
                             word_target: int) -> str:
        """构建章节写作 prompt"""
        title = context.get("title", "")
        outline = context.get("outline", {})
        characters = context.get("characters", [])

        # 查找该章节的大纲
        chapter_plan = ""
        for act in outline.get("acts", []):
            for ch in act.get("chapters", []):
                if ch.get("number") == chapter_num:
                    chapter_plan = f"章节标题: {ch.get('title', '')}\n摘要: {ch.get('summary', '')}"
                    break

        # 角色信息
        chars_info = ""
        for c in characters[:5]:
            chars_info += f"\n- {c.get('name', '?')}: {c.get('role', '')} - {c.get('background', '')}"

        # 前文摘要
        previous_summary = context.get("previous_summary", "")

        return f"""请撰写《{title}》的第 {chapter_num} 章。

{chapter_plan if chapter_plan else f"请根据故事发展自然推进第{chapter_num}章的情节。"}

角色信息:{chars_info}

前文摘要: {previous_summary if previous_summary else "这是开头章节，无需前文。"}

写作要求:
- 约 {word_target} 字
- 包含完整的场景、对白和描写
- 章节结尾留下悬念或自然过渡
- 使用 Markdown 格式
- 用中文写作"""

    def _call_claude(self, system_prompt: str, user_prompt: str,
                    temperature: float = 0.8) -> str:
        """实际调用 Claude API"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text
        except Exception as e:
            print(f"  ⚠️ Claude API 调用失败: {e}")
            return self._offline_chapter({}, 1, 3000)

    def _offline_chapter(self, context: Dict, chapter_num: int,
                        word_target: int) -> str:
        """离线模式下的章节模板（当 AI API 不可用时）"""
        title = context.get("title", "未命名作品")
        return f"""# 第{chapter_num}章

夜幕降临，星光点点洒落在古老的街道上。

--- (此处为第{chapter_num}章的正文内容)

*此章节由 AI 写作引擎在离线模式下生成模板。配置 ANTHROPIC_API_KEY 环境变量以启用 AI 写作。*

> 📝 写作提示: 设置环境变量 `ANTHROPIC_API_KEY` 后运行，即可通过 Claude API 进行真正的 AI 创作。
> 参考: https://docs.anthropic.com/zh-CN/docs/initial-setup
"""

    def _offline_scene(self, scene_desc: str, word_target: int) -> str:
        """离线场景模板"""
        return f"""## {scene_desc[:50]}

{scene_desc}

*此场景需要 AI API 来完成。请配置 ANTHROPIC_API_KEY 环境变量。*
"""
