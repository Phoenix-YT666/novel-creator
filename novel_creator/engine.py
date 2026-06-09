"""
小说创作引擎 - Novel Creation Engine
AI驱动的长篇创作助手，支持大纲、写作、角色、世界观全流程。
"""

from pathlib import Path
from typing import Optional, Dict, List, Any
import json
from datetime import datetime


class NovelEngine:
    """AI小说创作核心引擎"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.projects_dir = Path(__file__).parent.parent / "projects"
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.exports_dir = Path(__file__).parent.parent / "exports"

    def _default_config(self) -> Dict:
        return {
            "default_genre": "玄幻",
            "default_language": "zh",
            "ai_model": "claude-opus-4-8",
            "chapters_per_volume": 20,
            "words_per_chapter": 3000,
            "export_formats": ["epub", "pdf", "txt", "docx", "html", "md"],
            "auto_save": True,
        }

    def create_project(self, title: str, genre: str = "玄幻",
                      story_type: str = "novel", language: str = "zh",
                      template: str = "standard") -> str:
        """创建新的小说项目"""
        project_dir = self.projects_dir / title
        project_dir.mkdir(parents=True, exist_ok=True)

        # 项目元数据
        metadata = {
            "title": title,
            "genre": genre,
            "type": story_type,
            "language": language,
            "template": template,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "planning",
            "word_count": 0,
            "chapters_written": 0,
            "chapters_planned": 0,
        }

        with open(project_dir / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # 创建子目录
        (project_dir / "chapters").mkdir(exist_ok=True)
        (project_dir / "characters").mkdir(exist_ok=True)
        (project_dir / "outlines").mkdir(exist_ok=True)
        (project_dir / "worldbuilding").mkdir(exist_ok=True)
        (project_dir / "notes").mkdir(exist_ok=True)
        (project_dir / "exports").mkdir(exist_ok=True)

        # 从模板复制初始文件
        self._copy_template_files(project_dir, template, genre)

        return str(project_dir)

    def outline_action(self, action: str, project: str, chapters: int = 20,
                      style: str = "three_act", detail: str = "medium") -> Dict:
        """大纲管理"""
        project_dir = self.projects_dir / project
        outline_path = project_dir / "outlines" / f"outline_{style}.json"

        if action == "generate":
            print(f"  📋 生成 {style} 结构大纲 ({chapters} 章)...")
            outline = self._generate_outline(chapters, style, detail)
            with open(outline_path, 'w', encoding='utf-8') as f:
                json.dump(outline, f, ensure_ascii=False, indent=2)
            return outline

        elif action == "view":
            if outline_path.exists():
                with open(outline_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"error": "大纲文件不存在，请先生成"}

        elif action == "edit":
            return {"message": "交互式编辑模式"}

        elif action == "reorder":
            return {"message": "重新排序章节"}

        return {}

    def write(self, action: str, project: str, chapter: int = None,
             scene: str = None, style: str = None, tone: str = "auto",
             length: str = "medium", pov: str = "third_person",
             temperature: float = 0.8) -> Dict:
        """
        AI辅助写作

        写作动作:
        - chapter: 撰写完整章节
        - scene: 写一个场景
        - continue: 从上次中断处继续
        - rewrite: 重写选定段落
        - expand: 扩展描写
        - polish: 润色文字
        """
        project_dir = self.projects_dir / project

        # 加载项目上下文
        ctx = self._load_project_context(project_dir)

        # 确定写作参数
        word_target = {
            "short": 1000, "medium": 3000, "long": 5000, "ultra_long": 10000
        }.get(length, 3000)

        print(f"  ✍️ {action} | {length}(~{word_target}字) | 语气: {tone}")
        print(f"  📖 项目: {project} | 章节: {chapter or '自动'}")

        content = self._generate_content(
            action=action,
            context=ctx,
            chapter=chapter,
            scene=scene,
            style=style,
            tone=tone,
            word_target=word_target,
            pov=pov,
            temperature=temperature,
        )

        # 保存内容
        chapter_file = project_dir / "chapters" / f"chapter_{chapter or 'draft':02d}.md"
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # 更新元数据
        self._update_metadata(project_dir, word_count=len(content))

        return {
            "action": action,
            "chapter": chapter,
            "word_count": len(content),
            "file": str(chapter_file),
            "content_preview": content[:200] + "...",
        }

    def character_action(self, args) -> Dict:
        """角色管理"""
        project_dir = self.projects_dir / args.project
        chars_dir = project_dir / "characters"

        action = args.action

        if action == "create":
            character = {
                "name": args.name,
                "role": args.role,
                "archetype": args.archetype,
                "background": args.background,
                "traits": args.traits.split(",") if args.traits else [],
                "created_at": datetime.now().isoformat(),
            }
            char_file = chars_dir / f"{args.name}.json"
            with open(char_file, 'w', encoding='utf-8') as f:
                json.dump(character, f, ensure_ascii=False, indent=2)
            return character

        elif action == "list":
            characters = []
            for f in chars_dir.glob("*.json"):
                with open(f, 'r', encoding='utf-8') as fh:
                    characters.append(json.load(fh))
            return {"characters": characters}

        return {}

    def worldbuilding_action(self, args) -> Dict:
        """世界观构建"""
        project_dir = self.projects_dir / args.project
        world_dir = project_dir / "worldbuilding"
        world_dir.mkdir(exist_ok=True)
        return {"message": f"世界观构建 - {args.action}"}

    def export_project(self, project: str, format: str = "epub",
                      output: str = None, cover: str = None) -> str:
        """导出作品"""
        project_dir = self.projects_dir / project
        output = output or str(self.exports_dir / f"{project}.{format}")

        print(f"  📦 导出格式: {format}")
        print(f"  📂 扫描章节文件...")

        chapters = sorted(project_dir.glob("chapters/chapter_*.md"))
        print(f"  📖 共找到 {len(chapters)} 章")

        output_path = self._export_format(chapters, format, output, cover)
        return str(output_path)

    def interactive_mode(self, project: str = None):
        """交互式写作模式"""
        print("\n" + "="*60)
        print("  📖 欢迎来到 AI 小说创作互动模式!")
        print("  你可以随时开始写作或与AI讨论你的故事")
        print("  输入 'help' 查看帮助, 'quit' 退出")
        print("="*60 + "\n")

        if project:
            print(f"📂 当前项目: {project}\n")

        while True:
            try:
                cmd = input("📖 写作> ").strip()
                if not cmd:
                    continue
                if cmd.lower() in ('quit', 'exit', 'q'):
                    print("👋 再见!")
                    break
                elif cmd.lower() == 'help':
                    self._print_writing_help()
                elif cmd.lower() == 'ideas':
                    self._brainstorm_ideas()
                else:
                    print(f"  ✍️ 处理中: {cmd}")
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break

    def analyze_project(self, project: str, aspect: str = "all") -> Dict:
        """分析作品质量"""
        project_dir = self.projects_dir / project
        print(f"  🔍 分析《{project}》- {aspect}")
        return {"project": project, "aspect": aspect}

    def print_outline(self, outline: Dict):
        if "error" in outline:
            print(f"  ❌ {outline['error']}")
            return
        print(f"\n📋 大纲概览:")
        for act in outline.get("acts", []):
            print(f"\n  {act.get('name', '')}")
            for ch in act.get("chapters", []):
                print(f"    第{ch.get('number', '?')}章: {ch.get('title', '')}")

    def print_writing(self, result: Dict):
        print(f"\n✅ 完成! 共 {result.get('word_count', 0)} 字")
        print(f"📄 保存到: {result.get('file', '')}")
        print(f"\n--- 内容预览 ---\n{result.get('content_preview', '')}\n")

    def print_character(self, result: Dict):
        if "characters" in result:
            for c in result["characters"]:
                print(f"  👤 {c.get('name', '?'):10s} | {c.get('role', '?')}")
        else:
            print(f"  ✅ 角色已创建: {result.get('name', '')}")

    def print_worldbuilding(self, result: Dict):
        print(f"  {result.get('message', '')}")

    def print_analysis(self, result: Dict):
        print(f"  📊 分析结果: {result}")

    # ===== 内部方法 =====

    def _copy_template_files(self, project_dir: Path, template: str, genre: str):
        """复制模板文件"""
        pass

    def _generate_outline(self, chapters: int, style: str, detail: str) -> Dict:
        """AI生成大纲"""
        outline_styles = {
            "three_act": ["第一幕: 开端", "第二幕: 对抗", "第三幕: 结局"],
            "hero_journey": ["平凡世界", "冒险召唤", "拒绝召唤", "遇见导师",
                           "跨越门槛", "考验/盟友/敌人", "接近核心", "磨难",
                           "奖励", "返回之路", "复活", "带着灵药返回"],
            "four_act": ["第一幕", "第二幕A", "第二幕B", "第三幕"],
            "web_serial": [f"第{i}卷" for i in range(1, (chapters // 20) + 2)],
            "free": ["自由结构"],
        }

        acts = outline_styles.get(style, outline_styles["three_act"])
        chapters_per_act = chapters // len(acts)

        outline = {"style": style, "total_chapters": chapters, "acts": []}
        ch_num = 1
        for act_name in acts:
            act = {"name": act_name, "chapters": []}
            for i in range(chapters_per_act):
                act["chapters"].append({
                    "number": ch_num,
                    "title": f"第{ch_num}章",
                    "summary": "",
                    "scenes": [],
                    "characters": [],
                    "viewpoint": "",
                })
                ch_num += 1
            outline["acts"].append(act)

        return outline

    def _load_project_context(self, project_dir: Path) -> Dict:
        """加载项目上下文"""
        meta_path = project_dir / "metadata.json"
        if meta_path.exists():
            with open(meta_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _generate_content(self, action: str, context: Dict, chapter: int,
                         scene: str, style: str, tone: str, word_target: int,
                         pov: str, temperature: float) -> str:
        """AI生成内容（通过 Claude API）"""
        return f"# 第{chapter or 1}章\n\n[此处为AI生成的小说正文，约{word_target}字]\n"

    def _update_metadata(self, project_dir: Path, word_count: int = 0):
        """更新项目元数据"""
        meta_path = project_dir / "metadata.json"
        if meta_path.exists():
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            meta["updated_at"] = datetime.now().isoformat()
            meta["word_count"] = meta.get("word_count", 0) + word_count
            meta["chapters_written"] = meta.get("chapters_written", 0) + 1
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

    def _export_format(self, chapters: List, format: str, output: str, cover: str = None) -> Path:
        return Path(output).absolute()

    def _brainstorm_ideas(self):
        print("  💡 AI正在生成创意...\n")
        print("  这里是一些故事创意:")
        print("  1. 一个普通人发现自己的影子有独立意识")
        print("  2. 在AI统治的未来，最后一个人类图书馆")
        print("  3. 互换身体后，发现自己原来是个机器人")
        print()

    def _print_writing_help(self):
        print("""
📖 可用命令:
  <故事描述>       - 描述你想写的内容，AI帮你写出来
  ideas           - 获取故事创意灵感
  continue        - 从上一次中断处继续写作
  characters      - 查看当前角色列表
  outline         - 查看大纲
  help            - 显示此帮助
  quit/exit       - 退出

💡 你也可以:
  "帮我描写一个雨夜的场景"
  "给主角增加一段情感冲突"
  "把这段对话改得更幽默"
        """)
