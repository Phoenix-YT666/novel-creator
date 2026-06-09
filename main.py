"""
📖 AI小说创作助手 - 主入口
AI-powered novel writing assistant with outline, drafting, characters and publishing support.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from novel_creator.engine import NovelEngine


def main():
    parser = argparse.ArgumentParser(
        description="📖 AI小说创作助手 - Novel Creator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例 (Examples):
  # 创建新小说项目
  python main.py new "修真世界" --genre 玄幻

  # 生成大纲
  python main.py outline --project my_novel --chapters 30

  # 开始写作
  python main.py write --project my_novel --chapter 1

  # 角色设计
  python main.py character create --project my_novel --name 萧炎

  # 世界观构建
  python main.py worldbuilding --project my_novel

  # 导出作品
  python main.py export --project my_novel --format epub

  # 交互式写作
  python main.py interactive
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # === new: 创建新项目 ===
    new_parser = subparsers.add_parser("new", help="创建新的小说项目")
    new_parser.add_argument("title", help="小说标题")
    new_parser.add_argument("--genre", default="奇幻",
                          choices=["玄幻", "科幻", "武侠", "都市", "言情", "悬疑",
                                   "历史", "末日", "网游", "轻小说", "恐怖", "推理",
                                   "fantasy", "sci-fi", "romance", "mystery", "horror"])
    new_parser.add_argument("--type", default="novel",
                          choices=["short_story", "novella", "novel", "web_novel", "light_novel"])
    new_parser.add_argument("--language", default="zh", choices=["zh", "en", "ja"])
    new_parser.add_argument("--template", default="standard", help="项目模板")

    # === outline: 大纲管理 ===
    outline_parser = subparsers.add_parser("outline", help="生成和管理大纲")
    outline_parser.add_argument("action", nargs="?", default="generate",
                              choices=["generate", "view", "edit", "reorder"])
    outline_parser.add_argument("--project", required=True, help="项目名称")
    outline_parser.add_argument("--chapters", type=int, default=20, help="章节数")
    outline_parser.add_argument("--style", default="three_act",
                              choices=["three_act", "hero_journey", "four_act", "web_serial", "free"])
    outline_parser.add_argument("--detail", default="medium",
                              choices=["brief", "medium", "detailed"])

    # === write: 写作 ===
    write_parser = subparsers.add_parser("write", help="AI辅助写作")
    write_parser.add_argument("action", nargs="?", default="chapter",
                            choices=["chapter", "scene", "continue", "rewrite", "expand", "polish"])
    write_parser.add_argument("--project", required=True)
    write_parser.add_argument("--chapter", type=int, help="章节号")
    write_parser.add_argument("--scene", help="场景描述")
    write_parser.add_argument("--style", help="写作风格参考")
    write_parser.add_argument("--tone", default="auto",
                            choices=["auto", "serious", "humorous", "dark", "light", "suspenseful",
                                     "romantic", "epic", "casual"])
    write_parser.add_argument("--length", default="medium",
                            choices=["short", "medium", "long", "ultra_long"])
    write_parser.add_argument("--pov", default="third_person",
                            choices=["first_person", "third_person", "third_omniscient", "second_person"])
    write_parser.add_argument("--temperature", type=float, default=0.8, help="创意度 (0-1)")

    # === character: 角色管理 ===
    char_parser = subparsers.add_parser("character", help="角色设计与管理")
    char_parser.add_argument("action", choices=["create", "list", "edit", "delete", "relationship",
                                               "arc", "dialogue"])
    char_parser.add_argument("--project", required=True)
    char_parser.add_argument("--name", help="角色名称")
    char_parser.add_argument("--role", choices=["protagonist", "antagonist", "supporting",
                                               "mentor", "love_interest", "comic_relief", "custom"])
    char_parser.add_argument("--archetype", help="角色原型: hero,anti_hero,trickster,sage,etc")
    char_parser.add_argument("--background", help="角色背景描述")
    char_parser.add_argument("--traits", help="性格特征(逗号分隔)")

    # === worldbuilding: 世界观构建 ===
    world_parser = subparsers.add_parser("worldbuilding", help="世界观构建")
    world_parser.add_argument("action", nargs="?", default="generate",
                            choices=["generate", "view", "edit", "add_location", "add_faction",
                                     "add_magic_system", "add_technology", "timeline"])
    world_parser.add_argument("--project", required=True)
    world_parser.add_argument("--theme", help="世界主题描述")
    world_parser.add_argument("--era", help="时代背景")

    # === export: 导出 ===
    export_parser = subparsers.add_parser("export", help="导出作品")
    export_parser.add_argument("--project", required=True)
    export_parser.add_argument("--format", default="epub",
                             choices=["epub", "pdf", "txt", "docx", "html", "md", "json"])
    export_parser.add_argument("-o", "--output", help="输出路径")
    export_parser.add_argument("--cover", help="封面图片路径")
    export_parser.add_argument("--publish", action="store_true", help="发布到支持的平台")

    # === interactive: 交互式写作模式 ===
    inter_parser = subparsers.add_parser("interactive", help="进入交互式写作模式")
    inter_parser.add_argument("--project", help="已有项目名称")

    # === analyze: 分析已有作品 ===
    analyze_parser = subparsers.add_parser("analyze", help="分析作品质量")
    analyze_parser.add_argument("--project", required=True)
    analyze_parser.add_argument("--aspect", default="all",
                              choices=["all", "pacing", "characters", "dialogue", "plot", "style", "grammar"])

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    engine = NovelEngine()

    if args.command == "new":
        print(f"📖 创建新小说项目: 《{args.title}》")
        result = engine.create_project(
            title=args.title,
            genre=args.genre,
            story_type=args.type,
            language=args.language,
            template=args.template,
        )
        print(f"✅ 项目创建成功! 路径: {result}")
        print(f"💡 下一步: python main.py outline --project {args.title}")

    elif args.command == "outline":
        result = engine.outline_action(
            action=args.action,
            project=args.project,
            chapters=args.chapters,
            style=args.style,
            detail=args.detail,
        )
        engine.print_outline(result)

    elif args.command == "write":
        print(f"✍️ AI写作中...")
        result = engine.write(
            action=args.action,
            project=args.project,
            chapter=args.chapter,
            scene=args.scene,
            style=args.style,
            tone=args.tone,
            length=args.length,
            pov=args.pov,
            temperature=args.temperature,
        )
        engine.print_writing(result)

    elif args.command == "character":
        result = engine.character_action(args)
        engine.print_character(result)

    elif args.command == "worldbuilding":
        result = engine.worldbuilding_action(args)
        engine.print_worldbuilding(result)

    elif args.command == "export":
        print(f"📦 导出作品中...")
        result = engine.export_project(
            project=args.project,
            format=args.format,
            output=args.output,
            cover=args.cover,
        )
        print(f"✅ 导出成功: {result}")

    elif args.command == "interactive":
        engine.interactive_mode(project=getattr(args, 'project', None))

    elif args.command == "analyze":
        result = engine.analyze_project(args.project, aspect=args.aspect)
        engine.print_analysis(result)


if __name__ == "__main__":
    main()
