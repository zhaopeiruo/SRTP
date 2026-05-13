import argparse
import os
from src.guideline_manager import GuidelineManager
from src.evaluator import UIEvaluator
from src.config import Config

def main():
    parser = argparse.ArgumentParser(description="使用 VLLM 进行 UI 评估")
    parser.add_argument("--image", required=True, help="UI 图片文件的路径")
    parser.add_argument("--structure", help="UI 结构文件的路径 (可选, 支持 .json 或 .html)")
    parser.add_argument("--goal", help="评估目标 (例如：'视觉层级')。如果不提供，将在运行时询问。")
    parser.add_argument("--guidelines", default="data/guidelines.json", help="准则库 JSON 文件的路径")
    
    args = parser.parse_args()

    # 验证输入
    if not os.path.exists(args.image):
        print(f"错误: 未找到图片文件 {args.image}")
        return
    
    if args.structure and not os.path.exists(args.structure):
        print(f"错误: 未找到 UI 结构文件 {args.structure}")
        return

    # 获取评估目标
    goal = args.goal
    if not goal:
        try:
            goal = input("请输入评估目标 (例如：'视觉层级'): ").strip()
        except KeyboardInterrupt:
            print("\n操作已取消")
            return
        
    if not goal:
        print("错误: 必须提供评估目标")
        return

    try:
        # 初始化组件
        guideline_manager = GuidelineManager(args.guidelines)
        evaluator = UIEvaluator(guideline_manager)

        # 运行评估
        result = evaluator.evaluate(args.image, args.structure, goal)
        
        print("\n" + "="*50)
        print("评估结果")
        print("="*50)
        print(result)
        
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
