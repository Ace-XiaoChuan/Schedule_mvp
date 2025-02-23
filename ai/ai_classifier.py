import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
import joblib


# joblib 是一个用于 简化并行计算 和 高效序列化大型数据 的 Python 库。

class SimplyClassifier:
    def __init__(self):
        # 关于Pipeline:将多个处理步骤封装成单一对象的工具
        # 第一步：TfidfVectorizer 会将原始文本转换为 TF-IDF 特征矩阵（数值化的向量表示）。
        # 第二步：LinearSVC（支持向量机分类器）会**直接**使用上一步的输出特征进行训练或预测。
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer()),  # 文本转数值——特征提取
            ('clf', LinearSVC())  # 分类器
        ])

    def train(self):
        # 示例数据（后续可替换为文件读取）
        # fit()：教学的过程
        # dump()：让学生把学到的知识写在笔记本上
        # load()：下次直接让学生看笔记本，无需重新教学
        # fit 过程伪代码演示
        # def fit(texts, labels):
        #     # 1. 文本向量化
        #     X = tfidf.fit_transform(texts)  # 生成如下矩阵：
        #     '''
        #     [
        #         [0.5, 0.2, 0.1, ...],  # "完成项目报告" 的向量
        #         [0.3, 0.6, 0.0, ...],  # "编写代码" 的向量
        #         ...
        #     ]
        #     '''
        #
        #     # 2. 训练分类器
        #     clf.fit(X, labels)  # 找到最佳分割超平面
        texts = [
            "完成项目报告", "编写代码", "会议讨论",
            "喝下午茶", "公园散步", "看电影",
            "晚上睡觉", "午间小憩"
        ]
        labels = ["工作", "工作", "工作",
                  "休闲", "休闲", "休闲",
                  "睡眠", "睡眠"]
        print("🔄 开始训练分类器...")  # 调试输出
        self.model.fit(texts, labels)
        # dump())python100d提及，但不仅用于序列化，此处意在模型持久化（Model Persistence）
        joblib.dump(self.model, 'ai/simple_model.pkl')  # 保存模型
        print("✅ 模型训练完成并已保存！")  # 确认训练完成

        # 验证模型是否有效
        test_text = "看电影"
        prediction = self.model.predict([test_text])[0]
        print(f"测试预测 '{test_text}' => {prediction} (预期: 休闲)")

    def predict(self, text):
        model = joblib.load('ai/simple_model.pkl')
        return model.predict([text])[0]
