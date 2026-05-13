import json
import os

class GuidelineManager:
    def __init__(self, guidelines_path):
        self.guidelines_path = guidelines_path
        self.guidelines = self._load_guidelines()

    def _load_guidelines(self):
        """
        从 JSON 文件加载设计准则。
        期望的结构:
        [
            {
                "一级标题": "Foundations（基础）",
                "二级标题": "Accessibility",
                "三级标题": "Color & contrast（颜色与对比度）",
                "列表头": "目的与总原则",
                "列表内容": "...",
                "标注": "知识型"
            },
            ...
        ]
        """
        if not os.path.exists(self.guidelines_path):
            raise FileNotFoundError(f"未找到准则文件: {self.guidelines_path}")
        
        try:
            with open(self.guidelines_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise ValueError("准则文件不是有效的 JSON 格式。")

    def get_all_guidelines(self):
        return self.guidelines
    
    def get_guidelines_as_text(self):
        """
        将所有准则格式化为字符串，用于 Prompt 输入。
        """
        text = "设计准则库 (Design Guidelines Library):\n"
        for i, g in enumerate(self.guidelines):
            # 组合标题信息
            titles = f"{g.get('一级标题', '')} > {g.get('二级标题', '')} > {g.get('三级标题', '')}"
            header = g.get('列表头', '')
            content = g.get('列表内容', '')
            note = g.get('标注', '')
            
            # 格式化单条准则
            text += f"[{i+1}] {titles}\n"
            if header:
                text += f"    主题: {header}\n"
            text += f"    内容: {content}\n"
            if note:
                text += f"    类型: {note}\n"
            text += "\n"
        return text
