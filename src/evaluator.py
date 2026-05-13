import json
import os
from src.llm_client import LLMClient
from src.guideline_manager import GuidelineManager

class UIEvaluator:
    def __init__(self, guideline_manager: GuidelineManager):
        self.llm_client = LLMClient()
        self.guideline_manager = guideline_manager

    def evaluate(self, image_path, structure_path, goal):
        """
        协调评估流程。
        """
        print(f"开始评估任务，目标: {goal}")

        # 1. 将目标转化为具体指标
        metrics = self._translate_goal_to_metrics(goal)
        print(f"推导出的评估指标: {metrics}")

        # 2. 检索相关准则
        selected_guidelines = self._retrieve_guidelines(goal, metrics)
        print(f"筛选出的相关准则: {selected_guidelines}")

        # 3. 评估 UI
        evaluation_result = self._evaluate_ui(image_path, structure_path, goal, selected_guidelines)
        return evaluation_result

    def _translate_goal_to_metrics(self, goal):
        prompt = f"""
        你是一位 UI/UX 设计专家。
        用户希望针对以下目标评估一个移动端 UI 界面：“{goal}”。
        请将这个高层次的概念转化为具体、可衡量的设计指标或要素（例如：对比度、字体大小、留白使用、颜色一致性等）。
        请以逗号分隔的列表形式直接提供答案，不要包含其他解释。
        """
        messages = [{"role": "user", "content": prompt}]
        return self.llm_client.chat_completion(messages)

    def _retrieve_guidelines(self, goal, metrics):
        all_guidelines = self.guideline_manager.get_guidelines_as_text()
        prompt = f"""
        你是一位 UI/UX 设计专家。
        这里有一个设计准则库：
        {all_guidelines}

        本次评估的目标是：“{goal}”。
        相关的设计指标包括：{metrics}。

        请从准则库中筛选出与该目标和这些指标具体相关的准则。
        请以编号列表的形式返回相关的准则内容。
        """
        messages = [{"role": "user", "content": prompt}]
        return self.llm_client.chat_completion(messages)

    def _evaluate_ui(self, image_path, structure_path, goal, selected_guidelines):
        # 如果提供了结构文件则加载
        ui_data = "未提供结构数据"
        data_format = "Text"

        if structure_path:
            try:
                _, ext = os.path.splitext(structure_path)
                ext = ext.lower()
                
                with open(structure_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if ext == '.json':
                    try:
                        # 验证并格式化 JSON
                        ui_data = json.dumps(json.loads(content), indent=2, ensure_ascii=False)
                        data_format = "JSON"
                    except json.JSONDecodeError:
                        print(f"警告: JSON 文件格式错误，将作为普通文本处理")
                        ui_data = content
                        data_format = "Raw Text"
                elif ext in ['.html', '.htm']:
                    ui_data = content
                    data_format = "HTML"
                else:
                    ui_data = content
                    data_format = "Raw Text"
                    
            except Exception as e:
                print(f"警告: 无法加载 UI 结构文件: {e}")

        # 编码图片
        base64_image = self.llm_client.encode_image(image_path)

        prompt = f"""
        你是一位注重细节的 UI/UX 设计专家和前端工程师。
        
        **任务**: 根据选定的设计准则，深度评估提供的 UI 界面图片及其结构数据。你的核心任务是提供**可直接执行的代码级修改建议**。
        
        **评估目标**: {goal}
        
        **参考的设计准则**:
        {selected_guidelines}
        
        **UI 结构数据 ({data_format})**:
        {ui_data}
        
        **指令**:
        1. 仔细分析图片和结构数据（{data_format}）。
        2. 针对参考准则，逐一检查 UI 元素。
        3. **发现问题时，必须提供精确的参数化建议**。严禁使用"适当增加"、"调整颜色"、"优化间距"等模糊词汇。
           - **必须指出具体数值**：例如 "将间距从 10px 增加到 16px"、"将颜色 #AAAAAA 修改为 #595959"。
           - **必须提供具体代码/属性**：如果是 CSS，给出具体的 `color`, `margin`, `font-size`, `border-radius` 等属性值；如果是 JSON，给出修改后的键值对。
           - **解释依据**：简要说明计算过程（例如："#AAAAAA 在 #FFFFFF 背景下对比度仅为 2.3:1，改为 #595959 可达到 4.6:1"）。

        **输出格式要求**:
        请按以下结构列出每个问题（Markdown 格式）：
        
        ### 问题 [编号]: [简短描述]
        - **涉及元素**: [引用 ID/Class/标签]
        - **违反准则**: [准则编号/内容]
        - **问题分析**: [具体数据分析，如当前对比度数值、当前像素间距等]
        - **✅ 精确建议 (执行)**: 
          - "将 `color` 属性修改为 `#595959`"
          - "将 `padding-top` 设置为 `24px` (遵循 8pt 网格)"
          - "将 `border-radius` 设置为 `8px`"

        如果 UI 符合所有准则，请列出关键的具体参数（如"主按钮高度为 48dp，符合准则"）来证明你的判断。
        """

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        return self.llm_client.chat_completion(messages)
