import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
import joblib
from pathlib import Path


# joblib 是一个用于 简化并行计算 和 高效序列化大型数据 的 Python 库。

class SimpleClassifier:
    def __init__(self):
        # 这个魔术方法用以返回当前**文件**的绝对路径,mmd
        self.script_dir = Path(__file__).parent
        self.data_path = self.script_dir / "tasks.csv"
        self.model_path = self.script_dir / "simple_model.pkl"
        # 调试路径（完成后可删除）
        print(f"数据路径：{self.data_path}")
        print(f"模型路径：{self.model_path}")

        # 关于Pipeline:将多个处理步骤封装成单一对象的工具
        # 第一步：TfidfVectorizer 会将原始文本转换为 TF-IDF 特征矩阵（数值化的向量表示）。
        # 第二步：LinearSVC（支持向量机分类器）会**直接**使用上一步的输出特征进行训练或预测。
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer()),  # 文本转数值——特征提取
            ('clf', LinearSVC())  # 分类器
        ])

    def train(self):
        data = pd.read_csv(self.data_path)
        print(f"成功加载{len(data)}条真实样本数据")
        self.model.fit(data['text'], data['label'])
        joblib.dump(self.model, self.model_path)

    def predict(self, text):
        model = joblib.load('ai/simple_model.pkl')
        return model.predict([text])[0]
