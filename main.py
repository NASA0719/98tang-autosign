#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
98tang-autosign - 主入口文件

98堂论坛自动签到系统，专门为98堂论坛优化的自动签到工具。

特性:
- 智能浏览器自动化
- 拟人化操作行为
- 灵活的配置管理
- 详细的日志记录
- 模块化架构设计

使用方法:
    python main.py [--debug]

参数:
    --debug: 启用调试模式，输出详细日志信息
"""

import sys
import argparse
import signal
import atexit
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.app import AutoSignApp

# 全局变量用于存储应用实例
_app_instance = None


def cleanup_handler():
    """清理处理器"""
    global _app_instance
    if _app_instance:
        try:
            print("\n\ud83e\uddf9 正在清理资源...")
            _app_instance._cleanup()
            print("✅ 资源清理完成")
        except Exception as e:
            print(f"⚠️ 清理资源时出错: {e}")


def signal_handler(signum, frame):
    """信号处理器"""
    print(f"\n\ud83d\udea8 接收到信号 {signum}，正在安全退出...")
    cleanup_handler()
    sys.exit(128 + signum)


# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
if hasattr(signal, "SIGTERM"):
    signal.signal(signal.SIGTERM, signal_handler)  # 终止信号

# 注册退出处理器
atexit.register(cleanup_handler)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="98tang-autosign - 98堂论坛自动签到系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py              # 正常模式运行
  python main.py --debug      # 调试模式运行

配置文件:
  程序会自动读取 config.env 配置文件
  如果不存在，请复制 config.env.example 并修改配置
        """,
    )

    parser.add_argument(
        "--debug", action="store_true", help="启用调试模式（输出详细日志信息）"
    )

    parser.add_argument(
        "--config", default="config.env", help="指定配置文件路径（默认: config.env）"
    )

    args = parser.parse_args()

    # 检查配置文件是否存在
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {args.config}")
        print("请复制 config.env.example 为 config.env 并填写配置")
        return 1

    print("=" * 50)
    print("🤖 98tang-autosign")
    print("=" * 50)

    if args.debug:
        print("🔍 运行在调试模式")

    try:
        # 创建应用实例
        global _app_instance
        _app_instance = AutoSignApp(config_file=args.config, debug_mode=args.debug)
        app = _app_instance

        # 运行应用
        success = app.run()

        if success:
            print("✅ 程序执行完成")
            # 清理全局引用
            _app_instance = None
            return 0
        else:
            print("❌ 程序执行失败")
            # 清理全局引用
            _app_instance = None
            return 1

    except KeyboardInterrupt:
        print("\n⚠️  程序被用户中断")
        # 清理全局引用
        _app_instance = None
        return 130

    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
        if args.debug:
            import traceback

            print("详细错误信息:")
            traceback.print_exc()
        # 清理全局引用
        _app_instance = None
        return 1


if __name__ == "__main__":
    sys.exit(main())
